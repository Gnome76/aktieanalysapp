import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = 'bolag.json'

# Lista på alla kolumner vi använder
COLUMNS = [
    'bolagsnamn', 'nuvarande_kurs', 'vinst_forra_aret', 'forvantad_vinst_i_ar', 'forvantad_vinst_nasta_ar',
    'omsattning_forra_aret', 'forvantad_omsattningstillvaxt_i_ar_pct', 'forvantad_omsattningstillvaxt_nasta_ar_pct',
    'nuvarande_pe', 'pe_1', 'pe_2', 'pe_3', 'pe_4',
    'nuvarande_ps', 'ps_1', 'ps_2', 'ps_3', 'ps_4'
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ alla kolumner finns
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA
        return df[COLUMNS]
    else:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, ensure_ascii=False, indent=4)

def berakna_targetkurs_pe(row):
    try:
        vinst = float(row['forvantad_vinst_nasta_ar'])
        pe_medel = (float(row['pe_1']) + float(row['pe_2'])) / 2
        return vinst * pe_medel
    except:
        return None

def berakna_targetkurs_ps(row):
    try:
        ps_medel = (float(row['ps_1']) + float(row['ps_2'])) / 2
        oms_tillvxt_medel = (float(row['forvantad_omsattningstillvaxt_i_ar_pct']) + float(row['forvantad_omsattningstillvaxt_nasta_ar_pct'])) / 2 / 100
        oms_forra = float(row['omsattning_forra_aret'])
        target_ps = ps_medel * oms_forra * (1 + oms_tillvxt_medel)
        return target_ps
    except:
        return None

def undervardering_rad(row):
    try:
        if pd.isna(row['nuvarande_kurs']) or row['nuvarande_kurs'] == 0:
            return 0
        underv_pe = (row['targetkurs_pe'] - row['nuvarande_kurs']) / row['targetkurs_pe'] if row['targetkurs_pe'] else 0
        underv_ps = (row['targetkurs_ps'] - row['nuvarande_kurs']) / row['targetkurs_ps'] if row['targetkurs_ps'] else 0
        underv = max(underv_pe, underv_ps)
        return underv if underv > 0 else 0
    except:
        return 0

