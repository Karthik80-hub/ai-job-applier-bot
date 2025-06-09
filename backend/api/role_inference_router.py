import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from llm_modules.role_inference import infer_job_roles_from_resume
from uuid import uuid4
import shutil
import logging

# Create router
router = APIRouter(
    prefix="/api/roles",
    tags=["role-inference"],
    responses={404: {"description": "Not found"}},
)

# Setup logging
logger = logging.getLogger(__name__)

@router.post("/infer_roles")
async def infer_roles_from_resume(resume_file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX) and infer 3–5 ideal job roles.
    """
    try:
        file_ext = resume_file.filename.split(".")[-1].lower()
        if file_ext not in ["pdf", "doc", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload a PDF or DOCX.")

        os.makedirs("uploads", exist_ok=True)
        temp_path = f"uploads/{uuid4().hex}_{resume_file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(resume_file.file, f)

        logger.info(f"Saved uploaded resume to: {temp_path}")
        roles = infer_job_roles_from_resume(temp_path)
        os.remove(temp_path)

        return JSONResponse(content={"inferred_roles": [r.strip() for r in roles.split(",")]}, status_code=200)

    except Exception as e:
        logger.error(f"Failed to infer roles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "role-inference"} 