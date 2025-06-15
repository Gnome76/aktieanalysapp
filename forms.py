import streamlit as st

def input_form():
    with st.form(key="input_form"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forr_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forr_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Omsättningstillväxt i år %", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Omsättningstillväxt nästa år %", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
        pe1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        pe3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
        pe4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
        ps1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        ps3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
        ps4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Lägg till bolag")
        if submitted:
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forr_aret": vinst_forr_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forr_aret": omsattning_forr_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
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
            }
    return None

def edit_form(bolag):
    # Edit form visar ett bolag för uppdatering
    with st.form(key=f"edit_form_{bolag['bolagsnamn']}"):
        bolagsnamn = st.text_input("Bolagsnamn", value=bolag["bolagsnamn"], disabled=True)
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=bolag["nuvarande_kurs"])
        vinst_forr_aret = st.number_input("Vinst förra året", format="%.2f", value=bolag["vinst_forr_aret"])
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f", value=bolag["vinst_i_ar"])
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f", value=bolag["vinst_nastaar"])
        omsattning_forr_aret = st.number_input("Omsättning förra året", format="%.2f", value=bolag["omsattning_forr_aret"])
        omsattningstillvaxt_ar = st.number_input("Omsättningstillväxt i år %", format="%.2f", value=bolag["omsattningstillvaxt_ar"])
        omsattningstillvaxt_nasta_ar = st.number_input("Omsättningstillväxt nästa år %", format="%.2f", value=bolag["omsattningstillvaxt_nasta_ar"])
        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f", value=bolag["nuvarande_pe"])
        pe1 = st.number_input("P/E 1", min_value=0.0, format="%.2f", value=bolag["pe1"])
        pe2 = st.number_input("P/E 2", min_value=0.0, format="%.2f", value=bolag["pe2"])
        pe3 = st.number_input("P/E 3", min_value=0.0, format="%.2f", value=bolag["pe3"])
        pe4 = st.number_input("P/E 4", min_value=0.0, format="%.2f", value=bolag["pe4"])
        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f", value=bolag["nuvarande_ps"])
        ps1 = st.number_input("P/S 1", min_value=0.0, format="%.2f", value=bolag["ps1"])
        ps2 = st.number_input("P/S 2", min_value=0.0, format="%.2f", value=bolag["ps2"])
        ps3 = st.number_input("P/S 3", min_value=0.0, format="%.2f", value=bolag["ps3"])
        ps4 = st.number_input("P/S 4", min_value=0.0, format="%.2f", value=bolag["ps4"])

        submitted = st.form_submit_button("Uppdatera bolag")
        if submitted:
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forr_aret": vinst_forr_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forr_aret": omsattning_forr_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
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
            }
    return None
