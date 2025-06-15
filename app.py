import streamlit as st
from forms import input_form, edit_form
from utils import (
    calculate_targetkurs_pe,
    calculate_targetkurs_ps,
    calculate_undervardering,
)
from data_handler import load_data, save_data, delete_company

st.set_page_config(page_title="Aktieanalysapp", layout="wide")

# Ladda data från fil eller initiera tom lista i session_state
if "all_data" not in st.session_state:
    st.session_state["all_data"] = load_data()

# Lägg till nytt bolag via inputformulär
nytt_bolag = input_form()
if nytt_bolag:
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f"Bolaget {nytt_bolag['bolagsnamn']} är tillagt!")

# Sortera bolag baserat på undervärdering (störst först)
visa_data = st.session_state["all_data"]
visa_data.sort(key=calculate_undervardering, reverse=True)

# Välj bolag att redigera
valda_bolag_namn = [bolag["bolagsnamn"] for bolag in visa_data]
valt_bolag = st.selectbox("Välj bolag att redigera", [""] + valda_bolag_namn)

if valt_bolag:
    bolag = next(b for b in visa_data if b["bolagsnamn"] == valt_bolag)
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']}")
    uppdaterat_bolag = edit_form(bolag)
    if uppdaterat_bolag:
        index = visa_data.index(bolag)
        st.session_state["all_data"][index] = uppdaterat_bolag
        save_data(st.session_state["all_data"])
        st.success(f"Bolaget {valt_bolag} är uppdaterat!")

st.subheader("Alla bolag")
st.table(visa_data)

ta_bort_bolag = st.selectbox("Välj bolag att ta bort", [""] + valda_bolag_namn, key="remove_selectbox")
if ta_bort_bolag:
    if st.button(f"Ta bort {ta_bort_bolag}"):
        st.session_state["all_data"] = delete_company(st.session_state["all_data"], ta_bort_bolag)
        save_data(st.session_state["all_data"])
        st.success(f"Bolaget {ta_bort_bolag} är borttaget!")
        st.experimental_rerun()
