from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import json
import os
import time

from application_engine.job_status_service import log_and_notify

def get_selectors(job_url):
    with open("site_config.json", "r") as f:
        config = json.load(f)

    domain = urlparse(job_url).netloc.replace("www.", "")
    return config.get(domain, config["default"])

def apply_to_job(job, test=False):
    print(f" Applying to {job['title']} at {job['company']}")
    print(f" Navigating to: {job['url']}")

    resume_path = f"resume_templates/output/resume_{job['company'].lower().replace(' ', '_')}_{job['title'].lower().replace(' ', '_')}.txt"
    resume_path = os.path.abspath(resume_path)

    if test:
        print(" [TEST MODE] Skipping browser automation.")
        print(f" Would have filled form with resume: {resume_path}")
        log_and_notify(job, resume_path, status="test")
        return

    selectors = get_selectors(job["url"])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto(job["url"], timeout=60000)

            # Try clicking Apply to reveal form (if applicable)
            try:
                page.click('a[href^="#app"]')
                time.sleep(1)
            except:
                pass

            page.fill(selectors["name"], "Karthik Chunchu")
            page.fill(selectors["email"], "youremail@example.com")
            page.set_input_files(selectors["resume"], resume_path)
            page.click(selectors["submit"])

            print(f" Application submitted to {job['company']}")
            log_and_notify(job, resume_path, status="success")

        except Exception as e:
            print(f" Failed to apply to {job['company']} – {e}")
            log_and_notify(job, resume_path, status="failed")

        finally:
            time.sleep(2)
            browser.close()
