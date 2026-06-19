# 🏠 UrbanRoof AI – DDR Report Generation System

### (AI/ML Intern – Applied AI & Creative Systems Assessment Submission)

---

## 🌐 Live Application Preview

👉 Live Demo:
https://super-space-dollop-9v5g7pj4rvw39vx5-8501.app.github.dev/

🎥 Loom Walkthrough:
https://www.loom.com/share/6a4fa08b750942bfb4228b4a931f22f0

---

> 🚀 Live AI system that converts raw inspection reports into structured DDR outputs in real-time.

---

## 👨‍💻 Candidate Details

**Name:** Chitranshu Sanket

🔗 LinkedIn: https://www.linkedin.com/in/chitranshu-sanket/

---

## 📌 Assignment Context

This project was developed as part of the **AI/ML Intern – Applied AI & Creative Systems Assessment**.

### 🎯 Objective

To design and build an AI system that:

* Converts **raw inspection data** into a **structured DDR report**
* Demonstrates **real-world AI workflow design**
* Handles **imperfect, noisy, and incomplete data**

---

## 🚀 What I Built

I developed an **end-to-end AI pipeline** that:

* Extracts information from inspection and thermal reports
* Structures unorganized text into meaningful categories
* Applies reasoning to infer root causes and severity
* Generates a **client-ready Detailed Diagnostic Report (DDR)**

---

## 🧠 Key Design Philosophy

Instead of relying purely on LLMs, I built a:

👉 **Hybrid AI System (Rule-Based + LLM)**

This ensures:

* Reliability
* Reduced hallucinations
* Consistent outputs
* Better control over reasoning

---

## ⚙️ System Architecture

```text
PDF Input
   ↓
Text & Image Extraction (PyMuPDF)
   ↓
Structuring Engine (Custom Parsing)
   ↓
Validation Layer (Pydantic)
   ↓
Rule-Based Reasoning Engine
   ↓
LLM Refinement (Groq)
   ↓
Report Generator
   ↓
Streamlit Interface
```

---

## 🔍 How This Solves the Assignment Task

### ✔ Extract Relevant Observations

* Custom parsing and keyword grouping
* Area-wise issue extraction

### ✔ Combine Inspection & Thermal Data

* Unified structured data model
* Merging of observations from multiple report sources

### ✔ Avoid Duplicate Findings

* Deduplication logic during preprocessing

### ✔ Handle Missing or Conflicting Data

* Explicit conflict detection
* Missing information highlighted in final report

### ✔ Client-Friendly Report Generation

* Structured DDR format
* Readable and actionable output

### ✔ Include Images

* Images extracted from PDFs
* Associated with relevant observations
* Fallback handling when images are unavailable

### ✔ Prevent Hallucinated Information

* Rule-based reasoning relies only on extracted evidence
* LLM used solely for report refinement

### ✔ Generalize to Similar Reports

* Keyword-driven and structure-aware processing
* Not hardcoded to specific sample files

---

## 📊 DDR Output Structure

The generated report includes:

1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

---

## 🧠 Core Technical Components

### 1. Extraction Layer

* PyMuPDF for text extraction
* Image extraction from source PDFs

### 2. Structuring Engine

* Converts raw content into structured JSON
* Area-wise grouping and cleaning
* Noise reduction and normalization

### 3. Validation Layer

* Pydantic schema validation
* Consistent output structure
* Improved pipeline reliability

### 4. Reasoning Engine

#### Rule-Based Intelligence

Detects patterns such as:

* Dampness
* Leakage
* Cracks
* Water ingress
* Structural concerns

Infers:

* Root causes
* Severity levels
* Recommended actions

#### LLM Integration (Groq)

Used only for:

* Language refinement
* Report polishing
* Readability enhancement

### 5. Report Generator

* Generates clean Markdown DDR reports
* Maintains a consistent and professional structure

### 6. User Interface

Built with Streamlit:

* Upload PDF reports
* Run DDR generation
* View extracted structured data
* Download generated reports

---

## 🛠️ Tech Stack

* Python
* Streamlit
* PyMuPDF
* Pydantic
* Groq API
* Custom Rule-Based Reasoning Engine

---

## 🎯 Evaluation Criteria Mapping

| Criteria                  | Implementation                          |
| ------------------------- | --------------------------------------- |
| Accuracy                  | Structured extraction + validation      |
| Logical Merging           | Combined inspection and thermal reports |
| Missing/Conflict Handling | Explicit rule-based handling            |
| Clarity                   | Clean DDR output                        |
| System Thinking           | Modular AI pipeline                     |

---

## ⚠️ Current Limitations

* Image mapping is heuristic-based
* OCR is not implemented for scanned PDFs
* Thermal report quality affects extraction accuracy
* Reasoning rules can be expanded for broader coverage

---

## 🚀 Future Improvements

* OCR integration for scanned reports
* Advanced image-to-observation mapping
* API deployment for enterprise workflows
* Enhanced anomaly detection
* Multi-report comparison support

---

## 🎥 Submission Links

### 🔗 GitHub Repository

https://github.com/Chitranshu0/UrbanRoof-AI-Automated-DDR-Report-Generation-System

### 🌐 Live Demo

https://super-space-dollop-9v5g7pj4rvw39vx5-8501.app.github.dev/

### 🎥 Loom Demonstration

https://www.loom.com/share/6a4fa08b750942bfb4228b4a931f22f0

---

## 💡 Key Learning

This project demonstrates my ability to:

* Design practical AI systems
* Build reliable data processing pipelines
* Combine rule-based reasoning with LLM capabilities
* Handle messy and incomplete real-world data
* Focus on robustness and maintainability

---

## 🙌 Final Note

This assessment was an opportunity to demonstrate not only AI implementation skills but also system design thinking, reliability-focused engineering, and practical problem-solving. The solution prioritizes structured reasoning, maintainability, and real-world applicability over complexity for complexity’s sake.

---
