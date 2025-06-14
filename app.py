import streamlit as st
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Aktieanalys", layout="wide")

DATA_PATH = Path("data.json")

def load_data():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def calculate_target_pe(vinst, pe_list):
    try:
        pe_avg = sum(pe_list) / len(pe_list)
        return round(vinst * pe_avg, 2)
    except:
        return None

def calculate_target_ps(kurs, oms_tillv, ps_list):
    try:
        ps_avg = sum(ps_list) / len(ps_list)
        tillv_faktor = 1 + oms_tillv / 100
        return round(kurs * tillv_faktor * ps_avg, 2)
    except:
        return None

def main():
    st.title("📈 Aktieanalysapp")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    data = st.session_state.data

    # Nytt eller befintligt bolag
    bolagsnamn_lista = list(data.keys())
    valt_bolag = st.selectbox("Välj bolag att visa eller redigera", [""] + bolagsnamn_lista)

    if valt_bolag:
        bolag = data[valt_bolag]

        st.subheader(f"🔍 Nuvarande kurs för {valt_bolag}: {bolag['nuvarande_kurs']} kr")

        with st.expander("Redigera bolagsdata"):
            kurs = st.number_input("Nuvarande kurs", value=bolag["nuvarande_kurs"])
            vinst_ifjol = st.number_input("Vinst förra året", value=bolag["vinst_ifjol"])
            vinst_iar = st.number_input("Förväntad vinst i år", value=bolag["vinst_iar"])
            vinst_next = st.number_input("Förväntad vinst nästa år", value=bolag["vinst_next"])
            oms_ifjol = st.number_input("Omsättning förra året", value=bolag["oms_ifjol"])
            oms_tillv_iar = st.number_input("Omsättningstillväxt i år (%)", value=bolag["oms_tillv_iar"])
            oms_tillv_next = st.number_input("Omsättningstillväxt nästa år (%)", value=bolag["oms_tillv_next"])

            pe_nu = st.number_input("Nuvarande P/E", value=bolag["pe_nu"])
            pe_1 = st.number_input("P/E 1", value=bolag["pe_1"])
            pe_2 = st.number_input("P/E 2", value=bolag["pe_2"])
            pe_3 = st.number_input("P/E 3", value=bolag["pe_3"])
            pe_4 = st.number_input("P/E 4", value=bolag["pe_4"])

            ps_nu = st.number_input("Nuvarande P/S", value=bolag["ps_nu"])
            ps_1 = st.number_input("P/S 1", value=bolag["ps_1"])
            ps_2 = st.number_input("P/S 2", value=bolag["ps_2"])
            ps_3 = st.number_input("P/S 3", value=bolag["ps_3"])
            ps_4 = st.number_input("P/S 4", value=bolag["ps_4"])

            if st.button("✅ Uppdatera bolag"):
                data[valt_bolag] = {
                    "nuvarande_kurs": kurs,
                    "vinst_ifjol": vinst_ifjol,
                    "vinst_iar": vinst_iar,
                    "vinst_next": vinst_next,
                    "oms_ifjol": oms_ifjol,
                    "oms_tillv_iar": oms_tillv_iar,
                    "oms_tillv_next": oms_tillv_next,
                    "pe_nu": pe_nu,
                    "pe_1": pe_1,
                    "pe_2": pe_2,
                    "pe_3": pe_3,
                    "pe_4": pe_4,
                    "ps_nu": ps_nu,
                    "ps_1": ps_1,
                    "ps_2": ps_2,
                    "ps_3": ps_3,
                    "ps_4": ps_4,
                    "senast_andrad": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_data(data)
                st.success("Bolaget har uppdaterats.")

    st.markdown("---")
    st.subheader("➕ Lägg till nytt bolag")

    with st.form("add_bolag"):
        nytt_namn = st.text_input("Bolagsnamn")
        ny_kurs = st.number_input("Nuvarande kurs", value=0.0)
        ny_vinst_ifjol = st.number_input("Vinst förra året", value=0.0)
        ny_vinst_iar = st.number_input("Förväntad vinst i år", value=0.0)
        ny_vinst_next = st.number_input("Förväntad vinst nästa år", value=0.0)
        ny_oms_ifjol = st.number_input("Omsättning förra året", value=0.0)
        ny_oms_tillv_iar = st.number_input("Omsättningstillväxt i år (%)", value=0.0)
        ny_oms_tillv_next = st.number_input("Omsättningstillväxt nästa år (%)", value=0.0)

        ny_pe_nu = st.number_input("Nuvarande P/E", value=0.0)
        ny_pe_1 = st.number_input("P/E 1", value=0.0)
        ny_pe_2 = st.number_input("P/E 2", value=0.0)
        ny_pe_3 = st.number_input("P/E 3", value=0.0)
        ny_pe_4 = st.number_input("P/E 4", value=0.0)

        ny_ps_nu = st.number_input("Nuvarande P/S", value=0.0)
        ny_ps_1 = st.number_input("P/S 1", value=0.0)
        ny_ps_2 = st.number_input("P/S 2", value=0.0)
        ny_ps_3 = st.number_input("P/S 3", value=0.0)
        ny_ps_4 = st.number_input("P/S 4", value=0.0)

        submit = st.form_submit_button("💾 Spara nytt bolag")

        if submit and nytt_namn:
            data[nytt_namn] = {
                "nuvarande_kurs": ny_kurs,
                "vinst_ifjol": ny_vinst_ifjol,
                "vinst_iar": ny_vinst_iar,
                "vinst_next": ny_vinst_next,
                "oms_ifjol": ny_oms_ifjol,
                "oms_tillv_iar": ny_oms_tillv_iar,
                "oms_tillv_next": ny_oms_tillv_next,
                "pe_nu": ny_pe_nu,
                "pe_1": ny_pe_1,
                "pe_2": ny_pe_2,
                "pe_3": ny_pe_3,
                "pe_4": ny_pe_4,
                "ps_nu": ny_ps_nu,
                "ps_1": ny_ps_1,
                "ps_2": ny_ps_2,
                "ps_3": ny_ps_3,
                "ps_4": ny_ps_4,
                "senast_andrad": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            save_data(data)
            st.success("Nytt bolag sparat!")

if __name__ == "__main__":
    main()
