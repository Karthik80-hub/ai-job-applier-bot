# scrapers/greenhouse_scraper.py

import requests
from bs4 import BeautifulSoup

def fetch_jobs(board_url):
    jobs = []
    try:
        response = requests.get(board_url)
        soup = BeautifulSoup(response.text, "html.parser")

        for opening in soup.select("div.opening"):
            title = opening.find("a").text.strip()
            location = opening.find("span", class_="location").text.strip()
            url = "https://boards.greenhouse.io" + opening.find("a")["href"]
            jobs.append({
                "title": title,
                "company": board_url.split("/")[-1],
                "location": location,
                "url": url,
                "description": "",
                "source": "greenhouse"
            })
    except Exception as e:
        print(f"[Greenhouse Error] {e}")
    return jobs
