import fitz
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, output_image_dir: str = "images"):
        self.output_image_dir = output_image_dir
        os.makedirs(self.output_image_dir, exist_ok=True)
    
    def extract(self, inspection_pdf: str, thermal_pdf: str) -> Dict[str, Any]:
        logger.info("Extracting data from inspection and thermal PDFs.")
        
        inspection_text, insp_images = self._extract_pdf(inspection_pdf, "insp")
        thermal_text, therm_images = self._extract_pdf(thermal_pdf, "therm")
        
        return {
            "inspection_text": inspection_text,
            "thermal_text": thermal_text,
            "images": insp_images + therm_images
        }
        
    def _extract_pdf(self, pdf_path: str, prefix: str):
        if not os.path.exists(pdf_path):
            logger.warning(f"File not found: {pdf_path}")
            return "", []
            
        text = ""
        images = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                
                # Extract images
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_filename = f"{prefix}_p{page_num+1}_img{img_index}.{image_ext}"
                    image_filepath = os.path.join(self.output_image_dir, image_filename)
                    
                    with open(image_filepath, "wb") as f:
                        f.write(image_bytes)
                        
                    images.append({"path": image_filepath, "page": page_num + 1, "source": prefix})
        except Exception as e:
            logger.error(f"Error extracting from {pdf_path}: {str(e)}")
            
        return text, images
