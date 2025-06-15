import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Aktieanalysapp", layout="centered")

DATA_FILE = "aktier_data.csv"

def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        # Säkerställ att datumen är datetime
        df['insatt_datum'] = pd.to_datetime(df['insatt_datum'])
        df['senast_andrad'] = pd.to_datetime(df['senast_andrad'])
        return df
    except FileNotFoundError:
        columns = [
            'bolagsnamn', 'nuvarande_kurs',
            'vinst_forra_aret', 'vinst_aret', 'vinst_nastaar',
            'omsattning_forra_aret', 'omsattningstillvaxt_aret_pct', 'omsattningstillvaxt_nastaar_pct',
            'nuvarande_pe', 'pe1', 'pe2', 'pe3', 'pe4',
            'nuvarande_ps', 'ps1', 'ps2', 'ps3', 'ps4',
            'insatt_datum', 'senast_andrad'
        ]
        return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def calculate_targetkurs_pe(row):
    try:
        pe_avg = (float(row['pe1']) + float(row['pe2'])) / 2
        return row['vinst_nastaar'] * pe_avg
    except Exception:
        return None

def calculate_targetkurs_ps(row):
    try:
        ps_avg = (float(row['ps1']) + float(row['ps2'])) / 2
        oms_tillvxt_avg = (float(row['omsattningstillvaxt_aret_pct']) + float(row['omsattningstillvaxt_nastaar_pct'])) / 2 / 100
        omsattning = float(row['omsattning_forra_aret'])
        # Targetkurs PS = P/S medel * omsättning med tillväxt
        oms_justerad = omsattning * (1 + oms_tillvxt_avg)
        return ps_avg * oms_justerad
    except Exception:
        return None

def format_percentage(value):
    try:
        return f"{value:.1f} %"
    except Exception:
        return value

def valuation_color_and_emoji(ratio):
    if ratio < 0.7:
        return "green", "🟢"
    elif ratio < 1.0:
        return "orange", "🟠"
    else:
        return "red", "🔴"

def valuation_progress_bar(ratio, label):
    # ratio <1 undervärderad, >1 övervärderad
    if ratio is None:
        st.write(f"{label}: Data saknas")
        return
    color, emoji = valuation_color_and_emoji(ratio)
    pct = min(max(1 - ratio, 0), 1) if ratio < 1 else 0
    bar = f"{emoji} {'█' * int(pct * 20)}{'░' * (20 - int(pct * 20))}"
    st.markdown(f"**{label}:** <span style='color:{color}'>{bar} ({ratio:.2f}x)</span>", unsafe_allow_html=True)

