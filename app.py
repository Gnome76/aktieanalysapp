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
    df.to_json(DATA_PATH, orient="records")

def calculate_targets(df):
    def mean_pe(row):
        pes = [row.get(k, None) for k in ['pe1', 'pe2', 'pe3', 'pe4']]
        pes = [x for x in pes if pd.notnull(x)]
        return sum(pes)/len(pes) if pes else None

    def mean_ps(row):
        pss = [row.get(k, None) for k in ['ps1', 'ps2', 'ps3', 'ps4']]
        pss = [x for x in pss if pd.notnull(x)]
        return sum(pss)/len(pss) if pss else None

    df = df.copy()
    df['target_pe'] = df.apply(lambda r: r['vinst_nasta_ar'] * mean_pe(r) if pd.notnull(r['vinst_nasta_ar']) and mean_pe(r) else None, axis=1)
    df['omsattning_nasta_ar'] = df.apply(lambda r: r['omsattning_forra_aret'] * (1 + r['omsattningstillvaxt_nasta_ar_pct']/100) if pd.notnull(r['omsattning_forra_aret']) and pd.notnull(r['omsattningstillvaxt_nasta_ar_pct']) else None, axis=1)
    df['target_ps'] = df.apply(lambda r: r['omsattning_nasta_ar'] * mean_ps(r) if pd.notnull(r['omsattning_nasta_ar']) and mean_ps(r) else None, axis=1)

    df['undervardering_pe_pct'] = ((df['target_pe'] - df['nuvarande_kurs']) / df['nuvarande_kurs']) * 100
    df['undervardering_ps_pct'] = ((df['target_ps'] - df['nuvarande_kurs']) / df['nuvarande_kurs']) * 100

    df['max_undervardering'] = df[['undervardering_pe_pct', 'undervardering_ps_pct']].max(axis=1)

    return df

def format_undervardering(val):
    if pd.isnull(val):
        return "N/A"
    if val >= 30:
        emoji = "🟢⬆️"
        color = "green"
    elif val >= 10:
        emoji = "🟡↗️"
        color = "orange"
    elif val >= 0:
        emoji = "⚪➡️"
        color = "gray"
    else:
        emoji = "🔴⬇️"
        color = "red"
    val_str = f"{val:.1f}%"
    return f"<span style='color:{color}; font-weight:bold'>{val_str} {emoji}</span>"

def undervardering_progress(val):
    if pd.isnull(val):
        return 0
    # Normalize progress: cap at 50% undervärdering for progress bar max
    progress = min(max(val, 0), 50) / 50
    return progress

def bolagsform(st_session_state):
    st.header("Lägg till / Redigera bolag")

    if "data" not in st_session_state:
        st_session_state.data = load_data()

    df = st_session_state.data

    bolagsnamn = st.text_input("Bolagsnamn").strip()

    # Kontrollera om bolaget finns för redigering
    edit_mode = False
    if bolagsnamn and bolagsnamn in df['bolagsnamn'].values:
        edit_mode = True
        bolag_data = df[df['bolagsnamn'] == bolagsnamn].iloc[0]
    else:
        bolag_data = {}

    nuvarande_kurs = st.number_input("Nuvarande kurs (kr)", value=float(bolag_data.get('nuvarande_kurs', 0)), min_value=0.0)

    visa_detaljer = st.checkbox("Visa detaljerade nyckeltal")

    if visa_detaljer:
        vinst_forra_aret = st.number_input("Vinst föregående år", value=float(bolag_data.get('vinst_forra_aret', 0)))
        vinst_i_ar = st.number_input("Vinst i år", value=float(bolag_data.get('vinst_i_ar', 0)))
        vinst_nasta_ar = st.number_input("Vinst nästa år", value=float(bolag_data.get('vinst_nasta_ar', 0)))

        omsattning_forra_aret = st.number_input("Omsättning föregående år", value=float(bolag_data.get('omsattning_forra_aret', 0)))
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
        vinst_forra_aret = bolag_data.get('vinst_forra_aret', 0)
        vinst_i_ar = bolag_data.get('vinst_i_ar', 0)
        vinst_nasta_ar = bolag_data.get('vinst_nasta_ar', 0)
        omsattning_forra_aret = bolag_data.get('omsattning_forra_aret', 0)
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
            df.loc[df['bolagsnamn'] == bolagsnamn, df.columns != "insatt_datum"] = pd.Series(ny_rad)
            df.loc[df['bolagsnamn'] == bolagsnamn, 'insatt_datum'] = nu
        else:
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)

        st_session_state.data = df
        save_data(df)
        st.success(f"Bolag '{bolagsnamn}' sparat!")
        st.experimental_rerun()

def visa_aktier(st_session_state):
    st.header("Aktieöversikt")

    if "data" not in st_session_state:
        st_session_state.data = load_data()

    df = st_session_state.data
    if df.empty:
        st.info("Inga bolag sparade än.")
        return

    df = calculate_targets(df)

    visa_alla = st.checkbox("Visa alla bolag (inklusive övervärderade)", value=True)

    if not visa_alla:
        df = df[df['max_undervardering'] >= 30]

    if df.empty:
        st.info("Inga bolag matchar filtreringen.")
        return

    df_sorted = df.sort_values(by='max_undervardering', ascending=False)

    for _, row in df_sorted.iterrows():
        st.subheader(row['bolagsnamn'])
        st.write(f"Nuvarande kurs: {row['nuvarande_kurs']:.2f} kr")
        pe_val = row['undervardering_pe_pct']
        ps_val = row['undervardering_ps_pct']
        st.markdown(f"P/E undervärdering: {format_undervardering(pe_val)}", unsafe_allow_html=True)
        st.progress(undervardering_progress(pe_val))
        st.markdown(f"P/S undervärdering: {format_undervardering(ps_val)}", unsafe_allow_html=True)
        st.progress(undervardering_progress(ps_val))
        st.markdown("---")

def main():
    st.set_page_config(page_title="Aktieanalysapp", page_icon="📈", layout="centered")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    menu = ["Lägg till / Redigera bolag", "Visa aktier"]
    choice = st.sidebar.selectbox("Meny", menu)

    if choice == "Lägg till / Redigera bolag":
        bolagsform(st.session_state)
    elif choice == "Visa aktier":
        visa_aktier(st.session_state)

if __name__ == "__main__":
    main()
