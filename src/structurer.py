import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TextStructurer:
    """
    Converts raw extracted data into a structured DDR-ready JSON.
    Filters noise, checks relevance, cleans sentences, and categorizes by area.
    """

    AREA_SYNONYMS = {
        "Bathroom": ["bathroom", "washroom", "toilet", "bath", "wc", "nahani", "mb bathroom"],
        "Balcony": ["balcony", "deck", "patio"],
        "Terrace": ["terrace", "roof", "top", "overhead"],
        "External Wall": ["external wall", "outer wall", "facade", "wall", "skirting"],
        "Kitchen": ["kitchen", "sink", "utility"],
        "Bedroom": ["bedroom", "master bedroom", "guest bedroom"]
    }
    
    RELEVANT_KEYWORDS = [
        "dampness", "crack", "leakage", "seepage", "efflorescence", 
        "spalling", "vegetation", "gap", "gaps", "hollowness", "water ingress",
        "plumbing", "corrosion", "damage", "wear and tear", "issue"
    ]

    def structure(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Structuring raw text into DDR-ready JSON format.")

        inspection_text = raw_data.get("inspection_text", "")
        thermal_text = raw_data.get("thermal_text", "")
        images = raw_data.get("images", [])

        # Clean and split sentences
        inspection_sentences = self._clean_and_filter(inspection_text)
        thermal_sentences = self._clean_and_filter(thermal_text)
        
        logger.info(f"Cleaned sentences count: {len(inspection_sentences) + len(thermal_sentences)}")

        areas_dict = {}

        # Process area detection
        for area, keywords in self.AREA_SYNONYMS.items():
            insp_findings = self._match_sentences(inspection_sentences, keywords)
            therm_findings = self._match_sentences(thermal_sentences, keywords)

            if insp_findings or therm_findings:
                confidence = "High" if (len(insp_findings) + len(therm_findings)) >= 2 else "Medium"
                areas_dict[area] = {
                    "name": area,
                    "confidence": confidence,
                    "inspection_findings": insp_findings,
                    "thermal_findings": therm_findings,
                    "images": []
                }

        # Gather leftover sentences into General
        assigned_insp = set([f for a in areas_dict.values() for f in a["inspection_findings"]])
        assigned_therm = set([f for a in areas_dict.values() for f in a["thermal_findings"]])
        
        general_insp = [s for s in inspection_sentences if s not in assigned_insp]
        general_therm = [s for s in thermal_sentences if s not in assigned_therm]
        
        if general_insp or general_therm or not areas_dict:
            areas_dict["General"] = {
                "name": "General",
                "confidence": "Low",
                "inspection_findings": general_insp,
                "thermal_findings": general_therm,
                "images": []
            }

        areas_list = list(areas_dict.values())

        # Distribute images cleanly (max 2 per area)
        if areas_list and images:
            for i, img in enumerate(images):
                area_index = i % len(areas_list)
                if len(areas_list[area_index]["images"]) < 2:
                    areas_list[area_index]["images"].append(img["path"])

        for area in areas_list:
            if not area["images"]:
                area["images"] = ["Image Not Available"]

        structured_output = {
            "property_summary": "Not Available",
            "areas": areas_list,
            "root_cause": "Not Available",
            "severity": {
                "level": "Not Available",
                "reason": "Not Available"
            },
            "recommendations": ["Not Available"],
            "missing_info": []
        }

        logger.info("Structuring complete")
        return structured_output

    def _clean_and_filter(self, text: str) -> List[str]:
        if not text:
            return []
            
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        cleaned = []
        
        for s in raw_sentences:
            s = s.strip()
            if not s: continue
            
            s_lower = s.lower()
            
            # Exact noise matching
            if s_lower in ["yes", "no", "not sure", "y", "n", "n/a", "na", "-"]: continue
            if re.match(r'^input\s*1\.\d+', s_lower): continue
            if "page" in s_lower and len(s) < 15: continue
            if "section" in s_lower and len(s) < 15: continue
            if "table of content" in s_lower: continue
            if re.match(r'^(table\s+\d+|header|footer|index)\b', s_lower): continue
            
            # Must contain at least one relevant keyword
            if not any(kw in s_lower for kw in self.RELEVANT_KEYWORDS): continue
            
            # Sentence cleaning - remove leading noisy words
            s = re.sub(r'^(Condition of|Are the|Observed on|Condition:|Observation:|Note:)\s*', '', s, flags=re.IGNORECASE)
            s = re.sub(r'\s+', ' ', s)
            s = s.strip()
            
            if len(s) < 10: continue
            
            s = s[0].upper() + s[1:]
            
            # Transform fragments into proper sentences
            if re.match(r'^mb\s+bathroom', s, re.IGNORECASE):
                s = re.sub(r'^mb\s+bathroom\s+', '', s, flags=re.IGNORECASE)
                if s:
                    s = s[0].upper() + s[1:]
                    if not s.endswith('.') and not s.endswith('?'):
                        s += " observed in the master bathroom."
            
            if not s.endswith('.') and not s.endswith('?'):
                # Basic grammatical append if it looks like a fragment
                if not any(verb in s_lower for verb in ["is", "are", "shows", "observed", "detected", "found", "compromised", "leaked", "cracked", "indicates"]):
                    s += " observed."
                else:
                    s += "."
            
            cleaned.append(s)
            
        return list(dict.fromkeys(cleaned))

    def _match_sentences(self, sentences: List[str], keywords: List[str]) -> List[str]:
        matches = []
        for sentence in sentences:
            if any(kw.lower() in sentence.lower() for kw in keywords):
                matches.append(sentence)
        return matches