def main():
    st.title("📈 Aktieanalysapp")

    df = load_data()

    if 'df' not in st.session_state:
        st.session_state.df = df

    with st.expander("Lägg till / Redigera bolag"):
        with st.form("bolagsform"):
            bolagsnamn = st.text_input("Bolagsnamn", max_chars=50)
            nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
            vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
            vinst_aret = st.number_input("Förväntad vinst i år", format="%.2f")
            vinst_nastaar = st.number_input("Förväntad vinst nästa år", format="%.2f")
            omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
            omsattningstillvaxt_aret_pct = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
            omsattningstillvaxt_nastaar_pct = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")

            nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
            pe1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
            pe2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
            pe3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
            pe4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")

            nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
            ps1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
            ps2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
            ps3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
            ps4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

            submitted = st.form_submit_button("Spara")

            if submitted:
                if not bolagsnamn.strip():
                    st.error("Bolagsnamn måste fyllas i!")
                else:
                    now = datetime.datetime.now()
                    # Kontrollera om bolaget redan finns
                    if bolagsnamn in st.session_state.df['bolagsnamn'].values:
                        # Uppdatera befintligt bolag
                        idx = st.session_state.df.index[st.session_state.df['bolagsnamn'] == bolagsnamn][0]
                        st.session_state.df.loc[idx] = [
                            bolagsnamn, nuvarande_kurs,
                            vinst_forra_aret, vinst_aret, vinst_nastaar,
                            omsattning_forra_aret, omsattningstillvaxt_aret_pct, omsattningstillvaxt_nastaar_pct,
                            nuvarande_pe, pe1, pe2, pe3, pe4,
                            nuvarande_ps, ps1, ps2, ps3, ps4,
                            st.session_state.df.loc[idx, 'insatt_datum'], now
                        ]
                        st.success(f"Bolaget '{bolagsnamn}' uppdaterat!")
                    else:
                        # Lägg till nytt bolag
                        new_row = pd.DataFrame([[
                            bolagsnamn, nuvarande_kurs,
                            vinst_forra_aret, vinst_aret, vinst_nastaar,
                            omsattning_forra_aret, omsattningstillvaxt_aret_pct, omsattningstillvaxt_nastaar_pct,
                            nuvarande_pe, pe1, pe2, pe3, pe4,
                            nuvarande_ps, ps1, ps2, ps3, ps4,
                            now, now
                        ]], columns=st.session_state.df.columns)
                        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                        st.success(f"Bolaget '{bolagsnamn}' tillagt!")
                    save_data(st.session_state.df)

    st.markdown("---")

    if st.session_state.df.empty:
        st.info("Inga bolag sparade än. Lägg till bolag ovan.")
        return

    st.subheader("Alla bolag")
    # Lägg till targetkurser
    df_show = st.session_state.df.copy()
    df_show['targetkurs_pe'] = df_show.apply(calculate_targetkurs_pe, axis=1)
    df_show['targetkurs_ps'] = df_show.apply(calculate_targetkurs_ps, axis=1)

    # Beräkna undervärdering
    df_show['undervardering_pe'] = df_show['targetkurs_pe'] / df_show['nuvarande_kurs']
    df_show['undervardering_ps'] = df_show['targetkurs_ps'] / df_show['nuvarande_kurs']

    # Sortera efter max undervärdering
    df_show['max_undervardering'] = df_show[['undervardering_pe', 'undervardering_ps']].max(axis=1)
    df_show = df_show.sort_values(by='max_undervardering', ascending=False)

    # Filter undervärderade
    visa_undervarderade = st.checkbox("Visa endast minst 30% undervärderade bolag")
    if visa_undervarderade:
        df_show = df_show[(df_show['undervardering_pe'] >= 1.3) | (df_show['undervardering_ps'] >= 1.3)]

    st.dataframe(df_show[['bolagsnamn', 'nuvarande_kurs',
                         'targetkurs_pe', 'undervardering_pe',
                         'targetkurs_ps', 'undervardering_ps']].style.format({
                             'nuvarande_kurs': '{:.2f}',
                             'targetkurs_pe': '{:.2f}',
                             'undervardering_pe': '{:.2f}',
                             'targetkurs_ps': '{:.2f}',
                             'undervardering_ps': '{:.2f}',
                         }))

    st.markdown("---")

    st.subheader("Detaljerad vy - välj bolag")
    valda_bolag = st.selectbox("Välj bolag", options=st.session_state.df['bolagsnamn'].tolist())

    if valda_bolag:
        bolag_data = st.session_state.df[st.session_state.df['bolagsnamn'] == valda_bolag].iloc[0]

        st.write(f"### {valda_bolag}")
        st.write(f"**Nuvarande kurs:** {bolag_data['nuvarande_kurs']:.2f} SEK")

        target_pe = calculate_targetkurs_pe(bolag_data)
        target_ps = calculate_targetkurs_ps(bolag_data)

        underv_pe = target_pe / bolag_data['nuvarande_kurs'] if target_pe and bolag_data['nuvarande_kurs'] > 0 else None
        underv_ps = target_ps / bolag_data['nuvarande_kurs'] if target_ps and bolag_data['nuvarande_kurs'] > 0 else None

        # Visa progress bars och färger med emojis
        if target_pe:
            valuation_progress_bar(underv_pe, "Undervärdering P/E")
        else:
            st.write("Targetkurs P/E saknas.")

        if target_ps:
            valuation_progress_bar(underv_ps, "Undervärdering P/S")
        else:
            st.write("Targetkurs P/S saknas.")

        st.markdown("**Nyckeltal:**")
        nyckeltal = {
            "Vinst förra året": bolag_data['vinst_forra_aret'],
            "Förväntad vinst i år": bolag_data['vinst_aret'],
            "Förväntad vinst nästa år": bolag_data['vinst_nastaar'],
            "Omsättning förra året": bolag_data['omsattning_forra_aret'],
            "Omsättningstillväxt i år (%)": f"{bolag_data['omsattningstillvaxt_aret_pct']:.2f} %",
            "Omsättningstillväxt nästa år (%)": f"{bolag_data['omsattningstillvaxt_nastaar_pct']:.2f} %",
            "Nuvarande P/E": bolag_data['nuvarande_pe'],
            "P/E 1": bolag_data['pe1'],
            "P/E 2": bolag_data['pe2'],
            "P/E 3": bolag_data['pe3'],
            "P/E 4": bolag_data['pe4'],
            "Nuvarande P/S": bolag_data['nuvarande_ps'],
            "P/S 1": bolag_data['ps1'],
            "P/S 2": bolag_data['ps2'],
            "P/S 3": bolag_data['ps3'],
            "P/S 4": bolag_data['ps4'],
            "Insatt datum": bolag_data['insatt_datum'].strftime("%Y-%m-%d"),
            "Senast ändrad": bolag_data['senast_andrad'].strftime("%Y-%m-%d"),
        }
        for key, val in nyckeltal.items():
            st.write(f"**{key}:** {val}")

    st.markdown("---")
    st.write("© 2025 Aktieanalysapp")

if __name__ == "__main__":
    main()
