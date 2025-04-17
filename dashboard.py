import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# Database config
DB_CONFIG = {
    "dbname": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", 5432)
}

# CSS for background image
def inject_custom_css(image_name="Mountains"):
    background_url = {
        "Mountains": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1500&q=80",
        "Abstract": "https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=1500&q=80",
        "Dark": "https://images.unsplash.com/photo-1527774061928-d116bee1a47a?auto=format&fit=crop&w=1500&q=80"
    }.get(image_name, "")

    st.markdown(f"""
        <style>
        .stApp {{
            background: url("{background_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.88);
            border-radius: 10px;
            padding: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql("SELECT * FROM applications ORDER BY timestamp DESC", conn)
    conn.close()
    return df

# Page setup
st.set_page_config(page_title="AI Job Tracker", layout="wide")
st.sidebar.title("Settings")

# Sidebar controls
bg_choice = st.sidebar.selectbox("Background Image", ["Mountains", "Abstract", "Dark"])
refresh_seconds = st.sidebar.slider("Auto-refresh (seconds)", 10, 300, 60)
st_autorefresh(interval=refresh_seconds * 1000, key="refresh")

# Apply background
inject_custom_css(bg_choice)

# Load & prepare data
df = load_data()
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# Filters
st.sidebar.markdown("### Filter Data")
filter_title = st.sidebar.selectbox("Filter by Title", ["All"] + sorted(df["title"].unique()))
filter_company = st.sidebar.selectbox("Filter by Company", ["All"] + sorted(df["company"].unique()))

filtered_df = df.copy()
if filter_title != "All":
    filtered_df = filtered_df[filtered_df["title"] == filter_title]
if filter_company != "All":
    filtered_df = filtered_df[filtered_df["company"] == filter_company]

# Summary
st.title("AI Job Application Dashboard")
st.markdown("### Summary Metrics")
st.write(f"Total Applications: {len(filtered_df)}")
st.write(f"Unique Companies: {filtered_df['company'].nunique()}")
st.write(f"Unique Titles: {filtered_df['title'].nunique()}")

# Download filtered CSV
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Filtered Data as CSV", data=csv_data, file_name="filtered_applications.csv", mime="text/csv")

# Resume preview/download
st.markdown("### Resume Files")
for i, row in filtered_df.iterrows():
    st.markdown(f"**{row['title']}** at **{row['company']}** – {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    with open(row['resume_path'], "r", encoding="utf-8", errors="ignore") as f:
        resume_text = f.read()
    st.text_area("Resume Preview", resume_text[:3000], height=200, key=f"preview_{i}")
    with open(row["resume_path"], "rb") as f:
        st.download_button("Download Resume", f, file_name=os.path.basename(row["resume_path"]), key=f"dl_{i}")

# Chart data
df_daily = filtered_df.groupby("date").count()["id"]
st.markdown("### Applications Over Time")
fig, ax = plt.subplots()
ax.plot(df_daily.index, df_daily.values, marker="o", linewidth=2)
ax.set_title("Applications Submitted Per Day")
ax.set_xlabel("Date")
ax.set_ylabel("Number of Applications")
ax.grid(True)
st.pyplot(fig)
