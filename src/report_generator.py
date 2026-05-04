import os
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate(self, enriched_data: Dict[str, Any], filename: str = "DDR_Report.md") -> str:
        logger.info(f"Formatting and saving final DDR report: {filename}")
        
        md_content = enriched_data.get("full_markdown_report", "")
        
        if not md_content:
            md_content = "# Error\n\nReport generation failed. Please check the AI reasoning step."
            
        # Post-process the markdown to wrap raw image paths into actual markdown image tags
        lines = md_content.split("\n")
        processed_lines = []
        for line in lines:
            # If line is an image path (contains .png/.jpg/.jpeg) but isn't already a markdown image tag
            if re.search(r'\.(png|jpeg|jpg)$', line.strip().lower()) and not line.strip().startswith('!['):
                # Clean up bullets or extra spaces
                clean_path = line.replace('*', '').strip()
                processed_lines.append(f"![Image]({clean_path})")
            else:
                processed_lines.append(line)
                
        final_md = "\n".join(processed_lines)
            
        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_md)
            
        logger.info(f"Report saved to {output_path}")
        return output_path
