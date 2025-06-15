import json
import os

DATA_FILE = "bolag_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def delete_company(data, bolagsnamn):
    return [b for b in data if b.get("bolagsnamn", "").lower() != bolagsnamn.lower()]
