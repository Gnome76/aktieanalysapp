import streamlit as st
import json
import os
from datetime import datetime

DATA_PATH = "/tmp/data.json"  # skrivbar mapp i streamlitcloud

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    else:
        return []

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def calc_target_pe(bolag):
    pe_values = [bolag.get(f"pe{i}", 0) for i in range(1,5)]
    pe_avg = sum(pe_values)/4 if all(pe_values) else bolag.get("nuvarande_pe", 0)
    return pe_avg * bolag.get("forvantad_vinst_i_ar", 0)

def calc_target_ps(bolag):
    ps_values = [bolag.get(f"ps{i}", 0) for i in range(1,5)]
    ps_avg = sum(ps_values)/4 if all(ps_values) else bolag.get("nuvarande_ps", 0)
    omsattningstillvaxt_i_ar = bolag.get("forvantad_omsattningstillvaxt_i_ar", 0) / 100
    omsattning_i_fjol = bolag.get("omsattning_fjol", 0)
    omsattning_i_ar = omsattning_i_fjol * (1 + omsattningstillvaxt_i_ar)
    return ps_avg * omsattning_i_ar

def undervarderad(bolag):
    target_pe = calc_target_pe(bolag)
    target_ps = calc_target_ps(bolag)
    kurs = bolag.get("nuvarande_kurs", 0)
    undervard_pe = (target_pe - kurs) / target_pe if target_pe else 0
    undervard_ps = (target_ps - kurs) / target_ps if target_ps else 0
    return max(undervard_pe, undervard_ps)

