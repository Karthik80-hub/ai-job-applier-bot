import os
import requests
import time
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
BING_API_KEY = os.getenv("BING_API_KEY")  # Optional fallback

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
CAREER_KEYWORDS = ["careers", "jobs", "join-us", "work-with-us", "employment", "opportunities"]

def is_likely_career_page(url: str) -> bool:
    return any(kw in url.lower() for kw in CAREER_KEYWORDS)

def search_google_for_career_page(company: str) -> str | None:
    try:
        query = f"{company} careers site:{company}.com"
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        for item in resp.json().get("items", []):
            link = item.get("link", "")
            if is_likely_career_page(link):
                return link
    except Exception as e:
        print(f"[Google Career Page Error] {e}")
    return None

def extract_company_domains_from_roles(roles: list[str], max_companies=5) -> set:
    companies = set()
    for role in roles:
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": f"{role} jobs"}
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            for item in data.get("items", []):
                parsed = urlparse(item.get("link", ""))
                domain = parsed.netloc.replace("www.", "")
                base = domain.split('.')[0]
                if base and len(base) > 2:
                    companies.add(base.lower())
                if len(companies) >= max_companies:
                    break
        except Exception as e:
            print(f"[Google Role Search Error] {e}")
        time.sleep(1.2)
    return companies

def discover_career_urls_from_roles(roles: list[str]) -> list[dict]:
    company_set = extract_company_domains_from_roles(roles)
    results = []
    for company in sorted(company_set):
        print(f" Discovering career page for company: {company}")
        url = search_google_for_career_page(company)
        results.append({"company": company, "careers_url": url})
        time.sleep(1.5)
    return results

# --- Optional fallback methods (disabled for now) ---

# def search_bing(role: str) -> str | None:
#     try:
#         url = "https://api.bing.microsoft.com/v7.0/search"
#         headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
#         params = {"q": f"{role} careers"}
#         resp = requests.get(url, headers=headers, params=params, timeout=10)
#         results = resp.json()
#         for item in results.get("webPages", {}).get("value", []):
#             link = item.get("url")
#             if is_likely_career_page(link):
#                 return link
#     except Exception as e:
#         print(f"[Bing Error] {e}")
#     return None

# def search_duckduckgo(role: str) -> str | None:
#     try:
#         query = f"{role} careers"
#         url = f"https://duckduckgo.com/html/?q={query}"
#         resp = requests.get(url, headers=HEADERS, timeout=10)
#         for line in resp.text.split("\n"):
#             if "href=\"http" in line:
#                 start = line.find("href=\"") + 6
#                 end = line.find("\"", start)
#                 link = line[start:end]
#                 if is_likely_career_page(link):
#                     return link
#     except Exception as e:
#         print(f"[DuckDuckGo Error] {e}")
#     return None
