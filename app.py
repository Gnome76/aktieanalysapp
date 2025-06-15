
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

DATAFIL = "data.json"

# ---------------- Hjälpfunktioner ----------------

def load_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame(columns=[
        "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
        "oms_forra_aret", "oms_tillv_i_ar", "oms_tillv_nasta_ar", "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
        "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4", "insatt_datum", "senast_andrad"
    ])

def save_data(df):
    with open(DATAFIL, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

def berakna_target_undervardering(df):
    df = df.copy()
    df["targetkurs_pe"] = df["vinst_nasta_ar"].astype(float) * ((df["pe_1"].astype(float) + df["pe_2"].astype(float)) / 2)
    tillv_oms = (df["oms_tillv_i_ar"].astype(float) + df["oms_tillv_nasta_ar"].astype(float)) / 2 / 100
    ps_medel = (df["ps_1"].astype(float) + df["ps_2"].astype(float)) / 2
    df["targetkurs_ps"] = df["nuvarande_kurs"].astype(float) * (1 + tillv_oms) * ps_medel / df["ps_nu"].astype(float)
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)
    return df

# ---------------- Formulär för att lägga till/uppdatera ----------------

def bolagsform(df):
    st.subheader("Lägg till eller uppdatera bolag")
    bolagsnamn = st.text_input("Bolagsnamn")
    nuvarande_kurs = st.number_input("Nuvarande kurs", 0.0)
    vinst_forra_aret = st.number_input("Vinst förra året", 0.0)
    vinst_i_ar = st.number_input("Förväntad vinst i år", 0.0)
    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", 0.0)
    oms_forra_aret = st.number_input("Omsättning förra året", 0.0)
    oms_tillv_i_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", 0.0)
    oms_tillv_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", 0.0)
    pe_nu = st.number_input("Nuvarande P/E", 0.0)
    pe_1 = st.number_input("P/E 1", 0.0)
    pe_2 = st.number_input("P/E 2", 0.0)
    pe_3 = st.number_input("P/E 3", 0.0)
    pe_4 = st.number_input("P/E 4", 0.0)
    ps_nu = st.number_input("Nuvarande P/S", 0.0)
    ps_1 = st.number_input("P/S 1", 0.0)
    ps_2 = st.number_input("P/S 2", 0.0)
    ps_3 = st.number_input("P/S 3", 0.0)
    ps_4 = st.number_input("P/S 4", 0.0)

    if st.button("Spara bolag"):
        ny_rad = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "oms_forra_aret": oms_forra_aret,
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
            "insatt_datum": datetime.now().strftime("%Y-%m-%d"),
            "senast_andrad": datetime.now().strftime("%Y-%m-%d"),
        }

        if bolagsnamn in df["bolagsnamn"].values:
            df.loc[df["bolagsnamn"] == bolagsnamn] = ny_rad
            st.success(f"{bolagsnamn} uppdaterades!")
        else:
            df.loc[len(df)] = ny_rad
            st.success(f"{bolagsnamn} lades till!")

        save_data(df)
        st.session_state["refresh"] = True
        st.stop()
    return df

# ---------------- Undervärderade bolag ----------------

def visa_undervarderade(df):
    st.subheader("Undervärderade bolag")
    undervarderade = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)
    if len(undervarderade) == 0:
        st.info("Inga undervärderade bolag med minst 30 % rabatt.")
        return

    if "index" not in st.session_state:
        st.session_state.index = 0

    bolag = undervarderade.iloc[st.session_state.index]
    st.markdown(f"### {bolag['bolagsnamn']}")
    st.metric("Nuvarande kurs", f"{bolag['nuvarande_kurs']:.2f} kr")
    st.metric("Targetkurs P/E", f"{bolag['targetkurs_pe']:.2f} kr")
    st.metric("Targetkurs P/S", f"{bolag['targetkurs_ps']:.2f} kr")
    undervardering_procent = bolag["undervardering"] * 100
    st.progress(min(1.0, bolag["undervardering"]))
    st.markdown(f"📉 **Undervärdering:** {undervardering_procent:.1f} %")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Föregående", disabled=st.session_state.index == 0):
            st.session_state.index -= 1
            st.experimental_rerun()
    with col2:
        if st.button("Nästa", disabled=st.session_state.index >= len(undervarderade) - 1):
            st.session_state.index += 1
            st.experimental_rerun()

# ---------------- Huvudfunktion ----------------

def main():
    st.set_page_config(page_title="Aktieanalys", layout="wide")
    st.title("📊 Aktieanalysapp")

    df = load_data()
    if df.empty:
        df = load_data()

    if not df.empty:
        df = berakna_target_undervardering(df)

    df = bolagsform(df)

    if not df.empty:
        visa_undervarderade(df)

if __name__ == "__main__":
    main()
