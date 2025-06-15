import streamlit as st
from forms import input_form, edit_form
from utils import calculate_targetkurs_pe, calculate_targetkurs_ps, calculate_undervardering
from data_handler import load_data, save_data, delete_company

st.set_page_config(page_title="Aktieanalysapp", layout="wide")

# Initiera session state för data om det inte finns
if "all_data" not in st.session_state:
    st.session_state["all_data"] = load_data()  # Ladda data från JSON eller tom lista

st.header("Lägg till nytt bolag")

nytt_bolag = input_form()
if nytt_bolag:
    # Kontrollera om bolag redan finns (baserat på namn)
    existerande = next((b for b in st.session_state["all_data"] if b["bolagsnamn"].lower() == nytt_bolag["bolagsnamn"].lower()), None)
    if existerande:
        st.warning(f"Bolaget '{nytt_bolag['bolagsnamn']}' finns redan.")
    else:
        st.session_state["all_data"].append(nytt_bolag)
        save_data(st.session_state["all_data"])
        st.success(f"Bolaget '{nytt_bolag['bolagsnamn']}' tillagt.")

if st.session_state["all_data"]:
    st.header("Redigera befintligt bolag")

    bolagslista = [b["bolagsnamn"] for b in st.session_state["all_data"]]
    valt_bolag_namn = st.selectbox("Välj bolag att redigera", bolagslista)

    bolag = next(b for b in st.session_state["all_data"] if b["bolagsnamn"] == valt_bolag_namn)

    uppdaterat_bolag = edit_form(bolag)
    if uppdaterat_bolag:
        # Uppdatera bolaget i session_state
        index = st.session_state["all_data"].index(bolag)
        st.session_state["all_data"][index] = uppdaterat_bolag
        save_data(st.session_state["all_data"])
        st.success(f"Bolaget '{uppdaterat_bolag['bolagsnamn']}' uppdaterat.")

if st.session_state["all_data"]:
    st.header("Alla sparade bolag")
    for bolag in st.session_state["all_data"]:
        st.subheader(bolag["bolagsnamn"])
        kurs = bolag.get("nuvarande_kurs", 0.0)
        target_pe = calculate_targetkurs_pe(bolag)
        target_ps = calculate_targetkurs_ps(bolag)
        undervardering = calculate_undervardering(kurs, target_pe, target_ps)

        st.write(f"Nuvarande kurs: {kurs:.2f}")
        st.write(f"Targetkurs P/E: {target_pe:.2f}")
        st.write(f"Targetkurs P/S: {target_ps:.2f}")
        st.write(f"Undervärdering (%): {undervardering:.2f}")

        # Knapp för att ta bort bolaget
        if st.button(f"Ta bort {bolag['bolagsnamn']}"):
            st.session_state["all_data"] = delete_company(st.session_state["all_data"], bolag["bolagsnamn"])
            save_data(st.session_state["all_data"])
            st.experimental_rerun()
else:
    st.info("Inga bolag sparade ännu.")
