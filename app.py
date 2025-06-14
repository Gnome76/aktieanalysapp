import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_PATH = "aktier.json"

def load_data():
    if os.path.exists(DATA_PATH):
        try:
            return pd.read_json(DATA_PATH)
        except Exception:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_data(df):
    df.to_json(DATA_PATH, orient="records", force_ascii=False)

def calculate_targets(df):
    def mean_pe(row):
        pes = [row.get(k, None) for k in ['pe1', 'pe2', 'pe3', 'pe4']]
        pes = [x for x in pes if pd.notnull(x) and x > 0]
        return sum(pes)/len(pes) if pes else None

    def mean_ps(row):
        pss = [row.get(k, None) for k in ['ps1', 'ps2', 'ps3', 'ps4']]
        pss = [x for x in pss if pd.notnull(x) and x > 0]
        return sum(pss)/len(pss) if pss else None

    df = df.copy()
    df['target_pe'] = df.apply(lambda r: r['vinst_nasta_ar'] * mean_pe(r) if pd.notnull(r['vinst_nasta_ar']) and mean_pe(r) else None, axis=1)
    df['omsattning_nasta_ar'] = df.apply(lambda r: r['omsattning_forra_aret'] * (1 + r['omsattningstillvaxt_nasta_ar_pct']/100) if pd.notnull(r['omsattning_forra_aret']) and pd.notnull(r['omsattningstillvaxt_nasta_ar_pct']) else None, axis=1)
    df['target_ps'] = df.apply(lambda r: r['omsattning_nasta_ar'] * mean_ps(r) if pd.notnull(r['omsattning_nasta_ar']) and mean_ps(r) else None, axis=1)

    df['undervardering_pe_pct'] = ((df['target_pe'] - df['nuvarande_kurs']) / df['nuvarande_kurs']) * 100
    df['undervardering_ps_pct'] = ((df['target_ps'] - df['nuvarande_kurs']) / df['nuvarande_kurs']) * 100

    df['max_undervardering'] = df[['undervardering_pe_pct', 'undervardering_ps_pct']].max(axis=1)

    return df
