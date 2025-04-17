import os
import argparse
import threading
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from scrapers import jobright_scraper
from llm_modules import resume_matcher
from application_engine import form_filler
from application_engine.job_status_service import (
    init_db,
    has_applied,
    has_failed_before,
    export_successful_to_csv,
    get_success_count,
    send_csv_attachment
)

stop_signal = False

def run_job_cycle(test_mode=False):
    print("AI Job Applier Bot Started:", datetime.now())
    init_db()

    jobs = jobright_scraper.fetch_jobs()
    print(f"Found {len(jobs)} jobs.")

    matched_jobs = resume_matcher.filter_and_rank(jobs)
    print(f"Found {len(matched_jobs)} relevant jobs.")

    applied, skipped, failed = 0, 0, 0
    filtered_jobs = []

    for job in matched_jobs:
        if has_applied(job["url"]):
            print(f"Skipping {job['title']} (already applied)")
            skipped += 1
            continue
        if has_failed_before(job["url"]):
            print(f"Skipping {job['title']} (failed too many times)")
            skipped += 1
            continue
        try:
            resume_matcher.generate_custom_resume(job)
            filtered_jobs.append(job)
        except Exception as e:
            print(f"Failed to generate resume for {job['title']}: {e}")
            failed += 1

    print("Step 4: Submitting applications...")
    for job in filtered_jobs:
        try:
            form_filler.apply_to_job(job)
            applied += 1
        except Exception as e:
            print(f"Apply failed for {job['title']}: {e}")
            failed += 1

    # Export CSV after each cycle
    export_successful_to_csv()

    # Send CSV every 50 successful applications
    success_count = get_success_count()
    if success_count > 0 and success_count % 50 == 0:
        send_csv_attachment("successful_applications.csv")

    print(f"Job Cycle Completed: {datetime.now()}")
    print(f"Stats: Applied={applied}, Skipped={skipped}, Failed={failed}")
    print("-" * 50)

def input_listener(scheduler):
    global stop_signal
    while True:
        cmd = input("Type 'exit' or 'stop' to end the bot: ").strip().lower()
        if cmd in ["exit", "stop"]:
            stop_signal = True
            scheduler.shutdown()
            export_successful_to_csv()
            print("Bot stopped by user.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=60, help="Run interval in minutes")
    args = parser.parse_args()

    scheduler = BlockingScheduler()
    scheduler.add_job(run_job_cycle, trigger="interval", minutes=args.interval)
    
    print(f"Bot is running every {args.interval} minutes.")
    print("Type 'exit' or 'stop' to end the bot at any time.")

    listener_thread = threading.Thread(target=input_listener, args=(scheduler,), daemon=True)
    listener_thread.start()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        export_successful_to_csv()
        print("Bot terminated.")
