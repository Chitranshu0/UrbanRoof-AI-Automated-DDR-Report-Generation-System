import os
import json
import logging
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ReportReasoner:
    def __init__(self, model_name: str = "llama3-8b-8192"):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment. Please set it in your .env file.")
        # Groq client will automatically look for GROQ_API_KEY in env if not passed explicitly,
        # but passing it ensures we can handle the case where it might be loaded manually via load_dotenv.
        self.client = Groq(api_key=self.api_key) if self.api_key else Groq()
        self.model_name = model_name
        
    def _generate(self, prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior building inspection AI expert. Respond directly with the requested output based STRICTLY on the provided data. No conversational filler. No hallucination. If data is insufficient, respond with 'Not Available'."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.1, # Low temperature for factual consistency
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "Not Available"

    def generate_insights(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Generating insights using Groq API reasoning.")
        
        areas_json = json.dumps(validated_data.get("areas", []), indent=2)
        
        # Prompt Templates (Strict)
        summary_prompt = f"Generate a concise Property Summary using ONLY the following structured data:\n{areas_json}\nIf missing -> 'Not Available'."
        root_cause_prompt = f"Analyze the findings and determine the probable root cause from this data:\n{areas_json}\nIf there is a conflict -> mention it explicitly. If missing -> 'Not Available'."
        severity_prompt = f"Classify severity: Low, Medium, or High with reasoning based on this data:\n{areas_json}\nReturn ONLY a valid JSON object in this format: {{\"level\": \"High/Medium/Low/Not Available\", \"reason\": \"your reason\"}}."
        recommendations_prompt = f"Provide practical repair actions based on this data:\n{areas_json}\nReturn ONLY a valid JSON array of strings. No generic advice. If missing -> [\"Not Available\"]."
        
        # Generation calls
        summary = self._generate(summary_prompt)
        root_cause = self._generate(root_cause_prompt)
        
        try:
            severity_text = self._generate(severity_prompt)
            # Find JSON block if wrapped in markdown
            if "{" in severity_text:
                severity_text = severity_text[severity_text.find("{"):severity_text.rfind("}")+1]
            severity = json.loads(severity_text)
        except Exception as e:
            logger.error(f"Failed to parse severity. Error: {e}. Output was: {severity_text if 'severity_text' in locals() else 'None'}")
            severity = {"level": "Not Available", "reason": "Failed to generate"}
            
        try:
            recs_text = self._generate(recommendations_prompt)
            # Find JSON block if wrapped in markdown
            if "[" in recs_text:
                recs_text = recs_text[recs_text.find("["):recs_text.rfind("]")+1]
            recommendations = json.loads(recs_text)
        except Exception as e:
            logger.error(f"Failed to parse recommendations. Error: {e}. Output was: {recs_text if 'recs_text' in locals() else 'None'}")
            recommendations = ["Not Available"]
            
        # Merge AI generated insights back into our data structure
        enriched_data = validated_data.copy()
        enriched_data["property_summary"] = summary
        enriched_data["root_cause"] = root_cause
        enriched_data["severity"] = severity
        enriched_data["recommendations"] = recommendations
        
        return enriched_data
