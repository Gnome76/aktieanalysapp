import streamlit as st
from datetime import datetime

# Initiera datalagring i session_state
if "data" not in st.session_state:
    st.session_state.data = {}

if "valt_bolag" not in st.session_state:
    st.session_state.valt_bolag = None

st.title("Aktieanalysapp - Inmatning & Redigering")

# Välj bolag att redigera eller skapa nytt
valda_bolag = list(st.session_state.data.keys())
valda_bolag.insert(0, "-- Lägg till nytt bolag --")
valt = st.selectbox("Välj bolag att redigera", valda_bolag)

if valt == "-- Lägg till nytt bolag --":
    nytt_bolagsnamn = st.text_input("Bolagsnamn", value="")
    valt_bolag_data = None
else:
    nytt_bolagsnamn = valt
    valt_bolag_data = st.session_state.data.get(valt, {})

# Dela in i två kolumner för huvudfält
col1, col2 = st.columns(2)

with col1:
    nuvarande_kurs = st.number_input(
        "Nuvarande kurs",
        value=valt_bolag_data.get("nuvarande_kurs", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    vinst_fora_aret = st.number_input(
        "Vinst förra året",
        value=valt_bolag_data.get("vinst_fora_aret", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    vinst_i_ar = st.number_input(
        "Förväntad vinst i år",
        value=valt_bolag_data.get("vinst_i_ar", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    vinst_nasta_ar = st.number_input(
        "Förväntad vinst nästa år",
        value=valt_bolag_data.get("vinst_nasta_ar", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )

with col2:
    omsattning_fora_aret = st.number_input(
        "Omsättning förra året",
        value=valt_bolag_data.get("omsattning_fora_aret", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    omsattningstillvaxt_ar = st.number_input(
        "Förväntad omsättningstillväxt i år %",
        value=valt_bolag_data.get("omsattningstillvaxt_ar", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    omsattningstillvaxt_nasta_ar = st.number_input(
        "Förväntad omsättningstillväxt nästa år %",
        value=valt_bolag_data.get("omsattningstillvaxt_nasta_ar", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    nuvarande_pe = st.number_input(
        "Nuvarande P/E",
        value=valt_bolag_data.get("nuvarande_pe", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )

with st.expander("Övriga P/E och P/S värden"):
    pe1 = st.number_input(
        "P/E 1",
        value=valt_bolag_data.get("pe1", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    pe2 = st.number_input(
        "P/E 2",
        value=valt_bolag_data.get("pe2", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    pe3 = st.number_input(
        "P/E 3",
        value=valt_bolag_data.get("pe3", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    pe4 = st.number_input(
        "P/E 4",
        value=valt_bolag_data.get("pe4", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )

    nuvarande_ps = st.number_input(
        "Nuvarande P/S",
        value=valt_bolag_data.get("nuvarande_ps", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    ps1 = st.number_input(
        "P/S 1",
        value=valt_bolag_data.get("ps1", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    ps2 = st.number_input(
        "P/S 2",
        value=valt_bolag_data.get("ps2", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    ps3 = st.number_input(
        "P/S 3",
        value=valt_bolag_data.get("ps3", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )
    ps4 = st.number_input(
        "P/S 4",
        value=valt_bolag_data.get("ps4", 0.0) if valt_bolag_data else 0.0,
        format="%.2f",
        step=0.01,
    )

# Datum som sätts vid sparande
datum_nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if st.button("Spara bolag"):
    if nytt_bolagsnamn.strip() == "":
        st.error("Ange ett giltigt bolagsnamn!")
    else:
        st.session_state.data[nytt_bolagsnamn] = {
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_fora_aret": vinst_fora_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_fora_aret": omsattning_fora_aret,
            "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
            "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
            "nuvarande_pe": nuvarande_pe,
            "pe1": pe1,
            "pe2": pe2,
            "pe3": pe3,
            "pe4": pe4,
            "nuvarande_ps": nuvarande_ps,
            "ps1": ps1,
            "ps2": ps2,
            "ps3": ps3,
            "ps4": ps4,
            "senast_andrad": datum_nu,
        }
        st.success(f"Bolaget '{nytt_bolagsnamn}' har sparats/uppdaterats!")

        # Sätt valt bolag till det nya/uppdaterade så att UI reflekterar rätt
        st.session_state.valt_bolag = nytt_bolagsnamn

# Visa sparade bolag i tabell
if st.session_state.data:
    st.subheader("Sparade bolag")
    import pandas as pd

    df = pd.DataFrame.from_dict(st.session_state.data, orient="index")
    df.index.name = "Bolagsnamn"
    st.dataframe(df)

else:
    st.info("Inga bolag sparade än.")
