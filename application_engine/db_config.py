import os
from dotenv import load_dotenv

load_dotenv()  # <-- this loads your .env file

DB_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT", 5432),
    "dbname": os.getenv("PG_DB"),        # ❗ use "dbname", not "database"
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD")
}
