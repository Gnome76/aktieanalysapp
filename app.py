import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATAFIL = "data.json"

# ---------- Ladda eller initiera data ----------
def ladda_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn", "kurs", "vinst_forra", "vinst_i_ar", "vinst_nasta_ar",
            "oms_forra", "oms_tillv_i_ar", "oms_tillv_nasta_ar",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ])

def lagra_data(df):
    with open(DATAFIL, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# ---------- Beräkningar ----------
def berakna_target_och_undervardering(df):
    df["target_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    tillv_i_ar = df["oms_tillv_i_ar"] / 100
    tillv_nasta_ar = df["oms_tillv_nasta_ar"] / 100
    tillv_snitt = (tillv_i_ar + tillv_nasta_ar) / 2
    ps_snitt = (df["ps_1"] + df["ps_2"]) / 2
    df["target_ps"] = ps_snitt * df["kurs"] * (1 + tillv_snitt)

    df["undervardering_pe"] = ((df["target_pe"] - df["kurs"]) / df["target_pe"]) * 100
    df["undervardering_ps"] = ((df["target_ps"] - df["kurs"]) / df["target_ps"]) * 100

    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)
    df["kopvard"] = df["undervardering"] >= 30

    return df

# ---------- Formulär för att visa och lägga till/uppdatera bolag ----------
def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="bolagsform_unique"):
        namn = st.text_input("Bolagsnamn")
        kurs = st.number_input("Nuvarande kurs", 0.0, step=0.1)

        vinst_forra = st.number_input("Vinst förra året", step=0.1)
        vinst_i_ar = st.number_input("Förväntad vinst i år", step=0.1)
        vinst_nasta = st.number_input("Förväntad vinst nästa år", step=0.1)

        oms_forra = st.number_input("Omsättning förra året", step=0.1)
        tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", step=0.1)
        tillv_nasta = st.number_input("Omsättningstillväxt nästa år (%)", step=0.1)

        pe_nu = st.number_input("Nuvarande P/E", step=0.1)
        pe_1 = st.number_input("P/E 1", step=0.1)
        pe_2 = st.number_input("P/E 2", step=0.1)
        pe_3 = st.number_input("P/E 3", step=0.1)
        pe_4 = st.number_input("P/E 4", step=0.1)

        ps_nu = st.number_input("Nuvarande P/S", step=0.1)
        ps_1 = st.number_input("P/S 1", step=0.1)
        ps_2 = st.number_input("P/S 2", step=0.1)
        ps_3 = st.number_input("P/S 3", step=0.1)
        ps_4 = st.number_input("P/S 4", step=0.1)

        submitted = st.form_submit_button("Spara bolag")

    if submitted and namn:
        nytt_bolag = {
            "bolagsnamn": namn.strip(),
            "kurs": kurs,
            "vinst_forra": vinst_forra,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta,
            "oms_forra": oms_forra,
            "oms_tillv_i_ar": tillv_i_ar,
            "oms_tillv_nasta_ar": tillv_nasta,
            "pe_nu": pe_nu, "pe_1": pe_1, "pe_2": pe_2, "pe_3": pe_3, "pe_4": pe_4,
            "ps_nu": ps_nu, "ps_1": ps_1, "ps_2": ps_2, "ps_3": ps_3, "ps_4": ps_4,
            "insatt_datum": datetime.today().strftime("%Y-%m-%d"),
            "senast_andrad": datetime.today().strftime("%Y-%m-%d")
        }

        df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
        lagra_data(df)
        st.success("Bolaget har sparats.")
        st.session_state["refresh"] = True
        st.stop()

    return df

# ---------- Funktion för att lägga till eller uppdatera bolag ----------
def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    namn = bolag_ny["bolagsnamn"].strip().lower()
    if "bolagsnamn" not in df.columns:
        df = pd.DataFrame(columns=bolag_ny.keys())

    if namn in df["bolagsnamn"].str.lower().values:
        idx = df.index[df["bolagsnamn"].str.lower() == namn][0]
        for key in bolag_ny:
            df.at[idx, key] = bolag_ny[key]
    else:
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)
    return df


