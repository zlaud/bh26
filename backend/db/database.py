import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ["MONGODB_URI"])
db = client[os.environ.get("MONGODB_DB", "food_resilience")]

articles_col = db["articles"]
signals_col = db["signals"]
food_risks_col = db["food_risks"]