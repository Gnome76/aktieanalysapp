import json
import os

FILNAMN = "bolag_data.json"

def load_data():
    if not os.path.exists(FILNAMN):
        return []
    try:
        with open(FILNAMN, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except Exception:
        return []

def save_data(data):
    try:
        with open(FILNAMN, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Fel vid sparande: {e}")

def delete_company(data, bolagsnamn):
    ny_lista = [bolag for bolag in data if bolag.get("bolagsnamn") != bolagsnamn]
    save_data(ny_lista)
    return ny_lista
