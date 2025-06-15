import streamlit as st
from data_handler import load_data, save_data, delete_company
from forms import input_form, edit_form
from utils import calculate_targetkurs_pe, calculate_targetkurs_ps, calculate_undervardering

st.set_page_config(page_title="Aktieanalysapp", layout="wide")

if "all_data" not in st.session_state:
    st.session_state["all_data"] = load_data()

st.title("Aktieanalysapp - Översikt och analys")

st.header("Lägg till nytt bolag")

nytt_bolag = input_form()
if nytt_bolag is not None:
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' tillagt!")

st.header("Redigera bolag")

if st.session_state["all_data"]:
    bolag_namn_lista = [d["bolagsnamn"] for d in st.session_state["all_data"]]
    valt_bolag = st.selectbox("Välj bolag att redigera", bolag_namn_lista)

    if valt_bolag:
        index = bolag_namn_lista.index(valt_bolag)
        redigerat_bolag = edit_form(st.session_state["all_data"][index])
        if redigerat_bolag is not None:
            st.session_state["all_data"][index] = redigerat_bolag
            save_data(st.session_state["all_data"])
            st.success(f"Bolag '{valt_bolag}' uppdaterat!")
else:
    st.info("Inga bolag att redigera.")

st.header("Alla sparade bolag")

if st.session_state["all_data"]:
    for bolag in st.session_state["all_data"]:
        st.write(f"- **{bolag['bolagsnamn']}**")
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", [d["bolagsnamn"] for d in st.session_state["all_data"]])
    if st.button("Ta bort valt bolag"):
        delete_company(bolag_att_ta_bort, st.session_state["all_data"])
        save_data(st.session_state["all_data"])
        st.experimental_rerun()
else:
    st.info("Inga bolag sparade ännu.")

st.header("Undervärderade bolag")

visa_undervarderade_endast = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=True)

def sort_key(b):
    return max(
        calculate_undervardering(b, metod="pe"),
        calculate_undervardering(b, metod="ps")
    )

if st.session_state["all_data"]:
    if visa_undervarderade_endast:
        visa_data = [b for b in st.session_state["all_data"] if max(calculate_undervardering(b, metod="pe"), calculate_undervardering(b, metod="ps")) >= 30]
    else:
        visa_data = st.session_state["all_data"].copy()

    visa_data.sort(key=sort_key, reverse=True)

    for bolag in visa_data:
        target_pe = calculate_targetkurs_pe(bolag)
        target_ps = calculate_targetkurs_ps(bolag)
        undervardering_pe = calculate_undervardering(bolag, metod="pe")
        undervardering_ps = calculate_undervardering(bolag, metod="ps")

        st.subheader(bolag["bolagsnamn"])
        st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} kr")
        st.write(f"Targetkurs P/E: {target_pe:.2f} kr")
        st.write(f"Targetkurs P/S: {target_ps:.2f} kr")
        st.write(f"Undervärdering P/E: {undervardering_pe:.1f} %")
        st.write(f"Undervärdering P/S: {undervardering_ps:.1f} %")
        st.write("---")
else:
    st.info("Inga bolag att visa.")
