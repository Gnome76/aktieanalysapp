import streamlit as st
import json
import os
from datetime import datetime

DATA_PATH = "/app/data.json"  # Streamlit Cloud tillåter att skriva i /app-mappen

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def avg(values):
    valid = [v for v in values if isinstance(v, (int, float)) and v > 0]
    return sum(valid) / len(valid) if valid else 0

def calculate_targets(bolag):
    # Läs in värden från bolag (konvertera till rätt typ)
    try:
        vinst_i_år = float(bolag.get("förväntad_vinst_i_år", 0))
        vinst_nästa_år = float(bolag.get("förväntad_vinst_nästa_år", 0))
        omsättning_fj = float(bolag.get("omsättning_förra_året", 0))
        oms_tillv_i_år = float(bolag.get("förväntad_omsättningstillväxt_i_år", 0)) / 100
        oms_tillv_nästa_år = float(bolag.get("förväntad_omsättningstillväxt_nästa_år", 0)) / 100

        pe_values = [
            float(bolag.get("nuvarande_p_e", 0)),
            float(bolag.get("p_e_1", 0)),
            float(bolag.get("p_e_2", 0)),
            float(bolag.get("p_e_3", 0)),
            float(bolag.get("p_e_4", 0)),
        ]
        ps_values = [
            float(bolag.get("nuvarande_p_s", 0)),
            float(bolag.get("p_s_1", 0)),
            float(bolag.get("p_s_2", 0)),
            float(bolag.get("p_s_3", 0)),
            float(bolag.get("p_s_4", 0)),
        ]

        snitt_pe = avg(pe_values)
        snitt_ps = avg(ps_values)

        omsättning_i_år = omsättning_fj * (1 + oms_tillv_i_år)
        omsättning_nästa_år = omsättning_i_år * (1 + oms_tillv_nästa_år)

        target_pe_i_år = vinst_i_år * snitt_pe
        target_pe_nästa_år = vinst_nästa_år * snitt_pe
        target_ps_i_år = omsättning_i_år * snitt_ps
        target_ps_nästa_år = omsättning_nästa_år * snitt_ps

        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))

        undervärdering_pe_i_år = ((target_pe_i_år - nuvarande_kurs) / nuvarande_kurs * 100) if nuvarande_kurs else None
        undervärdering_pe_nästa_år = ((target_pe_nästa_år - nuvarande_kurs) / nuvarande_kurs * 100) if nuvarande_kurs else None
        undervärdering_ps_i_år = ((target_ps_i_år - nuvarande_kurs) / nuvarande_kurs * 100) if nuvarande_kurs else None
        undervärdering_ps_nästa_år = ((target_ps_nästa_år - nuvarande_kurs) / nuvarande_kurs * 100) if nuvarande_kurs else None

        return {
            "target_pe_i_år": target_pe_i_år,
            "target_pe_nästa_år": target_pe_nästa_år,
            "target_ps_i_år": target_ps_i_år,
            "target_ps_nästa_år": target_ps_nästa_år,
            "undervärdering_pe_i_år": undervärdering_pe_i_år,
            "undervärdering_pe_nästa_år": undervärdering_pe_nästa_år,
            "undervärdering_ps_i_år": undervärdering_ps_i_år,
            "undervärdering_ps_nästa_år": undervärdering_ps_nästa_år,
        }
    except Exception as e:
        return {}

def main():
    st.title("Aktieanalysapp")

    if "data" not in st.session_state:
        st.session_state.data = load_data()

    # Inmatningsformulär
    with st.form("ny_bolagsform"):
        st.subheader("Lägg till eller uppdatera bolag")
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_fj = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_år = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nästa_år = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsättning_fj = st.number_input("Omsättning förra året", format="%.2f")
        oms_tillv_i_år = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        oms_tillv_nästa_år = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")

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

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            if bolagsnamn == "":
                st.warning("Fyll i bolagsnamn!")
            else:
                nyckel = bolagsnamn.lower()
                nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.data[nyckel] = {
                    "bolagsnamn": bolagsnamn,
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_förra_året": vinst_fj,
                    "förväntad_vinst_i_år": vinst_i_år,
                    "förväntad_vinst_nästa_år": vinst_nästa_år,
                    "omsättning_förra_året": omsättning_fj,
                    "förväntad_omsättningstillväxt_i_år": oms_tillv_i_år,
                    "förväntad_omsättningstillväxt_nästa_år": oms_tillv_nästa_år,
                    "nuvarande_p_e": nuvarande_pe,
                    "p_e_1": pe_1,
                    "p_e_2": pe_2,
                    "p_e_3": pe_3,
                    "p_e_4": pe_4,
                    "nuvarande_p_s": nuvarande_ps,
                    "p_s_1": ps_1,
                    "p_s_2": ps_2,
                    "p_s_3": ps_3,
                    "p_s_4": ps_4,
                    "senast_uppdaterad": nu,
                }
                save_data(st.session_state.data)
                st.success(f"Bolag '{bolagsnamn}' sparat!")

    # Välj bolag
    bolag_nycklar = sorted(st.session_state.data.keys())
    if not bolag_nycklar:
        st.info("Inga bolag sparade än.")
        return

    valt_bolag_nyckel = st.selectbox("Välj bolag", bolag_nycklar)
    bolag = st.session_state.data.get(valt_bolag_nyckel, {})

    if bolag:
        st.subheader(f"Detaljer för {bolag.get('bolagsnamn', '')}")
        st.write(f"Nuvarande kurs: {bolag.get('nuvarande_kurs')}")
        st.write(f"Senast uppdaterad: {bolag.get('senast_uppdaterad')}")

        targets = calculate_targets(bolag)
        if targets:
            st.markdown("### Targetkurser (kr)")
            st.write(f"P/E i år: {targets['target_pe_i_år']:.2f} kr")
            st.write(f"P/E nästa år: {targets['target_pe_nästa_år']:.2f} kr")
            st.write(f"P/S i år: {targets['target_ps_i_år']:.2f} kr")
            st.write(f"P/S nästa år: {targets['target_ps_nästa_år']:.2f} kr")

            st.markdown("### Undervärdering / Övervärdering (%) jämfört med nuvarande kurs")
            def fmt_pct(x):
                if x is None:
                    return "-"
                return f"{x:+.2f} %"
            st.write(f"P/E i år: {fmt_pct(targets['undervärdering_pe_i_år'])}")
            st.write(f"P/E nästa år: {fmt_pct(targets['undervärdering_pe_nästa_år'])}")
            st.write(f"P/S i år: {fmt_pct(targets['undervärdering_ps_i_år'])}")
            st.write(f"P/S nästa år: {fmt_pct(targets['undervärdering_ps_nästa_år'])}")
        else:
            st.warning("Kan inte beräkna targetkurser för detta bolag.")

if __name__ == "__main__":
    main()
