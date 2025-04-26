import streamlit as st
import PyPDF2
import requests
import tempfile
from fpdf import FPDF
from google import genai
from google.genai import types

# 🔑 Set your API Key
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual key

# All SEBI regulations (shortened for readability here)
regulations = {
    "Buy-Back of Securities (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--buy-back-of-securities--regulations--2018.pdf",
    "Prohibition of Insider Trading (2015)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--prohibition-of-insider-trading--regulations-2015.pdf",
    "Mutual Funds (1996)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--mutual-funds--regulations-1996.pdf",
    # ... include all entries here as in your original list
}

# Utility: Extract text from PDF file
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

# Utility: Get regulation PDF and extract text
def get_regulation_text(url):
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        return extract_text_from_pdf(tmp.name)

# Gemini AI: Generate compliance audit text
def generate_compliance_analysis(reg_text, doc_text):
    client = genai.Client(api_key=GOOGLE_API_KEY)
    model = "gemini-2.5-flash-preview-04-17"
    prompt = f"""
You are a compliance auditor.

Compare the uploaded document with the SEBI regulation.

Identify:
- Any violations
- Any missing disclosures or clauses
- Gaps or inconsistencies
- Refer to specific regulation clauses if applicable

--- SEBI Regulation ---
{reg_text}

--- Uploaded Document ---
{doc_text}
"""
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(prompt)])
    ]
    config = types.GenerateContentConfig(response_mime_type="text/plain")
    output = ""
    for chunk in client.models.generate_content_stream(model=model, contents=contents, config=config):
        output += chunk.text
    return output

# Utility: Generate downloadable PDF from result
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest="S").encode("latin1")

# Streamlit App UI
st.set_page_config(page_title="SEBI Compliance Auditor", layout="wide")
st.title("📜 SEBI Compliance Auditor (AI-Powered)")

reg_name = st.selectbox("Choose a SEBI Regulation", list(regulations.keys()))
uploaded_pdf = st.file_uploader("Upload your PDF document for review", type="pdf")

if reg_name and uploaded_pdf:
    with st.spinner("Analyzing for compliance using Gemini..."):
        regulation_text = get_regulation_text(regulations[reg_name])
        document_text = extract_text_from_pdf(uploaded_pdf)
        result = generate_compliance_analysis(regulation_text, document_text)

        st.subheader("📋 AI Audit Result")
        st.text_area("Compliance Analysis", result, height=400)

        # Generate and provide downloadable PDF
        pdf_bytes = generate_pdf(result)
        st.download_button("📥 Download Report", data=pdf_bytes, file_name="SEBI_Compliance_Report.pdf", mime="application/pdf")
