# llm_modules/resume_tailor.py

import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
from docx2pdf import convert
from llm_modules.resume_parser import extract_text_from_pdf, extract_text_from_docx

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ATS_API_URL = os.getenv("ATS_API_URL", "http://localhost:9000/score")

def tailor_resume(base_resume_path, job, output_path):
    if base_resume_path.endswith(".pdf"):
        base_resume = extract_text_from_pdf(base_resume_path)
    elif base_resume_path.endswith(".docx"):
        base_resume = extract_text_from_docx(base_resume_path)
    else:
        raise ValueError("Resume must be in .pdf or .docx format")

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

    print(f"Tailored resume saved: TXT ➔ {txt_path}, DOCX ➔ {docx_path}")
    return {"txt": txt_path, "docx": docx_path, "pdf": pdf_path}

def score_and_filter_jobs(job_list, resume_path):
    """
    Score each job against the resume using ATS scoring and filter to high-match jobs.
    
    Args:
        job_list (list): List of job dictionaries with title, company, description, etc.
        resume_path (str): Path to the resume file (PDF/DOCX)
    
    Returns:
        list: Filtered list of jobs that meet the score threshold
    """
    print(f"\nScoring {len(job_list)} jobs against resume...")
    
    # Extract resume text
    if resume_path.endswith('.pdf'):
        resume_text = extract_text_from_pdf(resume_path)
    elif resume_path.endswith('.docx'):
        resume_text = extract_text_from_docx(resume_path)
    else:
        raise ValueError("Resume must be PDF or DOCX format")

    scored_jobs = []
    for job in job_list:
        try:
            # Get ATS score
            resp = requests.post(
                ATS_API_URL,
                json={
                    "resume_text": resume_text,
                    "job_description": job.get("description", "")
                }
            )
            
            if resp.status_code == 200:
                score_data = resp.json()
                match_score = score_data.get("Final ATS Score", 0)
                
                # Add score to job dict
                job["ats_score"] = match_score
                job["matched_keywords"] = score_data.get("Matched Keywords", [])
                job["missing_keywords"] = score_data.get("Missing Keywords", [])
                
                print(f"Job: {job.get('title')} at {job.get('company')} - Score: {match_score}%")
                
                # Only keep jobs with score > 70%
                if match_score > 70:
                    scored_jobs.append(job)
            else:
                print(f"Error scoring job {job.get('title')}: {resp.text}")
                
        except Exception as e:
            print(f"Failed to score job {job.get('title')}: {str(e)}")
            continue

    print(f"\nFound {len(scored_jobs)} high-match jobs (>70% ATS score)")
    
    # Save matched jobs to JSON for React dashboard
    save_matched_jobs_to_json(scored_jobs)
    
    return scored_jobs

def apply_to_jobs(filtered_jobs):
    """
    Apply to each job in the filtered list using tailored resumes.
    
    Args:
        filtered_jobs (list): List of jobs that passed ATS scoring
    """
    print(f"\nPreparing to apply to {len(filtered_jobs)} jobs...")
    
    # Create output directory for tailored resumes
    output_dir = "data/tailored_resumes"
    os.makedirs(output_dir, exist_ok=True)
    
    base_resume = os.getenv("RESUME_PATH", "data/KARTHIK_RESUME.pdf")
    
    for job in filtered_jobs:
        try:
            print(f"\nApplying to: {job.get('title')} at {job.get('company')}")
            print(f"ATS Score: {job.get('ats_score')}%")
            print(f"Matched Keywords: {', '.join(job.get('matched_keywords', []))}")
            
            # Generate tailored resume
            tailored_files = tailor_resume(base_resume, job, output_dir)
            
            # TODO: Implement actual job application logic here
            # This could involve:
            # 1. Selenium automation
            # 2. API calls to job boards
            # 3. Email applications
            # etc.
            
            print(f"Application prepared with tailored resume: {tailored_files['pdf']}")
            print(" Ready for submission via automation system")
            
        except Exception as e:
            print(f"Failed to apply to job at {job.get('company')}: {str(e)}")
            continue
            
    print("\nCompleted application preparation process")

import json
from datetime import datetime
import os

def save_matched_jobs_to_json(jobs: list, out_path: str = "matched_jobs/matched_jobs.json"):
    """Save scored and filtered jobs to JSON for React dashboard."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    for job in jobs:
        job["applied_at"] = datetime.now().strftime("%Y-%m-%d")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
    print(f"[INFO] Saved {len(jobs)} jobs to {out_path}")

