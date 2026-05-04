# src/validator.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Severity(BaseModel):
    level: str = "Not Available"
    reason: str = "Not Available"

class Area(BaseModel):
    name: str = "General"
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
            # Enforce structure but DO NOT fail if fields are missing (Pydantic will use defaults)
            ddr = DDRSchema(**normalized_data)
            return ddr.model_dump()
        except Exception as e:
            logger.error(f"Validation warning (safe fallback used): {e}")
            return normalized_data

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing values and ensure safe defaults without strict rejection."""
        safe_data = data.copy()
        
        safe_data["property_summary"] = safe_data.get("property_summary") or "Not Available"
        safe_data["root_cause"] = safe_data.get("root_cause") or "Not Available"
        
        recs = safe_data.get("recommendations", [])
        if not recs:
            safe_data["recommendations"] = ["Not Available"]
            
        sev = safe_data.get("severity", {})
        if not sev or not isinstance(sev, dict):
            safe_data["severity"] = {"level": "Not Available", "reason": "Not Available"}
        else:
            sev["level"] = sev.get("level") or "Not Available"
            sev["reason"] = sev.get("reason") or "Not Available"
            
        areas = safe_data.get("areas", [])
        for area in areas:
            if not area.get("images"):
                area["images"] = ["Image Not Available"]
                
        return safe_data
