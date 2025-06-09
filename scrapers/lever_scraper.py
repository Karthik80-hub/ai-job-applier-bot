# scrapers/lever_scraper.py

import requests
from bs4 import BeautifulSoup

def fetch_jobs(board_url):
    jobs = []
    try:
        response = requests.get(board_url)
        soup = BeautifulSoup(response.text, "html.parser")

        for el in soup.find_all("a", class_="posting-title"):
            title = el.find("h5").get_text(strip=True)
            location = el.find_next("span", class_="sort-by-location").text.strip()
            link = board_url + el["href"]
            jobs.append({
                "title": title,
                "company": board_url.split("//")[1].split(".")[0],
                "location": location,
                "url": link,
                "description": "",
                "source": "lever"
            })
    except Exception as e:
        print(f"[Lever Error] {e}")
    return jobs
