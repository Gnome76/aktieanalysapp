import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

DATA_PATH = "/mnt/data/bolag.json"  # Streamlit Cloud persistent path

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        if df.empty:
            df = skapa_tomt_df()
    else:
        df = skapa_tomt_df()
    return df

def save_data(df):
    with open(DATA_PATH, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

def skapa_tomt_df():
    kolumner = [
        "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_i_ar", "vinst_nasta_ar",
        "omsattning_fjol", "omsattningstillvaxt_i_ar_pct", "omsattningstillvaxt_nasta_ar_pct",
        "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
        "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
        "insatt_datum", "senast_andrad", "targetkurs_pe", "targetkurs_ps", "undervardering"
    ]
    return pd.DataFrame(columns=kolumner)

def berakna_target_och_undervardering(df):
    if df.empty:
        return df

    # Konvertera numeriska kolumner till float, fel blir NaN
    num_cols = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "nuvarande_kurs",
        "ps_1", "ps_2",
        "omsattningstillvaxt_i_ar_pct", "omsattningstillvaxt_nasta_ar_pct"
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Beräkna targetkurs baserat på pe (vinst nästa år * medel av pe_1 och pe_2)
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Beräkna genomsnittlig omsättningstillväxt (år 1 och 2)
    df["omsattningstillvaxt_medel"] = (df["omsattningstillvaxt_i_ar_pct"] + df["omsattningstillvaxt_nasta_ar_pct"]) / 2 / 100.0

    # Medel av ps_1 och ps_2
    df["ps_medel"] = (df["ps_1"] + df["ps_2"]) / 2

    # Beräkna targetkurs baserat på ps
    df["targetkurs_ps"] = df["ps_medel"] * (1 + df["omsattningstillvaxt_medel"]) * df["nuvarande_kurs"]

    # Beräkna undervärdering - högsta rabatt mellan targetkurs_pe och targetkurs_ps jämfört med nuvarande kurs
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    # Rensa temporära kolumner
    df.drop(columns=["omsattningstillvaxt_medel", "ps_medel", "undervardering_pe", "undervardering_ps"], inplace=True)

    return df

def visa_bolag(df):
    st.header("Sparade bolag")
    if df.empty:
        st.info("Inga bolag sparade än.")
        return df

    df = berakna_target_och_undervardering(df)

    visa_alla = st.checkbox("Visa alla bolag (utan filter)", value=False)
    if visa_alla:
        df_visning = df.copy()
    else:
        # Filtrera fram bolag med minst 30% undervärdering
        df_visning = df[df["undervardering"] >= 0.3]

    if df_visning.empty:
        st.warning("Inga bolag uppfyller filtreringskriterierna.")
        return df

    # Sortera på undervärdering (störst först)
    df_visning = df_visning.sort_values(by="undervardering", ascending=False)

    # Visa som tabell
    st.dataframe(df_visning[[
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering"
    ]].style.format({
        "nuvarande_kurs": "{:.2f}",
        "targetkurs_pe": "{:.2f}",
        "targetkurs_ps": "{:.2f}",
        "undervardering": "{:.2%}"
    }))

    # Möjlighet att ta bort bolag
    st.subheader("Ta bort bolag")
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=[""] + df["bolagsnamn"].tolist())
    if bolag_att_ta_bort:
        if st.button(f"Ta bort {bolag_att_ta_bort}"):
            df = df[df["bolagsnamn"] != bolag_att_ta_bort].reset_index(drop=True)
            save_data(df)
            st.success(f"Bolaget {bolag_att_ta_bort} har tagits bort.")
            st.session_state["refresh"] = True
            st.stop()
    return df


def main():
    st.title("Aktieanalysapp med sparande och redigering")

    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    df = load_data()

    # Formulär för att lägga till / uppdatera bolag
    df = bolagsform(df)

    # Visa sparade bolag med filter och borttagning
    df = visa_bolag(df)

    # Om en refresh är begärd (efter save eller delete), ladda om sidan
    if st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
