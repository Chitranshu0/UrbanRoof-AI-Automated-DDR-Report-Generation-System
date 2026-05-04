import os
import fitz  # PyMuPDF

os.makedirs("data", exist_ok=True)

# Generate Dummy Inspection PDF
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Building Inspection Report\n\nRoof: The roof shows minor cracking and peeling. Possible water leak.\nWall: Structural integrity of the north wall seems compromised.\nLiving Room: General wear and tear observed.", fontsize=12)
doc.save("data/dummy_inspection.pdf")
doc.close()

# Generate Dummy Thermal PDF
doc2 = fitz.open()
page2 = doc2.new_page()
page2.insert_text((50, 50), "Thermal Scan Report\n\nRoof: Thermal anomalies detected. High moisture pooling.\nWall: No thermal issues found on walls.\nKitchen: Missing insulation detected behind stove.", fontsize=12)
doc2.save("data/dummy_thermal.pdf")
doc2.close()

print("Dummy PDFs generated in data/ folder.")
