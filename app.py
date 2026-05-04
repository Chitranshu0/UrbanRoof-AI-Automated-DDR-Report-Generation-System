import streamlit as st
import os
import json
import shutil
from src.pipeline import DDRPipeline

# ---------------- Cleanup ----------------
def cleanup():
    try:
        if os.path.exists("images"):
            shutil.rmtree("images")
        if os.path.exists("outputs"):
            shutil.rmtree("outputs")
        os.makedirs("images", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)
    except Exception as e:
        print("ERROR:", str(e))

# ---------------- Setup ----------------
os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("images", exist_ok=True)

st.set_page_config(page_title="UrbanRoof AI DDR System", layout="wide")

st.title("🏠 UrbanRoof AI: Automated DDR Report Generation System")
st.markdown("Generate a **Detailed Diagnostic Report (DDR)** from Inspection & Thermal PDFs")

# ---------------- Sidebar ----------------
st.sidebar.header("⚙️ Options")

use_sample = st.sidebar.checkbox("Use Sample Data")
show_sample = st.sidebar.checkbox("Preview Sample PDFs")
show_json = st.sidebar.checkbox("Show Extracted JSON")

# ---------------- Sample Paths ----------------
sample_insp = os.path.join("data", "Sample Report.pdf")
sample_therm = os.path.join("data", "Thermal Images.pdf")

insp_path = None
therm_path = None

# ---------------- File Input ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Input")

    if use_sample:
        if os.path.exists(sample_insp) and os.path.exists(sample_therm):
            st.success("Using preloaded sample data")
            insp_path = sample_insp
            therm_path = sample_therm
        else:
            st.error("Sample PDF files were not found in the data folder.")
    else:
        inspection_file = st.file_uploader("Upload Inspection PDF", type=["pdf"])
        thermal_file = st.file_uploader("Upload Thermal PDF", type=["pdf"])

        if inspection_file and thermal_file:
            insp_path = os.path.join("data", "uploaded_inspection.pdf")
            therm_path = os.path.join("data", "uploaded_thermal.pdf")

            with open(insp_path, "wb") as f:
                f.write(inspection_file.getbuffer())
            with open(therm_path, "wb") as f:
                f.write(thermal_file.getbuffer())

# ---------------- Preview PDFs ----------------
if use_sample and show_sample:
    st.subheader("📂 Sample Data Preview")

    if os.path.exists(sample_insp) and os.path.exists(sample_therm):
        colA, colB = st.columns(2)

        with colA:
            st.markdown("**Inspection Report**")
            with open(sample_insp, "rb") as f:
                sample_insp_bytes = f.read()
            st.download_button("Download Sample Inspection", sample_insp_bytes, file_name="inspection.pdf")

        with colB:
            st.markdown("**Thermal Report**")
            with open(sample_therm, "rb") as f:
                sample_therm_bytes = f.read()
            st.download_button("Download Sample Thermal", sample_therm_bytes, file_name="thermal.pdf")
    else:
        st.warning("Sample PDF files are missing from the data folder, so preview is unavailable.")

# ---------------- Run Pipeline ----------------
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

                if not report_path or not os.path.exists(report_path):
                    st.error("Report generation failed.")
                else:
                    st.success("✅ Report generated successfully!")

                    # ---------------- Downloads ----------------
                    st.subheader("📥 Downloads")
                    c1, c2 = st.columns(2)

                    with open(report_path, "r", encoding="utf-8") as f:
                        md_content = f.read()

                    c1.download_button(
                        "Download Report",
                        md_content,
                        file_name="DDR_Report.md",
                        mime="text/markdown",
                        on_click=cleanup
                    )

                    json_path = "outputs/sample_output.json"
                    if os.path.exists(json_path):
                        with open(json_path, "r", encoding="utf-8") as f:
                            json_content = f.read()

                        c2.download_button(
                            "Download JSON",
                            json_content,
                            file_name="ddr_data.json",
                            mime="application/json",
                            on_click=cleanup
                        )

                    # ---------------- Output ----------------
                    st.subheader("📄 Report Output")
                    st.markdown(md_content)

                    # ---------------- JSON View ----------------
                    if show_json and os.path.exists(json_path):
                        st.subheader("📊 Structured JSON Data")
                        with open(json_path, "r", encoding="utf-8") as f:
                            json_data = json.load(f)
                        st.json(json_data)

            except Exception as e:
                print("ERROR:", str(e))
                st.error(f"Pipeline execution failed: {e}")