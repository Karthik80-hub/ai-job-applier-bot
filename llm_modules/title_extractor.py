# llm_modules/title_extractor.py

import os
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_job_titles(resume_text):
    prompt = (
        "Extract 5 to 10 job titles that the candidate is qualified for based on this resume. "
        "Return only a comma-separated list of job titles without any explanation.\n\n"
        f"Resume:\n{resume_text}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150
    )

    content = response.choices[0].message.content.strip()
    return [title.strip() for title in content.split(",") if title.strip()]

# Example test:
if __name__ == "__main__":
    sample_resume = """
    Experienced software engineer with skills in Python, TensorFlow, AWS SageMaker, and Docker. Worked on ML model training and deployment. Built full-stack web apps using Django and React.
    """
    titles = extract_job_titles(sample_resume)
    print(titles)
