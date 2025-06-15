import streamlit as st
from forms import input_form, edit_form
from utils import calculate_targetkurs_pe, calculate_targetkurs_ps, calculate_undervardering
from data_handler import load_data, save_data, delete_company

st.set_page_config(page_title="Aktieanalys", layout="wide")

# Ladda data vid start
all_data = load_data()

# Initiera session_state
if "all_data" not in st.session_state:
    st.session_state["all_data"] = all_data

if "selected_index" not in st.session_state:
    st.session_state["selected_index"] = 0

st.header("Lägg till nytt bolag")

nytt_bolag = input_form()
if nytt_bolag is not None:
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' tillagt!")

st.header("Redigera befintligt bolag")

if len(st.session_state["all_data"]) > 0:
    bolagsnamn_list = [bolag["bolagsnamn"] for bolag in st.session_state["all_data"]]
    vald = st.selectbox("Välj bolag att redigera", bolagsnamn_list, index=st.session_state["selected_index"])
    st.session_state["selected_index"] = bolagsnamn_list.index(vald)

    uppdaterat_bolag = edit_form(st.session_state["all_data"][st.session_state["selected_index"]])
    if uppdaterat_bolag is not None:
        st.session_state["all_data"][st.session_state["selected_index"]] = uppdaterat_bolag
        save_data(st.session_state["all_data"])
        st.success(f"Bolag '{uppdaterat_bolag['bolagsnamn']}' uppdaterat!")
else:
    st.info("Inga bolag att redigera ännu.")

st.header("Översikt av bolag")

if len(st.session_state["all_data"]) > 0:
    visa_data = st.session_state["all_data"].copy()

    # Beräkna targetkurser och undervärdering för varje bolag
    for bolag in visa_data:
        bolag["targetkurs_pe"] = calculate_targetkurs_pe(bolag)
        bolag["targetkurs_ps"] = calculate_targetkurs_ps(bolag)
        bolag["undervardering"] = calculate_undervardering(bolag)

    # Sortera efter mest undervärderade
    visa_data.sort(key=lambda b: b["undervardering"], reverse=True)

    visa_endast_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering")
    if visa_endast_undervarderade:
        visa_data = [b for b in visa_data if b["undervardering"] >= 30]

    import pandas as pd

    df = pd.DataFrame(visa_data)
    if not df.empty:
        df_display = df[[
            "bolagsnamn", "kurs", "targetkurs_pe", "targetkurs_ps", "undervardering"
        ]]
        st.dataframe(df_display)

        ta_bort = st.selectbox("Välj bolag att ta bort", df["bolagsnamn"].tolist(), key="ta_bort_select")
        if st.button("Ta bort valt bolag"):
            idx = next((i for i, b in enumerate(st.session_state["all_data"]) if b["bolagsnamn"] == ta_bort), None)
            if idx is not None:
                delete_company(idx, st.session_state["all_data"])
                save_data(st.session_state["all_data"])
                st.success(f"Bolag '{ta_bort}' borttaget.")
                st.experimental_rerun()
else:
    st.info("Inga bolag tillagda ännu.")

st.markdown("---")
st.markdown("© 2025 Din Aktieanalysapp — byggd med Streamlit")
