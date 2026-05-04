# src/structurer.py
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TextStructurer:
    """
    Converts raw extracted data into a structured DDR-ready JSON.
    Filters noise, checks relevance, and categorizes by area.
    """

    AREA_SYNONYMS = {
        "Bathroom": ["bathroom", "washroom", "toilet", "bath"],
        "Balcony": ["balcony", "deck"],
        "Terrace": ["terrace", "roof", "top"],
        "External Wall": ["external wall", "outer wall", "facade", "wall"],
    }
    
    RELEVANT_KEYWORDS = [
        "dampness", "crack", "leakage", "seepage", "efflorescence", 
        "spalling", "vegetation", "gap", "gaps", "hollowness", "water ingress"
    ]
    
    NOISE_KEYWORDS = [
        "section", "page", "table of content", "input 1", 
        "yes", "no", "not sure"
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
                areas_dict[area] = {
                    "name": area,
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
                "inspection_findings": general_insp,
                "thermal_findings": general_therm,
                "images": []
            }

        areas_list = list(areas_dict.values())

        # Improved image distribution (round-robin) up to 3 per area
        if areas_list and images:
            for i, img in enumerate(images):
                area_index = i % len(areas_list)
                if len(areas_list[area_index]["images"]) < 3:
                    areas_list[area_index]["images"].append(img["path"])

        # Mark "Image Not Available" for areas with no images
        for area in areas_list:
            if not area["images"]:
                area["images"] = ["Image Not Available"]

        # Build final expected structure
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

        logger.info("structuring complete")
        return structured_output

    def _clean_and_filter(self, text: str) -> List[str]:
        if not text:
            return []
            
        # Split sentences
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        cleaned = []
        
        for s in raw_sentences:
            s = s.strip()
            # Basic noise filtering
            if len(s) < 20: continue
            
            s_lower = s.lower()
            if any(noise in s_lower for noise in self.NOISE_KEYWORDS): continue
            
            # Relevance filtering
            if not any(kw in s_lower for kw in self.RELEVANT_KEYWORDS): continue
            
            # Fix broken sentences/spaces (e.g. "of Flat No.")
            s = re.sub(r'\s+', ' ', s)
            if "of flat no" in s_lower and len(s) < 30: continue
            
            cleaned.append(s)
            
        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned))

    def _match_sentences(self, sentences: List[str], keywords: List[str]) -> List[str]:
        matches = []
        for sentence in sentences:
            if any(kw.lower() in sentence.lower() for kw in keywords):
                matches.append(sentence)
        return matches