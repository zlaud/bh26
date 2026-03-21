import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path) as f:
        return json.load(f)