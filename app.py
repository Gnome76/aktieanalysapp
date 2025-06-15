import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATAFIL = "aktier_data.json"

# Funktion för att ladda data från JSON-fil
def ladda_data(filnamn=DATAFIL):
    if not os.path.exists(filnamn):
        return []
    try:
        with open(filnamn, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Fel vid inläsning av data: {e}")
        return []

# Funktion för att spara data till JSON-fil
def spara_data(data, filnamn=DATAFIL):
    try:
        with open(filnamn, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Fel vid sparande av data: {e}")

# Beräkna targetkurs baserat på P/E
def berakna_targetkurs_pe(vinst_nastaar, pe1, pe2):
    if vinst_nastaar is None or pe1 is None or pe2 is None:
        return None
    return vinst_nastaar * ((pe1 + pe2) / 2)

# Beräkna targetkurs baserat på P/S
def berakna_targetkurs_ps(ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
    if None in (ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
        return None
    oms_tillv_genomsnitt = (oms_tillv_1 + oms_tillv_2) / 2 / 100  # procent till decimal
    target_ps = ((ps1 + ps2) / 2) * (1 + oms_tillv_genomsnitt) * nuv_kurs
    return target_ps

# Beräkna undervärdering i procent
def berakna_undervardering(nuv_kurs, target_kurs):
    if nuv_kurs is None or target_kurs is None or target_kurs == 0:
        return None
    return (target_kurs - nuv_kurs) / target_kurs * 100

# Hitta bolag i listan efter namn
def hitta_bolag(data, bolagsnamn):
    for bolag in data:
        if bolag.get("bolagsnamn") == bolagsnamn:
            return bolag
    return None

# Ta bort bolag från listan
def ta_bort_bolag(data, bolagsnamn):
    ny_data = [bolag for bolag in data if bolag.get("bolagsnamn") != bolagsnamn]
    return ny_data

import json
import os

DATAFIL = "aktier_data.json"

# Ladda data från JSON-fil
def ladda_data(filnamn=DATAFIL):
    if not os.path.exists(filnamn):
        return []
    try:
        with open(filnamn, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Fel vid inläsning av data: {e}")
        return []

# Spara data till JSON-fil
def spara_data(data, filnamn=DATAFIL):
    try:
        with open(filnamn, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Fel vid sparande av data: {e}")

# Beräkna targetkurs baserat på P/E
def berakna_targetkurs_pe(vinst_nastaar, pe1, pe2):
    if vinst_nastaar is None or pe1 is None or pe2 is None:
        return None
    return vinst_nastaar * ((pe1 + pe2) / 2)

# Beräkna targetkurs baserat på P/S och omsättningstillväxt
def berakna_targetkurs_ps(ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
    if None in (ps1, ps2, oms_tillv_1, oms_tillv_2, nuv_kurs):
        return None
    oms_tillv_genomsnitt = (oms_tillv_1 + oms_tillv_2) / 2 / 100  # från procent till decimal
    target_ps = ((ps1 + ps2) / 2) * (1 + oms_tillv_genomsnitt) * nuv_kurs
    return target_ps

# Beräkna undervärdering i procent jämfört med targetkurs
def berakna_undervardering(nuv_kurs, target_kurs):
    if nuv_kurs is None or target_kurs is None or target_kurs == 0:
        return None
    return (target_kurs - nuv_kurs) / target_kurs * 100

import streamlit as st
import pandas as pd

def visa_oversikt(data):
    if not data:
        st.info("Inga bolag finns att visa.")
        return

    # Omvandla listan av dicts till DataFrame
    df = pd.DataFrame(data)

    # Beräkna targetkurser och undervärdering för varje bolag
    df["target_pe"] = df.apply(lambda row: berakna_targetkurs_pe(
        row.get("vinst_nasta_ar"),
        row.get("pe_1"),
        row.get("pe_2")), axis=1)

    df["target_ps"] = df.apply(lambda row: berakna_targetkurs_ps(
        row.get("ps_1"),
        row.get("ps_2"),
        row.get("omsattningstillvaxt_ar_1_pct"),
        row.get("omsattningstillvaxt_ar_2_pct"),
        row.get("nuvarande_kurs")), axis=1)

    df["undervardering_pe"] = df.apply(lambda row: berakna_undervardering(
        row.get("nuvarande_kurs"),
        row.get("target_pe")), axis=1)

    df["undervardering_ps"] = df.apply(lambda row: berakna_undervardering(
        row.get("nuvarande_kurs"),
        row.get("target_ps")), axis=1)

    # Ta högsta undervärderingen mellan P/E och P/S
    df["undervardering_max"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    # Checkbox för att visa endast undervärderade bolag med minst 30% rabatt
    visa_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", key="filter_undervarderade")

    if visa_undervarderade:
        df = df[df["undervardering_max"] >= 30]

    # Sortera efter högsta undervärdering
    df = df.sort_values(by="undervardering_max", ascending=False)

    # Visa relevant kolumner i tabellen
    kolumner = [
        "bolagsnamn", "nuvarande_kurs",
        "target_pe", "target_ps",
        "undervardering_pe", "undervardering_ps", "undervardering_max",
        "vinst_nasta_ar", "pe_1", "pe_2",
        "ps_1", "ps_2",
        "omsattningstillvaxt_ar_1_pct", "omsattningstillvaxt_ar_2_pct"
    ]

    st.dataframe(df[kolumner].round(2), use_container_width=True)

import streamlit as st
from datetime import datetime

def input_form():
    with st.form(key="form_nytt_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 (%)", format="%.2f")
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 (%)", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submit_button = st.form_submit_button(label="Lägg till bolag")

    if submit_button and bolagsnamn.strip():
        nytt_bolag = {
            "bolagsnamn": bolagsnamn.strip(),
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_forra_aret": omsattning_forra_aret,
            "omsattningstillvaxt_ar_1_pct": omsattningstillvaxt_ar_1_pct,
            "omsattningstillvaxt_ar_2_pct": omsattningstillvaxt_ar_2_pct,
            "nuvarande_pe": nuvarande_pe,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "pe_3": pe_3,
            "pe_4": pe_4,
            "nuvarande_ps": nuvarande_ps,
            "ps_1": ps_1,
            "ps_2": ps_2,
            "ps_3": ps_3,
            "ps_4": ps_4,
            "insatt_datum": datetime.now().isoformat(),
            "senast_andrad": datetime.now().isoformat()
        }
        return nytt_bolag
    return None

def edit_form(bolag):
    with st.form(key=f"form_redigera_{bolag['bolagsnamn']}"):
        st.write(f"Redigera bolag: **{bolag['bolagsnamn']}**")

        # Visa nuvarande kurs men gör den inte redigerbar
        nuvarande_kurs = st.number_input("Nuvarande kurs", value=bolag.get("nuvarande_kurs", 0.0), format="%.2f", disabled=True)

        # Visa övriga fält som redigerbara
        vinst_forra_aret = st.number_input("Vinst förra året", value=bolag.get("vinst_forra_aret", 0.0), format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", value=bolag.get("vinst_i_ar", 0.0), format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", value=bolag.get("vinst_nasta_ar", 0.0), format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", value=bolag.get("omsattning_forra_aret", 0.0), format="%.2f")
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 (%)", value=bolag.get("omsattningstillvaxt_ar_1_pct", 0.0), format="%.2f")
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 (%)", value=bolag.get("omsattningstillvaxt_ar_2_pct", 0.0), format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", value=bolag.get("nuvarande_pe", 0.0), format="%.2f")
        pe_1 = st.number_input("P/E 1", value=bolag.get("pe_1", 0.0), format="%.2f")
        pe_2 = st.number_input("P/E 2", value=bolag.get("pe_2", 0.0), format="%.2f")
        pe_3 = st.number_input("P/E 3", value=bolag.get("pe_3", 0.0), format="%.2f")
        pe_4 = st.number_input("P/E 4", value=bolag.get("pe_4", 0.0), format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", value=bolag.get("nuvarande_ps", 0.0), format="%.2f")
        ps_1 = st.number_input("P/S 1", value=bolag.get("ps_1", 0.0), format="%.2f")
        ps_2 = st.number_input("P/S 2", value=bolag.get("ps_2", 0.0), format="%.2f")
        ps_3 = st.number_input("P/S 3", value=bolag.get("ps_3", 0.0), format="%.2f")
        ps_4 = st.number_input("P/S 4", value=bolag.get("ps_4", 0.0), format="%.2f")

        submit_button = st.form_submit_button(label="Uppdatera bolag")

    if submit_button:
        uppdaterat_bolag = {
            "bolagsnamn": bolag["bolagsnamn"],
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_forra_aret": omsattning_forra_aret,
            "omsattningstillvaxt_ar_1_pct": omsattningstillvaxt_ar_1_pct,
            "omsattningstillvaxt_ar_2_pct": omsattningstillvaxt_ar_2_pct,
            "nuvarande_pe": nuvarande_pe,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "pe_3": pe_3,
            "pe_4": pe_4,
            "nuvarande_ps": nuvarande_ps,
            "ps_1": ps_1,
            "ps_2": ps_2,
            "ps_3": ps_3,
            "ps_4": ps_4,
            "insatt_datum": bolag.get("insatt_datum"),
            "senast_andrad": datetime.now().isoformat()
        }
        return uppdaterat_bolag
    return None

import streamlit as st
from utils import load_data, save_data, calculate_targetkurs_pe, calculate_targetkurs_ps, calculate_undervardering
from forms import input_form, edit_form
from datetime import datetime

st.set_page_config(page_title="Aktieanalysapp", layout="wide")

# Ladda data
data = load_data()

# Initiera session_state variabler
if "valda_index" not in st.session_state:
    st.session_state.valda_index = 0

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "filter_undervarderade" not in st.session_state:
    st.session_state.filter_undervarderade = False

def visa_bolag_ett_i_taget(index, bolag_lista):
    bolag = bolag_lista[index]
    st.header(f"Bolag: {bolag['bolagsnamn']}")
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} kr")
    target_pe = calculate_targetkurs_pe(bolag)
    target_ps = calculate_targetkurs_ps(bolag)
    underv = calculate_undervardering(bolag)
    st.write(f"Targetkurs P/E: {target_pe:.2f} kr")
    st.write(f"Targetkurs P/S: {target_ps:.2f} kr")
    st.write(f"Undervärdering: {underv:.2f} %")
    st.write(f"Köpvärd vid 30% rabatt: {target_pe*0.7:.2f} kr (P/E), {target_ps*0.7:.2f} kr (P/S)")
    st.write(f"Insatt datum: {bolag.get('insatt_datum', 'Okänt')}")
    st.write(f"Senast ändrad: {bolag.get('senast_andrad', 'Okänt')}")

def filtrera_undervarderade(data_lista):
    resultat = []
    for bolag in data_lista:
        underv = calculate_undervardering(bolag)
        if underv >= 30:
            resultat.append(bolag)
    return resultat

st.title("Aktieanalysapp")

# Checkbox för filtrering undervärderade bolag
filter_checkbox = st.checkbox("Visa endast undervärderade (>30% rabatt)", value=st.session_state.filter_undervarderade)
st.session_state.filter_undervarderade = filter_checkbox

# Filtrera data om checkbox är ikryssad
visa_data = data
if st.session_state.filter_undervarderade:
    visa_data = filtrera_undervarderade(data)

# Sortera bolag efter undervärdering (högst först)
visa_data.sort(key=calculate_undervardering, reverse=True)

# Visa alla bolag i tabellform (översikt)
with st.expander("Visa alla bolag (översikt)"):
    import pandas as pd
    df = pd.DataFrame(visa_data)
    if not df.empty:
        # Visa viktiga kolumner
        kolumner = ["bolagsnamn", "nuvarande_kurs"]
        df_vis = df[kolumner].copy()
        st.dataframe(df_vis)
    else:
        st.write("Inga bolag att visa.")

# Visa ett bolag i taget
if visa_data:
    idx = st.session_state.valda_index
    if idx >= len(visa_data):
        idx = 0
        st.session_state.valda_index = 0

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("⬅ Föregående"):
            st.session_state.valda_index = max(0, st.session_state.valda_index - 1)
    with col3:
        if st.button("Nästa ➡"):
            st.session_state.valda_index = min(len(visa_data) - 1, st.session_state.valda_index + 1)

    visa_bolag_ett_i_taget(st.session_state.valda_index, visa_data)

    # Redigera bolag knapp
    if st.button("Redigera detta bolag"):
        st.session_state.edit_mode = True
        st.session_state.redigera_bolag_namn = visa_data[st.session_state.valda_index]["bolagsnamn"]

else:
    st.write("Inga bolag att visa.")

# Visa inputformulär för nytt bolag
st.markdown("---")
st.header("Lägg till nytt bolag")
nytt_bolag = input_form()
if nytt_bolag:
    # Kontrollera om bolaget redan finns
    finns = any(b["bolagsnamn"].lower() == nytt_bolag["bolagsnamn"].lower() for b in data)
    if finns:
        st.warning("Bolaget finns redan. Använd redigeringsfunktionen för att uppdatera.")
    else:
        data.append(nytt_bolag)
        save_data(data)
        st.success(f"Bolaget {nytt_bolag['bolagsnamn']} har lagts till.")
        st.experimental_rerun()

# Redigera bolag - visa form om edit_mode är aktiv
if st.session_state.get("edit_mode", False):
    bolagsnamn = st.session_state.get("redigera_bolag_namn", None)
    if bolagsnamn:
        bolag_att_redigera = next((b for b in data if b["bolagsnamn"] == bolagsnamn), None)
        if bolag_att_redigera:
            uppdaterat = edit_form(bolag_att_redigera)
            if uppdaterat:
                # Uppdatera i data
                index = next(i for i, b in enumerate(data) if b["bolagsnamn"] == bolagsnamn)
                data[index] = uppdaterat
                save_data(data)
                st.success(f"Bolaget {bolagsnamn} har uppdaterats.")
                st.session_state.edit_mode = False
                st.experimental_rerun()
        else:
            st.error("Bolag hittades inte.")
    else:
        st.error("Inget bolagsnamn valt för redigering.")
