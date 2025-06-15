import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.set_page_config(page_title="Aktieanalys", layout="centered")

DATA_PATH = "/mount/src/aktieanalysapp/data.json"

# --- Ladda data ---
def las_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            return pd.DataFrame(data)
    else:
        return pd.DataFrame()

# --- Spara data ---
def spara_data(df):
    with open(DATA_PATH, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# --- Initiera DataFrame ---
def initiera_df():
    kolumner = [
        "bolagsnamn", "nuvarande_kurs", "vinst_forra", "vinst_i_ar", "vinst_nasta_ar",
        "oms_forra", "oms_tillv_i_ar", "oms_tillv_nasta_ar", "pe_nu", "pe_1", "pe_2",
        "pe_3", "pe_4", "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
        "insatt_datum", "senast_andrad"
    ]
    return pd.DataFrame(columns=kolumner)

# --- Lägg till eller uppdatera bolag ---
def lagg_till_eller_uppdatera_bolag(df, nytt_bolag):
    bolagsnamn_ny = str(nytt_bolag["bolagsnamn"]).lower()
    if "bolagsnamn" in df.columns:
        df["bolagsnamn_lower"] = df["bolagsnamn"].astype(str).str.lower()
        idx = df.index[df["bolagsnamn_lower"] == bolagsnamn_ny].tolist()
        df.drop(columns=["bolagsnamn_lower"], inplace=True)
    else:
        idx = []

    nytt_bolag["senast_andrad"] = datetime.now().strftime("%Y-%m-%d")
    
    if idx:
        for key in nytt_bolag:
            df.at[idx[0], key] = nytt_bolag[key]
    else:
        nytt_bolag["insatt_datum"] = datetime.now().strftime("%Y-%m-%d")
        df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)

    return df

# --- Formulär för att lägga till/redigera bolag ---
def visa_form(df):
    st.header("Lägg till eller redigera bolag")
    med_redigering = st.toggle("Visa avancerad inmatning")

    with st.form(key="form_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", 0.0)

        if med_redigering:
            vinst_forra = st.number_input("Vinst förra året", 0.0)
            vinst_i_ar = st.number_input("Förväntad vinst i år", 0.0)
            vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", 0.0)
            oms_forra = st.number_input("Omsättning förra året", 0.0)
            oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", 0.0)
            oms_tillv_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", 0.0)
            pe_nu = st.number_input("Nuvarande P/E", 0.0)
            pe_1 = st.number_input("P/E år 1", 0.0)
            pe_2 = st.number_input("P/E år 2", 0.0)
            pe_3 = st.number_input("P/E år 3", 0.0)
            pe_4 = st.number_input("P/E år 4", 0.0)
            ps_nu = st.number_input("Nuvarande P/S", 0.0)
            ps_1 = st.number_input("P/S år 1", 0.0)
            ps_2 = st.number_input("P/S år 2", 0.0)
            ps_3 = st.number_input("P/S år 3", 0.0)
            ps_4 = st.number_input("P/S år 4", 0.0)
        else:
            vinst_forra = vinst_i_ar = vinst_nasta_ar = 0.0
            oms_forra = oms_tillv_i_ar = oms_tillv_nasta_ar = 0.0
            pe_nu = pe_1 = pe_2 = pe_3 = pe_4 = 0.0
            ps_nu = ps_1 = ps_2 = ps_3 = ps_4 = 0.0

        submitted = st.form_submit_button("Spara")
        if submitted and bolagsnamn:
            nytt_bolag = {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra": vinst_forra,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "oms_forra": oms_forra,
                "oms_tillv_i_ar": oms_tillv_i_ar,
                "oms_tillv_nasta_ar": oms_tillv_nasta_ar,
                "pe_nu": pe_nu,
                "pe_1": pe_1,
                "pe_2": pe_2,
                "pe_3": pe_3,
                "pe_4": pe_4,
                "ps_nu": ps_nu,
                "ps_1": ps_1,
                "ps_2": ps_2,
                "ps_3": ps_3,
                "ps_4": ps_4,
            }
            df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
            spara_data(df)
            st.success("Bolaget har sparats!")
    return df

# --- Beräkna targetkurser ---
def beräkna_targetkurser(df):
    df = df.copy()
    df["targetkurs_pe"] = df.apply(lambda row: row["vinst_nasta_ar"] * ((row["pe_1"] + row["pe_2"]) / 2)
                                   if row["pe_1"] > 0 and row["pe_2"] > 0 else 0.0, axis=1)
    
    df["oms_tillv_snitt"] = df[["oms_tillv_i_ar", "oms_tillv_nasta_ar"]].mean(axis=1) / 100
    df["ps_snitt"] = df[["ps_1", "ps_2"]].mean(axis=1)
    
    df["targetkurs_ps"] = df["ps_snitt"] * df["oms_tillv_snitt"] * df["nuvarande_kurs"]
    
    df["underv_pe"] = ((df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]) * 100
    df["underv_ps"] = ((df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]) * 100

    df["underv_pe"] = df["underv_pe"].round(1)
    df["underv_ps"] = df["underv_ps"].round(1)

    return df

