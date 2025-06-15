import streamlit as st
import pandas as pd
from datetime import datetime

# --- Konstanter och kolumnlista
DATAFIL = "data.json"
KOLONNER = [
    "bolagsnamn", "kurs", "vinst_forra_ar", "vinst_i_ar", "vinst_nasta_ar",
    "omsattning_forra_ar", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
    "pe_1", "pe_2", "pe_3", "pe_4",
    "ps_1", "ps_2", "ps_3", "ps_4",
    "insatt_datum", "senast_andrad"
]

# --- Läs in data från JSON-fil, skapa tom DataFrame vid fel
def las_data():
    try:
        df = pd.read_json(DATAFIL)
        for col in KOLONNER:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[KOLONNER]
    except Exception:
        df = pd.DataFrame(columns=KOLONNER)
    return df

# --- Spara data till JSON-fil
def spara_data(df):
    try:
        df.to_json(DATAFIL, orient="records", force_ascii=False)
    except Exception as e:
        st.error(f"Kunde inte spara data: {e}")

# --- Beräkna targetkurser och undervärderingar
def berakna_targetkurser(df):
    if df.empty:
        return df

    num_cols = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "ps_1", "ps_2", "kurs",
        "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar"
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    df["oms_tillvaxt_medel"] = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 200
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + df["oms_tillvaxt_medel"]) * df["kurs"]

    df["undervärdering_pe_%"] = 100 * (df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"]
    df["undervärdering_ps_%"] = 100 * (df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"]

    df["max_undervärdering"] = df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)

    df["kopvard_pe"] = df["undervärdering_pe_%"] >= 30
    df["kopvard_ps"] = df["undervärdering_ps_%"] >= 30

    return df

# --- Lägg till eller uppdatera bolag i DataFrame
def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    bolagsnamn_ny = bolag_ny.get("bolagsnamn", "").strip()
    if bolagsnamn_ny == "":
        st.warning("Bolagsnamn kan inte vara tomt.")
        return df

    bolagsnamn_ny_lower = bolagsnamn_ny.lower()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if df.empty or "bolagsnamn" not in df.columns:
        bolag_ny["insatt_datum"] = now_str
        bolag_ny["senast_andrad"] = now_str
        df = pd.DataFrame([bolag_ny], columns=KOLONNER)
        st.success(f"Bolaget '{bolagsnamn_ny}' lades till.")
        return df

    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny_lower]

    if len(idx) > 0:
        i = idx[0]
        for key in bolag_ny:
            df.at[i, key] = bolag_ny[key]
        df.at[i, "senast_andrad"] = now_str
        st.success(f"Bolaget '{bolagsnamn_ny}' uppdaterades.")
    else:
        bolag_ny["insatt_datum"] = now_str
        bolag_ny["senast_andrad"] = now_str
        ny_rad = pd.DataFrame([bolag_ny], columns=KOLONNER)
        df = pd.concat([df, ny_rad], ignore_index=True)
        st.success(f"Bolaget '{bolagsnamn_ny}' lades till.")

    return df

# --- Visa formulär för att lägga till/uppdatera bolag
def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="form_lagg_till_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_ar = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        omsattning_forra_ar = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submit = st.form_submit_button("Spara bolag")

        if submit:
            nytt_bolag = {
                "bolagsnamn": bolagsnamn.strip(),
                "kurs": kurs,
                "vinst_forra_ar": vinst_forra_ar,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "omsattning_forra_ar": omsattning_forra_ar,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
                "pe_1": pe_1,
                "pe_2": pe_2,
                "pe_3": pe_3,
                "pe_4": pe_4,
                "ps_1": ps_1,
                "ps_2": ps_2,
                "ps_3": ps_3,
                "ps_4": ps_4,
            }
            df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
            spara_data(df)

    return df

# --- Visa bolag i tabell med möjlighet att filtrera undervärderade
def visa_bolag(df):
    st.header("Bolagslista och undervärdering")

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    df = berakna_targetkurser(df)

    visa_alla = st.checkbox("Visa alla bolag (annars endast undervärderade ≥30%)", value=False)

    if visa_alla:
        df_vis = df.copy()
    else:
        df_vis = df[(df["kopvard_pe"]) | (df["kopvard_ps"])]

    if df_vis.empty:
        st.info("Inga bolag uppfyller kriterierna.")
        return df

    df_vis = df_vis.sort_values(by="max_undervärdering", ascending=False)

    # Visa viktiga kolumner
    visa_kolumner = [
        "bolagsnamn", "kurs",
        "targetkurs_pe", "targetkurs_ps",
        "undervärdering_pe_%", "undervärdering_ps_%",
        "kopvard_pe", "kopvard_ps",
        "insatt_datum", "senast_andrad"
    ]
    st.dataframe(df_vis[visa_kolumner].style.format({
        "kurs": "{:.2f}",
        "targetkurs_pe": "{:.2f}",
        "targetkurs_ps": "{:.2f}",
        "undervärdering_pe_%": "{:.1f}%",
        "undervärdering_ps_%": "{:.1f}%"
    }), use_container_width=True)

    return df

# --- Ta bort bolag från DataFrame
def ta_bort_bolag(df):
    st.header("Ta bort bolag")

    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df

    bolagslista = df["bolagsnamn"].tolist()
    bolag_vald = st.selectbox("Välj bolag att ta bort", options=bolagslista)

    if st.button("Ta bort valt bolag"):
        df = df[df["bolagsnamn"] != bolag_vald]
        st.success(f"Bolaget '{bolag_vald}' togs bort.")
        spara_data(df)

    return df

# --- Del 5: Huvudfunktion och appstart

def main():
    st.title("Aktieanalysapp - Hantera bolag och nyckeltal")

    # Läs in data från fil (eller skapa tom DataFrame)
    df = las_data()

    # Visa inmatningsformulär för nytt eller befintligt bolag
    df = visa_form(df)

    # Visa och filtrera bolag, beräkna targetkurser och undervärdering
    df = visa_bolag(df)

    # Möjlighet att ta bort bolag
    df = ta_bort_bolag(df)

    # Spara data i fil efter ändringar
    spara_data(df)


if __name__ == "__main__":
    main()
