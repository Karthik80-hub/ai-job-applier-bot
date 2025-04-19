# tests/test_tailor_resume.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from llm_modules.resume_tailor import tailor_resume
import os

# Define a sample job description to simulate real use
sample_job = {
    "title": "Machine Learning Engineer",
    "company": "OpenAI",
    "description": """
We are looking for a Machine Learning Engineer with experience in:
- Large Language Models (LLMs)
- Prompt Engineering
- PyTorch / TensorFlow
- AWS SageMaker for deployment
- Docker and Kubernetes
"""
}

base_resume_path = "resume_templates/base_resume.txt"
output_path = "resume_templates/output"

# Make sure the output folder exists
os.makedirs(output_path, exist_ok=True)

# Call the tailoring function
tailor_resume(base_resume_path, sample_job, output_path)
