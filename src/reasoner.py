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
        self.client = Groq(api_key=self.api_key) if self.api_key else Groq()
        self.model_name = model_name
        
    def _generate(self, system_prompt: str, user_prompt: str) -> str:
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
                temperature=0.1, # Low temperature for factual consistency
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "Report Generation Failed."

    def trim_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        import copy
        trimmed = copy.deepcopy(data)
        for area in trimmed.get("areas", []):
            area["inspection_findings"] = area.get("inspection_findings", [])[:5]
            area["thermal_findings"] = area.get("thermal_findings", [])[:5]
            area["images"] = area.get("images", [])[:3]
        return trimmed

    def fallback_report(self, data: Dict[str, Any]) -> str:
        """Generates a safe fallback report if LLM fails completely."""
        lines = ["# Detailed Diagnostic Report (Fallback)\n"]
        
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
        lines.append("")
            
        lines.append("### 6. Additional Notes")
        lines.append("Generated via automated fallback due to LLM reasoning failure.\n")
        
        lines.append("### 7. Missing or Unclear Information")
        for m in data.get("missing_info", []):
            lines.append(f"* {m}")
        if not data.get("missing_info"):
            lines.append("* None reported.")
            
        return "\n".join(lines)

    def generate_insights(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Generating full DDR report using Groq API reasoning.")
        
        # Trim data before formatting into JSON string
        trimmed_data = self.trim_data(validated_data)
        structured_json = json.dumps(trimmed_data.get("areas", []), indent=2)
        
        system_prompt = """You are a professional building inspection analyst AI.

Your task is to convert structured inspection and thermal data into a clean, client-ready DDR (Detailed Diagnostic Report).

## ⚠️ CRITICAL RULES (STRICTLY FOLLOW)
1. DO NOT invent any facts.
2. ONLY use information present in input.
3. If information is missing -> write "Not Available".
4. If there is conflicting information -> explicitly mention the conflict.
5. Remove noise, incomplete phrases, and irrelevant text.
6. Merge duplicate observations into one clean statement.
7. Use simple, client-friendly language (non-technical).
8. Ensure logical consistency between inspection and thermal findings.

## 🧠 PROCESSING REQUIREMENTS

### Step 1: Clean Data
* Remove incomplete phrases (e.g., "of Flat No.")
* Remove repeated entries
* Convert broken sentences into meaningful observations

### Step 2: Logical Merging
* Combine inspection + thermal findings
* Group by area
* Align temperature anomalies with physical issues

### Step 3: Image Handling
* Attach ONLY relevant images to each area
* If too many -> select most relevant ones
* If no image available -> write "Image Not Available"
* Output the exact image path string provided in the input under the Images section.

## 📄 OUTPUT FORMAT (STRICT)
Generate output EXACTLY in this format:

### 1. Property Issue Summary
Provide a concise summary of major issues observed across the property.

### 2. Area-wise Observations
For each area:
**Area: <Area Name>**
* Observation 1
* Observation 2

**Thermal Insights:**
* Insight 1
* Insight 2

**Images:**
* <image_path_1>
* <image_path_2>
OR
"Image Not Available"

### 3. Probable Root Cause
Explain the likely cause of the issues based ONLY on observations.

### 4. Severity Assessment (with reasoning)
* Severity Level: Low / Medium / High
* Reason: Explain clearly based on findings

### 5. Recommended Actions
Provide practical and actionable repair steps.

### 6. Additional Notes
Include any extra useful information.

### 7. Missing or Unclear Information
Explicitly list:
* Missing data
* Conflicts between inspection and thermal reports"""

        user_prompt = f"INPUT DATA:\n{structured_json}"
        
        full_report = ""
        # Validation loop
        for attempt in range(2):
            full_report = self._generate(system_prompt, user_prompt)
            # Check validity
            if full_report and len(full_report) > 100 and "Property Issue Summary" in full_report:
                break
            logger.warning(f"LLM output invalid or too short on attempt {attempt+1}. Regenerating...")
        else:
            logger.error("LLM failed completely. Using fallback report generator.")
            full_report = self.fallback_report(trimmed_data)
            
        logger.info("LLM response received / fallback executed")
        
        # Merge back
        enriched_data = validated_data.copy()
        enriched_data["full_markdown_report"] = full_report
        
        return enriched_data
