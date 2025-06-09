import os
from llm_modules.role_inference import infer_job_roles_from_resume
from scrapers.company_discovery import discover_career_urls_from_roles
from scrapers.dynamic_scraper import dynamic_scrape_jobs as fetch_jobs_from_company_urls
from llm_modules.resume_tailor import score_and_filter_jobs, apply_to_jobs

def main_pipeline():
    # Step 1: Resume path
    RESUME_PATH = os.getenv("RESUME_PATH", "data/KARTHIK_RESUME.pdf")

    # Step 2: Extract job roles from resume
    print("\nInferring job roles from resume...")
    roles = infer_job_roles_from_resume(RESUME_PATH)
    print("Extracted roles:", roles)

    # Step 3: Discover career pages
    print("\nDiscovering company career pages...")
    career_results = discover_career_urls_from_roles(roles)
    career_urls = [res["careers_url"] for res in career_results if res["careers_url"]]
    print("Discovered career URLs:", career_urls)

    # Step 4: Scrape job listings
    print("\nScraping job listings from career pages...")
    jobs = fetch_jobs_from_company_urls(career_results)
    print(f"Found {len(jobs)} jobs from {len(career_urls)} companies.")

    # Step 5: Score & Filter by ATS
    print("\nScoring jobs using ATS matching logic...")
    filtered_jobs = score_and_filter_jobs(jobs, RESUME_PATH)
    print(f"Selected {len(filtered_jobs)} high-match jobs.")

    # Step 6: Apply to filtered jobs
    print("\nSubmitting applications to selected jobs...")
    apply_to_jobs(filtered_jobs)

    print("\nAuto-apply pipeline complete.")
    return "Pipeline completed successfully"

if __name__ == "__main__":
    main_pipeline()
