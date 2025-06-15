import streamlit as st
from data_handler import load_data, save_data, delete_company
from forms import input_form, edit_form
from utils import (
    calculate_targetkurs_pe,
    calculate_targetkurs_ps,
    calculate_undervardering
)

st.set_page_config(page_title="Aktieanalys", layout="centered")

# Initiera databas
if "all_data" not in st.session_state:
    st.session_state["all_data"] = load_data()

if "selected_company" not in st.session_state:
    st.session_state["selected_company"] = None

if "show_only_undervalued" not in st.session_state:
    st.session_state["show_only_undervalued"] = False

st.header("📈 Lägg till nytt bolag")

nytt_bolag = input_form()
if nytt_bolag:
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f"{nytt_bolag['bolagsnamn']} tillagt.")
    st.rerun()

st.header("📊 Bolagsöversikt")

# Checkbox för att filtrera undervärderade bolag
st.session_state["show_only_undervalued"] = st.checkbox("Visa endast bolag med >30% rabatt", value=st.session_state["show_only_undervalued"])

data_to_show = []
for bolag in st.session_state["all_data"]:
    undervardering = calculate_undervardering(bolag)
    if not st.session_state["show_only_undervalued"] or undervardering >= 30:
        data_to_show.append((undervardering, bolag))

# Sortera efter högst undervärdering
data_to_show.sort(reverse=True, key=lambda x: x[0])

if not data_to_show:
    st.info("Inga bolag att visa.")
else:
    for idx, (undervardering, bolag) in enumerate(data_to_show):
        with st.expander(f"{bolag['bolagsnamn']} ({round(undervardering)}% rabatt)"):
            st.write(f"📉 Nuvarande kurs: {bolag.get('nuvarande_kurs', 0):.2f} kr")
            st.write(f"🎯 Targetkurs P/E: {calculate_targetkurs_pe(bolag):.2f} kr")
            st.write(f"🎯 Targetkurs P/S: {calculate_targetkurs_ps(bolag):.2f} kr")
            st.write(f"💸 Undervärdering: {undervardering:.2f}%")
            st.write(f"📍 Köpvärd vid: {(calculate_targetkurs_pe(bolag) * 0.7):.2f} kr (30% rabatt)")

            uppdaterat_bolag = edit_form(bolag)
            if uppdaterat_bolag:
                # Ersätt i listan
                for i, b in enumerate(st.session_state["all_data"]):
                    if b["bolagsnamn"] == bolag["bolagsnamn"]:
                        st.session_state["all_data"][i] = uppdaterat_bolag
                        break
                save_data(st.session_state["all_data"])
                st.success(f"{bolag['bolagsnamn']} uppdaterat.")
                st.rerun()

            if st.button(f"❌ Ta bort {bolag['bolagsnamn']}", key=f"delete_{idx}"):
                st.session_state["all_data"] = delete_company(st.session_state["all_data"], bolag["bolagsnamn"])
                st.success(f"{bolag['bolagsnamn']} borttaget.")
                st.rerun()