def bolagsform(st_session_state):
    st.header("Lägg till / Redigera bolag")

    if "data" not in st_session_state:
        st_session_state.data = load_data()

    df = st_session_state.data

    bolagsnamn = st.text_input("Bolagsnamn").strip()

    # Kontrollera om bolaget finns för redigering
    edit_mode = False
    bolag_data = {}
    if bolagsnamn and bolagsnamn in df['bolagsnamn'].values:
        edit_mode = True
        bolag_data = df[df['bolagsnamn'] == bolagsnamn].iloc[0].to_dict()

    # Visa nuvarande kurs alltid
    nuvarande_kurs = st.number_input("Nuvarande kurs (kr)", value=float(bolag_data.get('nuvarande_kurs', 0.0)), min_value=0.0)

    visa_detaljer = st.checkbox("Visa detaljerade nyckeltal")

    if visa_detaljer:
        vinst_forra_aret = st.number_input("Vinst föregående år", value=float(bolag_data.get('vinst_forra_aret', 0.0)))
        vinst_i_ar = st.number_input("Vinst i år", value=float(bolag_data.get('vinst_i_ar', 0.0)))
        vinst_nasta_ar = st.number_input("Vinst nästa år", value=float(bolag_data.get('vinst_nasta_ar', 0.0)))

        omsattning_forra_aret = st.number_input("Omsättning föregående år", value=float(bolag_data.get('omsattning_forra_aret', 0.0)))
        omsattningstillvaxt_i_ar_pct = st.number_input("Omsättningstillväxt i år (%)", value=float(bolag_data.get('omsattningstillvaxt_i_ar_pct', 0.0)))
        omsattningstillvaxt_nasta_ar_pct = st.number_input("Omsättningstillväxt nästa år (%)", value=float(bolag_data.get('omsattningstillvaxt_nasta_ar_pct', 0.0)))

        pe1 = st.number_input("P/E år 1", value=float(bolag_data.get('pe1', 0.0)))
        pe2 = st.number_input("P/E år 2", value=float(bolag_data.get('pe2', 0.0)))
        pe3 = st.number_input("P/E år 3", value=float(bolag_data.get('pe3', 0.0)))
        pe4 = st.number_input("P/E år 4", value=float(bolag_data.get('pe4', 0.0)))

        ps1 = st.number_input("P/S år 1", value=float(bolag_data.get('ps1', 0.0)))
        ps2 = st.number_input("P/S år 2", value=float(bolag_data.get('ps2', 0.0)))
        ps3 = st.number_input("P/S år 3", value=float(bolag_data.get('ps3', 0.0)))
        ps4 = st.number_input("P/S år 4", value=float(bolag_data.get('ps4', 0.0)))
    else:
        # Default values om detaljer ej visas eller nytt bolag
        vinst_forra_aret = bolag_data.get('vinst_forra_aret', 0.0)
        vinst_i_ar = bolag_data.get('vinst_i_ar', 0.0)
        vinst_nasta_ar = bolag_data.get('vinst_nasta_ar', 0.0)
        omsattning_forra_aret = bolag_data.get('omsattning_forra_aret', 0.0)
        omsattningstillvaxt_i_ar_pct = bolag_data.get('omsattningstillvaxt_i_ar_pct', 0.0)
        omsattningstillvaxt_nasta_ar_pct = bolag_data.get('omsattningstillvaxt_nasta_ar_pct', 0.0)
        pe1 = bolag_data.get('pe1', 0.0)
        pe2 = bolag_data.get('pe2', 0.0)
        pe3 = bolag_data.get('pe3', 0.0)
        pe4 = bolag_data.get('pe4', 0.0)
        ps1 = bolag_data.get('ps1', 0.0)
        ps2 = bolag_data.get('ps2', 0.0)
        ps3 = bolag_data.get('ps3', 0.0)
        ps4 = bolag_data.get('ps4', 0.0)

    if st.button("Spara / Uppdatera"):
        if bolagsnamn == "":
            st.error("Ange ett bolagsnamn!")
            return

        nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ny_rad = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_forra_aret": omsattning_forra_aret,
            "omsattningstillvaxt_i_ar_pct": omsattningstillvaxt_i_ar_pct,
            "omsattningstillvaxt_nasta_ar_pct": omsattningstillvaxt_nasta_ar_pct,
            "pe1": pe1,
            "pe2": pe2,
            "pe3": pe3,
            "pe4": pe4,
            "ps1": ps1,
            "ps2": ps2,
            "ps3": ps3,
            "ps4": ps4,
            "insatt_datum": nu,
        }

        if edit_mode:
            # Uppdatera befintlig rad, inklusive insatt_datum
            idx = df.index[df['bolagsnamn'] == bolagsnamn][0]
            for key, value in ny_rad.items():
                df.at[idx, key] = value
        else:
            # Lägg till nytt bolag
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)

        save_data(df)
        st_session_state.data = df
        st.success(f"Bolaget '{bolagsnamn}' sparat/uppdaterat!")    
def visa_och_ta_bort_bolag(st_session_state):
    st.header("Översikt över sparade bolag")

    if "data" not in st_session_state:
        st_session_state.data = load_data()

    df = st_session_state.data

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return

    # Visa tabell
    st.dataframe(df)

    # Ta bort bolag
    ta_bort_bolag = st.selectbox("Välj bolag att ta bort", options=[""] + df["bolagsnamn"].tolist())
    if ta_bort_bolag and st.button("Ta bort valt bolag"):
        df = df[df["bolagsnamn"] != ta_bort_bolag].reset_index(drop=True)
        save_data(df)
        st_session_state.data = df
        st.success(f"Bolaget '{ta_bort_bolag}' har tagits bort.")
def main():
    st.set_page_config(page_title="Aktieanalysapp", layout="centered")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    if "bolagsindex" not in st.session_state:
        st.session_state.bolagsindex = 0

    st.title("📈 Aktieanalysapp")

    menyval = st.sidebar.radio("Meny", ["Lägg till / Redigera bolag", "Visa bolag", "Översikt och ta bort"])

    if menyval == "Lägg till / Redigera bolag":
        bolagsform(st.session_state)
    elif menyval == "Visa bolag":
        visa_bolag(st.session_state)
    elif menyval == "Översikt och ta bort":
        visa_och_ta_bort_bolag(st.session_state)

if __name__ == "__main__":
    main()       
