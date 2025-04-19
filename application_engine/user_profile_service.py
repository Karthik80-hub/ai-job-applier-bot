import os
import yaml
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SCHEMA_PATH = "configs/universal_signup_schema.yaml"


def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return yaml.safe_load(f)["universal_signup_questions"]


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432)
    )


def fetch_existing_answers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT section, key, value FROM user_profile")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    profile = {}
    for section, key, value in rows:
        profile.setdefault(section, {})[key] = value
    return profile


def save_answer(section, key, value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_profile (section, key, value)
        VALUES (%s, %s, %s)
        ON CONFLICT (section, key)
        DO UPDATE SET value = EXCLUDED.value
    """, (section, key, value))
    conn.commit()
    cur.close()
    conn.close()


def prompt_for_missing_answers(schema, existing_profile):
    for section, fields in schema.items():
        print(f"\n--- {section.replace('_', ' ').title()} ---")
        for key, meta in fields.items():
            label = meta.get("label", key)
            required = meta.get("required", False)
            current_value = existing_profile.get(section, {}).get(key)

            if not current_value:
                suffix = " *" if required else " (optional)"
                answer = input(f"{label}{suffix}: ").strip()
                while required and not answer:
                    print("This field is required.")
                    answer = input(f"{label}{suffix}: ").strip()
                if answer:
                    save_answer(section, key, answer)


def get_user_answer(section, key):
    profile = fetch_existing_answers()
    return profile.get(section, {}).get(key)


if __name__ == "__main__":
    schema = load_schema()
    profile = fetch_existing_answers()
    prompt_for_missing_answers(schema, profile)

    print("\nSaved answers:")
    print(fetch_existing_answers())
