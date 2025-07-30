from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
import re
from PIL import Image
import pdf2image
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to send resume & prompt to Gemini
def get_gemini_response(input_prompt, pdf_content, job_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, pdf_content[0], job_description])
    return response.text

# Function to extract first page of PDF and encode as base64 image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input for job description and resume
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

# Buttons
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage match")
submit_format = st.button("Improve Resume Format")
submit_projects = st.button("Suggest Better Projects")

# Prompts
input_prompt1 = """
You are an experienced Data Scientist. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match if the resume matches the job description. 
First, output the percentage; then list missing keywords; finally, provide your overall evaluation.
"""

input_prompt_format = """
You are a professional resume consultant. Analyze the layout and formatting of the uploaded resume. 
Suggest improvements including formatting consistency, font, margins, bullet points, alignment, and overall readability. 
Also, suggest appropriate sections to include for a data science or analytics role, such as:
- Summary or Objective
- Technical Skills
- Projects
- Work Experience
- Education
- Certifications
- Tools & Technologies
Provide clear and practical formatting advice.
"""

input_prompt_projects = """
You are a resume and career expert. Evaluate the projects mentioned in the resume in the context of the job description. 
If the projects are not strongly relevant, suggest better project ideas that would significantly improve the candidate's chances of getting shortlisted. 
Your suggestions should be aligned with the required tools, technologies, and responsibilities from the job description. 
List:
1. Irrelevant or weak projects (if any),
2. Recommended project ideas with titles and short descriptions.
"""

# Resume Review
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.warning("⚠️ Please upload the resume")

# ATS Matching and Rejection Logic
elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)

        match = re.search(r'(\d+)%', response)
        if match:
            percentage = int(match.group(1))
            if percentage < 80:
                st.error("❌ You are rejected. Match is less than 80%.")
            else:
                st.success("✅ You are shortlisted. Good job!")
        else:
            st.warning("⚠️ Could not extract match percentage from the response.")
    else:
        st.warning("⚠️ Please upload the resume")

# Resume Format Suggestions
elif submit_format:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt_format, pdf_content, input_text)
        st.subheader("Resume Format Suggestions")
        st.write(response)
    else:
        st.warning("⚠️ Please upload the resume")

# Suggest Better Projects
elif submit_projects:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt_projects, pdf_content, input_text)
        st.subheader("Suggested Project Improvements")
        st.write(response)
    else:
        st.warning("⚠️ Please upload the resume")
