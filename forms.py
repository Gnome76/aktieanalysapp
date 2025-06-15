import streamlit as st
from datetime import datetime

def input_form():
    with st.form(key="input_form"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_aret = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_aret = st.number_input("Omsättningstillväxt i år %", format="%.2f")
        omsattningstillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år %", format="%.2f")
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
                st.error("Bolagsnamn får inte vara tomt.")
                return None
            return {
                "bolagsnamn": bolagsnamn.strip(),
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_aret": vinst_aret,
                "vinst_nastaar": vinst_nastaar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_aret": omsattningstillvaxt_aret,
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
                "insatt_datum": datetime.now().isoformat(),
                "senast_andrad": None,
            }
    return None

def edit_form(bolag):
    # Ingen st.form pga undvik form i form. Endast inputs + knappar.
    st.write(f"Redigera bolag: **{bolag['bolagsnamn']}**")

    nuvarande_kurs = st.number_input(
        "Nuvarande kurs", value=bolag.get("nuvarande_kurs", 0.0), format="%.2f"
    )

    # Expander för övriga fält
    with st.expander("Visa och redigera övriga fält"):
        vinst_forra_aret = st.number_input(
            "Vinst förra året", value=bolag.get("vinst_forra_aret", 0.0), format="%.2f"
        )
        vinst_aret = st.number_input(
            "Förväntad vinst i år", value=bolag.get("vinst_aret", 0.0), format="%.2f"
        )
        vinst_nastaar = st.number_input(
            "Förväntad vinst nästa år", value=bolag.get("vinst_nastaar", 0.0), format="%.2f"
        )
        omsattning_forra_aret = st.number_input(
            "Omsättning förra året",
            value=bolag.get("omsattning_forra_aret", 0.0),
            format="%.2f",
        )
        omsattningstillvaxt_aret = st.number_input(
            "Omsättningstillväxt i år %",
            value=bolag.get("omsattningstillvaxt_aret", 0.0),
            format="%.2f",
        )
        omsattningstillvaxt_nastaar = st.number_input(
            "Omsättningstillväxt nästa år %",
            value=bolag.get("omsattningstillvaxt_nastaar", 0.0),
            format="%.2f",
        )
        pe_nuvarande = st.number_input(
            "Nuvarande P/E", value=bolag.get("pe_nuvarande", 0.0), format="%.2f"
        )
        pe_1 = st.number_input(
            "P/E 1", value=bolag.get("pe_1", 0.0), format="%.2f"
        )
        pe_2 = st.number_input(
            "P/E 2", value=bolag.get("pe_2", 0.0), format="%.2f"
        )
        pe_3 = st.number_input(
            "P/E 3", value=bolag.get("pe_3", 0.0), format="%.2f"
        )
        pe_4 = st.number_input(
            "P/E 4", value=bolag.get("pe_4", 0.0), format="%.2f"
        )
        ps_nuvarande = st.number_input(
            "Nuvarande P/S", value=bolag.get("ps_nuvarande", 0.0), format="%.2f"
        )
        ps_1 = st.number_input(
            "P/S 1", value=bolag.get("ps_1", 0.0), format="%.2f"
        )
        ps_2 = st.number_input(
            "P/S 2", value=bolag.get("ps_2", 0.0), format="%.2f"
        )
        ps_3 = st.number_input(
            "P/S 3", value=bolag.get("ps_3", 0.0), format="%.2f"
        )
        ps_4 = st.number_input(
            "P/S 4", value=bolag.get("ps_4", 0.0), format="%.2f"
        )

    if st.button("Uppdatera bolag"):
        from datetime import datetime

        return {
            "bolagsnamn": bolag["bolagsnamn"],
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_aret": vinst_aret,
            "vinst_nastaar": vinst_nastaar,
            "omsattning_forra_aret": omsattning_forra_aret,
            "omsattningstillvaxt_aret": omsattningstillvaxt_aret,
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
            "insatt_datum": bolag.get("insatt_datum"),
            "senast_andrad": datetime.now().isoformat(),
        }
    return None
