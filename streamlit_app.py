import streamlit as st
import PyPDF2
import requests
import tempfile
from fpdf import FPDF
from google import genai
from google.genai import types

# Configure API Key
genai.configure(api_key="YOUR_GOOGLE_API_KEY")  # Replace with your key

# All SEBI regulations
regulations = {
    "Appointment of Administrator & Refund Procedure (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/appointment-of-administrator-and-procedure-for-refunding-to-the-investors--regulations--2018.pdf",
    "Certification of Associated Persons in Securities Markets (2007)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/sebi--certification-of-associated-persons-in-the-securities-markets--regulations--2007.pdf",
    "Securitised Debt Instruments & Security Receipts (2008)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/sebi--issue-and-listing-of-securitised-debt-instruments-and-security-receipts--regulations--2008.pdf",
    "Prohibition of Fraudulent and Unfair Trade Practices (2003)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/sebi--prohibition-of-fraudulent-and-unfair-trade-practices-relating-to-securities-market--regulations--2003.pdf",
    "Bankers to an Issue (1994)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--bankers-to-an-issue--regulations-1994.pdf",
    "Buy-Back of Securities (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--buy-back-of-securities--regulations--2018.pdf",
    "Collective Investment Scheme (1999)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--collective-investment-scheme--regulations-1999.pdf",
    "Credit Rating Agencies (1999)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--credit-rating-agencies--regulations--1999.pdf",
    "Custodian Regulations (1996)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--custodian--regulations--1996.pdf",
    "Debenture Trustees (1993)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--debenture-trustees--regulations--1993.pdf",
    "Delisting of Equity Shares (2021)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--delisting-of-equity-shares--regulations--2021.pdf",
    "Depositories and Participants (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--depositories-and-participants--regulations--2018.pdf",
    "Employee Service Regulations (2001)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--employees--service--regulations--2001.pdf",
    "Foreign Portfolio Investors (2019)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--foreign-portfolio-investors--regulation--2019.pdf",
    "Foreign Venture Capital Investor (2000)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--foreign-portfolio-investors--regulation--2019.pdf",
    "Index Providers (2024)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--index-providers--regulations--2024.pdf",
    "Infrastructure Investment Trusts": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--infrastructure-investment-trusts--regulations.pdf",
    "Intermediaries (2008)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--intermediaries--regulations--2008.pdf",
    "Investment Advisers (2013)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--investment-advisers--regulations--2013.pdf",
    "Investor Protection Fund (2009)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--investor-protection-and-education-fund--regulations--2009.pdf",
    "Municipal Debt Securities": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--issue-and-listing-of-municipal-debt-securities-.pdf",
    "Non-Convertible Securities (2021)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--issue-and-listing-of-non-convertible-securities--regulations-2021.pdf",
    "Issue of Capital & Disclosure Requirements (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--issue-of-capital-and-disclosure-requirements--regulations--2018.pdf",
    "KYC Registration Agency (2011)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--kyc--know-your-client--registration-agency--regulations--2011.pdf",
    "Listing Obligations & Disclosure Requirements (2015)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--listing-obligations-and-disclosure-requirements--regulations--2015.pdf",
    "Merchant Bankers (1992)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--merchant-bankers--regulations--1992.pdf",
    "Mutual Funds (1996)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--mutual-funds--regulations-1996.pdf",
    "Board Meetings Procedure (2001)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--procedure-for-board-meetings--regulations--2001.pdf",
    "Prohibition of Insider Trading (2015)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--prohibition-of-insider-trading--regulations-2015.pdf",
    "REITs (2014)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--real-estate-investment-trusts--regulations--2014.pdf",
    "Registrars to Issue (1993)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--registrars-to-an-issue-and-share-transfer-agents--regulations-1993.pdf",
    "Research Analysts (2014)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--research-analysts--regulations--2014.pdf",
    "Self-Regulatory Organisations (2004)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--self-regulatory-organisations--regulations--2004.pdf",
    "Settlement Proceedings (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--settlement-proceedings--regulations-2018.pdf",
    "Share Based Employee Benefits & Sweat Equity (2021)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--share-based-employee-benefits-and-sweat-equity--regulations--2021.pdf",
    "Stock Brokers (1992)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--stock-brokers--regulations-1992.pdf",
    "Substantial Acquisition & Takeovers (2011)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--substantial-acquisition-of-shares-and-takeovers--regulations--2011.pdf",
    "Vault Managers (2021)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--vault-managers--regulations-2021.pdf",
    "Securities Contracts – Stock Exchanges (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-contracts--regulation---stock-exchanges-and-clearing-corporations--regulations--2018.pdf"
}

# Utility functions
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def get_regulation_text(url):
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        return extract_text_from_pdf(tmp.name)

def generate_compliance_analysis(reg_text, doc_text):
    prompt = f"""You are a compliance auditor. Check this document against the SEBI regulation. List violations, gaps, missing information, and relevant clauses.

Regulation:
{reg_text}

Uploaded Document:
{doc_text}
"""
    contents = [types.Content(role="user", parts=[types.Part.from_text(prompt)])]
    config = types.GenerateContentConfig(response_mime_type="text/plain")
    response = ""
    for chunk in genai.GenerativeModel("gemini-2.5-flash-preview-04-17").generate_content_stream(contents=contents, generation_config=config):
        response += chunk.text
    return response

def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest="S").encode("latin1")

# Streamlit UI
st.set_page_config(page_title="SEBI Compliance Auditor", layout="wide")
st.title("📜 SEBI Compliance Auditor (AI-Powered)")

reg_name = st.selectbox("Choose a SEBI Regulation", list(regulations.keys()))
uploaded_pdf = st.file_uploader("Upload Document for Compliance Check", type="pdf")

if reg_name and uploaded_pdf:
    with st.spinner("🔍 Analyzing for compliance..."):
        reg_text = get_regulation_text(regulations[reg_name])
        doc_text = extract_text_from_pdf(uploaded_pdf)
        result = generate_compliance_analysis(reg_text, doc_text)

        st.subheader("📋 AI Audit Result")
        st.text_area("Compliance Output", result, height=400)

        pdf_bytes = generate_pdf(result)
        st.download_button("📥 Download Report", data=pdf_bytes, file_name="SEBI_Compliance_Report.pdf", mime="application/pdf")
