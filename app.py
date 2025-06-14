import streamlit as st
import json
import os
from datetime import datetime

DATA_PATH = "data.json"

def load_data():
    if "data" not in st.session_state:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r") as f:
                st.session_state.data = json.load(f)
        else:
            st.session_state.data = {}

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)
def calc_target_pe(pe_values, vinst_nastaar):
    pe_snitt = sum(pe_values) / len(pe_values)
    return pe_snitt * vinst_nastaar

def calc_target_ps(ps_values, oms_tillvaxt, oms_forra_aret):
    ps_snitt = sum(ps_values) / len(ps_values)
    oms_nastaar = oms_forra_aret * (1 + oms_tillvaxt/100)
    return ps_snitt * oms_nastaar

def undervardering(nuvarande_kurs, targetkurs):
    return (targetkurs - nuvarande_kurs) / targetkurs * 100  # procentuell rabatt   
def main():
    st.title("Aktieanalysapp")

    load_data()

    with st.form("nytt_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_aret = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        oms_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        oms_tillvaxt_aret = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
        oms_tillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")

        p_e_values = []
        p_s_values = []

        p_e_values.append(st.number_input("P/E 1", format="%.2f"))
        p_e_values.append(st.number_input("P/E 2", format="%.2f"))
        p_e_values.append(st.number_input("P/E 3", format="%.2f"))
        p_e_values.append(st.number_input("P/E 4", format="%.2f"))

        p_s_values.append(st.number_input("P/S 1", format="%.2f"))
        p_s_values.append(st.number_input("P/S 2", format="%.2f"))
        p_s_values.append(st.number_input("P/S 3", format="%.2f"))
        p_s_values.append(st.number_input("P/S 4", format="%.2f"))

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            if bolagsnamn.strip() == "":
                st.error("Bolagsnamn måste fyllas i!")
            else:
                datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.data[bolagsnamn] = {
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_forra_aret": vinst_forra_aret,
                    "vinst_aret": vinst_aret,
                    "vinst_nastaar": vinst_nastaar,
                    "oms_forra_aret": oms_forra_aret,
                    "oms_tillvaxt_aret": oms_tillvaxt_aret,
                    "oms_tillvaxt_nastaar": oms_tillvaxt_nastaar,
                    "p_e_values": p_e_values,
                    "p_s_values": p_s_values,
                    "insatt_datum": datum,
                    "senast_andrad": datum
                }
                save_data(st.session_state.data)
                st.success(f"Bolag {bolagsnamn} sparat!")

    st.header("Sparade bolag")

    if st.session_state.data:
        bolagslista = list(st.session_state.data.keys())
        valt_bolag = st.selectbox("Välj bolag att visa/redigera", bolagslista)

        bolag = st.session_state.data.get(valt_bolag, None)
        if bolag:
            st.subheader(valt_bolag)
            st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']} kr")

            if st.checkbox("Visa/Redigera övriga fält"):
                ny_kurs = st.number_input("Nuvarande kurs", value=bolag['nuvarande_kurs'], format="%.2f")
                ny_vinst_forra_aret = st.number_input("Vinst förra året", value=bolag['vinst_forra_aret'], format="%.2f")
                ny_vinst_aret = st.number_input("Förväntad vinst i år", value=bolag['vinst_aret'], format="%.2f")
                ny_vinst_nastaar = st.number_input("Förväntad vinst nästa år", value=bolag['vinst_nastaar'], format="%.2f")
                ny_oms_forra_aret = st.number_input("Omsättning förra året", value=bolag['oms_forra_aret'], format="%.2f")
                ny_oms_tillvaxt_aret = st.number_input("Omsättningstillväxt i år (%)", value=bolag['oms_tillvaxt_aret'], format="%.2f")
                ny_oms_tillvaxt_nastaar = st.number_input("Omsättningstillväxt nästa år (%)", value=bolag['oms_tillvaxt_nastaar'], format="%.2f")

                nya_p_e_values = []
                for i, p_e in enumerate(bolag['p_e_values'], 1):
                    nya_p_e_values.append(st.number_input(f"P/E {i}", value=p_e, format="%.2f"))

                nya_p_s_values = []
                for i, p_s in enumerate(bolag['p_s_values'], 1):
                    nya_p_s_values.append(st.number_input(f"P/S {i}", value=p_s, format="%.2f"))

                if st.button("Uppdatera bolag"):
                    bolag['nuvarande_kurs'] = ny_kurs
                    bolag['vinst_forra_aret'] = ny_vinst_forra_aret
                    bolag['vinst_aret'] = ny_vinst_aret
                    bolag['vinst_nastaar'] = ny_vinst_nastaar
                    bolag['oms_forra_aret'] = ny_oms_forra_aret
                    bolag['oms_tillvaxt_aret'] = ny_oms_tillvaxt_aret
                    bolag['oms_tillvaxt_nastaar'] = ny_oms_tillvaxt_nastaar
                    bolag['p_e_values'] = nya_p_e_values
                    bolag['p_s_values'] = nya_p_s_values
                    bolag['senast_andrad'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(st.session_state.data)
                    st.success(f"Bolag {valt_bolag} uppdaterat!")
    else:
        st.info("Inga bolag sparade än.")

if __name__ == "__main__":
    main()
