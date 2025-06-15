import streamlit as st
from utils import (
    calculate_targetkurs_pe,
    calculate_targetkurs_ps,
    calculate_undervardering,
)
from forms import input_form, edit_form
from data_handler import load_data, save_data, delete_company

# Initiera session state
if "all_data" not in st.session_state:
    st.session_state["all_data"] = load_data()
if "selected_company" not in st.session_state:
    st.session_state["selected_company"] = None

# Nyckel för undervärderade bolag som vi bläddrar bland
if "undervarderade_list" not in st.session_state:
    st.session_state["undervarderade_list"] = []

# Index för bläddring
if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0

st.header("Lägg till nytt bolag")
nytt_bolag = input_form()
if nytt_bolag:
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f"Bolaget '{nytt_bolag['bolagsnamn']}' har lagts till.")

if st.session_state["all_data"]:
    bolagsnamn_list = [b["bolagsnamn"] for b in st.session_state["all_data"]]
    vald = st.selectbox("Välj bolag att redigera eller ta bort", bolagsnamn_list)
    st.session_state["selected_company"] = vald

    bolag = next((b for b in st.session_state["all_data"] if b["bolagsnamn"] == vald), None)
    if bolag:
        redigerat_bolag = edit_form(bolag)
        if redigerat_bolag:
            idx = bolagsnamn_list.index(vald)
            st.session_state["all_data"][idx] = redigerat_bolag
            save_data(st.session_state["all_data"])
            st.success(f"Bolaget '{vald}' har uppdaterats.")

        if st.button("Ta bort bolag"):
            st.session_state["all_data"] = delete_company(st.session_state["all_data"], vald)
            save_data(st.session_state["all_data"])
            st.success(f"Bolaget '{vald}' har tagits bort.")
            st.session_state["selected_company"] = None
else:
    st.info("Inga bolag sparade än.")

# Funktion för att uppdatera listan med undervärderade bolag, sorterade mest undervärderade först
def update_undervarderade():
    undervarderade = []
    for bolag in st.session_state["all_data"]:
        undervardering = calculate_undervardering(bolag)
        if undervardering > 0:  # Endast undervärderade bolag
            # Lägg till undervärdering som nyckel för enklare sortering
            bolag["undervardering_pct"] = undervardering
            undervarderade.append(bolag)
    # Sortera i fallande ordning (mest undervärderad först)
    undervarderade.sort(key=lambda x: x["undervardering_pct"], reverse=True)
    st.session_state["undervarderade_list"] = undervarderade
    st.session_state["current_index"] = 0  # Återställ index

if st.button("Uppdatera lista med undervärderade bolag"):
    update_undervarderade()

if st.session_state["undervarderade_list"]:
    bolag = st.session_state["undervarderade_list"][st.session_state["current_index"]]

    st.subheader(f"Undervärderat bolag #{st.session_state['current_index'] + 1} av {len(st.session_state['undervarderade_list'])}")
    st.write(f"**Bolagsnamn:** {bolag['bolagsnamn']}")
    st.write(f"🎯 Targetkurs P/E i år: {calculate_targetkurs_pe(bolag, nästa=False):.2f} kr")
    st.write(f"🎯 Targetkurs P/E nästa år: {calculate_targetkurs_pe(bolag, nästa=True):.2f} kr")
    st.write(f"🎯 Targetkurs P/S i år: {calculate_targetkurs_ps(bolag, nästa=False):.2f} kr")
    st.write(f"🎯 Targetkurs P/S nästa år: {calculate_targetkurs_ps(bolag, nästa=True):.2f} kr")
    st.write(f"📉 Undervärdering: {bolag['undervardering_pct']:.2f} %")
    rabatt_30 = calculate_targetkurs_pe(bolag) * 0.7
    st.write(f"💡 Köpvärd vid 30% rabatt: {rabatt_30:.2f} kr")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Föregående"):
            if st.session_state["current_index"] > 0:
                st.session_state["current_index"] -= 1
    with col2:
        if st.button("➡️ Nästa"):
            if st.session_state["current_index"] < len(st.session_state["undervarderade_list"]) - 1:
                st.session_state["current_index"] += 1
else:
    st.info("Inga undervärderade bolag i listan. Klicka på 'Uppdatera lista med undervärderade bolag' för att söka.")
