import streamlit as st
import os
import json
import shutil
from src.pipeline import DDRPipeline

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

# Ensure necessary directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("images", exist_ok=True)

st.set_page_config(page_title="UrbanRoof AI DDR System", layout="wide")

st.title("UrbanRoof AI: Automated DDR Report Generation System")
st.markdown("Upload your Inspection and Thermal PDFs to generate a Detailed Diagnostic Report.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload PDFs")
    inspection_file = st.file_uploader("Upload Inspection PDF", type=["pdf"])
    thermal_file = st.file_uploader("Upload Thermal PDF", type=["pdf"])

if st.button("Generate DDR Report"):
    if not inspection_file or not thermal_file:
        st.error("Please upload both Inspection and Thermal PDFs.")
    else:
        # Save uploaded files to data/
        insp_path = os.path.join("data", "uploaded_inspection.pdf")
        therm_path = os.path.join("data", "uploaded_thermal.pdf")
        
        with open(insp_path, "wb") as f:
            f.write(inspection_file.getbuffer())
        with open(therm_path, "wb") as f:
            f.write(thermal_file.getbuffer())
            
        st.info("Files uploaded successfully. Starting AI Pipeline...")
        
        with st.spinner("Running Pipeline (Extraction -> Structuring -> Validation -> Reasoning -> Generation)..."):
            pipeline = DDRPipeline()
            try:
                result = pipeline.run(insp_path, therm_path)
                report_path = result.get("report_path") if result else None
                
                if not report_path or not os.path.exists(report_path):
                    st.error("Report generation failed. Please try again.")
                else:
                    st.success("Report generated successfully!")
                    
                    st.subheader("Downloads")
                    c1, c2 = st.columns(2)
                    
                    with open(report_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                        
                    c1.download_button(
                        label="Download Markdown Report",
                        data=md_content,
                        file_name="DDR_Report.md",
                        mime="text/markdown",
                        on_click=cleanup
                    )
                    
                    json_path = "outputs/sample_output.json"
                    if os.path.exists(json_path):
                        with open(json_path, "r", encoding="utf-8") as f:
                            json_content = f.read()
                        c2.download_button(
                            label="Download JSON Data",
                            data=json_content,
                            file_name="ddr_data.json",
                            mime="application/json",
                            on_click=cleanup
                        )
                    
                    st.subheader("Report Output")
                    st.markdown(md_content)
                
            except Exception as e:
                print("ERROR:", str(e))
                st.error(f"Pipeline execution failed: {e}")
