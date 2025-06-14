import streamlit as st
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Aktieanalys", layout="wide")

DATA_PATH = Path("data/aktier.json")

def load_data():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

st.title("📊 Aktieanalysverktyg")
with st.form("add_form"):
    st.subheader("➕ Lägg till eller uppdatera bolag")
    namn = st.text_input("Bolagsnamn").strip()
    nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0)
    vinst_i_ar = st.number_input("Vinst i år")
    vinst_nasta_ar = st.number_input("Vinst nästa år")
    oms_vakst_i_ar = st.number_input("Omsättningstillväxt i år (%)")
    oms_vakst_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)")
    pe1 = st.number_input("P/E år 1")
    pe2 = st.number_input("P/E år 2")
    ps1 = st.number_input("P/S år 1")
    ps2 = st.number_input("P/S år 2")

    submitted = st.form_submit_button("💾 Spara")
    if submitted and namn:
        existing = next((b for b in st.session_state.data if b["bolagsnamn"] == namn), None)
        target_pe = vinst_nasta_ar * ((pe1 + pe2) / 2)
        tillv = ((oms_vakst_i_ar + oms_vakst_nasta_ar) / 2) / 100
        target_ps = (ps1 + ps2) / 2 * tillv * nuvarande_kurs

        nytt = {
            "bolagsnamn": namn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsättningstillväxt_i_ar": oms_vakst_i_ar,
            "omsättningstillväxt_nasta_ar": oms_vakst_nasta_ar,
            "pe1": pe1,
            "pe2": pe2,
            "ps1": ps1,
            "ps2": ps2,
            "target_pe": round(target_pe, 2),
            "target_ps": round(target_ps, 2),
            "senast_andrad": datetime.now().strftime("%Y-%m-%d")
        }

        if existing:
            st.session_state.data = [nytt if b["bolagsnamn"] == namn else b for b in st.session_state.data]
            st.success(f"{namn} uppdaterat!")
        else:
            st.session_state.data.append(nytt)
            st.success(f"{namn} tillagt!")

        save_data(st.session_state.data)
          # -------- Bolagsdetaljer och redigering --------
    st.subheader(f"📄 Detaljer för: {valda_bolag[bolagsindex]}")
    bolag = data[valda_bolag[bolagsindex]]
    st.markdown(f"**Nuvarande kurs:** {bolag['nuvarande_kurs']} kr")

    if st.checkbox("Visa/redigera alla nyckeltal"):
        with st.form(key="edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                vinst_forr = st.number_input("Vinst förra året", value=bolag["vinst_forr"], step=0.01)
                vinst_igar = st.number_input("Förväntad vinst i år", value=bolag["vinst_igar"], step=0.01)
                vinst_next = st.number_input("Förväntad vinst nästa år", value=bolag["vinst_next"], step=0.01)
                oms_forr = st.number_input("Omsättning förra året", value=bolag["oms_forr"], step=0.01)
                oms_tillv_igar = st.number_input("Tillväxt i år (%)", value=bolag["oms_tillv_igar"], step=0.1)
                oms_tillv_next = st.number_input("Tillväxt nästa år (%)", value=bolag["oms_tillv_next"], step=0.1)
            with col2:
                pe = [st.number_input(f"P/E {i+1}", value=bolag["pe"][i], step=0.1) for i in range(4)]
                ps = [st.number_input(f"P/S {i+1}", value=bolag["ps"][i], step=0.1) for i in range(4)]

            submitted = st.form_submit_button("Uppdatera")
            if submitted:
                bolag["vinst_forr"] = vinst_forr
                bolag["vinst_igar"] = vinst_igar
                bolag["vinst_next"] = vinst_next
                bolag["oms_forr"] = oms_forr
                bolag["oms_tillv_igar"] = oms_tillv_igar
                bolag["oms_tillv_next"] = oms_tillv_next
                bolag["pe"] = pe
                bolag["ps"] = ps
                bolag["senast_andrad"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_data(data)
                st.success("Bolaget har uppdaterats.")
    # -------- Navigering --------
    st.markdown("---")
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("⬅️ Föregående", use_container_width=True):
            st.session_state.index = (bolagsindex - 1) % len(valda_bolag)
    with col_next:
        if st.button("➡️ Nästa", use_container_width=True):
            st.session_state.index = (bolagsindex + 1) % len(valda_bolag)

# ----------------- Kör appen -----------------
if __name__ == "__main__":
    main()
