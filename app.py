import streamlit as st
import os
import docx2txt
import fitz  # PyMuPDF
from dotenv import load_dotenv
import re
import google.generativeai as genai
import spacy
from langdetect import detect



# Load spaCy models
nlp_en = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")
# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Streamlit configuration
st.set_page_config(page_title="ATS Resume parser with Gemini AI", layout="wide")

# Function to process text files
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return " ".join([page.get_text() for page in pdf_document])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(uploaded_file)
    return None


# Preprocess text
def preprocess_text(text):
    language = detect(text)
    nlp = nlp_fr if language == 'fr' else nlp_en
    
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)

# Generate Gemini prompt
def generate_prompt(job_desc, resume_text, prompt_type="match"):
    if prompt_type == "match":
        return f"""
        You are an ATS evaluator analyzing resume compatibility with the following job description:
        Job Description: {job_desc}
        Resume Text: {resume_text}

        Instructions:
        - Evaluate the resume based on keyword matches, context relevance, and overall content alignment.
        - Provide a detailed breakdown of gaps and strengths.
        - Format response as:
          SCORE: [calculated_score]
          REASON: [detailed explanation of matches and gaps].
        """
    elif prompt_type == "keywords":
        return f"""
        Analyze the following job description and identify important keywords categorized as follows:

        - Technical Skills
        - Soft Skills
        - Experience & Qualifications
        - Industry Knowledge

        Job Description: {job_desc}

        Format your response strictly as follows:
        Technical Skills: keyword1, keyword2, keyword3
        Soft Skills: keyword1, keyword2, keyword3
        Experience & Qualifications: keyword1, keyword2, keyword3
        Industry Knowledge: keyword1, keyword2, keyword3
        """
    elif prompt_type == "recommendations":
        return f"""
        You are a career coach. Analyze the resume for gaps against this job description:
        Job Description: {job_desc}
        Resume Text: {resume_text}

        Provide actionable recommendations to improve the resume. Include:
        1. Missing keywords and phrases.
        2. Suggestions for rephrasing or adding content.
        3. Strategies for better alignment with the job description.
        """

# Get Gemini response
def get_gemini_response(prompt):
    llm = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config
    )
    try:
        output = llm.generate_content(prompt)
        clean_output = output.text.strip()
        clean_output = re.sub(r"^Okay\s*,?\s*|\bHere's\b.*?:", "", clean_output, flags=re.I).strip()
        return clean_output
    except Exception as e:
        st.error(f"Error generating response with Gemini: {e}")
        return None

# Parse Gemini keywords response
def parse_keywords_response(response):
    keywords = {"Technical Skills": [], "Soft Skills": [], "Experience & Qualifications": [], "Industry Knowledge": []}
    for line in response.split("\n"):
        if line.startswith("Technical Skills:"):
            keywords["Technical Skills"] = line.split(":", 1)[1].split(",")
        elif line.startswith("Soft Skills:"):
            keywords["Soft Skills"] = line.split(":", 1)[1].split(",")
        elif line.startswith("Experience & Qualifications:"):
            keywords["Experience & Qualifications"] = line.split(":", 1)[1].split(",")
        elif line.startswith("Industry Knowledge:"):
            keywords["Industry Knowledge"] = line.split(":", 1)[1].split(",")
    return keywords

# Main App
def main():
    st.title("Enhanced ATS Resume Pro with Gemini AI")

    # Add custom CSS
    st.markdown(
        """
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f7fc;
            margin: 0;
        }

        .stTextArea {
            height: 50vh;
            font-size: 18px;
        }

        .stButton button {
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 12px 24px;
            border: none;
            cursor: pointer;
            border-radius: 8px;
            transition: background-color 0.3s;
        }

        .stButton button:hover {
            background-color: #45a049;
        }

        h1 {
            color: #2E3B55;
            font-size: 3rem;
            text-align: center;
            margin-top: 20px;
        }

        h2, h3 {
            color: #2E3B55;
        }

        .result-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .progress-bar {
            margin: 20px 0;
        }

        .keyword-list {
            font-size: 18px;
            margin-left: 20px;
        }

        .container {
            padding: 0;
            margin: 0;
        }

        .input-section {
            padding-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted black;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: black;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px 0;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position the tooltip above the text */
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        footer {
            text-align: center;
            padding: 20px;
            margin-top: 20px;
            border-top: 1px solid #ddd;
        }

        footer p {
            margin: 0;
            font-size: 16px;
        }

        footer span {
            color: red;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Input Section (without unnecessary blank space)
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    job_description = st.text_area("Paste the Job Description Here", height=400, help="Paste the job description for which you want to analyze the resume.")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF/DOCX)", type=["pdf", "docx"], help="Upload your resume in PDF or DOCX format.")
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file and job_description:
        resume_text = extract_text(uploaded_file)
        if not resume_text:
            st.error("Error extracting text from your resume. Please try again.")
            return

        # Preprocess text
        job_description = preprocess_text(job_description)
        resume_text = preprocess_text(resume_text)

        # Generate prompts and get responses
        match_prompt = generate_prompt(job_description, resume_text, "match")
        match_response = get_gemini_response(match_prompt)

        keywords_prompt = generate_prompt(job_description, resume_text, "keywords")
        keywords_response = get_gemini_response(keywords_prompt)

        recommendations_prompt = generate_prompt(job_description, resume_text, "recommendations")
        recommendations_response = get_gemini_response(recommendations_prompt)
        
        # Parse Gemini responses
        score_line = next((line for line in match_response.split('\n') if line.strip().startswith("SCORE:")), None)
        score_match = re.search(r"(\d+)", score_line.split(":")[1].strip()) if score_line else None
        score = float(score_match.group(1)) if score_match else 0.0

        reason_line = next((line for line in match_response.split('\n') if line.strip().startswith("REASON:")), None)
        reason = reason_line.split(":", 1)[1].strip() if reason_line else "No reason provided."

        # Parse the keywords response
        parsed_keywords = parse_keywords_response(keywords_response)

        # Display results
        st.markdown('<div class="result-card">', unsafe_allow_html=True)

        # ATS Score
        st.markdown(f"<h2>Your ATS Score: {score}%</h2>", unsafe_allow_html=True)
        st.progress(float(score) / 100)

        # Reason
        st.markdown("<h3>Reason</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{reason}</p>", unsafe_allow_html=True)

        # Identified Keywords
        st.markdown("<h3>Identified Keywords</h3>", unsafe_allow_html=True)
        for category, words in parsed_keywords.items():
            st.markdown(f"**{category}:**")
            st.markdown(f"<ul class='keyword-list'><li>{'</li><li>'.join(words)}</li></ul>", unsafe_allow_html=True)

        # Recommendations
        st.markdown("<h3>Recommendations</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{recommendations_response}</p>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Please upload your resume and paste the job description.")

    # Footer
    st.markdown(
        """
        <footer>
            <p>Developed by Anandhu Krishna with <span>&hearts;</span></p>
        </footer>
        """, unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
