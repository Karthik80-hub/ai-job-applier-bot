# llm_modules/resume_matcher.py

import os
from dotenv import load_dotenv
from openai import OpenAI
from llm_modules.resume_parser import extract_skills_from_resume

load_dotenv()

def filter_and_rank(jobs):
    resume_path = os.getenv("RESUME_PATH", "data/your_resume.pdf")
    resume_skills = extract_skills_from_resume(resume_path)
    filtered_jobs = []

    for job in jobs:
        title = job.get("title", "").lower()
        location = job.get("location", "").lower()
        company = job.get("company", "").lower()
        description = job.get("description", "").lower()

        # Exclusion filters (keep criteria.yaml for titles, keywords, companies)
        from configs.criteria_loader import load_criteria
        criteria = load_criteria()
        if any(ex in title for ex in criteria["exclude"]["titles"]):
            continue
        if any(ex in company for ex in criteria["exclude"]["companies"]):
            continue
        if any(ex in description for ex in criteria["exclude"]["keywords"]):
            continue

        # Title + Location match
        if not any(t in title for t in criteria["titles"]):
            continue
        if not any(loc in location for loc in criteria["locations"]):
            continue

        # Skills match from resume
        matched_skills = [skill for skill in resume_skills if skill in description]
        if len(matched_skills) >= 2:
            job["matched_skills"] = matched_skills
            filtered_jobs.append(job)

    return filtered_jobs

def generate_custom_resume(job, test=False):
    file_name = f"resume_templates/output/resume_{job['company'].lower().replace(' ', '_')}_{job['title'].lower().replace(' ', '_')}.txt"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    if test:
        result = f"""Tailored Resume Summary for {job['title']} at {job['company']}:
- Simulated resume (TEST MODE)
- Skills matched: {', '.join(job.get('matched_skills', []))}
- This is a placeholder. No OpenAI call was made."""
        print(f" [TEST MODE] Resume simulated and saved to {file_name}")
    else:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
You are a career assistant helping a candidate apply for jobs.
Based on the following job description, generate a tailored resume summary that highlights relevant skills, tools, and experience:

Job Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}

Candidate Background:
- Experienced in Machine Learning, Full Stack Development, and Cloud Engineering
- Proficient in Python, JavaScript, SQL, and common data structures
- Skilled in using ML frameworks like PyTorch, TensorFlow, and Hugging Face
- Built and deployed models using AWS (SageMaker, Lambda, Bedrock)
- Familiar with Docker, Kubernetes, CI/CD pipelines, and Terraform
- Developed APIs and applications with Django, FastAPI, PostgreSQL, and Redis
- Passionate about solving real-world problems with AI and automation

Generate a tailored resume summary under 200 words. Use bullet points and match keywords from the job description.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        result = response.choices[0].message.content
        print(f" Tailored resume saved to {file_name}")

    with open(file_name, "w") as f:
        f.write(result)
