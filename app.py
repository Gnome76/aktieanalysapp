import streamlit as st
import json
import os
from datetime import datetime

DATA_PATH = "/mnt/data/data.json"

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def calculate_targetkurs_pe(bolag):
    pe_vals = [bolag.get(f"pe{i}") for i in range(1,5)]
    pe_vals = [v for v in pe_vals if v is not None and v > 0]
    if not pe_vals or bolag.get("vinst_nastaar") is None:
        return None
    pe_snitt = sum(pe_vals) / len(pe_vals)
    return pe_snitt * bolag["vinst_nastaar"]

def calculate_targetkurs_ps(bolag):
    ps_vals = [bolag.get(f"ps{i}") for i in range(1,5)]
    ps_vals = [v for v in ps_vals if v is not None and v > 0]
    if not ps_vals or bolag.get("oms_nastaar") is None:
        return None
    ps_snitt = sum(ps_vals) / len(ps_vals)
    return ps_snitt * bolag["oms_nastaar"]

def undervarderingsprocent(nuvarande, target):
    if nuvarande is None or target is None or target == 0:
        return None
    return (target - nuvarande) / target * 100

def main():
    st.title("Aktieanalysapp")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    # Inmatning av nytt eller uppdatering
    with st.form("input_form"):
        bolagsnamn = st.text_input("Bolagsnamn", max_chars=30).strip()

        nuvarande_kurs = st.number_input("Nuvarande kurs (kr)", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året (kr)", min_value=0.0, format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år (kr)", min_value=0.0, format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år (kr)", min_value=0.0, format="%.2f")

        oms_forra_aret = st.number_input("Omsättning förra året (kr)", min_value=0.0, format="%.2f")
        oms_tillvaxt_i_ar = st.number_input("Omsättningstillväxt i år (%)", min_value=-100.0, format="%.2f")
        oms_tillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år (%)", min_value=-100.0, format="%.2f")
        oms_nastaar = oms_forra_aret * (1 + oms_tillvaxt_i_ar / 100) * (1 + oms_tillvaxt_nastaar / 100)

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

        submitted = st.form_submit_button("Spara bolag")

    if submitted:
        if bolagsnamn == "":
            st.error("Ange bolagsnamn!")
        else:
            st.session_state.data[bolagsnamn] = {
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "oms_forra_aret": oms_forra_aret,
                "oms_tillvaxt_i_ar": oms_tillvaxt_i_ar,
                "oms_tillvaxt_nastaar": oms_tillvaxt_nastaar,
                "oms_nastaar": oms_nastaar,
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
                "insatt_datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_data(st.session_state.data)
            st.success(f"Bolaget '{bolagsnamn}' sparat!")

    # Beräkna targetkurser och undervärdering
    bolag_lista = []
    for namn, bolag in st.session_state.data.items():
        bolag_copy = bolag.copy()
        bolag_copy["namn"] = namn
        bolag_copy["targetkurs_pe"] = calculate_targetkurs_pe(bolag)
        bolag_copy["targetkurs_ps"] = calculate_targetkurs_ps(bolag)
        bolag_copy["undervard_pe_pct"] = undervarderingsprocent(bolag.get("nuvarande_kurs"), bolag_copy["targetkurs_pe"])
        bolag_copy["undervard_ps_pct"] = undervarderingsprocent(bolag.get("nuvarande_kurs"), bolag_copy["targetkurs_ps"])
        bolag_lista.append(bolag_copy)

    def max_undervard(b):
        p = b.get("undervard_pe_pct") or -9999
        s = b.get("undervard_ps_pct") or -9999
        return max(p, s)

    bolag_lista_sorted = sorted(bolag_lista, key=max_undervard, reverse=True)

    visa_endast_undervard = st.checkbox("Visa endast bolag med minst 30% undervärdering")

    if visa_endast_undervard:
        bolag_lista_sorted = [b for b in bolag_lista_sorted if (b.get("undervard_pe_pct") or 0) >= 30 or (b.get("undervard_ps_pct") or 0) >= 30]

    if "index" not in st.session_state:
        st.session_state.index = 0

    if len(bolag_lista_sorted) == 0:
        st.info("Inga bolag att visa")
        return

    # Bläddra mellan bolag
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Föregående"):
            st.session_state.index = max(0, st.session_state.index - 1)
    with col3:
        if st.button("Nästa"):
            st.session_state.index = min(len(bolag_lista_sorted) - 1, st.session_state.index + 1)

    bolag_visas = bolag_lista_sorted[st.session_state.index]
    st.subheader(f"{bolag_visas['namn']} ({st.session_state.index+1} / {len(bolag_lista_sorted)})")

    st.write(f"Nuvarande kurs: {bolag_visas.get('nuvarande_kurs')} kr")

       # Visa detaljer i expanderbar sektion
    with st.expander("Visa/redigera detaljer"):
        bolagsnamn_edit = st.text_input("Bolagsnamn", value=bolag_visas["namn"], key="edit_bolagsnamn")
        nuvarande_kurs_edit = st.number_input("Nuvarande kurs (kr)", value=bolag_visas.get("nuvarande_kurs", 0.0), format="%.2f", key="edit_nuvarande_kurs")
        vinst_forra_aret_edit = st.number_input("Vinst förra året (kr)", value=bolag_visas.get("vinst_forra_aret", 0.0), format="%.2f", key="edit_vinst_forra_aret")
        vinst_i_ar_edit = st.number_input("Förväntad vinst i år (kr)", value=bolag_visas.get("vinst_i_ar", 0.0), format="%.2f", key="edit_vinst_i_ar")
        vinst_nastaar_edit = st.number_input("Förväntad vinst nästa år (kr)", value=bolag_visas.get("vinst_nastaar", 0.0), format="%.2f", key="edit_vinst_nastaar")

        oms_forra_aret_edit = st.number_input("Omsättning förra året (kr)", value=bolag_visas.get("oms_forra_aret", 0.0), format="%.2f", key="edit_oms_forra_aret")
        oms_tillvaxt_i_ar_edit = st.number_input("Omsättningstillväxt i år (%)", value=bolag_visas.get("oms_tillvaxt_i_ar", 0.0), format="%.2f", key="edit_oms_tillvaxt_i_ar")
        oms_tillvaxt_nastaar_edit = st.number_input("Omsättningstillväxt nästa år (%)", value=bolag_visas.get("oms_tillvaxt_nastaar", 0.0), format="%.2f", key="edit_oms_tillvaxt_nastaar")

        nuvarande_pe_edit = st.number_input("Nuvarande P/E", value=bolag_visas.get("nuvarande_pe", 0.0), format="%.2f", key="edit_nuvarande_pe")
        pe1_edit = st.number_input("P/E 1", value=bolag_visas.get("pe1", 0.0), format="%.2f", key="edit_pe1")
        pe2_edit = st.number_input("P/E 2", value=bolag_visas.get("pe2", 0.0), format="%.2f", key="edit_pe2")
        pe3_edit = st.number_input("P/E 3", value=bolag_visas.get("pe3", 0.0), format="%.2f", key="edit_pe3")
        pe4_edit = st.number_input("P/E 4", value=bolag_visas.get("pe4", 0.0), format="%.2f", key="edit_pe4")

        nuvarande_ps_edit = st.number_input("Nuvarande P/S", value=bolag_visas.get("nuvarande_ps", 0.0), format="%.2f", key="edit_nuvarande_ps")
        ps1_edit = st.number_input("P/S 1", value=bolag_visas.get("ps1", 0.0), format="%.2f", key="edit_ps1")
        ps2_edit = st.number_input("P/S 2", value=bolag_visas.get("ps2", 0.0), format="%.2f", key="edit_ps2")
        ps3_edit = st.number_input("P/S 3", value=bolag_visas.get("ps3", 0.0), format="%.2f", key="edit_ps3")
        ps4_edit = st.number_input("P/S 4", value=bolag_visas.get("ps4", 0.0), format="%.2f", key="edit_ps4")

        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            if st.button("Uppdatera bolag"):
                # Ta bort gammalt namn om ändrat
                if bolagsnamn_edit != bolag_visas["namn"]:
                    if bolagsnamn_edit in st.session_state.data:
                        st.error("Det finns redan ett bolag med detta namn!")
                    else:
                        st.session_state.data.pop(bolag_visas["namn"])
                # Beräkna omsättning nästa år på nytt
                oms_nastaar_edit = oms_forra_aret_edit * (1 + oms_tillvaxt_i_ar_edit / 100) * (1 + oms_tillvaxt_nastaar_edit / 100)
                st.session_state.data[bolagsnamn_edit] = {
                    "nuvarande_kurs": nuvarande_kurs_edit,
                    "vinst_forra_aret": vinst_forra_aret_edit,
                    "vinst_i_ar": vinst_i_ar_edit,
                    "vinst_nastaar": vinst_nastaar_edit,
                    "oms_forra_aret": oms_forra_aret_edit,
                    "oms_tillvaxt_i_ar": oms_tillvaxt_i_ar_edit,
                    "oms_tillvaxt_nastaar": oms_tillvaxt_nastaar_edit,
                    "oms_nastaar": oms_nastaar_edit,
                    "nuvarande_pe": nuvarande_pe_edit,
                    "pe1": pe1_edit,
                    "pe2": pe2_edit,
                    "pe3": pe3_edit,
                    "pe4": pe4_edit,
                    "nuvarande_ps": nuvarande_ps_edit,
                    "ps1": ps1_edit,
                    "ps2": ps2_edit,
                    "ps3": ps3_edit,
                    "ps4": ps4_edit,
                    "insatt_datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_data(st.session_state.data)
                st.success(f"Bolaget '{bolagsnamn_edit}' uppdaterat!")

        with col_edit2:
            if st.button("Ta bort bolag"):
                st.session_state.data.pop(bolag_visas["namn"])
                save_data(st.session_state.data)
                st.success(f"Bolaget '{bolag_visas['namn']}' borttaget!")
                # Justera index för att undvika fel
                st.session_state.index = max(0, st.session_state.index - 1) 
