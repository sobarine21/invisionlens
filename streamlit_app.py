import streamlit as st
import base64
from google import genai
from google.genai import types


# Initialize the Google GenAI Client using Streamlit secrets
def initialize_genai_client():
    client = genai.Client(
        vertexai=True,
        project=st.secrets["GOOGLE_CLOUD_PROJECT"],
        location=st.secrets["GOOGLE_CLOUD_LOCATION"],
    )
    return client


# Generate compliance report using the Gemini model
def generate_compliance_analysis(client, regulation_name, uploaded_pdf_content):
    model = "gemini-2.5-flash-preview-04-17"
    input_text = f"""
    Perform a compliance analysis based on the following regulation:
    Regulation Name: {regulation_name}
    PDF Content: {uploaded_pdf_content}
    """
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    # Stream the generated response
    compliance_report = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        compliance_report += chunk.text

    return compliance_report


# Streamlit App
def main():
    st.title("AI-Powered Compliance Analysis Application")
    st.sidebar.title("Options")
    
    # Dropdown to select regulation
    regulations = {
        "Appointment of Administrator and Procedure for Refunding to the Investors (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/appointment-of-administrator-and-procedure-for-refunding-to-the-investors--regulations--2018.pdf",
        "SEBI Certification of Associated Persons in the Securities Markets (2007)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/sebi--certification-of-associated-persons-in-the-securities-markets--regulations--2007.pdf",
        "SEBI Issue and Listing of Securitised Debt Instruments (2008)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/sebi--issue-and-listing-of-securitised-debt-instruments-and-security-receipts--regulations--2008.pdf",
        "SEBI Prohibition of Fraudulent and Unfair Trade Practices (2003)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/sebi--prohibition-of-fraudulent-and-unfair-trade-practices-relating-to-securities-market--regulations--2003.pdf",
        "SEBI Bankers to an Issue (1994)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--bankers-to-an-issue--regulations-1994.pdf",
        "SEBI Buy-Back of Securities (2018)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--buy-back-of-securities--regulations--2018.pdf",
        "SEBI Collective Investment Scheme (1999)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--collective-investment-scheme--regulations-1999.pdf",
        "SEBI Credit Rating Agencies (1999)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--credit-rating-agencies--regulations--1999.pdf",
        "SEBI Custodian (1996)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--custodian--regulations--1996.pdf",
        "SEBI Debenture Trustees (1993)": "https://eorclvgyabomabeqrcqc.supabase.co/storage/v1/object/public/sebiregulatorydb/regdb/securities-and-exchange-board-of-india--debenture-trustees--regulations--1993.pdf",
        # Add more regulations as needed
    }

    regulation_name = st.sidebar.selectbox(
        "Select a Regulation",
        options=list(regulations.keys()),
    )

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF for Analysis", type=["pdf"])

    # Button to perform analysis
    if st.button("Perform Compliance Analysis"):
        if not uploaded_file:
            st.error("Please upload a PDF file for analysis.")
            return

        # Extract content from the uploaded PDF
        pdf_content = uploaded_file.read()
        encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")

        # Initialize Google GenAI client
        client = initialize_genai_client()

        # Generate compliance analysis report
        st.info("Performing compliance analysis... This may take a few moments.")
        try:
            report = generate_compliance_analysis(client, regulation_name, encoded_pdf)
            st.success("Compliance Analysis Complete!")
            st.text_area("Compliance Audit Report", report, height=300)
        except Exception as e:
            st.error(f"An error occurred while performing the analysis: {str(e)}")


if __name__ == "__main__":
    main()
