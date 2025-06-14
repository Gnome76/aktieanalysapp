import streamlit as st
import json
import os
from datetime import datetime

DATA_PATH = "/tmp/data.json"

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {}

def calculate_targetkurs(bolag):
    try:
        pe_vals = [float(bolag.get(f"p/e {i}", 0)) for i in range(1,5)]
        pe_vals = [v for v in pe_vals if v > 0]
        pe_avg = sum(pe_vals)/len(pe_vals) if pe_vals else 0

        ps_vals = [float(bolag.get(f"p/s {i}", 0)) for i in range(1,5)]
        ps_vals = [v for v in ps_vals if v > 0]
        ps_avg = sum(ps_vals)/len(ps_vals) if ps_vals else 0

        vinst_nasta_aar = float(bolag.get("Förväntad vinst nästa år", 0))
        oms_tillv_aar = float(bolag.get("Förväntad Omsättningstillväxt i år %", 0)) / 100
        oms_nu = float(bolag.get("Omsättning förra året", 0))

        target_pe = pe_avg * vinst_nasta_aar if pe_avg and vinst_nasta_aar else 0
        oms_beraknad = oms_nu * (1 + oms_tillv_aar)
        target_ps = ps_avg * oms_beraknad if ps_avg and oms_beraknad else 0

        nuv_kurs = float(bolag.get("Nuvarande kurs", 0))
        undervar_pe = (target_pe - nuv_kurs) / nuv_kurs if nuv_kurs else 0
        undervar_ps = (target_ps - nuv_kurs) / nuv_kurs if nuv_kurs else 0
        max_undervar = max(undervar_pe, undervar_ps)

        return {
            "target_pe": target_pe,
            "target_ps": target_ps,
            "undervar_pe": undervar_pe,
            "undervar_ps": undervar_ps,
            "max_undervar": max_undervar
        }
    except Exception:
        return {
            "target_pe": 0,
            "target_ps": 0,
            "undervar_pe": 0,
            "undervar_ps": 0,
            "max_undervar": 0
        }