# ---------- Funktioner för beräkningar ----------
def beräkna_targetkurser(df):
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    tillv_genomsnitt = (df["oms_tillv_i_ar"] + df["oms_tillv_nasta_ar"]) / 2 / 100
    df["oms_snitt"] = df["oms_forra"] * (1 + tillv_genomsnitt)
    df["targetkurs_ps"] = (df[["ps_1", "ps_2"]].mean(axis=1)) * df["oms_snitt"] / df["kurs"]
    return df


def beräkna_undervärdering(df):
    df["undervärdering_pe_%"] = ((df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"] * 100).round(1)
    df["undervärdering_ps_%"] = ((df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"] * 100).round(1)
    df["köpvärd"] = (df["undervärdering_pe_%"] > 30) | (df["undervärdering_ps_%"] > 30)
    return df

# ---------- Funktion för att visa bolag med filtrering och navigation ----------
def visa_bolag(df):
    st.subheader("📊 Översikt av bolag")
    visa_endast_kopvard = st.checkbox("Visa endast köpvärda bolag (≥30 % rabatt)", value=False)

    if visa_endast_kopvard:
        filtrerat_df = df[df["köpvärd"] == True].copy()
    else:
        filtrerat_df = df.copy()

    filtrerat_df["max_undervärdering"] = filtrerat_df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)
    filtrerat_df.sort_values(by="max_undervärdering", ascending=False, inplace=True)
    filtrerat_df.reset_index(drop=True, inplace=True)

    if len(filtrerat_df) == 0:
        st.info("Inga bolag att visa.")
        return df

    if "bolags_index" not in st.session_state:
        st.session_state.bolags_index = 0

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Föregående", disabled=st.session_state.bolags_index <= 0):
            st.session_state.bolags_index -= 1
    with col3:
        if st.button("Nästa ➡️", disabled=st.session_state.bolags_index >= len(filtrerat_df) - 1):
            st.session_state.bolags_index += 1

    bolag = filtrerat_df.iloc[st.session_state.bolags_index]
    st.markdown(f"### {bolag['bolagsnamn']}")
    st.write(f"📌 Nuvarande kurs: {bolag['kurs']:.2f} kr")
    st.write(f"🎯 Targetkurs (P/E): {bolag['targetkurs_pe']:.2f} kr")
    st.write(f"🎯 Targetkurs (P/S): {bolag['targetkurs_ps']:.2f} kr")
    st.write(f"📉 Undervärdering P/E: {bolag['undervärdering_pe_%']} %")
    st.write(f"📉 Undervärdering P/S: {bolag['undervärdering_ps_%']} %")
    st.write(f"✅ Köpvärd: {'Ja' if bolag['köpvärd'] else 'Nej'}")

    if st.button("❌ Ta bort bolaget"):
        namn = bolag['bolagsnamn']
        df = df[df['bolagsnamn'] != namn]
        spara_data(df)
        st.success(f"{namn} har tagits bort.")
        st.session_state.bolags_index = 0
        st.rerun()

    return df

# ---------- Huvudfunktion för att köra hela appen ----------
def main():
    st.set_page_config(page_title="Aktieanalys", layout="centered")
    st.title("📈 Aktieanalysapp")

    df = ladda_data()
    df = beräkna_targetkurser(df)

    meny = st.sidebar.radio("Navigera", ["➕ Lägg till / Redigera bolag", "📊 Visa bolag"])

    if meny == "➕ Lägg till / Redigera bolag":
        df = visa_form(df)
    elif meny == "📊 Visa bolag":
        df = visa_bolag(df)

    # Spara automatiskt efter varje körning
    spara_data(df)

# Kör programmet
if __name__ == "__main__":
    main()
