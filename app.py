import streamlit as st
import pandas as pd

# Funktion för att initiera dataramen med rätt kolumner om den inte finns i session_state
def init_data():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nastaar",
            "omsattning_forra_aret", "omsattningstillvaxt_i_ar", "omsattningstillvaxt_nastaar",
            "nuvarande_pe", "pe1", "pe2", "pe3", "pe4",
            "nuvarande_ps", "ps1", "ps2", "ps3", "ps4",
            "insatt_datum", "senast_andrad"
        ])

# Beräkna targetkurs pe som medelvärde av pe1 och pe2 multiplicerat med vinst_nastaar
def berakna_targetkurs_pe(row):
    try:
        pe_med = (float(row["pe1"]) + float(row["pe2"])) / 2
        return float(row["vinst_nastaar"]) * pe_med
    except:
        return None

# Beräkna targetkurs ps som medelvärde ps1 och ps2 multiplicerat med omsättningstillväxt genomsnitt och nuvarande kurs
def berakna_targetkurs_ps(row):
    try:
        ps_med = (float(row["ps1"]) + float(row["ps2"])) / 2
        oms_tillv_med = (float(row["omsattningstillvaxt_i_ar"]) + float(row["omsattningstillvaxt_nastaar"])) / 2 / 100
        return ps_med * (1 + oms_tillv_med) * float(row["nuvarande_kurs"])
    except:
        return None

# Beräkna undervärdering procent för pe och ps
def berakna_undervardering(row):
    try:
        target_pe = row["targetkurs_pe"]
        target_ps = row["targetkurs_ps"]
        kurs = float(row["nuvarande_kurs"])
        underv_pe = (target_pe - kurs) / kurs if target_pe else 0
        underv_ps = (target_ps - kurs) / kurs if target_ps else 0
        return max(underv_pe, underv_ps)
    except:
        return 0

# Visa progress bar med färg och emoji baserat på procentuell undervärdering
def visa_progress_bar(procent):
    procent = max(min(procent, 1), 0)  # klipp mellan 0 och 1
    emoji = "🟢"
    färg = "#2ecc71"  # grön
    
    if procent > 0.5:
        emoji = "🔥"
        färg = "#e74c3c"  # röd
    elif procent > 0.3:
        emoji = "🟠"
        färg = "#f39c12"  # orange
    elif procent > 0.1:
        emoji = "🟡"
        färg = "#f1c40f"  # gul
    
    bar_html = f"""
    <div style='background:#ddd; border-radius:5px; width:100%; height:20px;'>
      <div style='background:{färg}; width:{procent*100}%; height:20px; border-radius:5px;'>
        <span style='padding-left:5px;color:#fff;font-weight:bold;'>{emoji} {int(procent*100)}%</span>
      </div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

# Visa bolagsinformation i en tabell
def visa_bolag_info(row):
    st.markdown(f"### {row['bolagsnamn']}")
    st.write(f"**Nuvarande kurs:** {row['nuvarande_kurs']}")
    st.write(f"**Vinst förra året:** {row['vinst_forra_aret']}")
    st.write(f"**Förväntad vinst i år:** {row['vinst_i_ar']}")
    st.write(f"**Förväntad vinst nästa år:** {row['vinst_nastaar']}")
    st.write(f"**Omsättning förra året:** {row['omsattning_forra_aret']}")
    st.write(f"**Förväntad omsättningstillväxt i år %:** {row['omsattningstillvaxt_i_ar']}")
    st.write(f"**Förväntad omsättningstillväxt nästa år %:** {row['omsattningstillvaxt_nastaar']}")
    st.write(f"**Nuvarande P/E:** {row['nuvarande_pe']}")
    st.write(f"P/E 1: {row['pe1']}, P/E 2: {row['pe2']}, P/E 3: {row['pe3']}, P/E 4: {row['pe4']}")
    st.write(f"**Nuvarande P/S:** {row['nuvarande_ps']}")
    st.write(f"P/S 1: {row['ps1']}, P/S 2: {row['ps2']}, P/S 3: {row['ps3']}, P/S 4: {row['ps4']}")
    st.write(f"**Insatt datum:** {row.get('insatt_datum', '')}")
    st.write(f"**Senast ändrad:** {row.get('senast_andrad', '')}")

def main():
    st.title("Aktieanalys - Undervärderade Bolag")

    init_data()
    df = st.session_state.df

    with st.sidebar:
        visa_alla = st.checkbox("Visa alla bolag (annars bara undervärderade)", value=False)

    # Beräkna targetkurser och undervärdering
    if not df.empty:
        df["targetkurs_pe"] = df.apply(berakna_targetkurs_pe, axis=1)
        df["targetkurs_ps"] = df.apply(berakna_targetkurs_ps, axis=1)
        df["undervardering"] = df.apply(berakna_undervardering, axis=1)
    else:
        st.info("Ingen data ännu")

    # Filtera undervärderade bolag
    if visa_alla:
        bolagslista = df.sort_values("undervardering", ascending=False).reset_index(drop=True)
    else:
        bolagslista = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)

    if bolagslista.empty:
        st.warning("Inga bolag att visa")
        return

    # Bläddringsindex
    if "index" not in st.session_state:
        st.session_state.index = 0

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⏮️ Föregående"):
            st.session_state.index = max(st.session_state.index - 1, 0)
    with col3:
        if st.button("Nästa ⏭️"):
            st.session_state.index = min(st.session_state.index + 1, len(bolagslista) - 1)

    # Visa valt bolag
    valt_bolag = bolagslista.iloc[st.session_state.index]
    visa_bolag_info(valt_bolag)

    # Visa undervärdering progress bar
    underv = valt_bolag["undervardering"]
    if underv > 0:
        st.markdown("### Undervärdering")
        visa_progress_bar(underv)
    else:
        st.write("Inte undervärderad just nu")

if __name__ == "__main__":
    main()
