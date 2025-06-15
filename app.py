import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_PATH = "data.json"

def las_in_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs",
            "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_ar_1_pct", "omsattningstillvaxt_ar_2_pct",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad",
        ])
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Säkerställ rätt datatyper
    num_cols = [
        "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
        "omsattning_forra_aret", "omsattningstillvaxt_ar_1_pct", "omsattningstillvaxt_ar_2_pct",
        "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
        "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["insatt_datum"] = pd.to_datetime(df["insatt_datum"], errors="coerce")
    df["senast_andrad"] = pd.to_datetime(df["senast_andrad"], errors="coerce")
    return df

def spara_data(df: pd.DataFrame):
    data = df.fillna("").to_dict(orient="records")
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, default=str)

def berakna_targetkurs_pe(rad):
    # targetkurs baserat på vinst_nasta_ar * medelvärdet av pe_1 och pe_2
    pe_med = (rad["pe_1"] + rad["pe_2"]) / 2
    return rad["vinst_nasta_ar"] * pe_med

def berakna_targetkurs_ps(rad):
    # Beräkna genomsnittlig omsättningstillväxt (år 1 och 2)
    oms_tillvxt_med = (rad["omsattningstillvaxt_ar_1_pct"] + rad["omsattningstillvaxt_ar_2_pct"]) / 2 / 100
    ps_med = (rad["ps_1"] + rad["ps_2"]) / 2
    # Targetkurs PS = genomsnittligt P/S * genomsnittlig omsättningstillväxt * nuvarande kurs (för att väga omsättningen)
    # Justering: Targetkurs PS = (ps_med * (1 + oms_tillvxt_med)) * rad["nuvarande_kurs"]
    # Eftersom omsättningstillväxten är i procent, multiplicera med (1 + tillväxt)
    return ps_med * (1 + oms_tillvxt_med) * rad["nuvarande_kurs"]

def berakna_undervardering(rad):
    target_pe = berakna_targetkurs_pe(rad)
    target_ps = berakna_targetkurs_ps(rad)
    kurs = rad["nuvarande_kurs"]

    underv_pe = 100 * (target_pe - kurs) / target_pe if target_pe else 0
    underv_ps = 100 * (target_ps - kurs) / target_ps if target_ps else 0

    # Ta den högsta undervärderingen som indikering (om båda finns)
    undervardering = max(underv_pe, underv_ps)
    return undervardering, target_pe, target_ps, underv_pe, underv_ps

import json
import os

DATAFIL = "aktier_data.json"

def las_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    return data

def spara_data(data):
    with open(DATAFIL, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def berakna_targetkurs_pe(vinst_nastaar, pe1, pe2):
    if vinst_nastaar is None or pe1 is None or pe2 is None:
        return None
    return vinst_nastaar * ((pe1 + pe2) / 2)

def berakna_targetkurs_ps(ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
    if None in (ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
        return None
    oms_tillv_genomsnitt = (oms_tillv_1 + oms_tillv_2) / 2 / 100  # från procent till decimal
    target_ps = ((ps1 + ps2) / 2) * (1 + oms_tillv_genomsnitt) * nuv_kurs
    return target_ps

def berakna_undervardering(nuv_kurs, target_kurs):
    if nuv_kurs is None or target_kurs is None or target_kurs == 0:
        return None
    return (target_kurs - nuv_kurs) / target_kurs * 100

def hitta_bolag(data, bolagsnamn):
    for bolag in data:
        if bolag.get("bolagsnamn") == bolagsnamn:
            return bolag
    return None

def spara_data(data, filnamn=DATAFIL):
    try:
        with open(filnamn, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Fel vid sparande av data: {e}")

def ladda_data(filnamn=DATAFIL):
    if not os.path.exists(filnamn):
        return []
    try:
        with open(filnamn, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Fel vid inläsning av data: {e}")
        return []

def ta_bort_bolag(data, bolagsnamn):
    ny_data = [bolag for bolag in data if bolag.get("bolagsnamn") != bolagsnamn]
    return ny_data

def main():
    st.title("Aktieanalysapp med Undervärdering och Redigering")

    # Ladda data
    data = ladda_data()

    # Visa och hantera bolag
    st.header("Lägg till nytt bolag")
    nytt_bolag = input_form()

    if nytt_bolag:
        data.append(nytt_bolag)
        spara_data(data)
        st.success(f"Bolaget {nytt_bolag['bolagsnamn']} tillagt!")

    st.header("Hantera befintliga bolag")

    # Välj bolag att redigera eller ta bort
    bolagslista = [bolag["bolagsnamn"] for bolag in data]
    valt_bolag = st.selectbox("Välj bolag att redigera eller ta bort", bolagslista, key="valj_bolag")

    if valt_bolag:
        bolag_data = next((b for b in data if b["bolagsnamn"] == valt_bolag), None)

        if bolag_data:
            redigerat_bolag = edit_form(bolag_data)
            if redigerat_bolag:
                # Uppdatera bolag i data
                for i, b in enumerate(data):
                    if b["bolagsnamn"] == valt_bolag:
                        data[i] = redigerat_bolag
                        break
                spara_data(data)
                st.success(f"Bolaget {valt_bolag} uppdaterat!")

            if st.button("Ta bort bolag", key="ta_bort_knapp"):
                data = ta_bort_bolag(data, valt_bolag)
                spara_data(data)
                st.success(f"Bolaget {valt_bolag} borttaget!")
                st.experimental_rerun()

    # Visa översikt och filtrering
    st.header("Översikt över bolag")
    visa_oversikt(data)

if __name__ == "__main__":
    main()
