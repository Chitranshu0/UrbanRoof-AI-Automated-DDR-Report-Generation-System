import argparse
import logging
import json
import os
import sys
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

# Ensure src module is in path so absolute imports work regardless of entry point
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor import PDFExtractor
from structurer import TextStructurer
from reasoner import ReportReasoner
from validator import SchemaValidator
from report_generator import ReportGenerator

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Pipeline")

# Define Graph State for LangGraph
class PipelineState(TypedDict):
    inspection_pdf: str
    thermal_pdf: str
    raw_data: Dict[str, Any]
    structured_data: Dict[str, Any]
    enriched_data: Dict[str, Any]
    validated_data: Dict[str, Any]
    report_path: str

class DDRPipeline:
    def __init__(self):
        self.extractor = PDFExtractor(output_image_dir="images")
        self.structurer = TextStructurer()
        self.reasoner = ReportReasoner()
        self.validator = SchemaValidator()
        self.report_generator = ReportGenerator(output_dir="outputs")
        self.graph = self._build_graph()

    def _build_graph(self):
        logger.info("Building LangGraph workflow orchestration.")
        workflow = StateGraph(PipelineState)

        # Define Nodes
        def extract_node(state: PipelineState):
            raw = self.extractor.extract(state["inspection_pdf"], state["thermal_pdf"])
            logger.info("extraction complete")
            return {"raw_data": raw}

        def structure_node(state: PipelineState):
            structured = self.structurer.structure(state["raw_data"])
            logger.info("Structuring complete")
            logger.info("Clean data ready")
            return {"structured_data": structured}

        def validate_node(state: PipelineState):
            validated = self.validator.validate(state["structured_data"])
            return {"validated_data": validated}

        def reason_node(state: PipelineState):
            enriched = self.reasoner.generate_insights(state["validated_data"])
            logger.info("LLM response received")
            return {"enriched_data": enriched}

        def generate_report_node(state: PipelineState):
            path = self.report_generator.generate(state["enriched_data"])
            logger.info("report generated")
            return {"report_path": path}

        # Add Nodes
        workflow.add_node("extract", extract_node)
        workflow.add_node("structure", structure_node)
        workflow.add_node("validate", validate_node)
        workflow.add_node("reason", reason_node)
        workflow.add_node("generate_report", generate_report_node)

        # Set Edges
        workflow.set_entry_point("extract")
        workflow.add_edge("extract", "structure")
        workflow.add_edge("structure", "validate")
        workflow.add_edge("validate", "reason")
        workflow.add_edge("reason", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def run(self, inspection_pdf: str, thermal_pdf: str):
        try:
            logger.info("Starting pipeline execution.")
            
            # Initial State
            initial_state = {
                "inspection_pdf": inspection_pdf,
                "thermal_pdf": thermal_pdf,
                "raw_data": {},
                "structured_data": {},
                "enriched_data": {},
                "validated_data": {},
                "report_path": ""
            }
            
            # Execute workflow
            result = self.graph.invoke(initial_state)
            
            logger.info(f"Pipeline finished successfully. Report at: {result['report_path']}")
            
            # Save final enriched JSON output for tracking
            os.makedirs("outputs", exist_ok=True)
            with open("outputs/sample_output.json", "w", encoding="utf-8") as f:
                json.dump(result["enriched_data"], f, indent=2)
                
            return result
        except Exception as e:
            print("ERROR:", str(e))
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
