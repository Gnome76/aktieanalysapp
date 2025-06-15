import streamlit as st

def input_form():
    """
    Formulär för att mata in nytt bolag med alla nyckeltal.
    Returnerar en dict med bolagsdata om formuläret skickas, annars None.
    """
    with st.form(key="input_form"):
        st.header("Lägg till nytt bolag")
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nastaar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")
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
            if not bolagsnamn:
                st.error("Bolagsnamn måste fyllas i.")
                return None
            return {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
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
            }
    return None

def edit_form(bolag):
    """
    Formulär för att visa och redigera ett befintligt bolag.
    Tar emot dict med bolagets data, returnerar uppdaterad dict eller None om avbryts.
    """
    with st.form(key=f"edit_form_{bolag['bolagsnamn']}"):
        st.header(f"Redigera bolag: {bolag['bolagsnamn']}")
        # Visa nuvarande kurs som readonly (kan visas i text)
        st.write(f"Nuvarande kurs: {bolag.get('nuvarande_kurs', 0.0)}")

        # Visa och redigera övriga fält
        vinst_forra_aret = st.number_input("Vinst förra året", value=bolag.get("vinst_forra_aret", 0.0), format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", value=bolag.get("vinst_i_ar", 0.0), format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", value=bolag.get("vinst_nastaar", 0.0), format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", value=bolag.get("omsattning_forra_aret", 0.0), format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", value=bolag.get("omsattningstillvaxt_ar", 0.0), format="%.2f")
        omsattningstillvaxt_nastaar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", value=bolag.get("omsattningstillvaxt_nastaar", 0.0), format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", value=bolag.get("nuvarande_pe", 0.0), format="%.2f")
        pe1 = st.number_input("P/E 1", value=bolag.get("pe1", 0.0), format="%.2f")
        pe2 = st.number_input("P/E 2", value=bolag.get("pe2", 0.0), format="%.2f")
        pe3 = st.number_input("P/E 3", value=bolag.get("pe3", 0.0), format="%.2f")
        pe4 = st.number_input("P/E 4", value=bolag.get("pe4", 0.0), format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", value=bolag.get("nuvarande_ps", 0.0), format="%.2f")
        ps1 = st.number_input("P/S 1", value=bolag.get("ps1", 0.0), format="%.2f")
        ps2 = st.number_input("P/S 2", value=bolag.get("ps2", 0.0), format="%.2f")
        ps3 = st.number_input("P/S 3", value=bolag.get("ps3", 0.0), format="%.2f")
        ps4 = st.number_input("P/S 4", value=bolag.get("ps4", 0.0), format="%.2f")

        submitted = st.form_submit_button("Uppdatera bolag")

        if submitted:
            uppdaterat_bolag = {
                "bolagsnamn": bolag["bolagsnamn"],  # Ej redigerbart här
                "nuvarande_kurs": bolag.get("nuvarande_kurs", 0.0),  # Kan ev. hanteras separat
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
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
            }
            return uppdaterat_bolag
    return None