def main():
    st.title("Aktieanalys - Inmatning & Undervärdering")

    if "data" not in st.session_state:
        st.session_state.data = load_data()
    if "valj_bolag" not in st.session_state:
        st.session_state.valj_bolag = None

    # Sortera bolag efter mest undervärderade (störst undervärderingsprocent)
    for bolag in st.session_state.data:
        bolag["undervardering"] = undervarderad(bolag)
    st.session_state.data.sort(key=lambda x: x["undervardering"], reverse=True)

    checkbox_filter = st.checkbox("Visa endast bolag undervärderade med minst 30%", value=False)

    # Filtrera om checkbox är ikryssad
    visningslista = [b for b in st.session_state.data if b["undervardering"] >= 0.3] if checkbox_filter else st.session_state.data

    # Bolagsval i rullista
    bolagsnamn_lista = [b["bolagsnamn"] for b in visningslista]
    valt_bolag = st.selectbox("Välj bolag att visa/redigera", bolagsnamn_lista)

    # Hitta valt bolagdata
    bolag_data = next((b for b in st.session_state.data if b["bolagsnamn"] == valt_bolag), None)

    if bolag_data:
        with st.form("redigera_bolag"):
            st.subheader(f"Redigera bolag: {valt_bolag}")

            # Visa alltid nuvarande kurs
            nuvarande_kurs = st.number_input("Nuvarande kurs", value=bolag_data.get("nuvarande_kurs", 0.0), step=0.01, format="%.2f")

            # Döljbara fält
            with st.expander("Visa/ändra övriga fält"):
                bolagsnamn = st.text_input("Bolagsnamn", value=bolag_data.get("bolagsnamn", ""))
                vinst_fjol = st.number_input("Vinst förra året", value=bolag_data.get("vinst_fjol", 0.0), format="%.2f")
                forvantad_vinst_i_ar = st.number_input("Förväntad vinst i år", value=bolag_data.get("forvantad_vinst_i_ar", 0.0), format="%.2f")
                forvantad_vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", value=bolag_data.get("forvantad_vinst_nasta_ar", 0.0), format="%.2f")
                omsattning_fjol = st.number_input("Omsättning förra året", value=bolag_data.get("omsattning_fjol", 0.0), format="%.2f")
                forvantad_omsattningstillvaxt_i_ar = st.number_input("Förväntad omsättningstillväxt i år %", value=bolag_data.get("forvantad_omsattningstillvaxt_i_ar", 0.0), format="%.2f")
                forvantad_omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år %", value=bolag_data.get("forvantad_omsattningstillvaxt_nasta_ar", 0.0), format="%.2f")
                nuvarande_pe = st.number_input("Nuvarande P/E", value=bolag_data.get("nuvarande_pe", 0.0), format="%.2f")
                pe1 = st.number_input("P/E 1", value=bolag_data.get("pe1", 0.0), format="%.2f")
                pe2 = st.number_input("P/E 2", value=bolag_data.get("pe2", 0.0), format="%.2f")
                pe3 = st.number_input("P/E 3", value=bolag_data.get("pe3", 0.0), format="%.2f")
                pe4 = st.number_input("P/E 4", value=bolag_data.get("pe4", 0.0), format="%.2f")
                nuvarande_ps = st.number_input("Nuvarande P/S", value=bolag_data.get("nuvarande_ps", 0.0), format="%.2f")
                ps1 = st.number_input("P/S 1", value=bolag_data.get("ps1", 0.0), format="%.2f")
                ps2 = st.number_input("P/S 2", value=bolag_data.get("ps2", 0.0), format="%.2f")
                ps3 = st.number_input("P/S 3", value=bolag_data.get("ps3", 0.0), format="%.2f")
                ps4 = st.number_input("P/S 4", value=bolag_data.get("ps4", 0.0), format="%.2f")

            submit = st.form_submit_button("Uppdatera")

            if submit:
                # Uppdatera bolagsdata
                bolag_data.update({
                    "bolagsnamn": bolagsnamn,
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_fjol": vinst_fjol,
                    "forvantad_vinst_i_ar": forvantad_vinst_i_ar,
                    "forvantad_vinst_nasta_ar": forvantad_vinst_nasta_ar,
                    "omsattning_fjol": omsattning_fjol,
                    "forvantad_omsattningstillvaxt_i_ar": forvantad_omsattningstillvaxt_i_ar,
                    "forvantad_omsattningstillvaxt_nasta_ar": forvantad_omsattningstillvaxt_nasta_ar,
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
                    "datum_insatt_eller_andrad": datetime.now().isoformat()
                })
                save_data(st.session_state.data)
                st.success("Bolag uppdaterat!")

    # Lägg till nytt bolag
    with st.expander("Lägg till nytt bolag"):
        with st.form("nytt_bolag_form"):
            nytt_bolagsnamn = st.text_input("Bolagsnamn")
            nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
            vinst_fjol = st.number_input("Vinst förra året", min_value=0.0, format="%.2f")
            forvantad_vinst_i_ar = st.number_input("Förväntad vinst i år", min_value=0.0, format="%.2f")
            forvantad_vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", min_value=0.0, format="%.2f")
            omsattning_fjol = st.number_input("Omsättning förra året", min_value=0.0, format="%.2f")
            forvantad_omsattningstillvaxt_i_ar = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
            forvantad_omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
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

            submit_nytt = st.form_submit_button("Lägg till bolag")

            if submit_nytt:
                if not nytt_bolagsnamn:
                    st.error("Ange ett bolagsnamn!")
                elif any(b["bolagsnamn"].lower() == nytt_bolagsnamn.lower() for b in st.session_state.data):
                    st.error("Bolaget finns redan!")
                else:
                    nytt_bolag = {
                        "bolagsnamn": nytt_bolagsnamn,
                        "nuvarande_kurs": nuvarande_kurs,
                        "vinst_fjol": vinst_fjol,
                        "forvantad_vinst_i_ar": forvantad_vinst_i_ar,
                        "forvantad_vinst_nasta_ar": forvantad_vinst_nasta_ar,
                        "omsattning_fjol": omsattning_fjol,
                        "forvantad_omsattningstillvaxt_i_ar": forvantad_omsattningstillvaxt_i_ar,
                        "forvantad_omsattningstillvaxt_nasta_ar": forvantad_omsattningstillvaxt_nasta_ar,
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
                        "datum_insatt_eller_andrad": datetime.now().isoformat()
                    }
                    st.session_state.data.append(nytt_bolag)
                    save_data(st.session_state.data)
                    st.success(f"Bolag {nytt_bolagsnamn} tillagt!")
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
