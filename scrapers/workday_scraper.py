# scrapers/workday_scraper.py

import requests

def fetch_jobs(api_url):
    jobs = []
    try:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "appliedFacets": {},
            "limit": 20,
            "offset": 0,
            "searchText": ""
        }
        response = requests.post(api_url, headers=headers, json=payload)
        data = response.json()

        for item in data.get("jobPostings", []):
            title = item["title"]
            location = item.get("locationsText", "")
            url = f"https://{api_url.split('/fs/')[0].split('//')[1]}/job/{item['externalPath']}"
            jobs.append({
                "title": title,
                "company": api_url.split("//")[1].split(".")[0],
                "location": location,
                "url": url,
                "description": "",
                "source": "workday"
            })
    except Exception as e:
        print(f"[Workday Error] {e}")
    return jobs
