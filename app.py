import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Filnamn för databasen
DB_FILE = "bolag_db.csv"

# Funktion för att ladda databasen
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn", "vinst_nastaar", "pe1", "pe2", "oms_tillv_1", "oms_tillv_2",
            "ps1", "ps2", "nuvarande_kurs", "insatt_datum", "senast_andrad"
        ])

# Funktion för att spara databasen
def save_data(df):
    df.to_csv(DB_FILE, index=False)

# Funktion för att räkna ut targetkurser
def berakna_targetkurser(row):
    try:
        target_pe = float(row["vinst_nastaar"]) * ((float(row["pe1"]) + float(row["pe2"])) / 2)
    except:
        target_pe = None
    try:
        tillv = (float(row["oms_tillv_1"]) + float(row["oms_tillv_2"])) / 2
        ps_snitt = (float(row["ps1"]) + float(row["ps2"])) / 2
        target_ps = float(row["nuvarande_kurs"]) * (1 + tillv / 100) * ps_snitt
    except:
        target_ps = None
    return target_pe, target_ps

# Funktion för att visa färg och emoji baserat på värdering
def visa_undervarderingsgrad(nuv_kurs, target):
    if target is None or pd.isna(target):
        return "Ej tillgänglig"

    undervardering = (target - nuv_kurs) / nuv_kurs * 100
    if undervardering >= 50:
        return f"🟢🟢🟢 {undervardering:.0f}% 🔥"
    elif undervardering >= 30:
        return f"🟢🟢 {undervardering:.0f}%"
    elif undervardering >= 10:
        return f"🟡 {undervardering:.0f}%"
    elif undervardering >= 0:
        return f"🟠 {undervardering:.0f}%"
    else:
        return f"🔴 {undervardering:.0f}%"

# Formulär för att lägga till eller redigera ett bolag
def bolagsform(session):
    st.header("Lägg till eller redigera bolag")
    df = session["data"]

    val = st.selectbox("Välj bolag att redigera eller skapa nytt", [""] + df["bolagsnamn"].tolist())
    nytt_bolag = val == ""

    if nytt_bolag:
        bolagsnamn = st.text_input("Bolagsnamn")
    else:
        bolagsnamn = val

    nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, value=float(df[df["bolagsnamn"] == bolagsnamn]["nuvarande_kurs"].values[0]) if not nytt_bolag else 0.0)

    med_avanserat = st.checkbox("Visa fler nyckeltal")
    if med_avanserat:
        vinst_nastaar = st.number_input("Vinst nästa år", min_value=0.0, value=float(df[df["bolagsnamn"] == bolagsnamn]["vinst_nastaar"].values[0]) if not nytt_bolag else 0.0)
        pe1 = st.number_input("P/E år 1", min_value=0.0, value=float(df[df["bolagsnamn"] == bolagsnamn]["pe1"].values[0]) if not nytt_bolag else 0.0)
        pe2 = st.number_input("P/E år 2", min_value=0.0, value=float(df[df["bolagsnamn"] == bolagsnamn]["pe2"].values[0]) if not nytt_bolag else 0.0)
        oms_tillv_1 = st.number_input("Omsättningstillväxt år 1 (%)", value=float(df[df["bolagsnamn"] == bolagsnamn]["oms_tillv_1"].values[0]) if not nytt_bolag else 0.0)
        oms_tillv_2 = st.number_input("Omsättningstillväxt år 2 (%)", value=float(df[df["bolagsnamn"] == bolagsnamn]["oms_tillv_2"].values[0]) if not nytt_bolag else 0.0)
        ps1 = st.number_input("P/S år 1", min_value=0.0, value=float(df[df["bolagsnamn"] == bolagsnamn]["ps1"].values[0]) if not nytt_bolag else 0.0)
        ps2 = st.number_input("P/S år 2", min_value=0.0, value=float(df[df["bolagsnamn"] == bolagsnamn]["ps2"].values[0]) if not nytt_bolag else 0.0)
    else:
        vinst_nastaar = pe1 = pe2 = oms_tillv_1 = oms_tillv_2 = ps1 = ps2 = 0.0

    if st.button("Spara"):
        data = {
            "bolagsnamn": bolagsnamn,
            "vinst_nastaar": vinst_nastaar,
            "pe1": pe1,
            "pe2": pe2,
            "oms_tillv_1": oms_tillv_1,
            "oms_tillv_2": oms_tillv_2,
            "ps1": ps1,
            "ps2": ps2,
            "nuvarande_kurs": nuvarande_kurs,
            "insatt_datum": datetime.now().strftime("%Y-%m-%d"),
            "senast_andrad": datetime.now().strftime("%Y-%m-%d")
        }

        df = df[df["bolagsnamn"] != bolagsnamn]
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

        save_data(df)
        st.session_state["data"] = df
        st.success("Bolaget har sparats.")

# Funktion för att visa tabell och filtrering
def visa_bolag(session):
    st.header("Bolagsöversikt")
    df = session["data"].copy()

    df["target_pe"], df["target_ps"] = zip(*df.apply(berakna_targetkurser, axis=1))
    df["undervardering_pe"] = df.apply(lambda row: visa_undervarderingsgrad(row["nuvarande_kurs"], row["target_pe"]), axis=1)
    df["undervardering_ps"] = df.apply(lambda row: visa_undervarderingsgrad(row["nuvarande_kurs"], row["target_ps"]), axis=1)

    visa_alla = st.checkbox("Visa endast undervärderade bolag (>30%)", value=True)

    if visa_alla:
        df = df[df.apply(lambda row: (
            (row["target_pe"] is not None and (row["target_pe"] - row["nuvarande_kurs"]) / row["nuvarande_kurs"] > 0.3) or
            (row["target_ps"] is not None and (row["target_ps"] - row["nuvarande_kurs"]) / row["nuvarande_kurs"] > 0.3)
        ), axis=1)]

    df.sort_values(by=["target_pe"], ascending=False, inplace=True)

    st.dataframe(df[[
        "bolagsnamn", "nuvarande_kurs", "target_pe", "undervardering_pe",
        "target_ps", "undervardering_ps"
    ]].reset_index(drop=True), use_container_width=True)

# Funktion för att ta bort bolag
def ta_bort_bolag(session):
    st.header("Ta bort bolag")
    df = session["data"]
    bolag = st.selectbox("Välj bolag att ta bort", df["bolagsnamn"].tolist())
    if st.button("Ta bort"):
        df = df[df["bolagsnamn"] != bolag]
        save_data(df)
        st.session_state["data"] = df
        st.success(f"{bolag} har tagits bort.")

# Huvudfunktion
def main():
    st.set_page_config(layout="centered", page_title="Aktieanalysapp")
    if "data" not in st.session_state:
        st.session_state["data"] = load_data()

    meny = st.sidebar.radio("Meny", ["Lägg till/Redigera", "Visa bolag", "Ta bort bolag"])

    if meny == "Lägg till/Redigera":
        bolagsform(st.session_state)
    elif meny == "Visa bolag":
        visa_bolag(st.session_state)
    elif meny == "Ta bort bolag":
        ta_bort_bolag(st.session_state)

if __name__ == "__main__":
    main()
