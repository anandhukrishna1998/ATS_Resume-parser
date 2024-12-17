# ATS Resume Parser with Gemini AI

This is an AI-powered ATS (Applicant Tracking System) Resume Parser that uses Gemini AI (from Google Generative AI) to analyze resumes and job descriptions. It matches resumes to job descriptions, extracts keywords, and provides recommendations for improving the resume to enhance compatibility with the job description.

## Features
- **ATS Compatibility Scoring**: Evaluate how well a resume matches a job description.
- **Keyword Extraction**: Identify key technical, soft skills, experience, and industry knowledge from job descriptions.
- **Recommendations**: Get actionable advice to improve resume alignment with job requirements.

## Technologies Used
- **Streamlit**: A framework to create interactive web apps.
- **Google Generative AI**: Used for natural language processing and analysis.
- **SpaCy**: For text preprocessing and language model handling.
- **PyMuPDF**: For extracting text from PDF resumes.
- **python-docx**: For extracting text from DOCX resumes.
- **LangDetect**: To detect the language of the text (English or French).

## Requirements

The following Python libraries are required to run this application:

- `streamlit`
- `python-docx`
- `PyMuPDF`
- `python-dotenv`
- `google-generativeai`
- `spacy`
- `langdetect`

## Setup

### 1. Clone this repository:

```bash
git clone https://github.com/yourusername/ats-resume-parser.git
cd ats-resume-parser
```

### 2. Install dependencies:

```bash
python -m venv venv
# On Windows use `venv\Scripts\activate`
source venv/bin/activate  
```

### 3. Install requirements:

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables:
Create a `.env` file in the project root directory and add your Google API key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 5. Run the app:
Once everything is set up, run the Streamlit app:

```bash
streamlit run app.py
```

### 6. Access the app:
After running the above command, the app will be hosted locally. Open your browser and navigate to the URL provided in the terminal (typically http://localhost:8501) to use the app.


## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.

