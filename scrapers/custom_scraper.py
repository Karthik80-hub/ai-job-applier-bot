# scrapers/custom_scraper.py
import requests
from bs4 import BeautifulSoup

def fetch_jobs(url):
    jobs = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try to find job title
        title = soup.find("h1")
        title = title.text.strip() if title else "Unknown Title"

        # Try to find job description
        desc_div = soup.find("div", {"class": "job-description"}) or soup.find("section")
        description = desc_div.get_text(separator="\n").strip() if desc_div else "No description available."

        # Build job dictionary
        job = {
            "title": title,
            "url": url,
            "company": "Unknown",
            "description": description
        }
        jobs.append(job)

    except Exception as e:
        print(f"[Custom Scraper Error] Failed to fetch job from {url}: {e}")

    return jobs
