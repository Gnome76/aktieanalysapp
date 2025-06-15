import streamlit as st
from datetime import datetime

# Samma lista av nycklar som i data_handler, fast för inputformulär

def input_form():
    with st.form(key="input_form_unique"):
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_i_ar = st.number_input("Omsättningstillväxt i år %", format="%.2f")
        omsattningstillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år %", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", format="%.2f")
        pe1 = st.number_input("P/E 1", format="%.2f")
        pe2 = st.number_input("P/E 2", format="%.2f")
        pe3 = st.number_input("P/E 3", format="%.2f")
        pe4 = st.number_input("P/E 4", format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", format="%.2f")
        ps1 = st.number_input("P/S 1", format="%.2f")
        ps2 = st.number_input("P/S 2", format="%.2f")
        ps3 = st.number_input("P/S 3", format="%.2f")
        ps4 = st.number_input("P/S 4", format="%.2f")

        submitted = st.form_submit_button("Lägg till bolag")

        if submitted and bolagsnamn != "":
            datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_i_ar": omsattningstillvaxt_i_ar,
                "omsattningstillvaxt_nastaar": omsattningstillvaxt_nastaar,
                "nuvarande_pe": nuvarande_pe,
                "pe1": pe1,
                "pe2": pe2,
                "pe3": pe3,
                "pe4": pe4,
                "nuvarande_ps": nuvarande_ps,
                "ps1": ps1,
                "ps2": ps2,
                "ps3": ps3,
                "ps4": ps4,
                "insatt_datum": datum,
                "senast_andrad": datum,
            }
        return None

def edit_form(bolag):
    with st.form(key=f"edit_form_{bolag['bolagsnamn']}"):
        st.text(f"Redigera bolag: {bolag['bolagsnamn']}")

        # Visa bara nuvarande kurs direkt, resten bakom en expanderbar knapp
        nuvarande_kurs = st.number_input("Nuvarande kurs", value=float(bolag.get("nuvarande_kurs", 0)), format="%.2f")

        with st.expander("Visa och redigera övriga fält"):
            vinst_forra_aret = st.number_input("Vinst förra året", value=float(bolag.get("vinst_forra_aret", 0)), format="%.2f")
            vinst_i_ar = st.number_input("Vinst i år", value=float(bolag.get("vinst_i_ar", 0)), format="%.2f")
            vinst_nastaar = st.number_input("Vinst nästa år", value=float(bolag.get("vinst_nastaar", 0)), format="%.2f")
            omsattning_forra_aret = st.number_input("Omsättning förra året", value=float(bolag.get("omsattning_forra_aret", 0)), format="%.2f")
            omsattningstillvaxt_i_ar = st.number_input("Omsättningstillväxt i år %", value=float(bolag.get("omsattningstillvaxt_i_ar", 0)), format="%.2f")
            omsattningstillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år %", value=float(bolag.get("omsattningstillvaxt_nastaar", 0)), format="%.2f")
            nuvarande_pe = st.number_input("Nuvarande P/E", value=float(bolag.get("nuvarande_pe", 0)), format="%.2f")
            pe1 = st.number_input("P/E 1", value=float(bolag.get("pe1", 0)), format="%.2f")
            pe2 = st.number_input("P/E 2", value=float(bolag.get("pe2", 0)), format="%.2f")
            pe3 = st.number_input("P/E 3", value=float(bolag.get("pe3", 0)), format="%.2f")
            pe4 = st.number_input("P/E 4", value=float(bolag.get("pe4", 0)), format="%.2f")
            nuvarande_ps = st.number_input("Nuvarande P/S", value=float(bolag.get("nuvarande_ps", 0)), format="%.2f")
            ps1 = st.number_input("P/S 1", value=float(bolag.get("ps1", 0)), format="%.2f")
            ps2 = st.number_input("P/S 2", value=float(bolag.get("ps2", 0)), format="%.2f")
            ps3 = st.number_input("P/S 3", value=float(bolag.get("ps3", 0)), format="%.2f")
            ps4 = st.number_input("P/S 4", value=float(bolag.get("ps4", 0)), format="%.2f")

        submitted = st.form_submit_button("Uppdatera bolag")

        if submitted:
            from datetime import datetime
            datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "bolagsnamn": bolag["bolagsnamn"],
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_i_ar": omsattningstillvaxt_i_ar,
                "omsattningstillvaxt_nastaar": omsattningstillvaxt_nastaar,
                "nuvarande_pe": nuvarande_pe,
                "pe1": pe1,
                "pe2": pe2,
                "pe3": pe3,
                "pe4": pe4,
                "nuvarande_ps": nuvarande_ps,
                "ps1": ps1,
                "ps2": ps2,
                "ps3": ps3,
                "ps4": ps4,
                "insatt_datum": bolag.get("insatt_datum", ""),
                "senast_andrad": datum,
            }
        return None
