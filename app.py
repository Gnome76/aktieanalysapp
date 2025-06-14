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
        pes = [x for x in pes if x is not None]
        return sum(pes)/len(pes) if pes else None

    def mean_ps(row):
        pss = [row.get(k, None) for k in ['ps1', 'ps2', 'ps3', 'ps4']]
        pss = [x for x in pss if x is not None]
        return sum(pss)/len(pss) if pss else None

    df = df.copy()
    df['target_pe'] = df.apply(lambda r: r['vinst_nasta_ar'] * mean_pe(r) if pd.notnull(r['vinst_nasta_ar']) and mean_pe(r) else None, axis=1)
    df['omsattning_nasta_ar'] = df.apply(lambda r: r['omsattning_forra_aret'] * (1 + r['omsattningstillvaxt_nasta_ar_pct']/100) if pd.notnull(r['omsattning_forra_aret']) and pd.notnull(r['omsattningstillvaxt_nasta_ar_pct']) else None, axis=1)
    df['target_ps'] = df.apply(lambda r: r['omsattning_nasta_ar'] * mean_ps(r) if pd.notnull(r['omsattning_nasta_ar']) and mean_ps(r) else None, axis=1)

    df['undervardering_pe_pct'] = ((df['target_pe'] - df['nuvarande_kurs']) / df['nuvarande_kurs']) * 100
    df['undervardering_ps_pct'] = ((df['target_ps'] - df['nuvarande_kurs']) / df['nuvarande_kurs']) * 100

    df['max_undervardering'] = df[['undervardering_pe_pct', 'undervardering_ps_pct']].max(axis=1)

    return df

def color_pct(val):
    if pd.isnull(val):
        return ""
    if val >= 30:
        return f"<span style='color:green;font-weight:bold'>{val:.2f}%</span>"
    elif val < 0:
        return f"<span style='color:red;font-weight:bold'>{val:.2f}%</span>"
    else:
        return f"{val:.2f}%"
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

    # Visa nuvarande kurs alltid
    nuvarande_kurs = st.number_input("Nuvarande kurs (kr)", value=float(bolag_data.get('nuvarande_kurs', 0)), min_value=0.0)

    visa_detaljer = st.checkbox("Visa detaljerade nyckeltal")

    # Visa övriga fält om checkbox är på
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
        # Default values if details not shown or new
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

        # Uppdatera eller lägg till
        if edit_mode:
            df.loc[df['bolagsnamn'] == bolagsnamn, df.columns != "insatt_datum"] = pd.Series(ny_rad)
            # Insatt datum ska uppdateras vid redigering också
            df.loc[df['bolagsnamn'] == bolagsnamn, 'insatt_datum'] = nu
        else:
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)

        save_data(df)
        st_session_state.data = df
        st.success(f"Bolaget '{bolagsnamn}' sparat/uppdaterat!")
def visa_bolag(st_session_state):
    st.header("Bolagslista & analys")

    if "data" not in st_session_state or st_session_state.data.empty:
        st.info("Inga bolag tillagda än.")
        return

    df = st_session_state.data.copy()

    # Beräkna targetkurser och undervärdering
    df = calculate_targets(df)

    # Checkbox för att filtrera undervärderade bolag (minst 30% undervärdering)
    filtrera_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)

    if filtrera_undervarderade:
        df = df[df['max_undervardering'] >= 30]

    if df.empty:
        st.info("Inga bolag matchar filtreringen.")
        return

    # Sortera på max undervärdering, störst först
    df = df.sort_values(by="max_undervardering", ascending=False).reset_index(drop=True)

    # Bläddra mellan bolag
    if "bolagsindex" not in st_session_state:
        st_session_state.bolagsindex = 0

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅ Föregående"):
            st_session_state.bolagsindex = max(st_session_state.bolagsindex - 1, 0)
    with col3:
        if st.button("Nästa ➡"):
            st_session_state.bolagsindex = min(st_session_state.bolagsindex + 1, len(df) - 1)

    idx = st_session_state.bolagsindex
    valda_bolag = df.iloc[idx]

    st.subheader(f"📄 Detaljer för: {valda_bolag['bolagsnamn']}")

    # Visa nyckeltal i tabellform, enklare formatering
    info = {
        "Nuvarande kurs": valda_bolag['nuvarande_kurs'],
        "Targetkurs P/E": valda_bolag['target_pe'],
        "Targetkurs P/S": valda_bolag['target_ps'],
        "Undervärdering P/E (%)": valda_bolag['undervardering_pe_pct'],
        "Undervärdering P/S (%)": valda_bolag['undervardering_ps_pct'],
        "Max undervärdering (%)": valda_bolag['max_undervardering'],
        "Insatt datum": valda_bolag.get('insatt_datum', ''),
    }

    df_visning = pd.DataFrame(info, index=[0]).T.rename(columns={0: "Värde"})

    # Färg på undervärderingar
    def highlight_undervardering(val):
        if isinstance(val, float):
            if val >= 30:
                color = "green"
            elif val < 0:
                color = "red"
            else:
                color = "black"
            return f"color: {color}; font-weight: bold"
        return ""

    st.dataframe(df_visning.style.applymap(highlight_undervardering, subset=["Värde"]))

    # Knapp för att ta bort bolaget
    if st.button("Ta bort detta bolag"):
        bolagsnamn = valda_bolag['bolagsnamn']
        df = df.drop(valda_bolag.name).reset_index(drop=True)
        save_data(df)
        st_session_state.data = df
        st_session_state.bolagsindex = max(0, st_session_state.bolagsindex - 1)
        st.success(f"Bolaget '{bolagsnamn}' borttaget.")
        st.experimental_rerun()
    def main():
    st.set_page_config(page_title="Aktieanalysapp", layout="centered")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    if "bolagsindex" not in st.session_state:
        st.session_state.bolagsindex = 0

    st.title("📈 Aktieanalysapp")

    menyval = st.sidebar.radio("Meny", ["Lägg till / Redigera bolag", "Visa bolag"])

    if menyval == "Lägg till / Redigera bolag":
        bolagsform(st.session_state)
    elif menyval == "Visa bolag":
        visa_bolag(st.session_state)

if __name__ == "__main__":
    main()    
