import json
import os

FILNAMN = "bolag_data.json"

def load_data():
    if not os.path.exists(FILNAMN):
        return []
    with open(FILNAMN, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(FILNAMN, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def delete_company(index, data):
    if 0 <= index < len(data):
        data.pop(index)
