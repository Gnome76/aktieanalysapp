import json
import os

DATAFIL = "data.json"

def load_data():
    if not os.path.exists(DATAFIL):
        return []
    try:
        with open(DATAFIL, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_data(data):
    try:
        with open(DATAFIL, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fel vid sparande: {e}")

def calculate_targetkurs_pe(vinst_nastaar, pe1, pe2):
    if None in (vinst_nastaar, pe1, pe2):
        return None
    return vinst_nastaar * ((pe1 + pe2) / 2)

def calculate_targetkurs_ps(ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
    if None in (ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
        return None
    oms_tillv_genomsnitt = (oms_tillv_1 + oms_tillv_2) / 2 / 100
    return ((ps1 + ps2) / 2) * (1 + oms_tillv_genomsnitt) * nuv_kurs

def calculate_undervardering(nuv_kurs, target_kurs):
    if None in (nuv_kurs, target_kurs) or target_kurs == 0:
        return None
    return (target_kurs - nuv_kurs) / target_kurs * 100
