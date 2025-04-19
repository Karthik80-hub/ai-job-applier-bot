# llm_modules/resume_tailor.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
from docx2pdf import convert

load_dotenv()

client = OpenAI()

def tailor_resume(base_resume_path, job, output_path):
    with open(base_resume_path, "r") as f:
        base_resume = f.read()

    job_description = job.get("description", "")
    job_title = job.get("title", "unknown-role").lower().replace(" ", "_")
    company = job.get("company", "unknown-company").lower().replace(" ", "_")

    prompt = f"""
You are a professional resume editor. Tailor the following resume to better fit the given job description.
Focus on integrating relevant skills, tools, and keywords from the JD while preserving the candidate's background.

--- JOB DESCRIPTION ---
{job_description}

--- ORIGINAL RESUME ---
{base_resume}

--- TAILORED RESUME ---
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert resume editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1800
    )

    tailored_resume = response.choices[0].message.content.strip()

    file_prefix = f"{output_path}/resume_openai_{job_title}_at_{company}"
    txt_path = file_prefix + ".txt"
    docx_path = file_prefix + ".docx"
    pdf_path = file_prefix + ".pdf"

    with open(txt_path, "w") as f:
        f.write(tailored_resume)

    doc = Document()
    for line in tailored_resume.split('\n'):
        doc.add_paragraph(line)
    doc.save(docx_path)

    try:
        convert(docx_path, pdf_path)
        print(f"PDF saved to: {pdf_path}")
    except Exception as e:
        print(f"PDF conversion failed: {e}")

    print(f"Tailored resume saved: TXT ➜ {txt_path}, DOCX ➜ {docx_path}")
    return {"txt": txt_path, "docx": docx_path, "pdf": pdf_path}
