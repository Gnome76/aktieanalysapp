import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATAFIL = "data.json"

st.set_page_config(page_title="Aktieanalys", layout="centered")

# ---------- Hjälpfunktioner ----------

def ladda_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return pd.DataFrame(columns=[
        "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
        "oms_forra_aret", "oms_tillv_i_ar", "oms_tillv_nasta_ar",
        "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
        "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
        "insatt_datum", "senast_andrad"
    ])

def spara_data(df):
    with open(DATAFIL, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

def berakna_target_och_undervardering(df):
    try:
        df["targetkurs_pe"] = df["vinst_nasta_ar"].astype(float) * (
            (df["pe_1"].astype(float) + df["pe_2"].astype(float)) / 2)
        tillv_i_ar = df["oms_tillv_i_ar"].astype(float) / 100
        tillv_nasta_ar = df["oms_tillv_nasta_ar"].astype(float) / 100
        snitt_tillv = (tillv_i_ar + tillv_nasta_ar) / 2
        snitt_ps = (df["ps_1"].astype(float) + df["ps_2"].astype(float)) / 2
        df["targetkurs_ps"] = df["nuvarande_kurs"].astype(float) * (1 + snitt_tillv) * snitt_ps / df["ps_nu"]
        df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]
        df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]
        df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)
    except Exception as e:
        st.error(f"Fel vid beräkning: {e}")
    return df

# ---------- Gränssnitt ----------

def visa_oversikt(df):
    st.subheader("📊 Översikt över bolag")
    if df.empty:
        st.info("Inga bolag har lagts till ännu.")
        return
    st.dataframe(df[["bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering"]]
                 .sort_values("undervardering", ascending=False), use_container_width=True)

def visa_undervarderade(df):
    undervarderade = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)
    if undervarderade.empty:
        st.info("Inga undervärderade bolag hittades.")
        return

    if "index" not in st.session_state:
        st.session_state.index = 0

    bolag = undervarderade.iloc[st.session_state.index]

    st.markdown(f"### 📉 {bolag['bolagsnamn']}")
    st.metric("📌 Nuvarande kurs", f"{bolag['nuvarande_kurs']:.2f} kr")
    st.metric("🎯 Targetkurs P/E", f"{bolag['targetkurs_pe']:.2f} kr")
    st.metric("🎯 Targetkurs P/S", f"{bolag['targetkurs_ps']:.2f} kr")
    st.metric("🔥 Undervärdering", f"{bolag['undervardering']*100:.1f} %")

    st.progress(min(bolag["undervardering"], 1.0))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Föregående") and st.session_state.index > 0:
            st.session_state.index -= 1
    with col2:
        if st.button("➡️ Nästa") and st.session_state.index < len(undervarderade) - 1:
            st.session_state.index += 1

def bolagsform(df):
    st.subheader("➕ Lägg till eller uppdatera bolag")
    bolagsnamn = st.text_input("Bolagsnamn")
    nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, step=0.1)
    vinst_forra_aret = st.number_input("Vinst förra året")
    vinst_i_ar = st.number_input("Förväntad vinst i år")
    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år")
    oms_forra_aret = st.number_input("Omsättning förra året")
    oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)")
    oms_tillv_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)")
    pe_nu = st.number_input("Nuvarande P/E")
    pe_1 = st.number_input("P/E 1")
    pe_2 = st.number_input("P/E 2")
    pe_3 = st.number_input("P/E 3")
    pe_4 = st.number_input("P/E 4")
    ps_nu = st.number_input("Nuvarande P/S")
    ps_1 = st.number_input("P/S 1")
    ps_2 = st.number_input("P/S 2")
    ps_3 = st.number_input("P/S 3")
    ps_4 = st.number_input("P/S 4")

    if st.button("💾 Spara bolag"):
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
            df.loc[df["bolagsnamn"] == bolagsnamn, ny_rad.keys()] = ny_rad.values()
            st.success("Bolaget uppdaterades!")
        else:
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            st.success("Bolaget lades till!")

        spara_data(df)
        st.experimental_rerun()

    return df

def ta_bort_bolag(df):
    st.subheader("🗑️ Ta bort bolag")
    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df
    bolag = st.selectbox("Välj bolag att ta bort", df["bolagsnamn"])
    if st.button("Radera"):
        df = df[df["bolagsnamn"] != bolag].reset_index(drop=True)
        spara_data(df)
        st.success(f"{bolag} raderades.")
        st.experimental_rerun()
    return df

# ---------- Huvudfunktion ----------

def main():
    df = ladda_data()
    df = berakna_target_och_undervardering(df)

    st.title("📈 Aktieanalysverktyg")

    meny = st.sidebar.radio("Navigera", ["📥 Lägg till/Uppdatera", "📋 Översikt", "💡 Undervärderade", "🗑️ Ta bort"])

    if meny == "📥 Lägg till/Uppdatera":
        df = bolagsform(df)
    elif meny == "📋 Översikt":
        visa_oversikt(df)
    elif meny == "💡 Undervärderade":
        visa_undervarderade(df)
    elif meny == "🗑️ Ta bort":
        df = ta_bort_bolag(df)

    spara_data(df)

if __name__ == "__main__":
    main()
