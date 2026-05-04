import os
import json
import shutil
import streamlit as st
from src.pipeline import DDRPipeline

# -------------------- Base Paths --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
LEGACY_DATA_DIR = os.path.join(BASE_DIR, "Data")

sample_insp = os.path.join(DATA_DIR, "sample_inspection.pdf")
sample_therm = os.path.join(DATA_DIR, "sample_thermal.pdf")

# -------------------- Helpers --------------------

def check_file(path, label):
    if not os.path.exists(path):
        return False, f"{label} not found at {path}"
    return True, ""


def cleanup():
    try:
        if os.path.exists(IMAGES_DIR):
            shutil.rmtree(IMAGES_DIR)
        if os.path.exists(OUTPUTS_DIR):
            shutil.rmtree(OUTPUTS_DIR)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
    except Exception as e:
        st.warning(f"Cleanup error: {e}")


def migrate_legacy_sample_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    legacy_samples = {
        os.path.join(LEGACY_DATA_DIR, "Sample Report.pdf"): sample_insp,
        os.path.join(LEGACY_DATA_DIR, "Thermal Images.pdf"): sample_therm,
    }

    for legacy_path, target_path in legacy_samples.items():
        if os.path.exists(legacy_path) and not os.path.exists(target_path):
            try:
                shutil.copyfile(legacy_path, target_path)
            except Exception as e:
                print(f"Unable to migrate legacy sample file {legacy_path}: {e}")


# -------------------- Setup --------------------
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

st.set_page_config(page_title="UrbanRoof AI DDR System", layout="wide")
migrate_legacy_sample_files()

st.title("🏠 UrbanRoof AI: Automated DDR Report Generation System")
st.markdown("Generate a **Detailed Diagnostic Report (DDR)** from Inspection & Thermal PDFs")

st.info(
    """
🎯 **AI Generalist Assignment Submission**

This system demonstrates a real-world AI workflow that converts unstructured inspection and thermal reports into structured DDR reports.
"""
)

with st.expander("🧠 How the System Works"):
    st.markdown(
        """
1. Extract text & images from PDFs  
2. Structure data into area-wise observations  
3. Validate using Pydantic  
4. Apply rule-based reasoning  
5. Use LLM for refinement  
6. Generate DDR report  
"""
    )

with st.expander("🎯 Assignment Coverage"):
    st.markdown(
        """
✔ Extract observations  
✔ Combine inspection + thermal data  
✔ Avoid duplicates  
✔ Handle missing/conflict data  
✔ Generate a client-friendly report  
✔ Include images  
"""
    )

with st.expander("⚙️ Tech Stack"):
    st.markdown(
        """
- Python  
- Streamlit  
- PyMuPDF  
- Pydantic  
- Groq LLM  
- Rule-based reasoning  
"""
    )

with st.expander("🚀 Why This Approach"):
    st.markdown(
        """
This system uses:  

👉 Rule-based reasoning → correctness  
👉 LLM → language refinement  

Ensures:  
- No hallucination  
- Consistent output  
- Real-world reliability  
"""
    )

with st.expander("📊 Limitations"):
    st.markdown(
        """
- Heuristic image mapping  
- No OCR support  
- Thermal data may be incomplete  
"""
    )

# -------------------- Sidebar --------------------
st.sidebar.header("⚙️ Options")
use_sample = st.sidebar.checkbox("Use Sample Data")
show_sample = st.sidebar.checkbox("Preview Sample PDFs")
show_json = st.sidebar.checkbox("Show Extracted JSON")

insp_path = None
therm_path = None

# -------------------- Sample Validation --------------------
insp_ok, insp_msg = check_file(sample_insp, "Inspection sample file")
therm_ok, therm_msg = check_file(sample_therm, "Thermal sample file")

if use_sample and (not insp_ok or not therm_ok):
    st.error("Sample files missing.")
    if insp_msg:
        st.text(insp_msg)
    if therm_msg:
        st.text(therm_msg)
    st.stop()

# -------------------- File Input --------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Input")
    if use_sample:
        st.success("Using preloaded sample data")
        insp_path = sample_insp
        therm_path = sample_therm
    else:
        inspection_file = st.file_uploader("Upload Inspection PDF", type=["pdf"])
        thermal_file = st.file_uploader("Upload Thermal PDF", type=["pdf"])

        if inspection_file and thermal_file:
            insp_path = os.path.join(DATA_DIR, "uploaded_inspection.pdf")
            therm_path = os.path.join(DATA_DIR, "uploaded_thermal.pdf")
            with open(insp_path, "wb") as f:
                f.write(inspection_file.getbuffer())
            with open(therm_path, "wb") as f:
                f.write(thermal_file.getbuffer())

# -------------------- Preview PDFs --------------------
if use_sample and show_sample:
    st.subheader("📂 Sample Data Preview")
    colA, colB = st.columns(2)
    if insp_ok:
        with colA:
            st.markdown("**Inspection Report**")
            with open(sample_insp, "rb") as f:
                st.download_button("Download Inspection Sample", f.read(), file_name="sample_inspection.pdf")
    else:
        colA.warning("Inspection sample unavailable.")

    if therm_ok:
        with colB:
            st.markdown("**Thermal Report**")
            with open(sample_therm, "rb") as f:
                st.download_button("Download Thermal Sample", f.read(), file_name="sample_thermal.pdf")
    else:
        colB.warning("Thermal sample unavailable.")

# -------------------- Generate ----------------
if st.button("🚀 Generate DDR Report"):
    if not insp_path or not therm_path:
        st.error("Please upload both PDFs or enable sample data.")
    else:
        st.info("Starting AI Pipeline...")
        with st.spinner("Running Pipeline..."):
            pipeline = DDRPipeline()
            try:
                result = pipeline.run(insp_path, therm_path)
                report_path = result.get("report_path") if result else None
                if report_path and not os.path.isabs(report_path):
                    report_path = os.path.join(BASE_DIR, report_path)

                json_path = os.path.join(OUTPUTS_DIR, "sample_output.json")

                if not report_path or not os.path.exists(report_path):
                    st.error("Report generation failed.")
                else:
                    st.success("✅ Report generated successfully!")
                    st.subheader("📥 Downloads")
                    c1, c2 = st.columns(2)
                    with open(report_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    c1.download_button(
                        "Download Report",
                        md_content,
                        file_name="DDR_Report.md",
                        mime="text/markdown",
                        on_click=cleanup,
                    )
                    if os.path.exists(json_path):
                        with open(json_path, "r", encoding="utf-8") as f:
                            json_content = f.read()
                        c2.download_button(
                            "Download JSON",
                            json_content,
                            file_name="ddr_data.json",
                            mime="application/json",
                            on_click=cleanup,
                        )

                    st.subheader("📄 Report Output")
                    st.markdown(md_content)

                    if show_json and os.path.exists(json_path):
                        st.subheader("📊 Structured JSON Data")
                        with open(json_path, "r", encoding="utf-8") as f:
                            json_data = json.load(f)
                        st.json(json_data)
            except Exception as e:
                st.error(f"Pipeline execution failed: {e}")
