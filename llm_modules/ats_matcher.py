# llm_modules/ats_matcher.py

import os
import nltk
import spacy
import string
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache
from llm_modules.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_images_from_pdf,
    extract_images_from_docx,
    ocr_text_from_images
)

# Download NLTK data only if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Singleton pattern for model loading
class ModelLoader:
    _nlp = None
    _model = None
    _stop_words = None

    @classmethod
    def get_nlp(cls):
        if cls._nlp is None:
            cls._nlp = spacy.load("en_core_web_sm")
        return cls._nlp

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._model

    @classmethod
    def get_stop_words(cls):
        if cls._stop_words is None:
            cls._stop_words = set(stopwords.words('english'))
        return cls._stop_words

# Initialize models lazily
def get_nlp():
    return ModelLoader.get_nlp()

def get_model():
    return ModelLoader.get_model()

def get_stop_words():
    return ModelLoader.get_stop_words()

@lru_cache(maxsize=1000)
def preprocess(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    tokens = nltk.word_tokenize(text)
    return ' '.join([word for word in tokens if word not in get_stop_words()])

@lru_cache(maxsize=100)
def extract_keywords(text):
    doc = get_nlp()(text)
    return list(set([chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 2]))


@lru_cache(maxsize=100)
def get_resume_sections(resume_text):
    sections = {'experience': '', 'skills': '', 'education': '', 'summary': ''}
    lines = resume_text.lower().splitlines()
    current_section = 'summary'
    for line in lines:
        if 'experience' in line:
            current_section = 'experience'
        elif 'skills' in line:
            current_section = 'skills'
        elif 'education' in line:
            current_section = 'education'
        else:
            sections[current_section] += ' ' + line
    return sections


def keyword_score(jd_keywords, resume_sections):
    all_text = ' '.join(resume_sections.values()).lower()
    matched = [word for word in jd_keywords if word in all_text]
    missing = [word for word in jd_keywords if word not in all_text]
    score = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0
    return round(score, 2), matched, missing


@lru_cache(maxsize=100)
def semantic_score(jd_text, resume_text):
    jd_emb = get_model().encode(jd_text, convert_to_tensor=True)
    res_emb = get_model().encode(resume_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(jd_emb, res_emb).item()
    return round(similarity * 100, 2)


def compute_ats_score(jd_text, resume_path):
    resume_text = ""
    images = []

    if resume_path.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_path)
        images = extract_images_from_pdf(resume_path)
    elif resume_path.endswith(".docx"):
        resume_text = extract_text_from_docx(resume_path)
        images = extract_images_from_docx(resume_path)
    else:
        return {"error": "Unsupported resume format"}

    ocr_text = ocr_text_from_images(images)
    resume_text += "\n" + ocr_text

    if not resume_text or len(resume_text.strip()) < 50:
        return {"error": "Resume content is too short or unreadable."}

    jd_clean = preprocess(jd_text)
    jd_keywords = list(set(extract_keywords(jd_text) + jd_clean.split()))
    resume_sections = get_resume_sections(resume_text)

    kw_score, matched, missing = keyword_score(jd_keywords, resume_sections)
    sem_score = semantic_score(jd_text, resume_text)

    final_score = round(0.6 * kw_score + 0.4 * sem_score, 2)

    return {
        "Final ATS Score": final_score,
        "Keyword Match Score": kw_score,
        "Semantic Similarity Score": sem_score,
        "Matched Keywords": matched,
        "Missing Keywords": missing,
        "Suggestions": f"Consider adding: {', '.join(missing[:10])}"
    }

def score_jobs_against_resume(jobs, resume_path="resume_templates/original/KARTHIK_RESUME.pdf"):
    results = []
    for job in jobs:
        try:
            score_result = compute_ats_score(job["description"], resume_path)
            job["ats_score"] = score_result.get("Final ATS Score", 0)
            job["Matched Keywords"] = score_result.get("Matched Keywords", [])
            job["Missing Keywords"] = score_result.get("Missing Keywords", [])
            results.append(job)
        except Exception as e:
            print(f"[ERROR] Failed to score job '{job.get('title', 'N/A')}': {e}")
    return results
