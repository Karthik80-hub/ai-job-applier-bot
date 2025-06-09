import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from llm_modules.role_inference import infer_job_roles_from_resume, extract_text_from_pdf

def test_pdf_extraction():
    """Test that PDF text extraction works."""
    try:
        # Use your actual PDF resume
        resume_path = "data/GHANI ANILKUMAR REDDY.pdf"
        
        # Basic file checks
        assert os.path.exists(resume_path), f"Resume file not found: {resume_path}"
        assert resume_path.lower().endswith('.pdf'), "File must be a PDF"
        
        # Test text extraction
        text = extract_text_from_pdf(resume_path)
        assert text, "PDF text extraction returned empty string"
        assert len(text) > 100, "PDF text extraction returned suspiciously short text"
        print(f"\nSuccessfully extracted {len(text)} characters from PDF")
            
    except Exception as e:
        pytest.fail(f"PDF extraction test failed: {str(e)}")

def test_role_inference_pdf():
    """Test role inference with PDF resume."""
    try:
        resume_path = "data/GHANI ANILKUMAR REDDY.pdf"
        
        # Test role inference
        roles = infer_job_roles_from_resume(resume_path)
        
        # Validate response
        assert isinstance(roles, str), "Roles should be returned as a string"
        assert len(roles) > 0, "Roles string should not be empty"
        assert "," in roles, "Roles should be comma-separated"
        
        # Count number of roles
        role_list = [role.strip() for role in roles.split(",")]
        assert 3 <= len(role_list) <= 5, f"Expected 3-5 roles, got {len(role_list)}"
        
        # Print roles for manual verification
        print("\nInferred Roles from PDF:")
        for role in role_list:
            print(f"  • {role}")
            
    except Exception as e:
        pytest.fail(f"Role inference test failed: {str(e)}")

# TODO: Add DOCX tests when needed
"""
def test_docx_extraction():
    # Test DOCX extraction functionality
    pass

def test_role_inference_docx():
    # Test role inference with DOCX
    pass
"""

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 