# 🏠 UrbanRoof AI – DDR Report Generation System  
### (AI Generalist | Applied AI Builder Assignment Submission)

---

## 🌐 Live Application Preview

👉 https://urbanroof-ai-automated-ddr-report-generation-system.streamlit.app/

[![Open App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://urbanroof-ai-automated-ddr-report-generation-system.streamlit.app/)

---

> 🚀 Live AI system that converts raw inspection reports into structured DDR outputs in real-time.
---

## 👨‍💻 Candidate Details

**Name:** Chitranshu Sanket
🔗 LinkedIn: https://www.linkedin.com/in/chitranshu-sanket/
📄 Resume: https://drive.google.com/file/d/1gkgY-MTst3mQF0F2KCjqpsjxFKlq5BWJ/view

---

## 📌 Assignment Context

This project was developed as part of the **AI Generalist | Applied AI Builder Assignment**.

### 🎯 Objective (as per assignment)

To design and build an AI system that:

* Converts **raw inspection data** into a **structured DDR report**
* Demonstrates **real-world AI workflow design**
* Handles **imperfect, noisy, and incomplete data**

---

## 🚀 What I Built

I developed an **end-to-end AI pipeline** that:

* Extracts information from inspection & thermal reports
* Structures unorganized text into meaningful categories
* Applies reasoning to infer root causes and severity
* Generates a **client-ready Detailed Diagnostic Report (DDR)**

---

## 🧠 Key Design Philosophy

Instead of relying purely on LLMs, I built a:

👉 **Hybrid AI System (Rule-Based + LLM)**

This ensures:

* Reliability
* No hallucination
* Consistent output
* Better control over reasoning

---

## ⚙️ System Architecture

```id="g0c6tr"
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

### ✔ Requirement: Extract relevant observations

→ Implemented using custom parsing + keyword grouping

---

### ✔ Requirement: Combine inspection + thermal data

→ Merged both sources into unified structured JSON

---

### ✔ Requirement: Avoid duplicate points

→ Deduplication logic applied during structuring

---

### ✔ Requirement: Handle missing/conflicting data

→ Explicit conflict detection logic
→ Missing data handled with fallback messaging

---

### ✔ Requirement: Client-friendly report

→ Clean Markdown DDR output
→ Structured and readable format

---

### ✔ Requirement: Include images

→ Images extracted from PDFs
→ Mapped to corresponding areas
→ Fallback: "Image Not Available"

---

### ✔ Requirement: Do NOT invent facts

→ Rule-based reasoning strictly uses extracted data

---

### ✔ Requirement: Generalize to similar reports

→ Keyword-based + structure-based approach
→ Not hardcoded to specific files

---

## 📊 Output Structure (DDR)

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

* PyMuPDF for text + image extraction

---

### 2. Structuring Engine

* Converts raw text into structured JSON
* Area-based grouping
* Noise filtering & cleaning

---

### 3. Validation Layer

* Pydantic ensures schema consistency
* Prevents pipeline failure

---

### 4. Reasoning Engine (Key Highlight)

#### Rule-Based Intelligence:

* Detects patterns:

  * Dampness
  * Leakage
  * Cracks
* Infers:

  * Root cause
  * Severity
  * Recommendations

#### LLM Usage (Groq):

* Used ONLY for:

  * Language refinement
  * Output polishing

---

### 5. Report Generator

* Produces clean Markdown DDR
* Ensures structured, client-ready format

---

### 6. UI Layer (Streamlit)

* Upload PDFs OR use sample data
* Preview reports
* Download outputs
* View structured JSON

---

## 🛠️ Tech Stack

* Python
* Streamlit
* PyMuPDF
* Pydantic
* Groq API
* Custom Rule-Based Logic

---

## 🎯 Evaluation Criteria Mapping

| Criteria                  | Implementation                     |
| ------------------------- | ---------------------------------- |
| Accuracy                  | Structured extraction + validation |
| Logical merging           | Combined inspection + thermal      |
| Missing/conflict handling | Explicit logic                     |
| Clarity                   | Clean DDR output                   |
| System thinking           | Modular pipeline design            |

---

## ⚠️ Limitations

* Image mapping is heuristic-based
* No OCR for scanned PDFs
* Thermal data may be incomplete

---

## 🚀 Future Improvements

* OCR integration
* Semantic image mapping
* API-based deployment
* Advanced anomaly detection

---

## 🎥 Submission Links

* 🔗 GitHub Repo: *https://github.com/Chitranshu0/UrbanRoof-AI-Automated-DDR-Report-Generation-System*
* 🌐 Live Demo: *https://urbanroof-ai-automated-ddr-report-generation-system.streamlit.app/*

---

## 💡 Key Learning

This project reflects my ability to:

* Design real-world AI pipelines
* Balance rule-based logic with LLMs
* Handle messy and incomplete data
* Focus on reliability over complexity

---

## 🙌 Final Note

This assignment helped me demonstrate not just AI usage, but **how to think, design, and build practical AI systems**.

---
