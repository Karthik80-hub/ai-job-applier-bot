# tests/test_parser_all.py

from utils.parser import parse_all_resumes

folder_path = "resume_templates/output"  # Update if your resumes are stored elsewhere

# Test all resumes in the folder (PDF/DOCX)
results = parse_all_resumes(folder_path, use_gpt=False, save_outputs=True)

for res in results:
    print(f"\nFile: {res['file']}")
    print("Parsed Info:")
    print(res["parsed"])
    print("-" * 60)
