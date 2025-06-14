
import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calculate_targets(bolag):
    try:
        pe_values = [float(bolag.get(f"pe{i}", 0)) for i in range(1, 5)]
        ps_values = [float(bolag.get(f"ps{i}", 0)) for i in range(1, 5)]
        pe_avg = sum(pe_values) / len(pe_values)
        ps_avg = sum(ps_values) / len(ps_values)

        vinst_nasta_ar = float(bolag.get("vinst_nasta_ar", 0))
        oms_tillv_nasta_ar = float(bolag.get("oms_tillv_nasta_ar", 0))
        oms_tillv_i_ar = float(bolag.get("oms_tillv_i_ar", 0))
        nuvarande_kurs = float(bolag.get("kurs", 0))

        target_pe = vinst_nasta_ar * pe_avg
        target_ps = nuvarande_kurs * (1 + oms_tillv_nasta_ar / 100) * ps_avg / float(bolag.get("ps0", 1))

        undervarderad_pe = round((target_pe - nuvarande_kurs) / nuvarande_kurs * 100, 2)
        undervarderad_ps = round((target_ps - nuvarande_kurs) / nuvarande_kurs * 100, 2)

        return round(target_pe, 2), round(target_ps, 2), undervarderad_pe, undervarderad_ps
    except Exception:
        return 0, 0, 0, 0

def main():
    st.title("📊 Aktieanalysapp")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    data = st.session_state.data

    with st.form("add_form", clear_on_submit=True):
        st.subheader("➕ Lägg till / uppdatera bolag")
        bolagsnamn = st.text_input("Bolagsnamn")
        kurs = st.number_input("Nuvarande kurs", step=0.01)
        vinst_ifjol = st.number_input("Vinst förra året", step=0.01)
        vinst_iar = st.number_input("Förväntad vinst i år", step=0.01)
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", step=0.01)
        oms_ifjol = st.number_input("Omsättning förra året", step=0.01)
        oms_tillv_i_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", step=0.01)
        oms_tillv_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", step=0.01)
        pe0 = st.number_input("Nuvarande P/E", step=0.01)
        pe_values = [st.number_input(f"P/E {i}", step=0.01) for i in range(1, 5)]
        ps0 = st.number_input("Nuvarande P/S", step=0.01)
        ps_values = [st.number_input(f"P/S {i}", step=0.01) for i in range(1, 5)]

        submitted = st.form_submit_button("💾 Spara")
        if submitted and bolagsnamn:
            data[bolagsnamn] = {
                "kurs": kurs,
                "vinst_ifjol": vinst_ifjol,
                "vinst_iar": vinst_iar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "oms_ifjol": oms_ifjol,
                "oms_tillv_i_ar": oms_tillv_i_ar,
                "oms_tillv_nasta_ar": oms_tillv_nasta_ar,
                "pe0": pe0,
                "ps0": ps0,
                "senast_andrad": datetime.now().strftime("%Y-%m-%d"),
            }
            for i in range(4):
                data[bolagsnamn][f"pe{i+1}"] = pe_values[i]
                data[bolagsnamn][f"ps{i+1}"] = ps_values[i]

            save_data(data)
            st.success(f"{bolagsnamn} sparat.")
            st.session_state.data = data

    if not data:
        st.info("Inga bolag inlagda ännu.")
        return

    st.divider()
    visa_alla = st.checkbox("Visa alla bolag", value=True)

    berakningar = {}
    for namn, bolag in data.items():
        tp, ts, uv_pe, uv_ps = calculate_targets(bolag)
        bolag["target_pe"] = tp
        bolag["target_ps"] = ts
        bolag["undervärdering_pe"] = uv_pe
        bolag["undervärdering_ps"] = uv_ps
        berakningar[namn] = max(uv_pe, uv_ps)

    sorterade_bolag = sorted(data.keys(), key=lambda x: berakningar.get(x, 0), reverse=True)

    if "index" not in st.session_state:
        st.session_state.index = 0

    valda_bolag = sorterade_bolag if visa_alla else [
        namn for namn in sorterade_bolag if data[namn].get("undervärdering_pe", 0) > 30 or data[namn].get("undervärdering_ps", 0) > 30
    ]

    if not valda_bolag:
        st.warning("Inga bolag matchar kriterierna.")
        return

    idx = st.session_state.index % len(valda_bolag)
    valt_bolag = valda_bolag[idx]
    b = data[valt_bolag]

    st.subheader(f"📄 Detaljer för: {valt_bolag}")
    st.metric("Nuvarande kurs", b["kurs"])
    st.write(f"Target P/E: {b['target_pe']} kr ({b['undervärdering_pe']} % undervärderad)")
    st.write(f"Target P/S: {b['target_ps']} kr ({b['undervärdering_ps']} % undervärderad)")
    st.write(f"Senast ändrad: {b.get('senast_andrad', 'okänt')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Föregående"):
            st.session_state.index -= 1
    with col2:
        if st.button("➡️ Nästa"):
            st.session_state.index += 1

if __name__ == "__main__":
    main()
