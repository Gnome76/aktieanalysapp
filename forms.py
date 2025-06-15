import streamlit as st
from datetime import datetime

def input_form():
    with st.form(key="input_form"):
        st.subheader("➕ Lägg till nytt bolag")

        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")

        vinst_fjol = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")

        oms_fjol = st.number_input("Omsättning förra året", format="%.2f")
        oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
        oms_tillv_nastaar = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")

        pe_nu = st.number_input("Nuvarande P/E", format="%.2f")
        pe1 = st.number_input("P/E 1", format="%.2f")
        pe2 = st.number_input("P/E 2", format="%.2f")
        pe3 = st.number_input("P/E 3", format="%.2f")
        pe4 = st.number_input("P/E 4", format="%.2f")

        ps_nu = st.number_input("Nuvarande P/S", format="%.2f")
        ps1 = st.number_input("P/S 1", format="%.2f")
        ps2 = st.number_input("P/S 2", format="%.2f")
        ps3 = st.number_input("P/S 3", format="%.2f")
        ps4 = st.number_input("P/S 4", format="%.2f")

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_fjol": vinst_fjol,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "oms_fjol": oms_fjol,
                "oms_tillv_i_ar": oms_tillv_i_ar,
                "oms_tillv_nastaar": oms_tillv_nastaar,
                "pe_nu": pe_nu,
                "pe1": pe1,
                "pe2": pe2,
                "pe3": pe3,
                "pe4": pe4,
                "ps_nu": ps_nu,
                "ps1": ps1,
                "ps2": ps2,
                "ps3": ps3,
                "ps4": ps4,
                "insatt_datum": str(datetime.now().date()),
                "senast_andrad": str(datetime.now().date())
            }
    return None

def edit_form(bolag):
    with st.form(key=f"edit_form_{bolag['bolagsnamn']}"):
        st.subheader(f"✏️ Redigera: {bolag['bolagsnamn']}")
        ny_kurs = st.number_input("Nuvarande kurs", value=bolag.get("nuvarande_kurs", 0.0), format="%.2f")

        visa_extra = st.checkbox("Visa och redigera övriga fält", key=f"show_extra_{bolag['bolagsnamn']}")

        uppdaterad = bolag.copy()
        uppdaterad["nuvarande_kurs"] = ny_kurs

        if visa_extra:
            uppdaterad["vinst_fjol"] = st.number_input("Vinst förra året", value=bolag.get("vinst_fjol", 0.0), format="%.2f")
            uppdaterad["vinst_i_ar"] = st.number_input("Förväntad vinst i år", value=bolag.get("vinst_i_ar", 0.0), format="%.2f")
            uppdaterad["vinst_nastaar"] = st.number_input("Förväntad vinst nästa år", value=bolag.get("vinst_nastaar", 0.0), format="%.2f")

            uppdaterad["oms_fjol"] = st.number_input("Omsättning förra året", value=bolag.get("oms_fjol", 0.0), format="%.2f")
            uppdaterad["oms_tillv_i_ar"] = st.number_input("Omsättningstillväxt i år (%)", value=bolag.get("oms_tillv_i_ar", 0.0), format="%.2f")
            uppdaterad["oms_tillv_nastaar"] = st.number_input("Omsättningstillväxt nästa år (%)", value=bolag.get("oms_tillv_nastaar", 0.0), format="%.2f")

            uppdaterad["pe_nu"] = st.number_input("Nuvarande P/E", value=bolag.get("pe_nu", 0.0), format="%.2f")
            uppdaterad["pe1"] = st.number_input("P/E 1", value=bolag.get("pe1", 0.0), format="%.2f")
            uppdaterad["pe2"] = st.number_input("P/E 2", value=bolag.get("pe2", 0.0), format="%.2f")
            uppdaterad["pe3"] = st.number_input("P/E 3", value=bolag.get("pe3", 0.0), format="%.2f")
            uppdaterad["pe4"] = st.number_input("P/E 4", value=bolag.get("pe4", 0.0), format="%.2f")

            uppdaterad["ps_nu"] = st.number_input("Nuvarande P/S", value=bolag.get("ps_nu", 0.0), format="%.2f")
            uppdaterad["ps1"] = st.number_input("P/S 1", value=bolag.get("ps1", 0.0), format="%.2f")
            uppdaterad["ps2"] = st.number_input("P/S 2", value=bolag.get("ps2", 0.0), format="%.2f")
            uppdaterad["ps3"] = st.number_input("P/S 3", value=bolag.get("ps3", 0.0), format="%.2f")
            uppdaterad["ps4"] = st.number_input("P/S 4", value=bolag.get("ps4", 0.0), format="%.2f")

        submitted = st.form_submit_button("Uppdatera")

        if submitted:
            uppdaterad["senast_andrad"] = str(datetime.now().date())
            return uppdaterad
    return None
