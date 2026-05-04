import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate(self, valid_ddr: Dict[str, Any], filename: str = "DDR_Report.md") -> str:
        logger.info(f"Generating final DDR report: {filename}")
        
        md_content = ["# Detailed Diagnostic Report (DDR)\n"]
        
        # 1. Property Issue Summary
        md_content.append("## 1. Property Issue Summary")
        md_content.append(f"{valid_ddr.get('property_summary', 'Not Available')}\n")
        
        # 2. Area-wise Observations
        md_content.append("## 2. Area-wise Observations")
        areas = valid_ddr.get("areas", [])
        if not areas:
            md_content.append("No area-wise data available.\n")
        for area in areas:
            md_content.append(f"### {area.get('name', 'Unknown Area')}")
            
            md_content.append("**Inspection Findings:**")
            if area.get('inspection_findings'):
                for f in area['inspection_findings']:
                    md_content.append(f"- {f}")
            else:
                md_content.append("- Not Available")
            md_content.append("")
            
            md_content.append("**Thermal Findings:**")
            if area.get('thermal_findings'):
                for f in area['thermal_findings']:
                    md_content.append(f"- {f}")
            else:
                md_content.append("- Not Available")
            md_content.append("")
            
            md_content.append("**Images:**")
            images = area.get('images', [])
            if images:
                for img in images:
                    # Render Markdown image. Assuming run from root directory
                    rel_img_path = os.path.join("..", img)
                    md_content.append(f"![Image]({rel_img_path})")
            else:
                md_content.append("Image Not Available")
            md_content.append("\n")
            
        # 3. Probable Root Cause
        md_content.append("## 3. Probable Root Cause")
        md_content.append(f"{valid_ddr.get('root_cause', 'Not Available')}\n")
        
        # 4. Severity Assessment
        md_content.append("## 4. Severity Assessment")
        severity = valid_ddr.get('severity', {})
        md_content.append(f"**Level:** {severity.get('level', 'Not Available')}  ")
        md_content.append(f"**Reason:** {severity.get('reason', 'Not Available')}\n")
        
        # 5. Recommended Actions
        md_content.append("## 5. Recommended Actions")
        recs = valid_ddr.get('recommendations', [])
        if recs:
            for r in recs:
                md_content.append(f"- {r}")
        else:
            md_content.append("- Not Available")
        md_content.append("\n")
        
        # 6. Additional Notes & 7. Missing Information
        md_content.append("## 6. Missing Information & Conflicts")
        missing = valid_ddr.get('missing_info', [])
        if missing:
            for m in missing:
                md_content.append(f"- {m}")
        else:
            md_content.append("- None reported.")
            
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))
            
        logger.info(f"Report saved to {output_path}")
        return output_path
