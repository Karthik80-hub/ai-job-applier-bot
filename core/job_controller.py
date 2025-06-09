# core/job_controller.py
from application_engine.job_status_service import (
    init_db, has_applied, has_failed_before, export_successful_to_csv,
    get_success_count, send_csv_attachment, log_and_notify
)
from scrapers.universal_scraper import fetch_all_jobs
from llm_modules import resume_matcher
from llm_modules.resume_tailor import tailor_resume
from application_engine import form_filler
import os, json, time
from datetime import datetime

def run_job_cycle(test_mode=False):
    print("AI Job Applier Bot Started:", datetime.now())
    init_db()

    jobs = fetch_all_jobs()
    print(f"Found {len(jobs)} jobs.")

    matched_jobs = []
    for job in jobs:
        try:
            job.update({"match_score": 100, "matched_skills": [], "missing_skills": []})
            matched_jobs.append(job)
        except Exception as e:
            print(f"Failed to score job {job.get('title', 'Unknown')}: {e}")
            continue

    filtered_jobs = []
    applied, skipped, failed = 0, 0, 0

    for job in matched_jobs:
        if has_applied(job["url"]) or has_failed_before(job["url"]) or job.get("match_score", 0) < 50:
            skipped += 1
            continue

        try:
            resume_matcher.generate_custom_resume(job)
            filtered_jobs.append(job)
        except Exception as e:
            print(f"Resume tailoring failed: {e}")
            failed += 1

    for job in filtered_jobs:
        try:
            form_filler.apply_to_job(job)
            log_and_notify(job, resume_path="resume_templates/output", status="success")
            applied += 1
        except Exception as e:
            log_and_notify(job, resume_path="resume_templates/output", status="failed")
            failed += 1

    export_successful_to_csv()
    if get_success_count() % 50 == 0:
        send_csv_attachment("successful_applications.csv")

    print(f"Cycle done: Applied={applied}, Skipped={skipped}, Failed={failed}")
