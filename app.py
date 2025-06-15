import streamlit as st
import pandas as pd
import json
import os

# Filväg för datafil i Streamlit Cloud
DATA_PATH = "aktiedata.json"

# Förväntade kolumner i DataFrame
EXPECTED_COLUMNS = [
    "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret",
    "vinst_i_ar", "vinst_nasta_ar", "oms_forra_aret",
    "oms_tillv_i_ar", "oms_tillv_nasta_ar",
    "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
    "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4"
]

def las_data():
    """Läser in data från json-fil, säkerställer att alla förväntade kolumner finns."""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Lägg till saknade kolumner med NaN som default
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA
        # Rensa index om det är fel
        df = df.reset_index(drop=True)
        return df
    else:
        # Skapa tom DataFrame med korrekta kolumner
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

def spara_data(df):
    """Sparar DataFrame till json-fil."""
    with open(DATA_PATH, "w") as f:
        json.dump(df.to_dict(orient="records"), f)

def konvertera_till_num(df):
    """Konverterar relevanta kolumner till numeriska värden, hanterar felaktiga värden."""
    nummer_kolumner = [
        "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
        "oms_forra_aret", "oms_tillv_i_ar", "oms_tillv_nasta_ar",
        "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
        "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4"
    ]
    for col in nummer_kolumner:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

import streamlit as st
import pandas as pd
from datetime import datetime

def berakna_targetkurser(df):
    # Kontrollera att nödvändiga kolumner finns för beräkning
    required_cols = ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "nuvarande_kurs",
                     "omsattning_1", "omsattning_2"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0  # Om kolumn saknas, skapa med 0 som default

    # Beräkna targetkurs baserat på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Beräkna omsättningstillväxt som genomsnittlig procentuell ökning
    oms_tillv = 0
    with pd.option_context('mode.use_inf_as_na', True):
        oms_tillv_1 = ((df["omsattning_1"] - df["omsattning_2"]) / df["omsattning_2"]).replace([pd.NA, pd.NaT], 0)
        oms_tillv = oms_tillv_1.fillna(0).replace([float('inf'), -float('inf')], 0)
    oms_tillv = oms_tillv.fillna(0)
    
    # Genomsnittlig omsättningstillväxt i decimalform, säkerställ att ej negativ
    oms_tillv_avg = oms_tillv.clip(lower=0)

    # Beräkna targetkurs baserat på P/S och omsättningstillväxt
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + oms_tillv_avg) * df["nuvarande_kurs"]

    return df

def visa_bolag(df):
    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    df = berakna_targetkurser(df)

    # Undervärdering i procent baserat på targetkurser och nuvarande kurs
    df["undervärdering_pe_%"] = ((df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]) * 100
    df["undervärdering_ps_%"] = ((df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]) * 100

    # Max undervärdering för enkel sortering
    df["max_undervärdering"] = df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)

    # Lägg till kolumn 'kopvard': True om nuvarande kurs är max 30% av targetkurs (antingen P/E eller P/S)
    df["kopvard"] = (
        (df["nuvarande_kurs"] <= 0.3 * df["targetkurs_pe"]) |
        (df["nuvarande_kurs"] <= 0.3 * df["targetkurs_ps"])
    )

    # Checkbox för att visa endast undervärderade bolag (minst 30% rabatt)
    visa_endast_undervarderade = st.checkbox("Visa endast undervärderade bolag (minst 30% rabatt)", value=True)

    if visa_endast_undervarderade:
        filtrerat_df = df[df["max_undervärdering"] >= 30].copy()
    else:
        filtrerat_df = df.copy()

    # Sortera filtrerat dataframe efter max undervärdering, fallande
    filtrerat_df = filtrerat_df.sort_values(by="max_undervärdering", ascending=False)

    # Visa tabell med relevanta kolumner
    st.dataframe(
        filtrerat_df[[
            "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps",
            "undervärdering_pe_%", "undervärdering_ps_%", "max_undervärdering", "kopvard"
        ]],
        use_container_width=True
    )

    return df

