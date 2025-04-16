import os 
from scrapers import jobright_scraper 
from llm_modules import resume_matcher 
from application_engine import form_filler 
from datetime import datetime 
 
def main(): 
    print("AI Job Applier Bot Started:", datetime.now()) 
    print("Step 1: Searching for job listings...") 
    jobs = jobright_scraper.fetch_jobs() 
    print("Found", len(jobs), "jobs.") 
    print("Step 2: Matching jobs...") 
    matched_jobs = resume_matcher.filter_and_rank(jobs) 
    print("Found", len(matched_jobs), "relevant jobs.") 
    print("Step 3: Customizing resumes...") 
    for job in matched_jobs: 
        resume_matcher.generate_custom_resume(job) 
    print("Step 4: Submitting applications...") 
    for job in matched_jobs: 
        form_filler.apply_to_job(job) 
    print("Done at:", datetime.now()) 
 
if __name__ == "__main__": 
    main() 
