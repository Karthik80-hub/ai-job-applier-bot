@echo off

REM ===== Create .gitignore =====
(
echo __pycache__/
echo .env
echo *.pyc
echo *.log
echo *.sqlite3
echo resume_templates/*.pdf
) > .gitignore

REM ===== Create requirements.txt =====
(
echo openai
echo playwright
echo bs4
echo requests
echo pydantic
echo python-dotenv
echo langchain
) > requirements.txt

REM ===== Create README.md =====
(
echo AI Job Application Bot
echo.
echo This project automates job applications using AI.
echo.
echo Features:
echo - Scrape jobs from multiple sources
echo - GPT-powered resume matching
echo - Auto-apply via headless browser
echo - Daily scheduling and tracking
echo.
echo Tech Stack:
echo - Python, Playwright
echo - OpenAI GPT / LangChain
echo - FastAPI (optional)
echo - MongoDB or SQLite
echo - Docker (optional)
echo.
echo Setup:
echo 1. Clone the repo and install dependencies:
echo    git clone https://github.com/Karthik80-hub/ai-job-applier-bot.git
echo    cd ai-job-applier-bot
echo    pip install -r requirements.txt
) > README.md

REM ===== Create main.py =====

echo import os > main.py
echo from scrapers import jobright_scraper >> main.py
echo from llm_modules import resume_matcher >> main.py
echo from application_engine import form_filler >> main.py
echo from datetime import datetime >> main.py
echo. >> main.py
echo def main(): >> main.py
echo     print("AI Job Applier Bot Started:", datetime.now()) >> main.py
echo     print("Step 1: Searching for job listings...") >> main.py
echo     jobs = jobright_scraper.fetch_jobs() >> main.py
echo     print("Found", len(jobs), "jobs.") >> main.py
echo     print("Step 2: Matching jobs...") >> main.py
echo     matched_jobs = resume_matcher.filter_and_rank(jobs) >> main.py
echo     print("Found", len(matched_jobs), "relevant jobs.") >> main.py
echo     print("Step 3: Customizing resumes...") >> main.py
echo     for job in matched_jobs: >> main.py
echo         resume_matcher.generate_custom_resume(job) >> main.py
echo     print("Step 4: Submitting applications...") >> main.py
echo     for job in matched_jobs: >> main.py
echo         form_filler.apply_to_job(job) >> main.py
echo     print("Done at:", datetime.now()) >> main.py
echo. >> main.py
echo if __name__ == "__main__": >> main.py
echo     main() >> main.py

REM ===== Create configs\job_criteria.yaml =====
if not exist configs mkdir configs

(
echo job_preferences:
echo   titles:
echo     - machine learning engineer
echo     - data scientist
echo     - ai engineer
echo     - applied scientist
echo     - mlops engineer
echo.
echo   required_skills:
echo     - python
echo     - pytorch
echo     - tensorflow
echo     - sagemaker
echo     - huggingface
echo     - docker
echo     - lambda
echo     - langchain
echo     - prompt engineering
echo.
echo   optional_skills:
echo     - airflow
echo     - fastapi
echo     - react
echo     - kubernetes
echo     - postgres
echo     - redis
echo.
echo   locations:
echo     - remote
echo     - united states
echo     - usa
echo.
echo   exclude:
echo     titles:
echo       - internship
echo       - intern
echo       - contractor
echo       - contract
echo       - senior manager
echo     companies:
echo       - oracle
echo       - infosys
echo     keywords:
echo       - unpaid
echo       - relocation required
) > configs\job_criteria.yaml
