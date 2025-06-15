import streamlit as st
from datetime import datetime

def input_form():
    with st.form(key="input_form"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")
        pe_nuvarande = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")
        ps_nuvarande = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Lägg till bolag")
        if submitted:
            if bolagsnamn.strip() == "":
                st.error("Ange bolagsnamn")
                return None
            bolag = {
                "bolagsnamn": bolagsnamn.strip(),
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                "omsattningstillvaxt_nastaar": omsattningstillvaxt_nastaar,
                "pe_nuvarande": pe_nuvarande,
                "pe_1": pe_1,
                "pe_2": pe_2,
                "pe_3": pe_3,
                "pe_4": pe_4,
                "ps_nuvarande": ps_nuvarande,
                "ps_1": ps_1,
                "ps_2": ps_2,
                "ps_3": ps_3,
                "ps_4": ps_4,
                "insatt_datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "senast_andrad": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return bolag
    return None

def edit_form(bolag):
    with st.form(key=f"edit_form_{bolag['bolagsnamn']}"):
        st.write(f"Redigera bolag: **{bolag['bolagsnamn']}**")
        # Visa nuvarande kurs som read-only
        st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f}")

        # Skapa checkbox för att visa övriga fält
        visa_ovriga = st.checkbox("Visa och redigera övriga fält")

        if visa_ovriga:
            vinst_forra_aret = st.number_input("Vinst förra året", value=bolag.get("vinst_forra_aret", 0.0), format="%.2f")
            vinst_i_ar = st.number_input("Förväntad vinst i år", value=bolag.get("vinst_i_ar", 0.0), format="%.2f")
            vinst_nastaar = st.number_input("Förväntad vinst nästa år", value=bolag.get("vinst_nastaar", 0.0), format="%.2f")
            omsattning_forra_aret = st.number_input("Omsättning förra året", value=bolag.get("omsattning_forra_aret", 0.0), format="%.2f")
            omsattningstillvaxt_ar = st.number_input("Omsättningstillväxt i år (%)", value=bolag.get("omsattningstillvaxt_ar", 0.0), format="%.2f")
            omsattningstillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år (%)", value=bolag.get("omsattningstillvaxt_nastaar", 0.0), format="%.2f")
            pe_nuvarande = st.number_input("Nuvarande P/E", value=bolag.get("pe_nuvarande", 0.0), format="%.2f")
            pe_1 = st.number_input("P/E 1", value=bolag.get("pe_1", 0.0), format="%.2f")
            pe_2 = st.number_input("P/E 2", value=bolag.get("pe_2", 0.0), format="%.2f")
            pe_3 = st.number_input("P/E 3", value=bolag.get("pe_3", 0.0), format="%.2f")
            pe_4 = st.number_input("P/E 4", value=bolag.get("pe_4", 0.0), format="%.2f")
            ps_nuvarande = st.number_input("Nuvarande P/S", value=bolag.get("ps_nuvarande", 0.0), format="%.2f")
            ps_1 = st.number_input("P/S 1", value=bolag.get("ps_1", 0.0), format="%.2f")
            ps_2 = st.number_input("P/S 2", value=bolag.get("ps_2", 0.0), format="%.2f")
            ps_3 = st.number_input("P/S 3", value=bolag.get("ps_3", 0.0), format="%.2f")
            ps_4 = st.number_input("P/S 4", value=bolag.get("ps_4", 0.0), format="%.2f")
        else:
            # Behåll gamla värden om checkbox inte är ikryssad
            vinst_forra_aret = bolag.get("vinst_forra_aret", 0.0)
            vinst_i_ar = bolag.get("vinst_i_ar", 0.0)
            vinst_nastaar = bolag.get("vinst_nastaar", 0.0)
            omsattning_forra_aret = bolag.get("omsattning_forra_aret", 0.0)
            omsattningstillvaxt_ar = bolag.get("omsattningstillvaxt_ar", 0.0)
            omsattningstillvaxt_nastaar = bolag.get("omsattningstillvaxt_nastaar", 0.0)
            pe_nuvarande = bolag.get("pe_nuvarande", 0.0)
            pe_1 = bolag.get("pe_1", 0.0)
            pe_2 = bolag.get("pe_2", 0.0)
            pe_3 = bolag.get("pe_3", 0.0)
            pe_4 = bolag.get("pe_4", 0.0)
            ps_nuvarande = bolag.get("ps_nuvarande", 0.0)
            ps_1 = bolag.get("ps_1", 0.0)
            ps_2 = bolag.get("ps_2", 0.0)
            ps_3 = bolag.get("ps_3", 0.0)
            ps_4 = bolag.get("ps_4", 0.0)

        submitted = st.form_submit_button("Uppdatera bolag")
        if submitted:
            bolag_uppdaterad = {
                "bolagsnamn": bolag["bolagsnamn"],
                "nuvarande_kurs": bolag["nuvarande_kurs"],  # nuvarande kurs är readonly
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                "omsattningstillvaxt_nastaar": omsattningstillvaxt_nastaar,
                "pe_nuvarande": pe_nuvarande,
                "pe_1": pe_1,
                "pe_2": pe_2,
                "pe_3": pe_3,
                "pe_4": pe_4,
                "ps_nuvarande": ps_nuvarande,
                "ps_1": ps_1,
                "ps_2": ps_2,
                "ps_3": ps_3,
                "ps_4": ps_4,
                "insatt_datum": bolag.get("insatt_datum", ""),
                "senast_andrad": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return bolag_uppdaterad
    return None
