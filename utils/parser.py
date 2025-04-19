# utils/parser.py

import re
import os
import json
import fitz  # PyMuPDF
import phonenumbers
from docx import Document
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Predefined skill keywords for basic matching
KNOWN_SKILLS = [
    "python", "tensorflow", "pytorch", "sagemaker", "huggingface", "docker", "kubernetes",
    "spark", "sql", "aws", "gcp", "azure", "airflow", "langchain", "flask", "fastapi"
]

def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Use .pdf or .docx")

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "".join([page.get_text() for page in doc])

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_valid_phone(text):
    for match in phonenumbers.PhoneNumberMatcher(text, None):
        return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    return None

def extract_basic_info(text):
    email = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone = extract_valid_phone(text)
    skills = [skill for skill in KNOWN_SKILLS if skill.lower() in text.lower()]

    # Smart name detection: first capitalized line, skip "---"
    name = None
    for line in text.splitlines():
        if line.strip() and line.strip()[0].isupper() and not line.strip().startswith("---"):
            name = line.strip()
            break

    return {
        "name": name or "Name not found",
        "email": email[0] if email else None,
        "phone": phone,
        "skills": skills
    }

def extract_with_gpt(text):
    prompt = f"""
Extract the following fields from this resume text and return in structured JSON format:
- Full name
- Email
- Phone number
- Skills
- Summary
- Education
- Experience

Resume text:
{text[:3500]}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional resume parser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1000
    )

    return response.choices[0].message.content

def save_json(data, output_path):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

def parse_resume(file_path, use_gpt=False, save_path=None):
    text = extract_text_from_file(file_path)

    if use_gpt:
        parsed = extract_with_gpt(text)
    else:
        parsed = extract_basic_info(text)

    if save_path:
        save_json(parsed, save_path)

    return parsed

def parse_all_resumes(folder_path, use_gpt=False, save_outputs=True):
    parsed_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf") or filename.endswith(".docx"):
            full_path = os.path.join(folder_path, filename)
            output_json = os.path.join(folder_path, filename.replace(".pdf", ".json").replace(".docx", ".json"))
            parsed = parse_resume(full_path, use_gpt=use_gpt, save_path=output_json if save_outputs else None)
            parsed_data.append({"file": filename, "parsed": parsed})

    return parsed_data
