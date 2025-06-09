from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import json
import os
import time

from application_engine.job_status_service import log_and_notify
from application_engine.user_profile_service import get_user_answer

def get_selectors(job_url):
    with open("site_config.json", "r") as f:
        config = json.load(f)

    domain = urlparse(job_url).netloc.replace("www.", "")
    return config.get(domain, config["default"])


def apply_to_job(job, test=False):
    print(f" Applying to {job['title']} at {job['company']}")
    print(f" Navigating to: {job['url']}")

    resume_path = f"resume_templates/output/resume_{job['company'].lower().replace(' ', '_')}_{job['title'].lower().replace(' ', '_')}.pdf"
    resume_path = os.path.abspath(resume_path)

    if test:
        print(" [TEST MODE] Skipping browser automation.")
        print(f" Would have filled form with resume: {resume_path}")
        log_and_notify(job, resume_path, status="test")
        return

    selectors = get_selectors(job["url"])

    # Fetch profile data from PostgreSQL
    full_name = get_user_answer("personal_info", "full_name") or ""
    email = get_user_answer("personal_info", "email") or ""
    first_name = full_name.split()[0] if full_name else ""
    last_name = full_name.split()[-1] if len(full_name.split()) > 1 else ""
    phone = get_user_answer("personal_info", "phone") or ""
    location = get_user_answer("personal_info", "location") or ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto(job["url"], timeout=60000)

            # Optional: click apply button to reveal form
            try:
                page.click('a[href^="#app"]')
                time.sleep(1)
            except:
                pass

            # Fill fields using selectors
            if "first_name" in selectors:
                page.fill(selectors["first_name"], first_name)
            if "last_name" in selectors:
                page.fill(selectors["last_name"], last_name)
            if "name" in selectors:
                page.fill(selectors["name"], full_name)
            if "email" in selectors:
                page.fill(selectors["email"], email)
            if "phone" in selectors and phone:
                page.fill(selectors["phone"], phone)
            if "location" in selectors and location:
                page.fill(selectors["location"], location)

            # Resume upload
            page.set_input_files(selectors["resume"], resume_path)

            # Submit
            page.click(selectors["submit"])

            print(f" Application submitted to {job['company']}")
            log_and_notify(job, resume_path, status="success")

        except Exception as e:
            print(f" Failed to apply to {job['company']} – {e}")
            log_and_notify(job, resume_path, status="failed")

        finally:
            time.sleep(2)
            browser.close()
