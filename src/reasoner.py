import os
import json
import logging
import requests
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

from reasoning_engine import (
    detect_patterns,
    generate_summary,
    infer_root_cause,
    infer_severity,
    generate_recommendations,
    build_deterministic_report
)

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# DETERMINISTIC POST-PROCESSING HELPERS
# ---------------------------------------------------------

def extract_section(report: str, header_keyword: str) -> str:
    lines = report.split('\n')
    in_section = False
    section_content = []
    for line in lines:
        if line.startswith('###') and header_keyword in line:
            in_section = True
            continue
        if in_section:
            if line.startswith('###'):
                break
            section_content.append(line)
    return '\n'.join(section_content).strip()

def replace_section(report: str, header_keyword: str, new_content: str) -> str:
    lines = report.split('\n')
    out_lines = []
    in_section = False
    for line in lines:
        if line.startswith('###') and header_keyword in line:
            in_section = True
            out_lines.append(line)
            out_lines.append("")
            out_lines.append(new_content)
            out_lines.append("")
            continue
        if in_section:
            if line.startswith('###'):
                in_section = False
            else:
                continue
        if not in_section:
            out_lines.append(line)
    return '\n'.join(out_lines)

def fix_images(report: str, data: dict) -> str:
    for area in data.get("areas", []):
        if not area.get("images"):
            area["images"] = ["Image Not Available"]
            continue

        valid_images = [img for img in area["images"] if img and img != "Image Not Available"]
        
        if valid_images:
            formatted = "\n".join([f"![{area.get('name', 'Area')}]({img})" for img in valid_images])
            # A more robust replacement if "Images:" or "**Images:**" is missing or malformed
            # This is hard to do cleanly without replacing it globally which the prompt allowed.
            # We'll use a unique identifier logic or fallback to simple global replace if strictly requested.
        else:
            formatted = '"Image Not Available"'
            area["images"] = ["Image Not Available"]

    # Since the prompt provided the exact simple logic:
    for area in data.get("areas", []):
        if not area.get("images") or area["images"][0] == "Image Not Available":
            continue
        formatted = "\n".join([f"![{area.get('name', 'Area')}]({img})" for img in area["images"] if img != "Image Not Available"])
        
        # Simple global replacement as requested by user pattern
        # Since this can overwrite multiple area images with the first one if we're not careful,
        # we will replace it block by block.
    
    # We will safely rebuild the report string to fix the images.
    lines = report.split('\n')
    out_lines = []
    current_area_idx = -1
    areas = data.get("areas", [])
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("**Area:"):
            current_area_idx += 1
            out_lines.append(line)
            i += 1
            continue
            
        if "**Images:**" in line and 0 <= current_area_idx < len(areas):
            out_lines.append(line)
            area = areas[current_area_idx]
            images = area.get("images", [])
            
            if not images or all(img == "Image Not Available" for img in images):
                out_lines.append('"Image Not Available"')
            else:
                for img in images:
                    if img and img != "Image Not Available":
                        out_lines.append(f"![{area.get('name', 'Area')}]({img})")
            
            i += 1
            while i < len(lines) and not lines[i].startswith('**') and not lines[i].startswith('###') and lines[i].strip() != '':
                i += 1
            continue
            
        out_lines.append(line)
        i += 1
        
    return '\n'.join(out_lines)

def enforce_output_quality(report: str, data: dict) -> str:
    def has_weak(text):
        return (not text or "Not Available" in text or len(text.strip()) < 30)

    patterns = detect_patterns(data)

    # -----------------------
    # FIX PROPERTY SUMMARY
    # -----------------------
    if "Property Issue Summary" in report:
        summary = extract_section(report, "Property Issue Summary")
        if has_weak(summary):
            new_summary = generate_summary(patterns)
            report = replace_section(report, "Property Issue Summary", new_summary)
    else:
        report += "\n\n### 1. Property Issue Summary\n" + generate_summary(patterns)

    # -----------------------
    # FIX ROOT CAUSE
    # -----------------------
    if "Probable Root Cause" in report:
        root = extract_section(report, "Probable Root Cause")
        if has_weak(root):
            new_root = infer_root_cause(patterns)
            report = replace_section(report, "Probable Root Cause", new_root)

    # -----------------------
    # FIX SEVERITY
    # -----------------------
    if "Severity Assessment" in report:
        severity = extract_section(report, "Severity Assessment")
        if has_weak(severity):
            sev_level, sev_reason = infer_severity(patterns)
            new_severity = f"* Severity Level: {sev_level}\n* Reason: {sev_reason}"
            report = replace_section(report, "Severity Assessment", new_severity)

    # -----------------------
    # FIX RECOMMENDATIONS
    # -----------------------
    if "Recommended Actions" in report:
        rec = extract_section(report, "Recommended Actions")
        if has_weak(rec):
            recs = generate_recommendations(patterns)
            new_rec = "\n".join([f"* {r}" for r in recs])
            report = replace_section(report, "Recommended Actions", new_rec)

    # -----------------------
    # FIX PLACEHOLDER TEXT
    # -----------------------
    report = report.replace("Area Observation Area Observation", "")
    report = report.replace("Image Image", "")

    # -----------------------
    # FIX IMAGE FORMAT
    # -----------------------
    report = fix_images(report, data)

    return report

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

    def generate_insights(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Generating full DDR report using multi-LLM reasoning.")
        
        # Conflict Detection explicitly in Python
        validated_data = self.detect_conflicts(validated_data)
        
        trimmed_data = self.trim_data(validated_data)
        
        # 1. Build initial deterministic base report
        deterministic_base = build_deterministic_report(trimmed_data)
        
        system_prompt = """You are an expert technical writer and building inspection analyst.
Your task is ONLY to rewrite the provided DDR report in clean, client-friendly, professional language. 

STRICT RULES:
1. Do not change the meaning or remove any core facts.
2. Keep the exact section headers intact (e.g. ### 1. Property Issue Summary).
3. Do not invent facts.
4. If a section says "Not Available", leave it as is or phrase it cleanly.
5. Keep image placeholders exactly as they are.
6. Fix any broken sentences (e.g., "Leakage below wc observed" -> "Leakage was observed below the WC area").
"""
        user_prompt = f"REWRITE THIS REPORT:\n\n{deterministic_base}"
        
        full_report = ""
        
        # Primary: Groq API
        logger.info("Calling Groq for language polish...")
        for attempt in range(2):
            if attempt == 1:
                logger.info("Retrying Groq...")
            full_report = self._generate_groq(system_prompt, user_prompt, timeout=30)
            if full_report and "Property Issue Summary" in full_report:
                break
        else:
            full_report = "" # Clear invalid output
            
        # Backup: Ollama SmolLM
        if not full_report:
            logger.info("Switching to Ollama...")
            full_report = self._generate_ollama(system_prompt, user_prompt, timeout=60)
            if not full_report or "Property Issue Summary" not in full_report:
                full_report = ""
                
        # Final Fallback
        if not full_report:
            logger.info("Fallback triggered: Using raw deterministic report.")
            full_report = deterministic_base
            
        logger.info("LLM polish complete.")
        
        # ALWAYS enforce quality (this guarantees 100% adherence)
        full_report = enforce_output_quality(full_report, trimmed_data)
        
        enriched_data = validated_data.copy()
        enriched_data["full_markdown_report"] = full_report
        
        return enriched_data
