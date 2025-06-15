import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# --- Del 1: Grundläggande setup och datalagring ---

DATA_PATH = "data.json"

def las_data() -> pd.DataFrame:
    """Läser in data från JSON-fil och returnerar DataFrame."""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att datum är datetime
        if "insatt_datum" in df.columns:
            df["insatt_datum"] = pd.to_datetime(df["insatt_datum"], errors="coerce")
        if "senast_andrad" in df.columns:
            df["senast_andrad"] = pd.to_datetime(df["senast_andrad"], errors="coerce")
        return df
    else:
        # Tom DataFrame med alla kolumner
        kolumner = [
            "bolagsnamn", "kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "oms_forra_aret", "oms_tillvaxt_i_ar_procent", "oms_tillvaxt_nasta_ar_procent",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=kolumner)

def spara_data(df: pd.DataFrame):
    """Sparar DataFrame till JSON-fil."""
    with open(DATA_PATH, "w") as f:
        json.dump(df.fillna("").to_dict(orient="records"), f)

# --- Del 2: Beräkningar och filtrering ---

def berakna_targetkurser(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in [
        "vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "kurs",
        "oms_tillvaxt_i_ar_procent", "oms_tillvaxt_nasta_ar_procent"
    ]:
        if col not in df.columns:
            df[col] = pd.NA
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["pe_medel"] = df[["pe_1", "pe_2"]].mean(axis=1)
    df["ps_medel"] = df[["ps_1", "ps_2"]].mean(axis=1)
    df["oms_tillvaxt_medel"] = df[["oms_tillvaxt_i_ar_procent", "oms_tillvaxt_nasta_ar_procent"]].mean(axis=1) / 100

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * df["pe_medel"]
    df["targetkurs_ps"] = df["ps_medel"] * (1 + df["oms_tillvaxt_medel"]) * df["kurs"]

    df["undervardering_pe_%"] = ((df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"]) * 100
    df["undervardering_ps_%"] = ((df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"]) * 100

    df["undervardering_pe_%"] = df["undervardering_pe_%"].replace([float("inf"), -float("inf")], pd.NA)
    df["undervardering_ps_%"] = df["undervardering_ps_%"].replace([float("inf"), -float("inf")], pd.NA)

    df["max_undervardering_%"] = df[["undervardering_pe_%", "undervardering_ps_%"]].max(axis=1)
    df["kopvard_30"] = df["max_undervardering_%"] >= 30

    return df

def filtrera_och_sortera(df: pd.DataFrame, bara_undervarderade: bool) -> pd.DataFrame:
    if bara_undervarderade:
        df_filtrerat = df[df["max_undervardering_%"] >= 30].copy()
    else:
        df_filtrerat = df.copy()

    df_filtrerat = df_filtrerat.sort_values(by="max_undervardering_%", ascending=False)
    return df_filtrerat.reset_index(drop=True)

# --- Del 3: Formulär, redigering och uppdatering ---

def lagg_till_eller_uppdatera_bolag(df: pd.DataFrame, bolag: dict) -> pd.DataFrame:
    bolagsnamn_ny = bolag["bolagsnamn"].strip().lower()
    df = df.copy()

    # Kontrollera om bolag finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()

    nu = datetime.now()
    if idx:
        # Uppdatera befintligt bolag
        i = idx[0]
        for key, value in bolag.items():
            df.at[i, key] = value
        df.at[i, "senast_andrad"] = nu
    else:
        # Lägg till nytt bolag
        bolag["insatt_datum"] = nu
        bolag["senast_andrad"] = nu
        df = pd.concat([df, pd.DataFrame([bolag])], ignore_index=True)

    return df

def visa_form(df: pd.DataFrame) -> pd.DataFrame:
    with st.form(key="form_inmatning"):
        st.subheader("Lägg till / uppdatera bolag")
        bolagsnamn = st.text_input("Bolagsnamn", max_chars=50)
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        oms_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        oms_tillvaxt_i_ar_procent = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
        oms_tillvaxt_nasta_ar_procent = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")
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

        submit = st.form_submit_button("Spara")

    if submit:
        nytt_bolag = {
            "bolagsnamn": bolagsnamn,
            "kurs": kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "oms_forra_aret": oms_forra_aret,
            "oms_tillvaxt_i_ar_procent": oms_tillvaxt_i_ar_procent,
            "oms_tillvaxt_nasta_ar_procent": oms_tillvaxt_nasta_ar_procent,
            "nuvarande_pe": nuvarande_pe,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "pe_3": pe_3,
            "pe_4": pe_4,
            "nuvarande_ps": nuvarande_ps,
            "ps_1": ps_1,
            "ps_2": ps_2,
            "ps_3": ps_3,
            "ps_4": ps_4,
        }
        df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
        spara_data(df)
        st.success(f"Bolaget '{bolagsnamn}' har sparats/uppdaterats.")

    return df

# --- Del 4: Visning, filtrering och presentation av bolag ---

def visa_bolag(df: pd.DataFrame):
    st.subheader("Sparade bolag")

    if df.empty:
        st.info("Inga bolag sparade än.")
        return

    # Checkbox för filtrering undervärderade
    bara_undervarderade = st.checkbox("Visa endast undervärderade bolag (≥ 30% rabatt)", value=False)

    df = berakna_targetkurser(df)
    df_vis = filtrera_och_sortera(df, bara_undervarderade)

    # Visa tabell med viktiga kolumner
    visningskolumner = [
        "bolagsnamn",
        "kurs",
        "targetkurs_pe",
        "targetkurs_ps",
        "max_undervardering_%",
        "kopvard_30"
    ]

    df_vis["kurs"] = df_vis["kurs"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    df_vis["targetkurs_pe"] = df_vis["targetkurs_pe"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    df_vis["targetkurs_ps"] = df_vis["targetkurs_ps"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    df_vis["max_undervardering_%"] = df_vis["max_undervardering_%"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    df_vis["kopvard_30"] = df_vis["kopvard_30"].map({True: "Ja", False: "Nej"})

    st.dataframe(df_vis[visningskolumner].rename(columns={
        "bolagsnamn": "Bolagsnamn",
        "kurs": "Nuvarande kurs",
        "targetkurs_pe": "Targetkurs P/E",
        "targetkurs_ps": "Targetkurs P/S",
        "max_undervardering_%": "Undervärderad %",
        "kopvard_30": "Köpvärd vid 30% rabatt"
    }), use_container_width=True)

    # Visa detaljerad vy av valt bolag (om något valt)
    valt_bolag = st.selectbox("Välj bolag för detaljerad vy", options=df_vis["bolagsnamn"].tolist())

    if valt_bolag:
        bolag_info = df_vis[df_vis["bolagsnamn"] == valt_bolag].iloc[0]
        st.markdown(f"### Detaljer för **{valt_bolag}**")
        st.write(f"- Nuvarande kurs: {bolag_info['kurs']:.2f}")
        st.write(f"- Targetkurs P/E: {bolag_info['targetkurs_pe']:.2f}")
        st.write(f"- Targetkurs P/S: {bolag_info['targetkurs_ps']:.2f}")
        st.write(f"- Undervärderad %: {bolag_info['max_undervardering_%']:.1f}%")
        st.write(f"- Köpvärd vid 30% rabatt: {'Ja' if bolag_info['kopvard_30'] else 'Nej'}")

        st.write("#### Nyckeltal")
        nyckeltal = {
            "Vinst förra året": bolag_info["vinst_forra_aret"],
            "Vinst i år": bolag_info["vinst_i_ar"],
            "Vinst nästa år": bolag_info["vinst_nasta_ar"],
            "Omsättning förra året": bolag_info["oms_forra_aret"],
            "Omsättningstillväxt i år (%)": bolag_info["oms_tillvaxt_i_ar_procent"],
            "Omsättningstillväxt nästa år (%)": bolag_info["oms_tillvaxt_nasta_ar_procent"],
            "Nuvarande P/E": bolag_info["nuvarande_pe"],
            "P/E 1": bolag_info["pe_1"],
            "P/E 2": bolag_info["pe_2"],
            "P/E 3": bolag_info["pe_3"],
            "P/E 4": bolag_info["pe_4"],
            "Nuvarande P/S": bolag_info["nuvarande_ps"],
            "P/S 1": bolag_info["ps_1"],
            "P/S 2": bolag_info["ps_2"],
            "P/S 3": bolag_info["ps_3"],
            "P/S 4": bolag_info["ps_4"],
            "Insatt datum": bolag_info["insatt_datum"].strftime("%Y-%m-%d %H:%M") if pd.notna(bolag_info["insatt_datum"]) else "",
            "Senast ändrad": bolag_info["senast_andrad"].strftime("%Y-%m-%d %H:%M") if pd.notna(bolag_info["senast_andrad"]) else ""
        }
        for nyckel, varde in nyckeltal.items():
            st.write(f"- **{nyckel}:** {varde}")

# --- Del 5: Huvudfunktion och appens körning ---

def main():
    st.title("Aktieanalysapp - Undervärderade bolag")
    df = las_data()

    # Visa formulär för att lägga till / uppdatera bolag
    df = visa_form(df)

    # Visa bolag och undervärderingsanalys
    visa_bolag(df)

    # Spara data i JSON-fil
    spara_data(df)

if __name__ == "__main__":
    main()
