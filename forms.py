import streamlit as st
from datetime import datetime

def input_form():
    with st.form(key="form_lagg_till_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 (%)", format="%.2f")
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 (%)", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", format="%.2f")
        pe_1 = st.number_input("P/E år 1", format="%.2f")
        pe_2 = st.number_input("P/E år 2", format="%.2f")
        pe_3 = st.number_input("P/E år 3", format="%.2f")
        pe_4 = st.number_input("P/E år 4", format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", format="%.2f")
        ps_1 = st.number_input("P/S år 1", format="%.2f")
        ps_2 = st.number_input("P/S år 2", format="%.2f")
        ps_3 = st.number_input("P/S år 3", format="%.2f")
        ps_4 = st.number_input("P/S år 4", format="%.2f")

        submitted = st.form_submit_button("Lägg till bolag")
        if submitted:
            if not bolagsnamn:
                st.error("Bolagsnamn måste anges!")
                return None
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar_1_pct": omsattningstillvaxt_ar_1_pct,
                "omsattningstillvaxt_ar_2_pct": omsattningstillvaxt_ar_2_pct,
                "nuvarande_pe": nuvarande_pe,
                "pe_1": pe_1,
                "pe_2": pe_2,
                "pe_3": pe_3,
                "pe_4": pe_4,
                "nuvarande_ps": nuvarande_ps,
                "ps_1": ps_1,
                "ps_2": ps_2,
                "ps_3": ps_3,
                "ps_4": ps_4,
                "insatt_datum": datetime.now().isoformat(),
                "senast_andrad": datetime.now().isoformat(),
            }
    return None

def edit_form(bolag_data):
    with st.form(key="form_redigera_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn", value=bolag_data.get("bolagsnamn", ""), disabled=True)
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=bolag_data.get("nuvarande_kurs", 0.0))
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f", value=bolag_data.get("vinst_forra_aret", 0.0))
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f", value=bolag_data.get("vinst_i_ar", 0.0))
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f", value=bolag_data.get("vinst_nasta_ar", 0.0))
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f", value=bolag_data.get("omsattning_forra_aret", 0.0))
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 (%)", format="%.2f", value=bolag_data.get("omsattningstillvaxt_ar_1_pct", 0.0))
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 (%)", format="%.2f", value=bolag_data.get("omsattningstillvaxt_ar_2_pct", 0.0))
        nuvarande_pe = st.number_input("Nuvarande P/E", format="%.2f", value=bolag_data.get("nuvarande_pe", 0.0))
        pe_1 = st.number_input("P/E år 1", format="%.2f", value=bolag_data.get("pe_1", 0.0))
        pe_2 = st.number_input("P/E år 2", format="%.2f", value=bolag_data.get("pe_2", 0.0))
        pe_3 = st.number_input("P/E år 3", format="%.2f", value=bolag_data.get("pe_3", 0.0))
        pe_4 = st.number_input("P/E år 4", format="%.2f", value=bolag_data.get("pe_4", 0.0))
        nuvarande_ps = st.number_input("Nuvarande P/S", format="%.2f", value=bolag_data.get("nuvarande_ps", 0.0))
        ps_1 = st.number_input("P/S år 1", format="%.2f", value=bolag_data.get("ps_1", 0.0))
        ps_2 = st.number_input("P/S år 2", format="%.2f", value=bolag_data.get("ps_2", 0.0))
        ps_3 = st.number_input("P/S år 3", format="%.2f", value=bolag_data.get("ps_3", 0.0))
        ps_4 = st.number_input("P/S år 4", format="%.2f", value=bolag_data.get("ps_4", 0.0))

        submitted = st.form_submit_button("Uppdatera bolag")
        if submitted:
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar_1_pct": omsattningstillvaxt_ar_1_pct,
                "omsattningstillvaxt_ar_2_pct": omsattningstillvaxt_ar_2_pct,
                "nuvarande_pe": nuvarande_pe,
                "pe_1": pe_1,
                "pe_2": pe_2,
                "pe_3": pe_3,
                "pe_4": pe_4,
                "nuvarande_ps": nuvarande_ps,
                "ps_1": ps_1,
                "ps_2": ps_2,
                "ps_3": ps_3,
                "ps_4": ps_4,
                "insatt_datum": bolag_data.get("insatt_datum", ""),
                "senast_andrad": datetime.now().isoformat(),
            }
    return None
