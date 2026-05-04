# src/structurer.py

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TextStructurer:
    """
    Converts raw extracted data into a structured DDR-ready JSON.
    """

    # Synonyms for better area detection
    AREA_SYNONYMS = {
        "Living Room": ["living room", "hall", "lounge"],
        "Bedroom": ["bedroom", "bed room"],
        "Kitchen": ["kitchen", "cooking area"],
        "Bathroom": ["bathroom", "washroom", "toilet"],
        "Wall": ["wall", "external wall", "internal wall"],
        "Roof": ["roof", "ceiling", "top slab"],
        "Basement": ["basement", "lower ground"]
    }

    def structure(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Structuring raw text into DDR-ready JSON format.")

        inspection_text = raw_data.get("inspection_text", "")
        thermal_text = raw_data.get("thermal_text", "")
        images = raw_data.get("images", [])

        # Split text into sentences
        inspection_sentences = self._split_sentences(inspection_text)
        thermal_sentences = self._split_sentences(thermal_text)

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

        # Fallback if no areas detected
        if not areas_dict:
            logger.warning("No specific areas detected. Using fallback.")
            areas_dict["General Property"] = {
                "name": "General Property",
                "inspection_findings": inspection_sentences,
                "thermal_findings": thermal_sentences,
                "images": []
            }

        areas_list = list(areas_dict.values())

        # Improved image distribution (round-robin)
        if areas_list:
            for i, img in enumerate(images):
                area_index = i % len(areas_list)
                areas_list[area_index]["images"].append(img["path"])

        # Build DDR structure (LLM will fill later)
        structured_output = {
            "property_summary": "Not Available",
            "areas": areas_list,
            "root_cause": "Not Available",
            "severity": {
                "level": "Not Available",
                "reason": "Not Available"
            },
            "recommendations": [],
            "additional_notes": [],
            "missing_info": []
        }

        return structured_output

    def _split_sentences(self, text: str) -> List[str]:
        """
        Improved sentence splitting.
        Handles ., !, ?, and newlines.
        """
        if not text:
            return []

        sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _match_sentences(self, sentences: List[str], keywords: List[str]) -> List[str]:
        """
        Match sentences containing any keyword.
        """
        matches = []
        for sentence in sentences:
            for kw in keywords:
                if kw.lower() in sentence.lower():
                    matches.append(sentence)
                    break
        return matches