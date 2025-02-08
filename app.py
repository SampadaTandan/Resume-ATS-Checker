import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the input prompt correctly
input_prompt = """
Hey, act like a skilled and experienced ATS (Application Tracking System) with a deep understanding of the tech field, including software engineering, data science, data analytics, and big data engineering. 

Your task is to evaluate the resume based on the given job description. Assume the job market is highly competitive and provide the best assistance for improving resumes. 

Assign a percentage match based on the job description and identify missing keywords with high accuracy.

Resume: {text}

Job Description: {jd}

I want the response in one structured string with the format: 

{{
    "JD Match": "XX%", 
    "MissingKeywords": ["Keyword1", "Keyword2", ...], 
    "Profile Summary": "..."
}}
"""

# Gemini Pro Response
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += str(reader.pages[page].extract_text())  
    return text

# Streamlit App
st.title("🚀 Smart ATS - Resume Evaluator")
st.markdown("**Optimize Your Resume for ATS & Increase Your Chances!**")

jd = st.text_area("📌 Paste the Job Description Here")
uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type="pdf", help="Upload a PDF file of your resume.")

submit = st.button("🔍 Analyze Resume")

if submit:
    if uploaded_file is not None and jd:
        text = input_pdf_text(uploaded_file)
        formatted_prompt = input_prompt.format(text=text, jd=jd)  # ✅ This will work now
        response = get_gemini_response(formatted_prompt)
        
        try:
            response_data = json.loads(response)  # Convert string response to dictionary
            
            st.subheader("📊 **ATS Evaluation Results**")

            # Display JD match percentage
            st.markdown(f"### ✅ **Match Score:** `{response_data['JD Match']}`")

            # Display Missing Keywords in a better format
            st.markdown("### ❌ **Missing Keywords:**")
            if response_data["MissingKeywords"]:
                for keyword in response_data["MissingKeywords"]:
                    st.markdown(f"- 🔹 {keyword}")
            else:
                st.markdown("*No missing keywords! Your resume is well-optimized!* 🎉")

            # Display Profile Summary
            st.markdown("### 📝 **Profile Summary:**")
            if response_data["Profile Summary"]:
                st.info(response_data["Profile Summary"])
            else:
                st.warning("No profile summary was generated.")

        except json.JSONDecodeError:
            st.error("Error parsing the response. Please try again.")

    else:
        st.warning("⚠️ Please upload a resume and paste a job description before submitting.")
