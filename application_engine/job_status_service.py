import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv
from application_engine.db_config import DB_CONFIG

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            title TEXT,
            company TEXT,
            location TEXT,
            url TEXT,
            resume_path TEXT,
            status TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_and_notify(job, resume_path, status="success"):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO applications (timestamp, title, company, location, url, resume_path, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        datetime.now(),
        job["title"],
        job["company"],
        job["location"],
        job["url"],
        resume_path,
        status
    ))
    conn.commit()
    cur.close()
    conn.close()
    send_email(job, status)

def has_applied(job_url):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM applications WHERE url = %s AND status = 'success'", (job_url,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def has_failed_before(job_url, max_retries=2):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applications WHERE url = %s AND status = 'failed'", (job_url,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count >= max_retries

def export_successful_to_csv(filename="successful_applications.csv"):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, title, company, location, url, resume_path, status
        FROM applications
        WHERE status = 'success'
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    cur.close()
    conn.close()
    print(f"Exported successful applications to {filename}")

def get_success_count():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applications WHERE status = 'success'")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def send_csv_attachment(csv_file):
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg["Subject"] = "CSV Report: Successful Job Applications"
    msg["From"] = sender
    msg["To"] = receiver

    body = MIMEText("Attached is your latest job application report.")
    msg.attach(body)

    with open(csv_file, "rb") as f:
        attachment = MIMEApplication(f.read(), Name=os.path.basename(csv_file))
        attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(csv_file)}"'
        msg.attach(attachment)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
        print(f"CSV emailed to {receiver}")

def send_email(job, status):
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")

    subject = f"{'Success' if status == 'success' else 'Failure'} - Applied to: {job['title']} at {job['company']}"
    body = f"""
Job Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
URL: {job['url']}
Status: {status.upper()}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
        print(f"Email sent to {receiver}")
