import streamlit as st
from data_handler import load_data, save_data, delete_company
from forms import input_form, edit_form
from utils import calculate_targetkurs_pe, calculate_targetkurs_ps, calculate_undervardering

st.set_page_config(page_title="Aktieanalysapp", layout="wide")

# Initiera all_data i session_state som en lista — alltid!
if "all_data" not in st.session_state or not isinstance(st.session_state["all_data"], list):
    data = load_data()
    if not isinstance(data, list):
        data = []
    st.session_state["all_data"] = data

st.title("Aktieanalysapp - Översikt och analys")

# Visa formulär för att lägga till nytt bolag
nytt_bolag = input_form()
if nytt_bolag is not None:
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' tillagt!")

# Om inga bolag finns, visa meddelande och stoppa
if not st.session_state["all_data"]:
    st.info("Inga bolag sparade ännu.")
    st.stop()

# Välj bolag att redigera
bolagsnamn_lista = [bolag["bolagsnamn"] for bolag in st.session_state["all_data"]]
valt_bolag = st.selectbox("Välj bolag att redigera", bolagsnamn_lista)

if valt_bolag:
    # Hitta bolaget i listan
    bolag_data = next((b for b in st.session_state["all_data"] if b["bolagsnamn"] == valt_bolag), None)
    if bolag_data:
        uppdaterat_bolag = edit_form(bolag_data)
        if uppdaterat_bolag is not None:
            # Uppdatera listan i session_state
            index = st.session_state["all_data"].index(bolag_data)
            st.session_state["all_data"][index] = uppdaterat_bolag
            save_data(st.session_state["all_data"])
            st.success(f"Bolag '{valt_bolag}' uppdaterat!")

st.header("Sparade bolag och analys")

# Sortera bolag baserat på undervärdering (exempel)
visa_data = st.session_state["all_data"].copy()
visa_data.sort(key=calculate_undervardering, reverse=True)

for bolag in visa_data:
    st.subheader(bolag["bolagsnamn"])
    target_pe = calculate_targetkurs_pe(bolag)
    target_ps = calculate_targetkurs_ps(bolag)
    underv = calculate_undervardering(bolag)
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']}")
    st.write(f"Targetkurs P/E: {target_pe:.2f}")
    st.write(f"Targetkurs P/S: {target_ps:.2f}")
    st.write(f"Undervärdering: {underv:.2f}%")

    if st.button(f"Ta bort {bolag['bolagsnamn']}"):
        st.session_state["all_data"] = delete_company(st.session_state["all_data"], bolag["bolagsnamn"])
        st.experimental_rerun()
