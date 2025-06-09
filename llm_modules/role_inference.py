import os
from dotenv import load_dotenv
from openai import OpenAI
import fitz  # PyMuPDF for PDF text extraction
import docx
import re
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Fix for Windows terminal logging
if not sys.stderr:
    logger.disabled = True

# Load environment variables
load_dotenv()

def clean_text(text: str) -> str:
    """Clean extracted text from common issues."""
    # Remove special characters and extra whitespace
    text = re.sub(r'[\u200b\xa0]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    # Remove email header artifacts
    text = re.sub(r'From:.*?Subject:', '', text, flags=re.DOTALL)
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    return text.strip()

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file with error handling."""
    try:
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        raise

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file with error handling."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
        raise

def infer_job_roles_from_resume(file_path: str) -> str:
    """
    Infer job roles from a resume file (PDF or DOCX).
    Returns a comma-separated string of 3-5 job roles.
    """
    logger.info(f"Processing resume: {file_path}")
    
    # Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    # Extract text based on file type
    file_ext = file_path.lower().split('.')[-1]
    if file_ext == "pdf":
        resume_text = extract_text_from_pdf(file_path)
    elif file_ext in ["doc", "docx"]:
        resume_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    # Truncate text to avoid token limits
    max_chars = 3000
    if len(resume_text) > max_chars:
        logger.warning(f"Resume text truncated from {len(resume_text)} to {max_chars} characters")
        resume_text = resume_text[:max_chars]

    prompt = f"""
Act as an expert recruiter with 10+ years of experience. Based on the following resume content, infer 3 to 5 job roles or titles this candidate is most suited for in today's job market. Your output should only be a comma-separated list of job roles.

Resume:
{resume_text}
"""

    try:
        # ✅ Correct instantiation with new SDK
        client = OpenAI()  # Automatically reads from env var OPENAI_API_KEY

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert recruiter. Provide job role recommendations as a comma-separated list."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        roles = response.choices[0].message.content.strip()
        logger.info(f"Successfully inferred roles: {roles}")
        return roles
        
    except Exception as e:
        logger.error(f"Error during role inference: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        resume_path = os.getenv("RESUME_PATH")
        if not resume_path:
            raise ValueError("RESUME_PATH not set in environment variables")
            
        roles = infer_job_roles_from_resume(resume_path)
        print("\nSuggested Roles:")
        for role in roles.split(","):
            print(f"  • {role.strip()}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise
