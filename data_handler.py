# data_handler.py
import json
import os

DATA_FILE = "bolag_data.json"

def load_data():
    """
    Läser in data från JSON-fil.
    Returnerar en lista med bolag (tom lista om fil inte finns).
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except (json.JSONDecodeError, IOError):
        return []

def save_data(data):
    """
    Sparar data (lista med bolag) till JSON-fil.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Fel vid sparande av data: {e}")

def delete_company(data, bolagsnamn):
    """
    Tar bort bolag med angivet bolagsnamn från data.
    Returnerar uppdaterad lista.
    """
    ny_data = [bolag for bolag in data if bolag.get("bolagsnamn") != bolagsnamn]
    return ny_data
