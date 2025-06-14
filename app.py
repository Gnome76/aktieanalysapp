import streamlit as st
import json
import os
from datetime import datetime

# Initiera refresh-flagg
if "refresh" not in st.session_state:
    st.session_state["refresh"] = False

# Om refresh är satt, "starta om" appen en gång
if st.session_state["refresh"]:
    st.session_state["refresh"] = False
    # Ingen experimental_rerun, vi stoppar här och låter appen ritas om
    st.stop()

# Filväg för datalagring
if os.path.exists("/mnt/data") and os.access("/mnt/data", os.W_OK):
    DATA_PATH = "/mnt/data/bolag.json"
else:
    DATA_PATH = "/tmp/bolag.json"

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    dir_path = os.path.dirname(DATA_PATH)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

# Ladda data vid start
if "data" not in st.session_state:
    st.session_state.data = load_data()

def add_or_update_bolag(namn, kurs, v_fj, v_i_a, v_n_a, o_fj, o_i_a_pct, o_n_a_pct,
                       p_e_nu, p_e_1, p_e_2, p_e_3, p_e_4,
                       p_s_nu, p_s_1, p_s_2, p_s_3, p_s_4):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.data[namn] = {
        "nuvarande_kurs": kurs,
        "vinst_fj": v_fj,
        "vinst_ia": v_i_a,
        "vinst_na": v_n_a,
        "omsattning_fj": o_fj,
        "omsattning_ia_pct": o_i_a_pct,
        "omsattning_na_pct": o_n_a_pct,
        "pe_nu": p_e_nu,
        "pe_1": p_e_1,
        "pe_2": p_e_2,
        "pe_3": p_e_3,
        "pe_4": p_e_4,
        "ps_nu": p_s_nu,
        "ps_1": p_s_1,
        "ps_2": p_s_2,
        "ps_3": p_s_3,
        "ps_4": p_s_4,
        "insatt_eller_andrad": now
    }
    save_data(st.session_state.data)
    st.success(f"Bolag '{namn}' har sparats/uppdaterats.")

st.title("Aktieanalysapp - Inmatning av bolag")

with st.form("bolag_form"):
    namn = st.text_input("Bolagsnamn")
    kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
    v_fj = st.number_input("Vinst förra året", format="%.2f")
    v_i_a = st.number_input("Förväntad vinst i år", format="%.2f")
    v_n_a = st.number_input("Förväntad vinst nästa år", format="%.2f")
    o_fj = st.number_input("Omsättning förra året", format="%.2f")
    o_i_a_pct = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
    o_n_a_pct = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
    p_e_nu = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
    p_e_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
    p_e_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
    p_e_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
    p_e_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")
    p_s_nu = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
    p_s_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
    p_s_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
    p_s_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
    p_s_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Spara bolag")
    if submitted:
        if namn.strip() == "":
            st.error("Ange ett bolagsnamn.")
        else:
            add_or_update_bolag(
                namn.strip(), kurs, v_fj, v_i_a, v_n_a, o_fj, o_i_a_pct, o_n_a_pct,
                p_e_nu, p_e_1, p_e_2, p_e_3, p_e_4,
                p_s_nu, p_s_1, p_s_2, p_s_3, p_s_4
            )
            st.session_state["refresh"] = True
            st.stop()

st.markdown("---")

val = st.selectbox("Välj bolag att visa/ändra", options=[""] + list(st.session_state.data.keys()))

if val:
    bolag = st.session_state.data[val]
    st.write(f"**Bolag:** {val}")
    for nyckel, varde in bolag.items():
        st.write(f"{nyckel}: {varde}")

    if st.button(f"Ta bort {val}"):
        del st.session_state.data[val]
        save_data(st.session_state.data)
        st.success(f"Bolag '{val}' borttaget.")
        st.session_state["refresh"] = True
        st.stop()
