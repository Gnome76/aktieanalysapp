import json
import os

DATA_FILE = "bolag_data.json"

def load_data():
    """Läser in data från JSON-fil. Returnerar lista med bolag."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []

def save_data(data):
    """Sparar data (lista med bolag) till JSON-fil."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def delete_company(data, bolagsnamn):
    """
    Tar bort bolag med angivet bolagsnamn från data-listan.
    Sparar uppdaterad lista och returnerar den.
    """
    updated_data = [b for b in data if b.get("bolagsnamn") != bolagsnamn]
    save_data(updated_data)
    return updated_data
