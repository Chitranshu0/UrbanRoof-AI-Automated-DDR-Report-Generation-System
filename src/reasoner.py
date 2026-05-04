import os
import json
import logging
import requests
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
        self.client = Groq(api_key=self.api_key) if self.api_key else Groq()
        self.model_name = model_name
        
    def _generate_groq(self, system_prompt: str, user_prompt: str, timeout: int = 30) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.1,
                timeout=timeout
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return ""

    def _generate_ollama(self, system_prompt: str, user_prompt: str, timeout: int = 60) -> str:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "smollm:latest",
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return ""

    def _validate_output(self, text: str) -> bool:
        if not text or len(text) < 150:
            return False
        required_sections = [
            "Property Issue Summary",
            "Area-wise Observations"
        ]
        return all(section in text for section in required_sections)

    def trim_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        import copy
        trimmed = copy.deepcopy(data)
        for area in trimmed.get("areas", []):
            insp = [f for f in area.get("inspection_findings", []) if f]
            therm = [f for f in area.get("thermal_findings", []) if f]
            imgs = [img for img in area.get("images", []) if img and img != "Image Not Available"]
            
            area["inspection_findings"] = insp[:3]
            area["thermal_findings"] = therm[:3]
            area["images"] = imgs[:2] if imgs else ["Image Not Available"]
        return trimmed

    def detect_conflicts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect discrepancies between inspection and thermal data."""
        if "missing_info" not in data:
            data["missing_info"] = []
            
        for area in data.get("areas", []):
            insp = area.get("inspection_findings", [])
            therm = area.get("thermal_findings", [])
            
            if insp and not therm:
                # Add conflict
                area_name = area.get("name", "this area")
                conflict_msg = f"Conflict: Inspection indicates issues in {area_name} but thermal data does not confirm a clear anomaly. This may indicate intermittent or concealed leakage."
                if conflict_msg not in data["missing_info"]:
                    data["missing_info"].append(conflict_msg)
        return data

    def fallback_report(self, data: Dict[str, Any]) -> str:
        """Generates a safe fallback report if ALL LLMs fail completely."""
        lines = ["# Detailed Diagnostic Report\n"]
        
        lines.append("### 1. Property Issue Summary")
        lines.append(data.get("property_summary", "Not Available") + "\n")
        
        lines.append("### 2. Area-wise Observations")
        for area in data.get("areas", []):
            lines.append(f"**Area: {area.get('name', 'General')}**")
            for f in area.get("inspection_findings", []):
                lines.append(f"* {f}")
            if not area.get("inspection_findings"):
                lines.append("* Not Available")
                
            lines.append("\n**Thermal Insights:**")
            for f in area.get("thermal_findings", []):
                lines.append(f"* {f}")
            if not area.get("thermal_findings"):
                lines.append("* Not Available")
                
            lines.append("\n**Images:**")
            for img in area.get("images", []):
                if img == "Image Not Available":
                    lines.append('"Image Not Available"')
                else:
                    lines.append(f"* {img}")
            lines.append("")
            
        lines.append("### 3. Probable Root Cause")
        lines.append(data.get("root_cause", "Not Available") + "\n")
        
        lines.append("### 4. Severity Assessment")
        sev = data.get("severity", {})
        lines.append(f"* Severity Level: {sev.get('level', 'Not Available')}")
        lines.append(f"* Reason: {sev.get('reason', 'Not Available')}\n")
        
        lines.append("### 5. Recommended Actions")
        for r in data.get("recommendations", []):
            lines.append(f"* {r}")
        if not data.get("recommendations"):
            lines.append("* Not Available")
        lines.append("")
            
        lines.append("### 6. Additional Notes")
        lines.append("Generated via automated fallback due to LLM reasoning failures.\n")
        
        lines.append("### 7. Missing or Unclear Information")
        for m in data.get("missing_info", []):
            lines.append(f"* {m}")
        if not data.get("missing_info"):
            lines.append("* None reported.")
            
        return "\n".join(lines)

    def generate_insights(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Generating full DDR report using multi-LLM reasoning.")
        
        # Conflict Detection explicitly in Python
        validated_data = self.detect_conflicts(validated_data)
        
        trimmed_data = self.trim_data(validated_data)
        structured_json = json.dumps(trimmed_data.get("areas", []), indent=2)
        
        system_prompt = """You are a professional building inspection expert.

Your task is to perform Two-Stage Reasoning:
STAGE 1: Insight Extraction
First, analyze the data to extract key issues per area, moisture patterns, and thermal anomalies.

STAGE 2: DDR Generation
Then, generate a Detailed Diagnostic Report (DDR) using those insights.

STRICT RULES:
* Use ONLY provided data. DO NOT invent facts.
* If partial data exists -> infer cautiously. If missing -> "Not Available".
* Language must be simple, client-friendly English. No jargon. No incomplete sentences. Example: instead of "Leakage below wc observed", write "Leakage observed below the WC area."
* Logical Linking: Ensure a logical flow from Observation -> Cause -> Action.

### OUTPUT FORMAT (MANDATORY EXACT SECTIONS)

### 1. Property Issue Summary
-> Summarize major issues.

### 2. Area-wise Observations
For each area:
**Area: <Area Name>**
* <Observation sentence>
**Thermal Insights:**
* <Thermal insight>
**Images:**
* <exact_image_path_from_input>
* <exact_image_path_from_input>
OR
"Image Not Available"

### 3. Probable Root Cause
-> Link defects to the findings logically.

### 4. Severity Assessment
* Severity Level: Low / Medium / High
* Reason: based on spread + persistence

### 5. Recommended Actions
-> Practical fixes clearly linked to the root causes.

### 6. Additional Notes
-> Mention any additional insights or correlation.

### 7. Missing or Unclear Information
-> List any missing data or conflicts detected."""

        user_prompt = f"INPUT DATA:\n{structured_json}"
        
        full_report = ""
        
        # Primary: Groq API
        logger.info("Calling Groq...")
        for attempt in range(2):
            if attempt == 1:
                logger.info("Retrying Groq...")
            full_report = self._generate_groq(system_prompt, user_prompt, timeout=30)
            if self._validate_output(full_report):
                break
        else:
            full_report = "" # Clear invalid output
            
        # Backup: Ollama SmolLM
        if not full_report:
            logger.info("Switching to Ollama...")
            full_report = self._generate_ollama(system_prompt, user_prompt, timeout=60)
            if not self._validate_output(full_report):
                full_report = ""
                
        # Final Fallback
        if not full_report:
            logger.info("Fallback triggered")
            full_report = self.fallback_report(trimmed_data)
            
        logger.info("LLM response received")
        
        enriched_data = validated_data.copy()
        enriched_data["full_markdown_report"] = full_report
        
        return enriched_data
