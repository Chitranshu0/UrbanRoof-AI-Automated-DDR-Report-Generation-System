from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Area(BaseModel):
    name: str = "Not Available"
    inspection_findings: List[str] = Field(default_factory=list)
    thermal_findings: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

class DDR(BaseModel):
    property_summary: str = "Not Available"
    areas: List[Area] = Field(default_factory=list)
    root_cause: str = "Not Available"
    severity: Dict[str, str] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def clean_and_check(self) -> 'DDR':
        # Clean duplicates
        for area in self.areas:
            area.inspection_findings = list(dict.fromkeys(area.inspection_findings))
            area.thermal_findings = list(dict.fromkeys(area.thermal_findings))
            
            # Simple missing info / conflict detection
            if "leak" in " ".join(area.inspection_findings).lower() and not area.thermal_findings:
                self.missing_info.append(f"Possible conflict/missing: Leak mentioned in {area.name} inspection but no thermal anomalies found.")
                
            if not area.inspection_findings and not area.thermal_findings:
                self.missing_info.append(f"Missing findings for area: {area.name}")

        # Handle empty fields globally
        if not self.property_summary: self.property_summary = "Not Available"
        if not self.root_cause: self.root_cause = "Not Available"
        if not self.areas: self.missing_info.append("No areas found in the report.")
        
        # Deduplicate missing info
        self.missing_info = list(dict.fromkeys(self.missing_info))
        return self

class SchemaValidator:
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Validating and cleaning data using Pydantic.")
        try:
            ddr = DDR(**data)
            return ddr.model_dump()
        except Exception as e:
            logger.error(f"Validation error: {e}")
            # Fallback to pure dict if strictly needed or bubble error
            return data
