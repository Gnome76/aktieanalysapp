import json
import os

DATA_FILE = "bolag_data.json"

# Lista på alla nycklar som varje bolag ska ha med standardvärden
REQUIRED_KEYS = {
    "bolagsnamn": "",
    "nuvarande_kurs": 0.0,
    "vinst_forra_aret": 0.0,
    "vinst_i_ar": 0.0,
    "vinst_nastaar": 0.0,
    "omsattning_forra_aret": 0.0,
    "omsattningstillvaxt_i_ar": 0.0,
    "omsattningstillvaxt_nastaar": 0.0,
    "nuvarande_pe": 0.0,
    "pe1": 0.0,
    "pe2": 0.0,
    "pe3": 0.0,
    "pe4": 0.0,
    "nuvarande_ps": 0.0,
    "ps1": 0.0,
    "ps2": 0.0,
    "ps3": 0.0,
    "ps4": 0.0,
    "insatt_datum": "",
    "senast_andrad": "",
}

def validate_bolag_data(bolag):
    # Se till att alla nycklar finns, annars lägg till standardvärde
    for key, default in REQUIRED_KEYS.items():
        if key not in bolag:
            bolag[key] = default
    return bolag

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Validera varje bolag
        data = [validate_bolag_data(b) for b in data]
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def delete_company(data, bolagsnamn):
    new_data = [b for b in data if b["bolagsnamn"] != bolagsnamn]
    save_data(new_data)
    return new_data
