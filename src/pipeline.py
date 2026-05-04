import argparse
import logging
import json
import os
import sys
from typing import Dict, Any

# Ensure src module is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor import PDFExtractor
from structurer import TextStructurer
from reasoner import ReportReasoner
from validator import SchemaValidator
from report_generator import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Pipeline")


class DDRPipeline:
    def __init__(self):
        self.extractor = PDFExtractor(output_image_dir="images")
        self.structurer = TextStructurer()
        self.validator = SchemaValidator()
        self.reasoner = ReportReasoner()
        self.report_generator = ReportGenerator(output_dir="outputs")

    def run(self, inspection_pdf: str, thermal_pdf: str) -> Dict[str, Any]:
        try:
            logger.info("Starting pipeline execution...")

            # -----------------------
            # STEP 1: Extract
            # -----------------------
            raw_data = self.extractor.extract(inspection_pdf, thermal_pdf)
            logger.info("Extraction complete")

            # -----------------------
            # STEP 2: Structure
            # -----------------------
            structured_data = self.structurer.structure(raw_data)
            logger.info("Structuring complete")

            # -----------------------
            # STEP 3: Validate
            # -----------------------
            validated_data = self.validator.validate(structured_data)
            logger.info("Validation complete")

            # -----------------------
            # STEP 4: Reasoning
            # -----------------------
            enriched_data = self.reasoner.generate_insights(validated_data)
            logger.info("Reasoning complete")

            # -----------------------
            # STEP 5: Generate Report
            # -----------------------
            report_path = self.report_generator.generate(enriched_data)
            logger.info(f"Report generated at: {report_path}")

            # -----------------------
            # Save JSON output
            # -----------------------
            os.makedirs("outputs", exist_ok=True)
            with open("outputs/sample_output.json", "w", encoding="utf-8") as f:
                json.dump(enriched_data, f, indent=2)

            return {
                "raw_data": raw_data,
                "structured_data": structured_data,
                "validated_data": validated_data,
                "enriched_data": enriched_data,
                "report_path": report_path
            }

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Automated DDR Report Generation Pipeline")
    parser.add_argument("--inspection", required=True, help="Path to inspection PDF")
    parser.add_argument("--thermal", required=True, help="Path to thermal PDF")
    args = parser.parse_args()

    pipeline = DDRPipeline()
    pipeline.run(args.inspection, args.thermal)


if __name__ == "__main__":
    main()