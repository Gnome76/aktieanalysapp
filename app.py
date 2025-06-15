import streamlit as st
from data_handler import load_data, save_data, delete_company
from forms import input_form, edit_form
from utils import (
    calculate_targetkurs_pe,
    calculate_targetkurs_ps,
    calculate_undervardering,
)

st.set_page_config(page_title="Aktieanalys", layout="wide")

if "all_data" not in st.session_state:
    st.session_state["all_data"] = load_data()

st.header("📈 Lägg till nytt bolag")
with st.expander("➕ Lägg till bolag"):
    nytt_bolag = input_form()
    if nytt_bolag:
        st.session_state["all_data"].append(nytt_bolag)
        save_data(st.session_state["all_data"])
        st.success("Bolag tillagt!")

st.header("📊 Översikt")
if st.session_state["all_data"]:
    visa_alla = st.checkbox("Visa alla bolag", value=True)
    bolag_att_visa = []

    for bolag in st.session_state["all_data"]:
        undervardering = calculate_undervardering(bolag)
        bolag["undervardering"] = undervardering
        if visa_alla or undervardering >= 30:
            bolag_att_visa.append(bolag)

    bolag_att_visa.sort(key=lambda x: x["undervardering"], reverse=True)

    if bolag_att_visa:
        index = st.number_input(
            "Bläddra bland bolag", min_value=0, max_value=len(bolag_att_visa) - 1, step=1
        )
        bolag = bolag_att_visa[index]

        st.subheader(f"📌 {bolag['bolagsnamn']}")
        st.write(f"💵 Nuvarande kurs: {bolag['nuvarande_kurs']} kr")
        st.write(f"🎯 Targetkurs P/E i år: {calculate_targetkurs_pe(bolag, nästa=False):.2f} kr")
        st.write(f"🎯 Targetkurs P/E nästa år: {calculate_targetkurs_pe(bolag, nästa=True):.2f} kr")
        st.write(f"🎯 Targetkurs P/S i år: {calculate_targetkurs_ps(bolag, nästa=False):.2f} kr")
        st.write(f"🎯 Targetkurs P/S nästa år: {calculate_targetkurs_ps(bolag, nästa=True):.2f} kr")
        st.write(f"📉 Undervärdering: {bolag['undervardering']} %")
        st.write("✅ Köpvärd vid minst 30% rabatt")

        # Redigera
        st.markdown("---")
        st.subheader("✏️ Redigera bolag")
        uppdaterat_bolag = edit_form(bolag)
        if uppdaterat_bolag:
            st.session_state["all_data"][index] = uppdaterat_bolag
            save_data(st.session_state["all_data"])
            st.success("Bolaget har uppdaterats.")

        # Ta bort
        if st.button("🗑️ Ta bort bolag"):
            st.session_state["all_data"] = delete_company(st.session_state["all_data"], bolag["bolagsnamn"])
            save_data(st.session_state["all_data"])
            st.experimental_rerun()
    else:
        st.info("Inga bolag matchar filtret.")
else:
    st.warning("Inga bolag har lagts till ännu.")
