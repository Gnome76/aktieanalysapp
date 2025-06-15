import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "bolag_data.json"

def las_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()

def spara_data(df):
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

def berakna_target_och_undervardering(df):
    if df.empty:
        return df
    # Säkerställ att kolumner finns och konvertera till float där möjligt
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "omsattningstillvaxt_ar_1", "omsattningstillvaxt_ar_2", "nuvarande_kurs"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # Targetkurs baserat på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    # Targetkurs baserat på P/S och omsättningstillväxt
    medel_oms_tillvaxt = (df["omsattningstillvaxt_ar_1"] + df["omsattningstillvaxt_ar_2"]) / 2 / 100
    medel_ps = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = medel_ps * (1 + medel_oms_tillvaxt) * df["nuvarande_kurs"]
    
    # Undervärdering = max rabatt av P/E eller P/S mål jämfört med nuvarande kurs
    df["undervardering_pe"] = 1 - df["nuvarande_kurs"] / df["targetkurs_pe"].replace(0, pd.NA)
    df["undervardering_ps"] = 1 - df["nuvarande_kurs"] / df["targetkurs_ps"].replace(0, pd.NA)
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1).fillna(0)
    df["undervardering"] = df["undervardering"].clip(lower=0)  # Negativa värden blir 0
    
    return df

def bolagsform(df):
    st.header("Lägg till / Uppdatera bolag")
    with st.form("bolagsformulär", clear_on_submit=False):
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        omsattningstillvaxt_ar_1 = st.number_input("Omsättningstillväxt år 1 (%)", format="%.2f")
        omsattningstillvaxt_ar_2 = st.number_input("Omsättningstillväxt år 2 (%)", format="%.2f")
        
        submitted = st.form_submit_button("Spara")
        if submitted:
            if bolagsnamn == "":
                st.warning("Fyll i ett bolagsnamn.")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ny_rad = {
                    "bolagsnamn": bolagsnamn,
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "pe_1": pe_1,
                    "pe_2": pe_2,
                    "ps_1": ps_1,
                    "ps_2": ps_2,
                    "omsattningstillvaxt_ar_1": omsattningstillvaxt_ar_1,
                    "omsattningstillvaxt_ar_2": omsattningstillvaxt_ar_2,
                    "insatt_datum": now,
                    "senast_andrad": now
                }
                # Kolla om bolaget finns, uppdatera i så fall
                if "bolagsnamn" in df.columns and bolagsnamn in df["bolagsnamn"].values:
                    idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
                    for key, val in ny_rad.items():
                        df.at[idx, key] = val
                else:
                    df = df.append(ny_rad, ignore_index=True)
                spara_data(df)
                st.success(f"{bolagsnamn} sparat!")
                # Uppdatera session state flagga för refresh (för bläddring etc)
                st.session_state["refresh"] = True
    return df

def ta_bort_bolag(df):
    st.header("Ta bort bolag")
    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df
    val = st.selectbox("Välj bolag att ta bort", df["bolagsnamn"].tolist())
    if st.button("Ta bort"):
        df = df[df["bolagsnamn"] != val].reset_index(drop=True)
        spara_data(df)
        st.success(f"{val} borttaget.")
        st.session_state["refresh"] = True
    return df

def visa_undervarderade(df):
    st.header("Undervärderade bolag")
    if df.empty:
        st.info("Inga bolag finns ännu.")
        return
    # Filtrera undervärderade
    df_undervard = df[df["undervardering"] >= 0.3].copy()
    if df_undervard.empty:
        st.info("Inga bolag är undervärderade med minst 30% just nu.")
        return
    df_undervard = df_undervard.sort_values(by="undervardering", ascending=False).reset_index(drop=True)
    
    # Bläddringsindex i session_state
    if "index" not in st.session_state or st.session_state.get("refresh", False):
        st.session_state["index"] = 0
        st.session_state["refresh"] = False
    
    i = st.session_state["index"]
    bolag = df_undervard.iloc[i]
    
    st.subheader(f"{bolag['bolagsnamn']} ({i+1} av {len(df_undervard)})")
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} SEK")
    st.write(f"Targetkurs P/E: {bolag['targetkurs_pe']:.2f} SEK")
    st.write(f"Targetkurs P/S: {bolag['targetkurs_ps']:.2f} SEK")
    st.write(f"Undervärdering: {bolag['undervardering']*100:.1f} %")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Föregående"):
            if st.session_state["index"] > 0:
                st.session_state["index"] -= 1
    with col2:
        if st.button("Nästa"):
            if st.session_state["index"] < len(df_undervard) - 1:
                st.session_state["index"] += 1

def main():
    st.title("Aktieanalysapp - Undervärderade Bolag")
    df = las_data()
    df = berakna_target_och_undervardering(df)
    
    df = bolagsform(df)
    df = ta_bort_bolag(df)
    
    visa_undervarderade(df)
    
    # Uppdatera vy utan st.experimental_rerun
    if st.session_state.get("refresh", False):
        st.experimental_rerun()  # Om det inte fungerar i din miljö, byt till st.stop() + flagga-logik

if __name__ == "__main__":
    main()
