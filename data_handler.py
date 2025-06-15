import json
import os

DATA_FILE = "bolag_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_company(data, nytt_bolag):
    data.append(nytt_bolag)
    save_data(data)
    return data

def update_company(data, uppdaterat_bolag):
    for idx, bolag in enumerate(data):
        if bolag["bolagsnamn"] == uppdaterat_bolag["bolagsnamn"]:
            data[idx] = uppdaterat_bolag
            save_data(data)
            return data
    # Om ej finns, lägg till
    data.append(uppdaterat_bolag)
    save_data(data)
    return data

def delete_company(data, bolagsnamn):
    data = [b for b in data if b["bolagsnamn"] != bolagsnamn]
    save_data(data)
    return data
