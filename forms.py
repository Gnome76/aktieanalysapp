import streamlit as st
from datetime import datetime

def input_form():
    """Formulär för att lägga till nytt bolag"""
    with st.form(key="input_form"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 %", format="%.2f")
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 %", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
        pe_1 = st.number_input("P/E år 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E år 2", min_value=0.0, format="%.2f")
        pe_3 = st.number_input("P/E år 3", min_value=0.0, format="%.2f")
        pe_4 = st.number_input("P/E år 4", min_value=0.0, format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S år 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S år 2", min_value=0.0, format="%.2f")
        ps_3 = st.number_input("P/S år 3", min_value=0.0, format="%.2f")
        ps_4 = st.number_input("P/S år 4", min_value=0.0, format="%.2f")

        submit = st.form_submit_button("Lägg till bolag")

    if submit and bolagsnamn:
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

def edit_form(bolag):
    """Formulär för att redigera befintligt bolag"""
    with st.form(key="edit_form"):
        nuvarande_kurs = st.number_input("Nuvarande kurs", value=bolag["nuvarande_kurs"], min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", value=bolag["vinst_forra_aret"], format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", value=bolag["vinst_i_ar"], format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", value=bolag["vinst_nasta_ar"], format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", value=bolag["omsattning_forra_aret"], format="%.2f")
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 %", value=bolag["omsattningstillvaxt_ar_1_pct"], format="%.2f")
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 %", value=bolag["omsattningstillvaxt_ar_2_pct"], format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", value=bolag["nuvarande_pe"], min_value=0.0, format="%.2f")
        pe_1 = st.number_input("P/E år 1", value=bolag["pe_1"], min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E år 2", value=bolag["pe_2"], min_value=0.0, format="%.2f")
        pe_3 = st.number_input("P/E år 3", value=bolag["pe_3"], min_value=0.0, format="%.2f")
        pe_4 = st.number_input("P/E år 4", value=bolag["pe_4"], min_value=0.0, format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", value=bolag["nuvarande_ps"], min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S år 1", value=bolag["ps_1"], min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S år 2", value=bolag["ps_2"], min_value=0.0, format="%.2f")
        ps_3 = st.number_input("P/S år 3", value=bolag["ps_3"], min_value=0.0, format="%.2f")
        ps_4 = st.number_input("P/S år 4", value=bolag["ps_4"], min_value=0.0, format="%.2f")

        submit = st.form_submit_button("Uppdatera bolag")

    if submit:
        bolag.update({
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
            "senast_andrad": datetime.now().isoformat(),
        })
        return bolag
    return None
