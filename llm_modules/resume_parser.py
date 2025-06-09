# llm_modules/resume_parser.py

import fitz  # PyMuPDF
import docx
import re
import io
import zipfile
from PIL import Image
import pytesseract

# Windows path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                full_text += text
            else:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                full_text += ocr_text

        print(f"[DEBUG] Extracted {len(full_text)} characters from PDF.")
        return full_text
    except Exception as e:
        print(f"[ERROR] PDF parsing failed: {e}")
        return ""

def extract_images_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        images = []
        for page_num in range(len(doc)):
            for img in doc.get_page_images(page_num):
                xref = img[0]
                base_image = doc.extract_image(xref)
                images.append(base_image["image"])
        return images
    except Exception as e:
        print(f"[WARN] PDF image extraction failed: {e}")
        return []

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        print(f"[DEBUG] Extracted {len(text)} characters from DOCX.")
        return text
    except Exception as e:
        print(f"[ERROR] DOCX parsing failed: {e}")
        return ""

def extract_images_from_docx(docx_path):
    images = []
    try:
        with zipfile.ZipFile(docx_path, "r") as archive:
            for file in archive.namelist():
                if file.startswith("word/media/") and file.lower().endswith((".png", ".jpg", ".jpeg")):
                    images.append(archive.read(file))
    except Exception as e:
        print(f"[WARN] DOCX image extraction failed: {e}")
    return images

def ocr_text_from_images(image_bytes_list):
    texts = []
    for img_bytes in image_bytes_list:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(img)
            if text.strip():
                texts.append(text)
        except Exception as e:
            print(f"[WARN] OCR failed for one image: {e}")
    return "\n".join(texts)

def clean_and_tokenize(text):
    text = text.lower()
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\-\+\.]{1,}\b", text)
    return list(set(words))  # Deduplicated skills

def extract_skills_from_resume(file_path):
    raw_text = ""
    image_text = ""

    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
        image_text = ocr_text_from_images(extract_images_from_pdf(file_path))
    elif file_path.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
        image_text = ocr_text_from_images(extract_images_from_docx(file_path))
    else:
        raise ValueError("Unsupported file type. Only .pdf and .docx supported.")

    combined_text = raw_text + "\n" + image_text
    print(f"[INFO] Total combined text length: {len(combined_text)} characters")
    return clean_and_tokenize(combined_text)

def extract_full_resume_text(file_path):
    """
    Extract full text content from a resume file, including OCR of any images.
    Returns the complete raw text instead of tokenized skills.
    """
    raw_text = ""
    image_text = ""

    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
        image_text = ocr_text_from_images(extract_images_from_pdf(file_path))
    elif file_path.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
        image_text = ocr_text_from_images(extract_images_from_docx(file_path))
    else:
        raise ValueError("Unsupported file type. Only .pdf and .docx supported.")

    combined_text = raw_text + "\n" + image_text
    print(f"[INFO] Total combined resume text length: {len(combined_text)} characters")
    
    # Debug output (temporary)
    try:
        with open("debug_resume_output.txt", "w", encoding="utf-8") as f:
            f.write(combined_text)
        print("[DEBUG] Wrote extracted text to debug_resume_output.txt")
    except Exception as e:
        print(f"[WARN] Could not write debug file: {e}")
    
    return combined_text