def main():
    st.title("Aktieanalysapp med full funktionalitet")

    # Ladda data
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    df = st.session_state.data.copy()

    # Beräkna targetkurser
    df['targetkurs_pe'] = df.apply(berakna_targetkurs_pe, axis=1)
    df['targetkurs_ps'] = df.apply(berakna_targetkurs_ps, axis=1)
    df['undervardering'] = df.apply(undervardering_rad, axis=1)

    st.sidebar.header("Filtrering och visning")

    visa_undervarderade = st.sidebar.checkbox("Visa endast undervärderade (≥30%)", value=False)
    undervardering_grans = 0.3

    if visa_undervarderade:
        df_vis = df[df['undervardering'] >= undervardering_grans]
    else:
        df_vis = df

    # Sortera på undervärdering högst först
    df_vis = df_vis.sort_values(by='undervardering', ascending=False).reset_index(drop=True)

    # --- Lägg till nytt bolag ---
    st.header("Lägg till nytt bolag")
    with st.form("nytt_bolag_form"):
        ny_bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        forvantad_vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        forvantad_vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        forvantad_omsattningstillvaxt_i_ar_pct = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
        forvantad_omsattningstillvaxt_nasta_ar_pct = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", format="%.2f")
        pe_1 = st.number_input("P/E 1", format="%.2f")
        pe_2 = st.number_input("P/E 2", format="%.2f")
        pe_3 = st.number_input("P/E 3", format="%.2f")
        pe_4 = st.number_input("P/E 4", format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", format="%.2f")
        ps_1 = st.number_input("P/S 1", format="%.2f")
        ps_2 = st.number_input("P/S 2", format="%.2f")
        ps_3 = st.number_input("P/S 3", format="%.2f")
        ps_4 = st.number_input("P/S 4", format="%.2f")

        add_submit = st.form_submit_button("Lägg till bolag")

    if add_submit:
        if ny_bolagsnamn.strip() == "":
            st.error("Bolagsnamn får inte vara tomt!")
        elif ny_bolagsnamn in df['bolagsnamn'].values:
            st.error("Bolaget finns redan! Redigera det istället.")
        else:
            ny_rad = {
                'bolagsnamn': ny_bolagsnamn,
                'nuvarande_kurs': nuvarande_kurs,
                'vinst_forra_aret': vinst_forra_aret,
                'forvantad_vinst_i_ar': forvantad_vinst_i_ar,
                'forvantad_vinst_nasta_ar': forvantad_vinst_nasta_ar,
                'omsattning_forra_aret': omsattning_forra_aret,
                'forvantad_omsattningstillvaxt_i_ar_pct': forvantad_omsattningstillvaxt_i_ar_pct,
                'forvantad_omsattningstillvaxt_nasta_ar_pct': forvantad_omsattningstillvaxt_nasta_ar_pct,
                'nuvarande_pe': nuvarande_pe,
                'pe_1': pe_1,
                'pe_2': pe_2,
                'pe_3': pe_3,
                'pe_4': pe_4,
                'nuvarande_ps': nuvarande_ps,
                'ps_1': ps_1,
                'ps_2': ps_2,
                'ps_3': ps_3,
                'ps_4': ps_4
            }
            df = df.append(ny_rad, ignore_index=True)
            save_data(df)
            st.session_state.data = df
            st.success(f"Bolag '{ny_bolagsnamn}' tillagt!")

    # --- Redigera befintligt bolag ---
    st.header("Redigera eller ta bort bolag")

    val = st.selectbox("Välj bolag att redigera", options=[""] + list(df['bolagsnamn']))

    if val:
        rad = df[df['bolagsnamn'] == val].iloc[0]

        # Visa fälten för redigering
        ny_bolagsnamn = st.text_input("Bolagsnamn", rad['bolagsnamn'])
        nuvarande_kurs = st.number_input("Nuvarande kurs", value=float(rad['nuvarande_kurs']), min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", value=float(rad['vinst_forra_aret']), format="%.2f")
        forvantad_vinst_i_ar = st.number_input("Förväntad vinst i år", value=float(rad['forvantad_vinst_i_ar']), format="%.2f")
        forvantad_vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", value=float(rad['forvantad_vinst_nasta_ar']), format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", value=float(rad['omsattning_forra_aret']), format="%.2f")
        forvantad_omsattningstillvaxt_i_ar_pct = st.number_input("Förväntad omsättningstillväxt i år %", value=float(rad['forvantad_omsattningstillvaxt_i_ar_pct']), format="%.2f")
        forvantad_omsattningstillvaxt_nasta_ar_pct = st.number_input("Förväntad omsättningstillväxt nästa år %", value=float(rad['forvantad_omsattningstillvaxt_nasta_ar_pct']), format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", value=float(rad['nuvarande_pe']), format="%.2f")
        pe_1 = st.number_input("P/E 1", value=float(rad['pe_1']), format="%.2f")
        pe_2 = st.number_input("P/E 2", value=float(rad['pe_2']), format="%.2f")
        pe_3 = st.number_input("P/E 3", value=float(rad['pe_3']), format="%.2f")
        pe_4 = st.number_input("P/E 4", value=float(rad['pe_4']), format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", value=float(rad['nuvarande_ps']), format="%.2f")
        ps_1 = st.number_input("P/S 1", value=float(rad['ps_1']), format="%.2f")
        ps_2 = st.number_input("P/S 2", value=float(rad['ps_2']), format="%.2f")
        ps_3 = st.number_input("P/S 3", value=float(rad['ps_3']), format="%.2f")
        ps_4 = st.number_input("P/S 4", value=float(rad['ps_4']), format="%.2f")

        if st.button("Uppdatera bolag"):
            idx = df.index[df['bolagsnamn'] == val][0]
            df.loc[idx] = [
                ny_bolagsnamn, nuvarande_kurs, vinst_forra_aret, forvantad_vinst_i_ar, forvantad_vinst_nasta_ar,
                omsattning_forra_aret, forvantad_omsattningstillvaxt_i_ar_pct, forvantad_omsattningstillvaxt_nasta_ar_pct,
                nuvarande_pe, pe_1, pe_2, pe_3, pe_4,
                nuvarande_ps, ps_1, ps_2, ps_3, ps_4
            ]
            save_data(df)
            st.session_state.data = df
            st.success("Bolaget uppdaterat!")

        if st.button("Ta bort bolag"):
            df = df[df['bolagsnamn'] != val]
            save_data(df)
            st.session_state.data = df
            st.success(f"Bolaget '{val}' borttaget!")

    # --- Visa alla bolag i tabell ---
    st.header("Alla sparade bolag")
    vis_df = df_vis.copy()
    vis_df_display = vis_df[['bolagsnamn', 'nuvarande_kurs', 'targetkurs_pe', 'targetkurs_ps', 'undervardering']]
    vis_df_display['undervardering (%)'] = (vis_df_display['undervardering'] * 100).round(1)
    vis_df_display = vis_df_display.drop(columns=['undervardering'])
    st.dataframe(vis_df_display)

    # --- Bläddra ett bolag i taget (mobilvy) ---
    st.header("Bläddra bland bolag (ett i taget)")

    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0

    max_idx = len(df_vis) - 1

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Föregående") and st.session_state.current_idx > 0:
            st.session_state.current_idx -= 1
    with col3:
        if st.button("Nästa") and st.session_state.current_idx < max_idx:
            st.session_state.current_idx += 1

    if len(df_vis) > 0:
        rad = df_vis.iloc[st.session_state.current_idx]

        st.subheader(f"{rad['bolagsnamn']}")
        st.write(f"Nuvarande kurs: {rad['nuvarande_kurs']:.2f} SEK")
        st.write(f"Targetkurs (P/E): {rad['targetkurs_pe']:.2f} SEK" if rad['targetkurs_pe'] else "Targetkurs (P/E): -")
        st.write(f"Targetkurs (P/S): {rad['targetkurs_ps']:.2f} SEK" if rad['targetkurs_ps'] else "Targetkurs (P/S): -")
        st.write(f"Undervärdering: {rad['undervardering']*100:.1f} %")
    else:
        st.write("Inga bolag att visa.")

if __name__ == "__main__":
    main()
