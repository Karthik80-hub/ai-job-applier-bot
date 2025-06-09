from scrapers.greenhouse_scraper import fetch_jobs as fetch_greenhouse
from scrapers.workday_scraper import fetch_jobs as fetch_workday
from scrapers.custom_scraper import fetch_jobs as fetch_custom  # Fallback

def dynamic_scrape_jobs(discovered_sources: list[dict]) -> list[dict]:
    jobs = []

    for source in discovered_sources:
        url = source.get("careers_url")
        if not url:
            continue

        print(f"Scraping: {url}")
        try:
            if "greenhouse.io" in url:
                jobs.extend(fetch_greenhouse(url))
            elif "workday" in url:
                jobs.extend(fetch_workday(url))
            else:
                print(f"[Fallback] Using custom scraper for: {url}")
                jobs.extend(fetch_custom(url))
        except Exception as e:
            print(f"[Scraping Error] {url}: {e}")

    return jobs
