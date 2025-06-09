# scrapers/universal_scraper.py

import yaml
from pathlib import Path

from scrapers.jobright_scraper import fetch_jobs as fetch_jobright
from scrapers.greenhouse_scraper import fetch_jobs as fetch_greenhouse
from scrapers.lever_scraper import fetch_jobs as fetch_lever
from scrapers.workday_scraper import fetch_jobs as fetch_workday
from scrapers.icims_scraper import fetch_jobs as fetch_icims
from scrapers.custom_scraper import fetch_jobs as fetch_custom


def load_job_sources():
    with open(Path("configs") / "job_sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("sources", [])


def fetch_all_jobs():
    all_jobs = []

    # Jobright always
    all_jobs.extend(fetch_jobright())

    job_sources = load_job_sources()
    for source in job_sources:
        platform = source.get("platform", "").lower()
        url = source.get("url")
        name = source.get("name")

        try:
            if platform == "greenhouse":
                jobs = fetch_greenhouse(url)
            elif platform == "lever":
                jobs = fetch_lever(url)
            elif platform == "workday":
                jobs = fetch_workday(url)
            elif platform == "icims":
                jobs = fetch_icims(url)
            else:
                print(f"[Fallback] Using custom scraper for: {name} ({platform})")
                jobs = fetch_custom(url)
            
            all_jobs.extend(jobs)

        except Exception as e:
            print(f"[Error] Failed to fetch from {name} ({platform}): {e}")

    return all_jobs
