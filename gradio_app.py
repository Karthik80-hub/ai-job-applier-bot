import os
import gradio as gr
import tempfile
import threading
import pandas as pd
import psycopg2
import requests
import mimetypes
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
from application_engine.db_config import DB_CONFIG
from core.job_controller import run_job_cycle
from pipeline_controller import main_pipeline
import pytesseract
from llm_modules.resume_parser import extract_full_resume_text

# Path for Tesseract (required for resume image OCR)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ATS_API_URL = os.getenv("ATS_API_URL", "http://localhost:9000/score")

bot_running = False
bot_thread = None

def toggle_bot(state):
    global bot_running, bot_thread
    if state == "Start Bot" and not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=run_forever)
        bot_thread.start()
        return "Bot is running..."
    elif state == "Stop Bot" and bot_running:
        bot_running = False
        return "Bot stopped."
    return "No action taken."

def run_forever():
    while bot_running:
        run_job_cycle()

def analyze(resume_file, job_description):
    if resume_file is None:
        return "Error: No resume uploaded.", "", "", "", "", ""

    resume_path = resume_file.name  # Gradio already saved it
    filename = os.path.basename(resume_path)
    
    # Check if the file exists and has content
    if not os.path.exists(resume_path):
        return "Error: Upload failed - file not found.", "", "", "", "", ""
    
    file_size = os.path.getsize(resume_path)
    if file_size < 100:
        return "Error: Uploaded file appears to be empty or too small.", "", "", "", "", ""

    print(f"[DEBUG] Resume file path: {resume_path}")
    print(f"[DEBUG] File size: {file_size} bytes")

    # Extract text for AI processing
    try:
        resume_text = extract_full_resume_text(resume_path)
        if not resume_text or not resume_text.strip():
            return "Error: Could not extract text from resume. Please ensure it's not image-based or corrupted.", "", "", "", "", ""
        
        print(f"[DEBUG] Extracted {len(resume_text)} characters of text")
    except Exception as e:
        print(f"[ERROR] Text extraction failed: {e}")
        return f"Error: Failed to extract text - {str(e)}", "", "", "", "", ""

    # Send to ATS API
    try:
        mime = mimetypes.guess_type(resume_path)[0] or "application/octet-stream"
        print(f"[DEBUG] File MIME type: {mime}")

        with open(resume_path, "rb") as f:
            resume_bytes = f.read()
            resp = requests.post(
                ATS_API_URL,
                files={"resume_file": (filename, resume_bytes, mime)},
                data={"job_description": job_description},
                timeout=60
            )

        if resp.status_code != 200:
            raise Exception(f"ATS API Error: {resp.status_code} - {resp.text}")

        ats_scores = resp.json()
        score = f"{ats_scores.get('Final ATS Score', 0)}%"
        matched = ", ".join(ats_scores.get("Matched Keywords", []))
        missing = ", ".join(ats_scores.get("Missing Keywords", []))

    except Exception as e:
        print(f"[ERROR] ATS API request failed: {e}")
        return f"Error: ATS API request failed - {str(e)}", "", "", "", "", ""

    # Generate AI responses using extracted text
    try:
        cover = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Write a cover letter:\n{job_description}\n\nResume:\n{resume_text}"}],
            temperature=0.7,
            max_tokens=500
        ).choices[0].message.content.strip()

        summary = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Generate a summary:\n{job_description}\n\nResume:\n{resume_text}"}],
            temperature=0.7,
            max_tokens=400
        ).choices[0].message.content.strip()

        screening = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Answer 'Why do you want this job?':\n{job_description}\n\nResume:\n{resume_text}"}],
            temperature=0.7,
            max_tokens=300
        ).choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] OpenAI API error: {str(e)}")
        return score, matched, missing, f"OpenAI Error: {str(e)}", "", ""

    return score, matched, missing, cover, summary, screening

def fetch_applications(status="all"):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        if status != "all":
            cur.execute("SELECT * FROM applications WHERE status = %s ORDER BY timestamp DESC", (status,))
        else:
            cur.execute("SELECT * FROM applications ORDER BY timestamp DESC")
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def export_csv(status):
    df = fetch_applications(status)
    path = "job_export.csv"
    df.to_csv(path, index=False)
    return path

def run_full_pipeline():
    try:
        main_pipeline()
        return "Pipeline Completed Successfully"
    except Exception as e:
        return f"Pipeline Failed: {str(e)}"

def create_gradio_ui():
    with gr.Blocks(title="Unified AI Job Application Bot") as demo:
        with gr.Tab("Copilot UI"):
            gr.Markdown("## Upload Resume and Job Description")
            resume = gr.File(file_types=[".pdf", ".docx"])
            jd = gr.Textbox(lines=10, label="Job Description")
            analyze_btn = gr.Button("Analyze")
            score = gr.Textbox(label="Match Score")
            matched = gr.Textbox(label="Matched Skills")
            missing = gr.Textbox(label="Missing Skills")
            cover = gr.Textbox(label="Cover Letter")
            summary = gr.Textbox(label="Resume Summary")
            screening = gr.Textbox(label="Screening Answer")

            analyze_btn.click(analyze, inputs=[resume, jd], outputs=[score, matched, missing, cover, summary, screening])

        with gr.Tab("Bot Control"):
            gr.Markdown("## Toggle Bot (24/7 mode)")
            bot_toggle = gr.Radio(["Start Bot", "Stop Bot"], label="Bot Control")
            bot_status = gr.Textbox(label="Status")
            bot_toggle.change(toggle_bot, inputs=bot_toggle, outputs=bot_status)

            gr.Markdown("## Run Full Auto-Apply Pipeline")
            run_btn = gr.Button("Run Pipeline Now")
            run_output = gr.Textbox(label="Pipeline Status")
            run_btn.click(run_full_pipeline, outputs=run_output)

        with gr.Tab("Dashboard"):
            gr.Markdown("## Application Dashboard")
            status_filter = gr.Radio(["all", "success", "failed"], label="Filter by Status", value="all")
            df_output = gr.Dataframe()
            load_btn = gr.Button("Load Applications")
            export_btn = gr.Button("Export CSV")
            csv_file = gr.File()

            load_btn.click(fetch_applications, inputs=status_filter, outputs=df_output)
            export_btn.click(export_csv, inputs=status_filter, outputs=csv_file)

    return demo

if __name__ == "__main__":
    demo = create_gradio_ui()
    demo.launch()
