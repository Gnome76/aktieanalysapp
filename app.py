import streamlit as st
from utils import (
    calculate_targetkurs_pe,
    calculate_targetkurs_ps,
    calculate_undervardering
)
from data_handler import load_data, save_data, delete_company
from forms import input_form, edit_form
import datetime

st.set_page_config(page_title="Aktieanalys", page_icon="📈", layout="centered")

if "refresh" not in st.session_state:
    st.session_state["refresh"] = False

# Ladda data
all_data = load_data()

st.title("Aktieanalysapp")

if st.session_state["refresh"]:
    st.session_state["refresh"] = False
    st.experimental_rerun()

st.header("Lägg till nytt bolag")

nytt_bolag = input_form()
if nytt_bolag:
    nytt_bolag["insatt_datum"] = datetime.datetime.now().isoformat()
    all_data.append(nytt_bolag)
    save_data(all_data)
    st.success(f"{nytt_bolag['bolagsnamn']} har lagts till.")
    st.session_state["refresh"] = True
    st.stop()

st.header("Redigera eller ta bort bolag")

bolag_namn_lista = [bolag["bolagsnamn"] for bolag in all_data]

val = st.selectbox("Välj bolag att redigera eller ta bort", bolag_namn_lista)

if val:
    bolag_att_redigera = next((b for b in all_data if b["bolagsnamn"] == val), None)
    if bolag_att_redigera:
        uppdaterad_data = edit_form(bolag_att_redigera)
        if uppdaterad_data:
            uppdaterad_data["insatt_datum"] = datetime.datetime.now().isoformat()
            # Uppdatera bolag i all_data
            for i, b in enumerate(all_data):
                if b["bolagsnamn"] == val:
                    all_data[i] = uppdaterad_data
                    break
            save_data(all_data)
            st.success(f"{val} uppdaterades.")
            st.session_state["refresh"] = True
            st.stop()

        if st.button(f"Ta bort {val}"):
            delete_company(all_data, val)
            save_data(all_data)
            st.success(f"{val} togs bort.")
            st.session_state["refresh"] = True
            st.stop()
