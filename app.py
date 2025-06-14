import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Aktieanalysapp", layout="centered")

# Initiera session_state
if "data" not in st.session_state:
    st.session_state.data = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

def calculate_targetkurs_pe(vinst_nasta_ar, pe_values):
    pe_values = [v for v in pe_values if v > 0]
    if vinst_nasta_ar and pe_values:
        return vinst_nasta_ar * (sum(pe_values) / len(pe_values))
    return None

def calculate_targetkurs_ps(oms_nasta_ar, ps_values, oms_vxt_nasta_ar):
    ps_values = [v for v in ps_values if v > 0]
    if oms_nasta_ar and ps_values and oms_vxt_nasta_ar is not None:
        ps_avg = sum(ps_values) / len(ps_values)
        # Här antas oms_nasta_ar redan är omsättning för nästa år inkl tillväxt
        return ps_avg * oms_nasta_ar
    return None

def undervardering(nuvarande_kurs, targetkurs):
    if nuvarande_kurs and targetkurs:
        return (targetkurs - nuvarande_kurs) / targetkurs * 100
    return None

def add_or_update_bolag(data, nytt_bolag):
    for i, bolag in enumerate(data):
        if bolag["Bolagsnamn"].lower() == nytt_bolag["Bolagsnamn"].lower():
            data[i] = nytt_bolag
            return
    data.append(nytt_bolag)

def main():
    st.title("Aktieanalysapp")

    st.header("Lägg till eller uppdatera bolag")

    bolagsnamn = st.text_input("Bolagsnamn").strip()

    nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
    vinst_fjol = st.number_input("Vinst förra året", format="%.2f")
    vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
    omsattning_fjol = st.number_input("Omsättning förra året", format="%.2f")
    oms_vxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
    oms_vxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")

    pe_nu = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
    pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
    pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
    pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
    pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")

    ps_nu = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
    ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
    ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
    ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
    ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

    if st.button("Spara bolag"):
        if not bolagsnamn:
            st.error("Bolagsnamn måste fyllas i")
        else:
            nytt_bolag = {
                "Bolagsnamn": bolagsnamn,
                "Nuvarande kurs": nuvarande_kurs,
                "Vinst förra året": vinst_fjol,
                "Förväntad vinst i år": vinst_i_ar,
                "Förväntad vinst nästa år": vinst_nasta_ar,
                "Omsättning förra året": omsattning_fjol,
                "Omsättningstillväxt i år %": oms_vxt_ar,
                "Omsättningstillväxt nästa år %": oms_vxt_nasta_ar,
                "Nuvarande P/E": pe_nu,
                "P/E 1": pe_1,
                "P/E 2": pe_2,
                "P/E 3": pe_3,
                "P/E 4": pe_4,
                "Nuvarande P/S": ps_nu,
                "P/S 1": ps_1,
                "P/S 2": ps_2,
                "P/S 3": ps_3,
                "P/S 4": ps_4,
                "Datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            add_or_update_bolag(st.session_state.data, nytt_bolag)
            st.success(f"Bolag '{bolagsnamn}' sparat/uppdaterat!")

    if not st.session_state.data:
        st.info("Inga bolag sparade ännu.")
        return

    # Beräkna targetkurser och undervärdering
    for bolag in st.session_state.data:
        # Beräkna omsättning för nästa år med tillväxt
        oms_nasta_ar = bolag["Omsättning förra året"] * (1 + bolag["Omsättningstillväxt nästa år %"] / 100)

        target_pe = calculate_targetkurs_pe(
            bolag["Förväntad vinst nästa år"],
            [bolag["P/E 1"], bolag["P/E 2"], bolag["P/E 3"], bolag["P/E 4"]],
        )
        target_ps = calculate_targetkurs_ps(
            oms_nasta_ar,
            [bolag["P/S 1"], bolag["P/S 2"], bolag["P/S 3"], bolag["P/S 4"]],
            bolag["Omsättningstillväxt nästa år %"],
        )
        bolag["Targetkurs P/E"] = target_pe
        bolag["Targetkurs P/S"] = target_ps

        underv_pe = undervardering(bolag["Nuvarande kurs"], target_pe)
        underv_ps = undervardering(bolag["Nuvarande kurs"], target_ps)
        bolag["Undervärdering P/E %"] = underv_pe if underv_pe is not None else -9999
        bolag["Undervärdering P/S %"] = underv_ps if underv_ps is not None else -9999
        bolag["Max undervärdering"] = max(bolag["Undervärdering P/E %"], bolag["Undervärdering P/S %"])

    st.header("Bolagslista")

    visa_endast_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)

    data_sorted = sorted(st.session_state.data, key=lambda x: x["Max undervärdering"], reverse=True)

    if visa_endast_undervarderade:
        data_sorted = [b for b in data_sorted if b["Max undervärdering"] >= 30]

    if not data_sorted:
        st.warning("Inga bolag matchar filter.")
        return

    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Föregående") and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
    with col3:
        if st.button("Nästa →") and st.session_state.current_index < len(data_sorted) - 1:
            st.session_state.current_index += 1

    bolag = data_sorted[st.session_state.current_index]

    st.subheader(f"{bolag['Bolagsnamn']} ({st.session_state.current_index + 1} av {len(data_sorted)})")
    st.write(f"**Nuvarande kurs:** {bolag['Nuvarande kurs']:.2f} kr")

    show_details = st.checkbox("Visa detaljerade nyckeltal", key="details_checkbox")

    if show_details:
        with st.expander("Nyckeltal och beräkningar"):
            st.write(f"Vinst förra året: {bolag['Vinst förra året']}")
            st.write(f"Förväntad vinst i år: {bolag['Förväntad vinst i år']}")
            st.write(f"Förväntad vinst nästa år: {bolag['Förväntad vinst nästa år']}")
            st.write(f"Omsättning förra året: {bolag['Omsättning förra året']}")
            st.write(f"Omsättningstillväxt i år (%): {bolag['Omsättningstillväxt i år %']}")
            st.write(f"Omsättningstillväxt nästa år (%): {bolag['Omsättningstillväxt nästa år %']}")
            st.write(f"Nuvarande P/E: {bolag['Nuvarande P/E']}")
            st.write(f"P/E 1: {bolag['P/E 1']}")
            st.write(f"P/E 2: {bolag['P/E 2']}")
            st.write(f"P/E 3: {bolag['P/E 3']}")
            st.write(f"P/E 4: {bolag['P/E 4']}")
            st.write(f"Nuvarande P/S: {bolag['Nuvarande P/S']}")
            st.write(f"P/S 1: {bolag['P/S 1']}")
            st.write(f"P/S 2: {bolag['P/S 2']}")
            st.write(f"P/S 3: {bolag['P/S 3']}")
            st.write(f"P/S 4: {bolag['P/S 4']}")
            st.write(f"Targetkurs P/E: {bolag['Targetkurs P/E']:.2f}" if bolag['Targetkurs P/E'] else "Targetkurs P/E: Ej beräknad")
            st.write(f"Targetkurs P/S: {bolag['Targetkurs P/S']:.2f}" if bolag['Targetkurs P/S'] else "Targetkurs P/S: Ej beräknad")
            st.write(f"Undervärdering P/E %: {bolag['Undervärdering P/E %']:.2f}%")
            st.write(f"Undervärdering P/S %: {bolag['Undervärdering P/S %']:.2f}%")

    st.markdown("---")
    st.write("Visa ett bolag i taget med möjlighet att bläddra.")

if __name__ == "__main__":
    main()
