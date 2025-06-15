import json
import os
from typing import List, Dict, Optional

DATA_FILE = "bolag_data.json"

def load_data(filepath: str = DATA_FILE) -> List[Dict]:
    """
    Läser in data från JSON-fil och returnerar som lista av dict.
    Returnerar tom lista om fil inte finns eller är tom/korrupt.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                # Om filen inte innehåller en lista, returnera tom lista
                return []
    except (json.JSONDecodeError, IOError):
        # Fel vid läsning eller parsing av filen
        return []

def save_data(data: List[Dict], filepath: str = DATA_FILE) -> None:
    """
    Sparar data (lista av dict) till JSON-fil.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        # Hantera skrivfel, t.ex. logga eller visa meddelande i app
        print(f"Fel vid sparande av data: {e}")
