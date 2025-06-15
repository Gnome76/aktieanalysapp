# data_handler.py

import os
import json
from datetime import datetime

DATA_FILE = "bolag_data.json"

# Alla fält vi vill att varje bolag alltid ska ha
REQUIRED_FIELDS = {
    "bolagsnamn": "",
    "nuvarande_kurs": 0.0,
    "vinst_fjol": 0.0,
    "vinst_igar": 0.0,
    "vinst_nastaar": 0.0,
    "oms_fjol": 0.0,
    "oms_tillv_igar": 0.0,
    "oms_tillv_nastaar": 0.0,
    "pe_nu": 0.0,
    "pe1": 0.0,
    "pe2": 0.0,
    "pe3": 0.0,
    "pe4": 0.0,
    "ps_nu": 0.0,
    "ps1": 0.0,
    "ps2": 0.0,
    "ps3": 0.0,
    "ps4": 0.0,
    "insatt_datum": "",
    "senast_andrad": ""
}

def ensure_required_fields(bolag: dict) -> dict:
    """
    Säkerställ att varje bolag har alla fält från REQUIRED_FIELDS.
    Fyll i defaultvärden där det saknas.
    """
    for field, default_value in REQUIRED_FIELDS.items():
        bolag.setdefault(field, default_value)
    return bolag

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                # Se till att varje bolag får med alla nödvändiga fält
                updated_data = [ensure_required_fields(b) for b in data]
                return updated_data
            except Exception:
                return []
    return []

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def delete_company(index):
    data = load_data()
    if 0 <= index < len(data):
        del data[index]
        save_data(data)
