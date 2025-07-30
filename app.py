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

# Extract first page of PDF and encode as base64 image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [{
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# ----------------------------- UI Setup ----------------------------- #
st.set_page_config(page_title="🧠 ATS Resume Expert", layout="centered", page_icon="📄")

st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>📄 ATS Resume Expert</h1>
    <p style='text-align: center;'>Get expert insights on your resume using AI. Improve your format, project relevance, and match score against job descriptions!</p>
    <hr style="border: 1px solid #eee;">
""", unsafe_allow_html=True)

with st.expander("ℹ️ How to Use"):
    st.markdown("""
    - 📌 Paste your **job description**.
    - 📎 Upload your **resume PDF**.
    - ✅ Click on the buttons to get feedback, match %, formatting suggestions, or better projects.
    """)

# -------------------------- Inputs -------------------------- #
input_text = st.text_area("📝 Paste Job Description", key="input", height=200)
uploaded_file = st.file_uploader("📎 Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully.")

# -------------------------- Buttons -------------------------- #
col1, col2 = st.columns(2)
with col1:
    submit1 = st.button("📊 Resume Evaluation")
    submit_format = st.button("🖋️ Improve Format")
with col2:
    submit3 = st.button("📈 ATS Match %")
    submit_projects = st.button("💡 Suggest Better Projects")

# -------------------------- Prompts -------------------------- #
input_prompt1 = """You are an experienced Data Scientist. Review the resume based on the job description. Highlight strengths and weaknesses."""
input_prompt3 = """You are a skilled ATS. Give the % match of the resume with the job description. Also list missing keywords and overall evaluation."""
input_prompt_format = """You are a resume consultant. Suggest improvements in formatting, layout, and structure for a data science role."""
input_prompt_projects = """You are a resume expert. Suggest better project ideas aligned with the job description and role."""

# ------------------------ Responses ------------------------ #
if submit1:
    if uploaded_file is not None:
        with st.spinner("Analyzing resume..."):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("📊 Resume Evaluation")
        st.markdown(response)
    else:
        st.warning("⚠️ Please upload your resume.")

elif submit3:
    if uploaded_file is not None:
        with st.spinner("Calculating ATS Match..."):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("📈 ATS Match Result")
        st.markdown(response)

        match = re.search(r'(\d+)%', response)
        if match:
            percentage = int(match.group(1))
            if percentage < 80:
                st.error(f"❌ Match Score: {percentage}% — Rejected. Consider improving your resume.")
            else:
                st.success(f"✅ Match Score: {percentage}% — Great! You’re likely to be shortlisted.")
        else:
            st.warning("⚠️ Couldn’t extract the match percentage. Please review the job/resume input.")
    else:
        st.warning("⚠️ Please upload your resume.")

elif submit_format:
    if uploaded_file is not None:
        with st.spinner("Evaluating resume format..."):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt_format, pdf_content, input_text)
        st.subheader("🖋️ Format Suggestions")
        st.markdown(response)
    else:
        st.warning("⚠️ Please upload your resume.")

elif submit_projects:
    if uploaded_file is not None:
        with st.spinner("Analyzing projects..."):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt_projects, pdf_content, input_text)
        st.subheader("💡 Project Recommendations")
        st.markdown(response)
    else:
        st.warning("⚠️ Please upload your resume.")
