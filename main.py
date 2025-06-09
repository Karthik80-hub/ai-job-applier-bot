import os
import argparse
import threading
import time
import subprocess
from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import psycopg2
from application_engine.db_config import DB_CONFIG

from scrapers.universal_scraper import fetch_all_jobs
from llm_modules import resume_matcher
from llm_modules.resume_tailor import tailor_resume
from application_engine import form_filler
from application_engine.job_status_service import (
    init_db,
    has_applied,
    has_failed_before,
    export_successful_to_csv,
    get_success_count,
    send_csv_attachment,
    log_and_notify
)
from backend.api.role_inference_router import router as role_router
from gradio_app import create_gradio_ui
from gradio.routes import mount_gradio_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

stop_signal = False

app = FastAPI(
    title="AI Job Applier Bot",
    description="AI-powered job application assistant",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Pydantic models
class JobApplication(BaseModel):
    job_id: str
    resume_path: str = "resume_templates/output"

class JobResponse(BaseModel):
    title: str
    company: str
    location: str
    url: str
    description: str
    matched_skills: List[str]
    match_score: float
    status: str = "pending"

class ATSScoreRequest(BaseModel):
    job_description: str
    resume_path: str

class ATSScoreResponse(BaseModel):
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    feedback: str

def run_ats_scorer(job_description: str, resume_path: str) -> Dict[str, Any]:
    """Run ATS scoring in a separate process to avoid dependency conflicts"""
    try:
        input_data = {
            "job_description": job_description,
            "resume_path": resume_path
        }
        
        result = subprocess.run(
            ['python', 'llm_modules/ats_runner.py'],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            check=True
        )
        
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ATS scoring failed: {e.stderr}")
        raise HTTPException(status_code=500, detail="ATS scoring failed")
    except Exception as e:
        print(f"Error in ATS scoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def run_job_cycle(test_mode=False):
    print("AI Job Applier Bot Started:", datetime.now())
    init_db()

    jobs = fetch_all_jobs()
    print(f"Found {len(jobs)} jobs.")

    matched_jobs = []
    for job in jobs:
        try:
            # Score each job using the separate ATS process
            score_result = run_ats_scorer(job["description"], os.getenv("RESUME_PATH"))
            job.update({
                "match_score": score_result["score"],
                "matched_skills": score_result["matched_skills"],
                "missing_skills": score_result["missing_skills"],
                "ats_feedback": score_result["feedback"]
            })
            matched_jobs.append(job)
        except Exception as e:
            print(f"Failed to score job {job.get('title', 'Unknown')}: {e}")
            continue

    print(f"Scored {len(matched_jobs)} jobs.")

    filtered_jobs = []
    applied, skipped, failed = 0, 0, 0

    for job in matched_jobs:
        if has_applied(job["url"]):
            print(f"Skipping {job['title']} (already applied)")
            skipped += 1
            continue
        if has_failed_before(job["url"]):
            print(f"Skipping {job['title']} (failed too many times)")
            skipped += 1
            continue
        if job.get("match_score", 0) < 50:
            print(f"Skipping {job['title']} (low ATS score: {job['match_score']}%)")
            skipped += 1
            continue

        try:
            # Use resume_matcher for custom resume generation
            resume_matcher.generate_custom_resume(job)
            filtered_jobs.append(job)
        except Exception as e:
            print(f"Failed to tailor resume for {job['title']}: {e}")
            failed += 1

    # Save filtered jobs to file for API access
    os.makedirs("matched_jobs", exist_ok=True)
    with open("matched_jobs/matched_jobs.json", "w") as f:
        json.dump(filtered_jobs, f)

    print("Step 4: Submitting applications...")
    for job in filtered_jobs:
        try:
            form_filler.apply_to_job(job)
            log_and_notify(job, resume_path="resume_templates/output", status="success")
            applied += 1
        except Exception as e:
            print(f"Apply failed for {job['title']}: {e}")
            log_and_notify(job, resume_path="resume_templates/output", status="failed")
            failed += 1

    export_successful_to_csv()

    success_count = get_success_count()
    if success_count > 0 and success_count % 50 == 0:
        send_csv_attachment("successful_applications.csv")

    print(f"Job Cycle Completed: {datetime.now()}")
    print(f"Stats: Applied={applied}, Skipped={skipped}, Failed={failed}")
    print("-" * 50)

def input_listener():
    global stop_signal
    while True:
        cmd = input("Type 'exit' or 'stop' to end the bot: ").strip().lower()
        if cmd in ["exit", "stop"]:
            stop_signal = True
            export_successful_to_csv()
            print("Bot stopped by user.")
            break

# API Endpoints
@app.get("/api/jobs", response_model=List[JobResponse])
async def get_matched_jobs():
    logger.info("API request received: GET /api/jobs")
    try:
        # First try to read from the cached file
        try:
            with open("matched_jobs/matched_jobs.json", "r") as f:
                jobs = json.load(f)
                if jobs:
                    logger.info(f"Returning {len(jobs)} cached jobs")
                    return jobs
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No cached jobs found, fetching new ones")
            pass

        # If no cached jobs or empty, fetch new ones
        jobs = fetch_all_jobs()
        logger.info(f"Fetched {len(jobs)} new jobs")
        
        # Score and filter jobs
        matched_jobs = []
        for job in jobs:
            if not has_applied(job["url"]) and not has_failed_before(job["url"]):
                try:
                    score_result = run_ats_scorer(job["description"], os.getenv("RESUME_PATH"))
                    job_data = {
                        "title": job.get("title", "Unknown Title"),
                        "company": job.get("company", "Unknown Company"),
                        "location": job.get("location", "Remote"),
                        "url": job.get("url", "#"),
                        "description": job.get("description", "No description available"),
                        "matched_skills": score_result.get("matched_skills", []),
                        "match_score": score_result.get("score", 0),
                        "status": "pending"
                    }
                    matched_jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Failed to process job {job.get('title', 'Unknown')}: {e}")
                    continue
        
        # Cache the results
        os.makedirs("matched_jobs", exist_ok=True)
        with open("matched_jobs/matched_jobs.json", "w") as f:
            json.dump(matched_jobs, f)
        
        logger.info(f"Returning {len(matched_jobs)} matched jobs")
        return matched_jobs
    except Exception as e:
        logger.error(f"Error in /api/jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_id}/apply")
async def apply_to_job(job_id: str, background_tasks: BackgroundTasks):
    logger.info(f"API request received: POST /api/jobs/{job_id}/apply")
    try:
        # Read matched jobs
        with open("matched_jobs/matched_jobs.json", "r") as f:
            jobs = json.load(f)
        
        # Find the job
        job = next((j for j in jobs if j["url"] == job_id), None)
        if not job:
            logger.error(f"Job not found: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
            
        # Check if already applied
        if has_applied(job["url"]):
            logger.warning(f"Already applied to job: {job_id}")
            raise HTTPException(status_code=400, detail="Already applied to this job")
            
        # Start application process in background
        logger.info(f"Starting application process for job: {job_id}")
        background_tasks.add_task(process_job_application, job)
        
        return {"message": "Application process started", "job_id": job_id}
    except Exception as e:
        logger.error(f"Error in /api/jobs/{job_id}/apply: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve React app's index.html for root route
@app.get("/")
async def serve_spa():
    """Serve the React SPA index.html"""
    return FileResponse("frontend/build/index.html")

@app.get("/api/jobs")
async def get_jobs():
    """Return mock jobs for testing UI performance"""
    try:
        # Use mock data instead of slow fetch_all_jobs()
        mock_jobs = [
            {
                "id": 1,
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "Remote",
                "description": "Example job description...",
                "url": "https://example.com/job1",
                "posted_date": "2024-03-20"
            },
            {
                "id": 2,
                "title": "Machine Learning Engineer",
                "company": "AI Solutions",
                "location": "New York, NY",
                "description": "Another example job...",
                "url": "https://example.com/job2",
                "posted_date": "2024-03-19"
            }
            # Add more mock jobs as needed
        ]
        return {"jobs": mock_jobs, "total": len(mock_jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{full_path:path}")
async def serve_spa_paths(full_path: str):
    """Serve the React SPA for all non-API routes"""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse("frontend/build/index.html")

@app.post("/api/score_resume", response_model=ATSScoreResponse)
async def score_resume(request: ATSScoreRequest):
    try:
        result = run_ats_scorer(request.job_description, request.resume_path)
        return ATSScoreResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_job_application(job: Dict[str, Any]):
    try:
        # Tailor resume
        tailor_resume(os.getenv("RESUME_PATH"), job, output_path="resume_templates/output")
        
        # Submit application
        form_filler.apply_to_job(job)
        log_and_notify(job, resume_path="resume_templates/output", status="success")
    except Exception as e:
        log_and_notify(job, resume_path="resume_templates/output", status="failed")
        print(f"Failed to process application: {str(e)}")

# Include routers
app.include_router(role_router, prefix="/api/roles")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "AI Job Applier Bot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "role_inference": "/api/roles/infer_roles",
            "health_check": "/api/roles/health",
            "gradio_ui": "/gradio"
        }
    }

# Mount Gradio UI inside FastAPI using v4.x method
gradio_ui = create_gradio_ui()
app = mount_gradio_app(app, gradio_ui, path="/gradio")

if __name__ == "__main__":
    logger.info("Starting AI Job Application Service")
    print("Type 'exit' or 'stop' to end the bot at any time.")

    # Start the input listener thread
    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

    # Run the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

    # The job cycle will run in the background through the API endpoints
    try:
        while not stop_signal:
            time.sleep(1)  # Keep main thread alive
    except (KeyboardInterrupt, SystemExit):
        export_successful_to_csv()
        logger.info("Service terminated.")
