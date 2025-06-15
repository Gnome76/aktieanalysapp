import json
import os

DATAFIL = "aktier_data.json"

def load_data(filnamn=DATAFIL):
    if not os.path.exists(filnamn):
        return []
    try:
        with open(filnamn, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fel vid inläsning av data: {e}")
        return []

def save_data(data, filnamn=DATAFIL):
    try:
        with open(filnamn, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fel vid sparande av data: {e}")

def calculate_targetkurs_pe(vinst_nastaar, pe1, pe2):
    if vinst_nastaar is None or pe1 is None or pe2 is None:
        return None
    try:
        pe_med = (pe1 + pe2) / 2
        return vinst_nastaar * pe_med
    except Exception:
        return None

def calculate_targetkurs_ps(ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
    if None in (ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
        return None
    try:
        oms_tillv_genomsnitt = (oms_tillv_1 + oms_tillv_2) / 2 / 100  # från procent till decimal
        ps_med = (ps1 + ps2) / 2
        return ps_med * (1 + oms_tillv_genomsnitt) * nuv_kurs
    except Exception:
        return None

def calculate_undervardering(nuv_kurs, target_kurs):
    if nuv_kurs is None or target_kurs is None or target_kurs == 0:
        return None
    try:
        return (target_kurs - nuv_kurs) / target_kurs * 100
    except Exception:
        return None
