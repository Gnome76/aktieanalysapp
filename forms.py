import streamlit as st

def input_form():
    with st.form(key="input_form"):
        bolagsnamn = st.text_input("Bolagsnamn")
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")

        vinst_fj = st.number_input("Vinst förra året", min_value=0.0, format="%.2f")
        vinst_i_aar = st.number_input("Förväntad vinst i år", min_value=0.0, format="%.2f")
        vinst_nasta_aar = st.number_input("Förväntad vinst nästa år", min_value=0.0, format="%.2f")

        omsattning_fj = st.number_input("Omsättning förra året", min_value=0.0, format="%.2f")
        omsattningstillvxt_i_aar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvxt_nasta_aar = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")

        pe_nu = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
        pe1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        pe3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
        pe4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")

        ps_nu = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
        ps1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        ps3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
        ps4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Lägg till bolag")
        if submitted:
            if bolagsnamn.strip() == "":
                st.warning("Bolagsnamn måste fyllas i.")
                return None
            return {
                "bolagsnamn": bolagsnamn,
                "kurs": kurs,
                "vinst_fj": vinst_fj,
                "vinst_i_aar": vinst_i_aar,
                "vinst_nasta_aar": vinst_nasta_aar,
                "omsattning_fj": omsattning_fj,
                "omsattningstillvxt_i_aar": omsattningstillvxt_i_aar,
                "omsattningstillvxt_nasta_aar": omsattningstillvxt_nasta_aar,
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
            }
    return None


def edit_form(bolag):
    with st.form(key="edit_form"):
        kurs = st.number_input("Nuvarande kurs", value=bolag.get("kurs", 0.0), min_value=0.0, format="%.2f")

        # Här kan du lägga till fler fält som ska kunna redigeras, eller gömma detaljer och visa vid behov

        submitted = st.form_submit_button("Uppdatera bolag")
        if submitted:
            bolag["kurs"] = kurs
            # Uppdatera även datumfält om du vill
            return bolag
    return None
