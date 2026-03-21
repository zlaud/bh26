from dotenv import load_dotenv
load_dotenv()

from database import db

try:
    db.command("ping")
    print("Connected to MongoDB")
    print("Collections:", db.list_collection_names())
except Exception as e:
    print(f"Connection failed: {e}")