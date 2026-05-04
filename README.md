# UrbanRoof AI Automated DDR Report Generation System

An end-to-end, modular AI pipeline that converts inspection and thermal PDF documents into a structured Detailed Diagnostic Report (DDR).

## 🧱 Architecture

1. **Extractor** (`src/extractor.py`): Uses PyMuPDF to extract text and images from PDFs.
2. **Structurer** (`src/structurer.py`): Converts raw text into a structured JSON representation (rule-based parsing & chunking).
3. **Reasoner** (`src/reasoner.py`): Simulates an LLM to reason over structured data, identifying summary, root causes, severity, and recommendations.
4. **Validator** (`src/validator.py`): Uses Pydantic to strictly enforce schema, detect missing info, and resolve conflicting insights.
5. **Report Generator** (`src/report_generator.py`): Generates a client-ready, clean Markdown DDR file.
6. **Pipeline** (`src/pipeline.py`): Orchestrates all steps using **LangGraph** to ensure a robust, state-based workflow execution.

## 📁 Folder Structure

```
.
├── data/                  # Input PDFs go here
├── images/                # Extracted images
├── outputs/               # Final DDR reports (.md and .json)
├── src/                   # Source code modules
│   ├── extractor.py
│   ├── structurer.py
│   ├── validator.py
│   ├── reasoner.py
│   ├── report_generator.py
│   ├── pipeline.py
├── requirements.txt       # Python dependencies
├── generate_dummy_pdfs.py # Test file generation script
└── README.md              # Project documentation
```

## 🛠️ Setup & Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 How to Run

Place your sample PDF files in the `data/` folder. If you don't have PDFs, you can use the dummy generator!

Run the pipeline CLI from the root folder:
```bash
python src/pipeline.py --inspection data/sample_inspection.pdf --thermal data/sample_thermal.pdf
```

### Example (using generated Dummy PDFs)

We have provided a small script to generate dummy PDFs and a run script if you want to see it in action without bringing your own files! 
```bash
python generate_dummy_pdfs.py
python src/pipeline.py --inspection data/dummy_inspection.pdf --thermal data/dummy_thermal.pdf
```

The output report will be saved to `outputs/DDR_Report.md`, and the raw validated JSON will be at `outputs/sample_output.json`.