def main():
    st.title("Aktieanalysapp")

    if "data" not in st.session_state:
        st.session_state.data = load_data()
    if "refresh" not in st.session_state:
        st.session_state.refresh = False

    if st.session_state.refresh:
        st.session_state.refresh = False
        st.stop()

    def update_data():
        save_data(st.session_state.data)
        st.session_state.refresh = True
        st.stop()

    bolagslista = list(st.session_state.data.keys())
    valt_bolag = st.sidebar.selectbox("Välj bolag att redigera", ["--Nytt bolag--"] + bolagslista)

    if valt_bolag == "--Nytt bolag--":
        nytt = {}
        nytt["Bolagsnamn"] = st.text_input("Bolagsnamn")
        nytt["Nuvarande kurs"] = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        nytt["Vinst förra året"] = st.number_input("Vinst förra året", min_value=0.0, format="%.2f")
        nytt["Förväntad vinst i år"] = st.number_input("Förväntad vinst i år", min_value=0.0, format="%.2f")
        nytt["Förväntad vinst nästa år"] = st.number_input("Förväntad vinst nästa år", min_value=0.0, format="%.2f")
        nytt["Omsättning förra året"] = st.number_input("Omsättning förra året", min_value=0.0, format="%.2f")
        nytt["Förväntad Omsättningstillväxt i år %"] = st.number_input("Omsättningstillväxt i år %", min_value=0.0, max_value=100.0, format="%.2f")
        nytt["Förväntad Omsättningstillväxt nästa år %"] = st.number_input("Omsättningstillväxt nästa år %", min_value=0.0, max_value=100.0, format="%.2f")
        nytt["Nuvarande p/e"] = st.number_input("Nuvarande p/e", min_value=0.0, format="%.2f")
        for i in range(1,5):
            nytt[f"p/e {i}"] = st.number_input(f"P/E {i}", min_value=0.0, format="%.2f", key=f"pe{i}")
        nytt["Nuvarande p/s"] = st.number_input("Nuvarande p/s", min_value=0.0, format="%.2f")
        for i in range(1,5):
            nytt[f"p/s {i}"] = st.number_input(f"P/S {i}", min_value=0.0, format="%.2f", key=f"ps{i}")

        if st.button("Lägg till bolag"):
            if nytt["Bolagsnamn"].strip() == "":
                st.error("Bolagsnamn får inte vara tomt.")
            elif nytt["Bolagsnamn"] in st.session_state.data:
                st.error("Bolaget finns redan.")
            else:
                nytt["Datum"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.data[nytt["Bolagsnamn"]] = nytt
                update_data()
            else:
        bolag = st.session_state.data[valt_bolag]

        st.write(f"### Redigera bolag: {valt_bolag}")
        st.write(f"**Nuvarande kurs:** {bolag['Nuvarande kurs']:.2f} kr")

        visa_detaljer = st.checkbox("Visa detaljerade fält")

        if visa_detaljer:
            bolag["Vinst förra året"] = st.number_input("Vinst förra året", value=float(bolag.get("Vinst förra året", 0)), format="%.2f", key="vinst_fj")
            bolag["Förväntad vinst i år"] = st.number_input("Förväntad vinst i år", value=float(bolag.get("Förväntad vinst i år", 0)), format="%.2f", key="vinst_aar")
            bolag["Förväntad vinst nästa år"] = st.number_input("Förväntad vinst nästa år", value=float(bolag.get("Förväntad vinst nästa år", 0)), format="%.2f", key="vinst_nasta")
            bolag["Omsättning förra året"] = st.number_input("Omsättning förra året", value=float(bolag.get("Omsättning förra året", 0)), format="%.2f", key="oms_fj")
            bolag["Förväntad Omsättningstillväxt i år %"] = st.number_input("Omsättningstillväxt i år %", value=float(bolag.get("Förväntad Omsättningstillväxt i år %", 0)), min_value=0.0, max_value=100.0, format="%.2f", key="oms_tillv_aar")
            bolag["Förväntad Omsättningstillväxt nästa år %"] = st.number_input("Omsättningstillväxt nästa år %", value=float(bolag.get("Förväntad Omsättningstillväxt nästa år %", 0)), min_value=0.0, max_value=100.0, format="%.2f", key="oms_tillv_nasta")
            bolag["Nuvarande p/e"] = st.number_input("Nuvarande p/e", value=float(bolag.get("Nuvarande p/e", 0)), format="%.2f", key="pe_nuv")
            for i in range(1,5):
                bolag[f"p/e {i}"] = st.number_input(f"P/E {i}", value=float(bolag.get(f"p/e {i}", 0)), format="%.2f", key=f"pe_redig{i}")
            bolag["Nuvarande p/s"] = st.number_input("Nuvarande p/s", value=float(bolag.get("Nuvarande p/s", 0)), format="%.2f", key="ps_nuv")
            for i in range(1,5):
                bolag[f"p/s {i}"] = st.number_input(f"P/S {i}", value=float(bolag.get(f"p/s {i}", 0)), format="%.2f", key=f"ps_redig{i}")

        if st.button("Uppdatera bolag"):
            bolag["Datum"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.data[valt_bolag] = bolag
            update_data()

        if st.button("Ta bort bolag"):
            del st.session_state.data[valt_bolag]
            update_data()

    # Visa alla bolag i tabell med targetkurser och undervärdering
    all_data = []
    for namn, bolag in st.session_state.data.items():
        berakning = calculate_targetkurs(bolag)
        rad = bolag.copy()
        rad.update(berakning)
        all_data.append(rad)

    # Checkbox för att visa endast undervärderade (>30% undervärdering)
    endast_undervarde = st.checkbox("Visa endast bolag med minst 30% undervärdering")

    if endast_undervarde:
        all_data = [b for b in all_data if b["max_undervar"] >= 0.3]

    # Sortera på max undervärdering (fallande)
    all_data = sorted(all_data, key=lambda x: x["max_undervar"], reverse=True)

    if all_data:
        import pandas as pd
        df = pd.DataFrame(all_data)
        # Dölj vissa mindre intressanta kolumner
        kolumner_att_visa = ["Bolagsnamn", "Nuvarande kurs", "target_pe", "target_ps", "undervar_pe", "undervar_ps", "max_undervar"]
        df = df[kolumner_att_visa]
        df["Nuvarande kurs"] = df["Nuvarande kurs"].map("{:.2f}".format)
        df["target_pe"] = df["target_pe"].map("{:.2f}".format)
        df["target_ps"] = df["target_ps"].map("{:.2f}".format)
        df["undervar_pe"] = df["undervar_pe"].map("{:.2%}".format)
        df["undervar_ps"] = df["undervar_ps"].map("{:.2%}".format)
        df["max_undervar"] = df["max_undervar"].map("{:.2%}".format)

        st.write("## Översikt över bolag")
        st.dataframe(df)
    else:
        st.info("Inga bolag att visa med nuvarande filter.")

if __name__ == "__main__":
    main()        
