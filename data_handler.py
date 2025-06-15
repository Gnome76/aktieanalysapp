import json
import os

DATA_FILE = "bolag_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def delete_company(data, company_name):
    new_data = [item for item in data if item["bolagsnamn"] != company_name]
    save_data(new_data)
