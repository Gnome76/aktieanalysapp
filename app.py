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

if st.session_state["selected_company"]:
    bolag = next((b for b in st.session_state["all_data"] if b["bolagsnamn"] == st.session_state["selected_company"]), None)
    if bolag:
        st.subheader(f"Data för {bolag['bolagsnamn']}")

        st.write(f"🎯 Targetkurs P/E i år: {calculate_targetkurs_pe(bolag, nästa=False):.2f} kr")
        st.write(f"🎯 Targetkurs P/E nästa år: {calculate_targetkurs_pe(bolag, nästa=True):.2f} kr")
        st.write(f"🎯 Targetkurs P/S i år: {calculate_targetkurs_ps(bolag, nästa=False):.2f} kr")
        st.write(f"🎯 Targetkurs P/S nästa år: {calculate_targetkurs_ps(bolag, nästa=True):.2f} kr")

        undervardering = calculate_undervardering(bolag)
        st.write(f"📉 Undervärdering: {undervardering:.2f} %")

        rabatt_30 = calculate_targetkurs_pe(bolag) * 0.7
        st.write(f"💡 Köpvärd vid 30% rabatt: {rabatt_30:.2f} kr")
