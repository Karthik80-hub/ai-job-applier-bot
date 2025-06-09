#!/usr/bin/env python
import json
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from llm_modules.ats_matcher import compute_ats_score
from llm_modules.resume_parser import extract_text_from_pdf

def process_ats_request(input_data):
    try:
        # Extract job and resume data
        job_description = input_data.get("job_description", "")
        resume_path = input_data.get("resume_path", "")
        
        if not job_description or not resume_path:
            return {"error": "Missing job description or resume path"}
            
        if not os.path.exists(resume_path):
            return {"error": f"Resume file not found: {resume_path}"}

        # Compute ATS score
        score_result = compute_ats_score(job_description, resume_path)
        
        return score_result

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Process the request
        result = process_ats_request(input_data)
        
        # Output result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1) 