from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class Severity(BaseModel):
    level: str = "Not Available"
    reason: str = "Not Available"

class Area(BaseModel):
    name: str = "General"
    confidence: str = "Medium"
    inspection_findings: List[str] = Field(default_factory=list)
    thermal_findings: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

class DDRSchema(BaseModel):
    property_summary: str = "Not Available"
    areas: List[Area] = Field(default_factory=list)
    root_cause: str = "Not Available"
    severity: Severity = Field(default_factory=Severity)
    recommendations: List[str] = Field(default_factory=lambda: ["Not Available"])
    missing_info: List[str] = Field(default_factory=list)

class SchemaValidator:
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Validating structured data.")
        normalized_data = self.normalize(data)
        try:
            # Enforce structure but DO NOT reject if something is slightly off
            ddr = DDRSchema(**normalized_data)
            return ddr.model_dump()
        except Exception as e:
            logger.error(f"Validation warning (using safe normalized fallback): {e}")
            return normalized_data

    def _normalize_text(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return "Not Available"
        text = text.strip()
        if not text:
            return "Not Available"
        # Capitalize sentence
        text = text[0].upper() + text[1:]
        if not text.endswith('.') and not text.endswith('?'):
            text += "."
        return text

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing values and ensure safe defaults without strict rejection."""
        safe_data = data.copy() if data else {}
        
        safe_data["property_summary"] = self._normalize_text(safe_data.get("property_summary"))
        safe_data["root_cause"] = self._normalize_text(safe_data.get("root_cause"))
        
        recs = safe_data.get("recommendations", [])
        if not recs or not isinstance(recs, list):
            safe_data["recommendations"] = ["Not Available"]
        else:
            safe_data["recommendations"] = [self._normalize_text(r) for r in recs if r and str(r).strip()]
            if not safe_data["recommendations"]:
                safe_data["recommendations"] = ["Not Available"]
            
        sev = safe_data.get("severity", {})
        if not sev or not isinstance(sev, dict):
            safe_data["severity"] = {"level": "Not Available", "reason": "Not Available"}
        else:
            sev["level"] = self._normalize_text(sev.get("level"))
            sev["reason"] = self._normalize_text(sev.get("reason"))
            
        areas = safe_data.get("areas", [])
        if not areas or not isinstance(areas, list):
            safe_data["areas"] = []
        else:
            # Clean text in areas, remove empty strings
            for area in areas:
                area_name = self._normalize_text(area.get("name")).rstrip('.')
                area["name"] = area_name if area_name != "Not Available" else "General"
                
                area["confidence"] = area.get("confidence") or "Medium"
                
                insp = area.get("inspection_findings", [])
                area["inspection_findings"] = list(dict.fromkeys([self._normalize_text(f) for f in insp if f and str(f).strip()]))
                
                therm = area.get("thermal_findings", [])
                area["thermal_findings"] = list(dict.fromkeys([self._normalize_text(f) for f in therm if f and str(f).strip()]))
                
                imgs = area.get("images", [])
                area["images"] = [img for img in imgs if img and str(img).strip()] if imgs else ["Image Not Available"]
                
        return safe_data
