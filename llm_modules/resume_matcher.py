# llm_modules/resume_matcher.py

from dotenv import load_dotenv
load_dotenv()

from configs.criteria_loader import load_criteria

def filter_and_rank(jobs):
    criteria = load_criteria()
    filtered_jobs = []

    for job in jobs:
        title = job.get("title", "").lower()
        location = job.get("location", "").lower()
        company = job.get("company", "").lower()
        description = job.get("description", "").lower()

        # Exclusion filters
        if any(ex in title for ex in criteria["exclude"]["titles"]):
            continue
        if any(ex in company for ex in criteria["exclude"]["companies"]):
            continue
        if any(ex in description for ex in criteria["exclude"]["keywords"]):
            continue

        # Title match
        if not any(t in title for t in criteria["titles"]):
            continue

        # Location match
        if not any(loc in location for loc in criteria["locations"]):
            continue

        # Skills check (basic)
        matched_skills = [
            skill for skill in criteria["required_skills"]
            if skill in description
        ]
        if len(matched_skills) >= 2:  # you can tweak this threshold
            job["matched_skills"] = matched_skills
            filtered_jobs.append(job)

    return filtered_jobs



import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file

def generate_custom_resume(job):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
You are a career assistant helping a candidate apply for jobs.
Based on the following job description, generate a tailored resume summary that highlights relevant skills, tools, and experience:

Job Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}

Candidate Background:
- 4 years in ML, Full Stack Development, and AWS
- Worked on ML model deployment using SageMaker, Bedrock
- Hands-on with PyTorch, TensorFlow, HuggingFace, LangChain
- Built MLOps pipelines with Docker, Lambda, Terraform
- Deployed apps with Django, FastAPI, PostgreSQL, Redis

Generate a tailored resume summary under 200 words. Use bullet points and match keywords from the job description.
"""

    client = openai.OpenAI(api_key=openai.api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content

    file_name = f"resume_templates/output/resume_{job['company'].lower().replace(' ', '_')}_{job['title'].lower().replace(' ', '_')}.txt"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    with open(file_name, "w") as f:
        f.write(result)

    print(f"✅ Tailored resume saved to {file_name}")
