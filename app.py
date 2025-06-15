import streamlit as st
import pandas as pd
from datetime import datetime

# --- Funktioner för beräkningar av targetkurser och undervärdering ---
def berakna_targetkurs_pe(row):
    try:
        pe_avg = (row['pe1'] + row['pe2']) / 2
        return row['vinst_nastaar'] * pe_avg
    except Exception:
        return None

def berakna_targetkurs_ps(row):
    try:
        ps_avg = (row['ps1'] + row['ps2']) / 2
        oms_avg_tillvxt = (row['omsattningstillvaxt_ar1'] + row['omsattningstillvaxt_ar2']) / 2 / 100
        return ps_avg * (1 + oms_avg_tillvxt) * row['nuvarande_kurs']
    except Exception:
        return None

def berakna_undervardering(row):
    try:
        if row['targetkurs_pe'] and row['nuvarande_kurs']:
            underv = (row['targetkurs_pe'] - row['nuvarande_kurs']) / row['targetkurs_pe']
            return round(underv, 3)
        else:
            return 0
    except Exception:
        return 0

# --- Initiera data ---
def init_data():
    if "df" not in st.session_state:
        # Tom DataFrame med alla fält
        st.session_state.df = pd.DataFrame(columns=[
            'bolagsnamn', 'nuvarande_kurs', 'vinst_forra_aret', 'vinst_aret',
            'vinst_nastaar', 'omsattning_forra_aret', 'omsattningstillvaxt_ar1',
            'omsattningstillvaxt_ar2', 'pe_nu', 'pe1', 'pe2', 'pe3', 'pe4',
            'ps_nu', 'ps1', 'ps2', 'ps3', 'ps4', 'insatt_datum', 'senast_andrad'
        ])

def main():
    st.title("Aktieanalysapp")

    init_data()
    df = st.session_state.df

    # Kontroll om df är tom
    if df.empty:
        st.info("Inga bolag sparade än. Lägg till bolag i appen.")
        return

    # Beräkningar, lägg till kolumner om de inte finns
    if 'targetkurs_pe' not in df.columns or 'undervardering' not in df.columns:
        df["targetkurs_pe"] = df.apply(berakna_targetkurs_pe, axis=1)
        df["targetkurs_ps"] = df.apply(berakna_targetkurs_ps, axis=1)
        df["undervardering"] = df.apply(berakna_undervardering, axis=1)
        st.session_state.df = df

    visa_alla = st.checkbox("Visa alla bolag (annars endast undervärderade > 30%)")

    if "undervardering" not in df.columns:
        st.warning("Ingen beräkning av undervärdering finns ännu. Lägg till data först.")
        return

    if visa_alla:
        bolagslista = df.sort_values("undervardering", ascending=False).reset_index(drop=True)
    else:
        bolagslista = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)

    if bolagslista.empty:
        st.info("Inga bolag matchar kriterierna.")
        return

    # Bläddra mellan bolag
    index = st.session_state.get("index", 0)

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Föregående") and index > 0:
            index -= 1
    with col3:
        if st.button("Nästa") and index < len(bolagslista) - 1:
            index += 1

    st.session_state["index"] = index

    bolag = bolagslista.iloc[index]
    st.subheader(f"{bolag['bolagsnamn']} (index {index + 1} av {len(bolagslista)})")
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']}")
    st.write(f"Undervärdering: {bolag['undervardering']*100:.1f} %")

    # Visa mer nyckeltal
    st.write("**Nyckeltal:**")
    nyckeltal = {
        "Vinst förra året": bolag['vinst_forra_aret'],
        "Förväntad vinst i år": bolag['vinst_aret'],
        "Förväntad vinst nästa år": bolag['vinst_nastaar'],
        "Omsättning förra året": bolag['omsattning_forra_aret'],
        "Omsättningstillväxt i år %": bolag['omsattningstillvaxt_ar1'],
        "Omsättningstillväxt nästa år %": bolag['omsattningstillvaxt_ar2'],
        "Nuvarande P/E": bolag['pe_nu'],
        "P/E 1": bolag['pe1'],
        "P/E 2": bolag['pe2'],
        "P/E 3": bolag['pe3'],
        "P/E 4": bolag['pe4'],
        "Nuvarande P/S": bolag['ps_nu'],
        "P/S 1": bolag['ps1'],
        "P/S 2": bolag['ps2'],
        "P/S 3": bolag['ps3'],
        "P/S 4": bolag['ps4'],
    }
    for k,v in nyckeltal.items():
        st.write(f"{k}: {v}")

if __name__ == "__main__":
    main()