# --- Visa nyckeltal för ett bolag ---
def visa_bolag(df, index):
    bolag = df.iloc[index]
    st.subheader(f"📊 {bolag['bolagsnamn']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nuvarande kurs", f"{bolag['nuvarande_kurs']:.2f} kr")
        st.metric("Targetkurs P/E", f"{bolag['targetkurs_pe']:.2f} kr")
        st.metric("Undervärdering P/E", f"{bolag['underv_pe']:.1f} %")
    with col2:
        st.metric("Targetkurs P/S", f"{bolag['targetkurs_ps']:.2f} kr")
        st.metric("Undervärdering P/S", f"{bolag['underv_ps']:.1f} %")

    # Visa om köpvärd enligt 30% rabatt
    kopepe = bolag["underv_pe"] >= 30
    kopeps = bolag["underv_ps"] >= 30
    status_pe = "✅" if kopepe else "❌"
    status_ps = "✅" if kopeps else "❌"
    
    st.markdown(f"**Köpvärd enligt P/E (≥30%)**: {status_pe}")
    st.markdown(f"**Köpvärd enligt P/S (≥30%)**: {status_ps}")

# --- Filtrera och sortera bolag ---
def filtrera_bolag(df, endast_undervarderade=True):
    df = beräkna_targetkurser(df)
    
    if endast_undervarderade:
        df = df[(df["underv_pe"] >= 30) | (df["underv_ps"] >= 30)]

    df = df.copy()
    df["max_underv"] = df[["underv_pe", "underv_ps"]].max(axis=1)
    df = df.sort_values(by="max_underv", ascending=False).reset_index(drop=True)
    return df

# --- Visa bolag ett i taget med bläddringsknappar ---
def visa_ett_i_taget(df):
    if df.empty:
        st.info("Inga bolag att visa.")
        return

    if "index_bolag" not in st.session_state:
        st.session_state.index_bolag = 0

    total = len(df)
    index = st.session_state.index_bolag

    visa_bolag(df, index)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Föregående") and index > 0:
            st.session_state.index_bolag -= 1
            st.experimental_rerun()
    with col3:
        if st.button("Nästa ➡️") and index < total - 1:
            st.session_state.index_bolag += 1
            st.experimental_rerun()

    st.caption(f"Visar bolag {index + 1} av {total}")

# --- Visa tabell över alla bolag ---
def visa_oversiktstabell(df):
    df = beräkna_targetkurser(df)
    visa_df = df[[
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps",
        "underv_pe", "underv_ps", "senast_andrad"
    ]].copy()

    visa_df = visa_df.rename(columns={
        "bolagsnamn": "Bolagsnamn",
        "nuvarande_kurs": "Kurs",
        "targetkurs_pe": "Target P/E",
        "targetkurs_ps": "Target P/S",
        "underv_pe": "Underv. P/E %",
        "underv_ps": "Underv. P/S %",
        "senast_andrad": "Uppdaterad"
    })

    st.subheader("📈 Översikt över bolag")
    st.dataframe(visa_df, use_container_width=True)

# --- Huvudfunktion ---
def main():
    st.title("📊 Aktieanalysapp")

    df = las_data()

    # --- Formulär för att lägga till/redigera bolag ---
    with st.expander("➕ Lägg till eller redigera bolag"):
        df = visa_form(df)

    # --- Filter: endast undervärderade? ---
    endast_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=True)

    # --- Välj visningsläge ---
    visningslage = st.radio("Välj visningsläge", ["Visa ett bolag i taget", "Visa alla i tabell"])

    # --- Filtrera data ---
    filtrerad_df = filtrera_bolag(df, endast_undervarderade)

    # --- Visa bolag beroende på läge ---
    if visningslage == "Visa ett bolag i taget":
        visa_ett_i_taget(filtrerad_df)
    else:
        visa_oversiktstabell(filtrerad_df)

    # --- Spara uppdaterad data ---
    spara_data(df)

if __name__ == "__main__":
    main()

# --- Hjälpfunktion för att konvertera till rätt datatyper ---
def konvertera_datatyper(df):
    # Säkerställ att numeriska kolumner är rätt formaterade
    numeriska_kolumner = [
        "nuvarande_kurs", "vinst_forra_ar", "vinst_i_ar", "vinst_nasta_ar",
        "oms_forra_ar", "oms_tillv_i_ar_%", "oms_tillv_nasta_ar_%",
        "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
        "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4"
    ]
    for kolumn in numeriska_kolumner:
        if kolumn in df.columns:
            df[kolumn] = pd.to_numeric(df[kolumn], errors='coerce')

    # Konvertera datumfält om de finns
    for datokolumn in ["insatt_datum", "senast_andrad"]:
        if datokolumn in df.columns:
            df[datokolumn] = pd.to_datetime(df[datokolumn], errors='coerce')

    return df

# Säkerhetsåtgärd: körning på Streamlit Cloud
try:
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error("Ett oväntat fel inträffade. Kontrollera att alla fält är ifyllda korrekt.")
    st.exception(e)