def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    # Säkerställ att DataFrame inte är None
    if df is None or df.empty:
        df = pd.DataFrame(columns=bolag_ny.keys())

    # Rensa ny bolag-data från tomma strängar som ska vara None
    for k, v in bolag_ny.items():
        if v == "":
            bolag_ny[k] = None

    # Kontrollera om bolag redan finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolag_ny["bolagsnamn"].lower()]

    if len(idx) > 0:
        # Uppdatera existerande rad
        i = idx[0]
        for col, val in bolag_ny.items():
            df.at[i, col] = val
        df.at[i, "senast_andrad"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Lägg till ny rad med insatt_datum och senast_andrad
        bolag_ny["insatt_datum"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bolag_ny["senast_andrad"] = bolag_ny["insatt_datum"]
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)

    return df

import streamlit as st
import pandas as pd

def berakna_targetkurser(df):
    # Säkerställ att nödvändiga kolumner finns, annars fyll med NaN
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "oms_tillvaxt_ar", "oms_tillvaxt_nasta_ar"]:
        if col not in df.columns:
            df[col] = float("nan")

    # Targetkurs baserat på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Targetkurs baserat på P/S och omsättningstillväxt
    medel_oms_tillv = (df["oms_tillvaxt_ar"].fillna(0) + df["oms_tillvaxt_nasta_ar"].fillna(0)) / 2
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + medel_oms_tillv / 100) * df["oms_forra_ar"]

    # Undervärdering i procent
    df["undervärdering_pe_%"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"] * 100
    df["undervärdering_ps_%"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"] * 100

    # Max undervärdering för sortering och presentation
    df["max_undervärdering"] = df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)

    # Köp-rekommendation: köp om nuvarande kurs är max 30% av targetkurs (lägsta av pe/ps)
    df["targetkurs_min"] = df[["targetkurs_pe", "targetkurs_ps"]].min(axis=1)
    df["kopvard"] = df["nuvarande_kurs"] <= df["targetkurs_min"] * 0.3

    return df

def visa_bolag(df):
    st.header("Översikt - Sparade bolag")

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    # Beräkna targetkurser och undervärdering
    df = berakna_targetkurser(df)

    # Filter: checkbox för att visa endast undervärderade bolag (>30% undervärdering)
    endast_undervard = st.checkbox("Visa endast undervärderade bolag (>30%)", value=False)

    if endast_undervard:
        filtrerat_df = df[df["max_undervärdering"] >= 30]
    else:
        filtrerat_df = df.copy()

    if filtrerat_df.empty:
        st.warning("Inga bolag matchar filtreringen.")
        return df

    # Sortera på max undervärdering, fallande
    filtrerat_df = filtrerat_df.sort_values(by="max_undervärdering", ascending=False)

    # Visa tabell med viktiga kolumner
    visningskolumner = [
        "bolagsnamn",
        "nuvarande_kurs",
        "targetkurs_pe",
        "targetkurs_ps",
        "undervärdering_pe_%",
        "undervärdering_ps_%",
        "max_undervärdering",
        "kopvard"
    ]
    # Kontrollera att alla kolumner finns, annars skapa med NaN
    for col in visningskolumner:
        if col not in filtrerat_df.columns:
            filtrerat_df[col] = float("nan")

    df_visning = filtrerat_df[visningskolumner].copy()
    df_visning["kopvard"] = df_visning["kopvard"].apply(lambda x: "Ja" if x else "Nej")

    st.dataframe(df_visning.style.format({
        "nuvarande_kurs": "{:.2f}",
        "targetkurs_pe": "{:.2f}",
        "targetkurs_ps": "{:.2f}",
        "undervärdering_pe_%": "{:.1f} %",
        "undervärdering_ps_%": "{:.1f} %",
        "max_undervärdering": "{:.1f} %",
    }))

    # Ta bort bolag - välj bolag att ta bort
    st.subheader("Ta bort bolag")
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=[""] + list(df["bolagsnamn"].unique()), index=0)
    if bolag_att_ta_bort:
        if st.button(f"Ta bort {bolag_att_ta_bort}"):
            df = df[df["bolagsnamn"] != bolag_att_ta_bort].reset_index(drop=True)
            st.success(f"Bolaget {bolag_att_ta_bort} har tagits bort.")
            # Uppdatera lagring efter borttagning
            spara_data(df)
            st.experimental_rerun()

    # Visa ett bolag i taget med bläddring
    st.subheader("Detaljerad vy - ett bolag i taget")
    bolag_list = filtrerat_df["bolagsnamn"].unique().tolist()
    if bolag_list:
        if "index_bolag" not in st.session_state:
            st.session_state["index_bolag"] = 0

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Föregående"):
                st.session_state["index_bolag"] = max(0, st.session_state["index_bolag"] - 1)
        with col3:
            if st.button("Nästa ➡️"):
                st.session_state["index_bolag"] = min(len(bolag_list) - 1, st.session_state["index_bolag"] + 1)

        current_bolag = bolag_list[st.session_state["index_bolag"]]
        bolag_data = filtrerat_df[filtrerat_df["bolagsnamn"] == current_bolag].iloc[0]

        st.markdown(f"### {current_bolag}")
        st.write(f"Nuvarande kurs: {bolag_data['nuvarande_kurs']:.2f} SEK")
        st.write(f"Targetkurs P/E: {bolag_data['targetkurs_pe']:.2f} SEK")
        st.write(f"Targetkurs P/S: {bolag_data['targetkurs_ps']:.2f} SEK")
        st.write(f"Max undervärdering: {bolag_data['max_undervärdering']:.1f} %")
        st.write(f"Köpvärd (<=30% av target): {'Ja' if bolag_data['kopvard'] else 'Nej'}")

    return df

def spara_data(df):
    try:
        df.to_json("bolag_data.json", orient="records", indent=2)
    except Exception as e:
        st.error(f"Kunde inte spara data: {e}")

def las_data():
    try:
        df = pd.read_json("bolag_data.json")
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "bolagsnamn",
            "nuvarande_kurs",
            "vinst_forra_ar",
            "vinst_i_ar",
            "vinst_nasta_ar",
            "oms_forra_ar",
            "oms_tillvaxt_ar",
            "oms_tillvaxt_nasta_ar",
            "nuvarande_pe",
            "pe_1",
            "pe_2",
            "pe_3",
            "pe_4",
            "nuvarande_ps",
            "ps_1",
            "ps_2",
            "ps_3",
            "ps_4"
        ])

import streamlit as st
import pandas as pd

# --- Funktioner från tidigare delar ska finnas här ---
# antar att berakna_targetkurser, visa_bolag, spara_data, las_data finns definierade

def main():
    st.set_page_config(page_title="Aktieanalysapp", layout="wide")

    st.title("Aktieanalysapp - Undervärderade Bolag")

    # Ladda data vid start
    df = las_data()

    # Visa inmatningsformulär för nytt eller redigera bolag
    with st.expander("Lägg till / Redigera bolag", expanded=True):
        df = visa_form(df)

    # Visa bolag, undervärdering, tabell, filtrering, radering, detaljerad vy
    df = visa_bolag(df)

    # Spara data efter eventuella ändringar
    spara_data(df)

if __name__ == "__main__":
    main()
