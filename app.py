import streamlit as st
import json
import os
from datetime import datetime

DATA_PATH = "data.json"

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_targetkurs_pe(vinst_nastaar, pe_values):
    pe_avg = sum(pe_values) / len(pe_values)
    return vinst_nastaar * pe_avg if vinst_nastaar and pe_avg else None

def calculate_targetkurs_ps(oms_nastaar, oms_tillvaxt_ars, ps_values):
    ps_avg = sum(ps_values) / len(ps_values)
    oms_vaxande = oms_nastaar * (1 + oms_tillvaxt_ars/100) if oms_nastaar and oms_tillvaxt_ars else None
    if oms_vaxande and ps_avg:
        return oms_vaxande * ps_avg
    return None

def main():
    st.title("Aktieanalysapp")

    data = load_data()
    if "data" not in st.session_state:
        st.session_state.data = data

    # --- Form för nytt/uppdatera bolag ---
    st.header("Lägg till / uppdatera bolag")
    bolagsnamn = st.text_input("Bolagsnamn").strip()

    kurs = st.number_input("Nuvarande kurs (kr)", min_value=0.0, format="%.2f")
    vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
    vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
    vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")

    oms_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
    oms_tillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
    oms_tillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")

    p_e_current = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
    p_e_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
    p_e_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
    p_e_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
    p_e_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")

    p_s_current = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
    p_s_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
    p_s_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
    p_s_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
    p_s_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

    if st.button("Spara bolag"):
        if not bolagsnamn:
            st.error("Ange ett bolagsnamn!")
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.data[bolagsnamn] = {
                "kurs": kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nastaar": vinst_nastaar,
                "oms_forra_aret": oms_forra_aret,
                "oms_tillvaxt_ar": oms_tillvaxt_ar,
                "oms_tillvaxt_nasta_ar": oms_tillvaxt_nasta_ar,
                "p_e_current": p_e_current,
                "p_e_1": p_e_1,
                "p_e_2": p_e_2,
                "p_e_3": p_e_3,
                "p_e_4": p_e_4,
                "p_s_current": p_s_current,
                "p_s_1": p_s_1,
                "p_s_2": p_s_2,
                "p_s_3": p_s_3,
                "p_s_4": p_s_4,
                "insatt_datum": now_str
            }
            save_data(st.session_state.data)
            st.success(f"{bolagsnamn} sparad/uppdaterad!")

    st.markdown("---")

    # --- Välj bolag att visa/redigera ---
    if st.session_state.data:
        st.header("Redigera bolag")
        valt_bolag = st.selectbox("Välj bolag", options=list(st.session_state.data.keys()))

        if valt_bolag:
            bolag = st.session_state.data[valt_bolag]
            kurs = st.number_input("Nuvarande kurs (kr)", value=bolag["kurs"], min_value=0.0, format="%.2f", key="edit_kurs")
            vinst_forra_aret = st.number_input("Vinst förra året", value=bolag["vinst_forra_aret"], format="%.2f", key="edit_vinst_forra_aret")
            vinst_i_ar = st.number_input("Förväntad vinst i år", value=bolag["vinst_i_ar"], format="%.2f", key="edit_vinst_i_ar")
            vinst_nastaar = st.number_input("Förväntad vinst nästa år", value=bolag["vinst_nastaar"], format="%.2f", key="edit_vinst_nastaar")

            oms_forra_aret = st.number_input("Omsättning förra året", value=bolag["oms_forra_aret"], format="%.2f", key="edit_oms_forra_aret")
            oms_tillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", value=bolag["oms_tillvaxt_ar"], format="%.2f", key="edit_oms_tillvaxt_ar")
            oms_tillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", value=bolag["oms_tillvaxt_nasta_ar"], format="%.2f", key="edit_oms_tillvaxt_nasta_ar")

            p_e_current = st.number_input("Nuvarande P/E", value=bolag["p_e_current"], min_value=0.0, format="%.2f", key="edit_p_e_current")
            p_e_1 = st.number_input("P/E 1", value=bolag["p_e_1"], min_value=0.0, format="%.2f", key="edit_p_e_1")
            p_e_2 = st.number_input("P/E 2", value=bolag["p_e_2"], min_value=0.0, format="%.2f", key="edit_p_e_2")
            p_e_3 = st.number_input("P/E 3", value=bolag["p_e_3"], min_value=0.0, format="%.2f", key="edit_p_e_3")
            p_e_4 = st.number_input("P/E 4", value=bolag["p_e_4"], min_value=0.0, format="%.2f", key="edit_p_e_4")

            p_s_current = st.number_input("Nuvarande P/S", value=bolag["p_s_current"], min_value=0.0, format="%.2f", key="edit_p_s_current")
            p_s_1 = st.number_input("P/S 1", value=bolag["p_s_1"], min_value=0.0, format="%.2f", key="edit_p_s_1")
            p_s_2 = st.number_input("P/S 2", value=bolag["p_s_2"], min_value=0.0, format="%.2f", key="edit_p_s_2")
            p_s_3 = st.number_input("P/S 3", value=bolag["p_s_3"], min_value=0.0, format="%.2f", key="edit_p_s_3")
            p_s_4 = st.number_input("P/S 4", value=bolag["p_s_4"], min_value=0.0, format="%.2f", key="edit_p_s_4")

            if st.button("Uppdatera bolag"):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.data[valt_bolag] = {
                    "kurs": kurs,
                    "vinst_forra_aret": vinst_forra_aret,
                    "vinst_i_ar": vinst_i_ar,
                    "vinst_nastaar": vinst_nastaar,
                    "oms_forra_aret": oms_forra_aret,
                    "oms_tillvaxt_ar": oms_tillvaxt_ar,
                    "oms_tillvaxt_nasta_ar": oms_tillvaxt_nasta_ar,
                    "p_e_current": p_e_current,
                    "p_e_1": p_e_1,
                    "p_e_2": p_e_2,
                    "p_e_3": p_e_3,
                    "p_e_4": p_e_4,
                    "p_s_current": p_s_current,
                    "p_s_1": p_s_1,
                    "p_s_2": p_s_2,
                    "p_s_3": p_s_3,
                    "p_s_4": p_s_4,
                    "insatt_datum": now_str
                }
                save_data(st.session_state.data)
                st.success(f"{valt_bolag} uppdaterad!")

    else:
        st.info("Inga bolag sparade än.")

    st.markdown("---")

    # --- Visa bolag och beräkna targetkurser och undervärdering ---
    st.header("Bolagslista")

    visa_undervaerd = st.checkbox("Visa endast minst 30% undervärderade bolag", value=False)

    def is_undervaerd(bolag):
        # Target P/E baserat på nästa års vinst och P/E snitt
        pe_values = [bolag["p_e_1"], bolag["p_e_2"], bolag["p_e_3"], bolag["p_e_4"]]
        target_pe = calculate_targetkurs_pe(bolag["vinst_nastaar"], pe_values)
        # Target P/S baserat på omsättning nästa år * tillväxt och P/S snitt
        ps_values = [bolag["p_s_1"], bolag["p_s_2"], bolag["p_s_3"], bolag["p_s_4"]]
        target_ps = calculate_targetkurs_ps(bolag["oms_forra_aret"], bolag["oms_tillvaxt_nasta_ar"], ps_values)
        if target_pe is None or target_ps is None:
            return False
        nuvarande_kurs = bolag["kurs"]
        # Rabatt (undervärdering) i procent:
        rabatt_pe = (target_pe - nuvarande_kurs) / target_pe if target_pe else 0
        rabatt_ps = (target_ps - nuvarande_kurs) / target_ps if target_ps else 0
        return rabatt_pe >= 0.30 or rabatt_ps >= 0.30

    for namn, bolag in st.session_state.data.items():
        # Beräkningar:
        pe_values = [bolag["p_e_1"], bolag["p_e_2"], bolag["p_e_3"], bolag["p_e_4"]]
        target_pe = calculate_targetkurs_pe(bolag["vinst_nastaar"], pe_values)
        ps_values = [bolag["p_s_1"], bolag["p_s_2"], bolag["p_s_3"], bolag["p_s_4"]]
        target_ps = calculate_targetkurs_ps(bolag["oms_forra_aret"], bolag["oms_tillvaxt_nasta_ar"], ps_values)
        nuvarande_kurs = bolag["kurs"]

        rabatt_pe = ((target_pe - nuvarande_kurs) / target_pe) if target_pe else None
        rabatt_ps = ((target_ps - nuvarande_kurs) / target_ps) if target_ps else None

        if visa_undervaerd and not is_undervaerd(bolag):
            continue

        st.subheader(namn)
        st.write(f"Nuvarande kurs: {nuvarande_kurs:.2f} kr")
        st.write(f"Targetkurs (P/E): {target_pe:.2f} kr" if target_pe else "Targetkurs (P/E): -")
        st.write(f"Targetkurs (P/S): {target_ps:.2f} kr" if target_ps else "Targetkurs (P/S): -")
        if rabatt_pe is not None:
            st.write(f"Undervärdering (P/E): {rabatt_pe*100:.1f} %")
        if rabatt_ps is not None:
            st.write(f"Undervärdering (P/S): {rabatt_ps*100:.1f} %")
        st.write(f"Inlagt / Uppdaterat: {bolag.get('insatt_datum','-')}")

if __name__ == "__main__":
    main()
