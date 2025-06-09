# scrapers/icims_scraper.py

import requests
from bs4 import BeautifulSoup

def fetch_jobs(board_url):
    jobs = []
    try:
        response = requests.get(board_url)
        soup = BeautifulSoup(response.text, "html.parser")

        for el in soup.select(".iCIMS_JobsTable > tbody > tr"):
            title = el.find("a").text.strip()
            location = el.select_one("td:nth-child(2)").text.strip()
            url = el.find("a")["href"]
            jobs.append({
                "title": title,
                "company": board_url.split("//")[1].split(".")[0],
                "location": location,
                "url": url,
                "description": "",
                "source": "icims"
            })
    except Exception as e:
        print(f"[iCIMS Error] {e}")
    return jobs
