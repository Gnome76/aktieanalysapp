import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Filnamn för data
DATA_PATH = "data.json"

# --- Funktion: Läs in data från fil ---
def las_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()  # tom df
    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att datumen är datetime (om kolumner finns)
        for col in ["insatt_datum", "senast_andrad"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Fel vid inläsning av data: {e}")
        return pd.DataFrame()

# --- Funktion: Spara data till fil ---
def spara_data(df):
    try:
        with open(DATA_PATH, "w") as f:
            json_data = df.fillna("").to_dict(orient="records")
            json.dump(json_data, f, default=str)
    except Exception as e:
        st.error(f"Fel vid sparning av data: {e}")

# --- Funktion: Beräkna targetkurser och undervärdering ---
def berakna_targetkurser(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Säkerställ att nödvändiga kolumner finns
    required_cols = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "ps_1", "ps_2", "omsattningstillvaxt_1", "omsattningstillvaxt_2", "nuvarande_kurs",
        "nuvarande_pe", "nuvarande_ps"
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.warning(f"Saknade kolumner för beräkningar: {', '.join(missing)}")
        return df

    def safe_mean(x, y):
        try:
            return (float(x) + float(y)) / 2
        except:
            return None

    # Beräkna targetkurs baserat på P/E
    df["targetkurs_pe"] = df.apply(
        lambda row: (row["vinst_nasta_ar"] * safe_mean(row["pe_1"], row["pe_2"]))
        if pd.notnull(row["vinst_nasta_ar"]) and safe_mean(row["pe_1"], row["pe_2"]) is not None
        else None,
        axis=1,
    )

    # Beräkna genomsnittlig omsättningstillväxt (i decimalform)
    def omsattningstillvaxt_medel(row):
        try:
            return (float(row["omsattningstillvaxt_1"]) + float(row["omsattningstillvaxt_2"])) / 200  # proc till dec
        except:
            return 0

    df["omsattningstillvaxt_medel"] = df.apply(omsattningstillvaxt_medel, axis=1)

    # Beräkna targetkurs baserat på P/S
    def berakna_ps(row):
        try:
            ps_medel = safe_mean(row["ps_1"], row["ps_2"])
            if ps_medel is None or pd.isnull(row["nuvarande_kurs"]) or pd.isnull(row["omsattningstillvaxt_medel"]):
                return None
            omsattningstillvaxt_faktor = 1 + row["omsattningstillvaxt_medel"]
            return ps_medel * omsattningstillvaxt_faktor * row["nuvarande_kurs"]
        except:
            return None

    df["targetkurs_ps"] = df.apply(berakna_ps, axis=1)

    # Beräkna undervärdering i % (med hänsyn till targetkurs_pe och targetkurs_ps)
    def undervarderad_pct(row):
        try:
            kurs = row["nuvarande_kurs"]
            targets = [x for x in [row["targetkurs_pe"], row["targetkurs_ps"]] if x is not None]
            if not targets or kurs == 0 or pd.isnull(kurs):
                return None
            target_max = max(targets)
            return round((target_max - kurs) / target_max * 100, 2)
        except:
            return None

    df["undervarderad_pct"] = df.apply(undervarderad_pct, axis=1)

    # Beräkna köpvärd vid 30% rabatt (targetkurs * 0.7)
    df["kopvard_30procent"] = df[["targetkurs_pe", "targetkurs_ps"]].max(axis=1) * 0.7

    return df


# --- Funktion: Filtrera bolag baserat på undervärdering ---
def filtrera_bolag(df: pd.DataFrame, endast_undervarderade: bool) -> pd.DataFrame:
    if df.empty:
        return df
    df = berakna_targetkurser(df)
    if endast_undervarderade:
        return df[df["undervarderad_pct"] >= 30].sort_values(by="undervarderad_pct", ascending=False)
    else:
        return df.sort_values(by="undervarderad_pct", ascending=False)

import streamlit as st
import pandas as pd
import json
import os

DATA_PATH = "aktiedata.json"

# --- Funktion: Läs in data från JSON-fil ---
def lasa_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)

# --- Funktion: Spara data till JSON-fil ---
def spara_data(df: pd.DataFrame):
    with open(DATA_PATH, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# --- Funktion: Lägg till eller uppdatera bolag i DataFrame ---
def lagg_till_eller_uppdatera_bolag(df: pd.DataFrame, nytt_bolag: dict) -> pd.DataFrame:
    bolagsnamn_ny = nytt_bolag["bolagsnamn"].strip().lower()
    if df.empty:
        nytt_bolag["insatt_datum"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        nytt_bolag["senast_andrad"] = nytt_bolag["insatt_datum"]
        return pd.DataFrame([nytt_bolag])

    # Kontrollera om bolaget redan finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()
    if idx:
        # Uppdatera befintligt bolag
        idx = idx[0]
        for key, value in nytt_bolag.items():
            df.at[idx, key] = value
        df.at[idx, "senast_andrad"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Lägg till nytt bolag
        nytt_bolag["insatt_datum"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        nytt_bolag["senast_andrad"] = nytt_bolag["insatt_datum"]
        df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)
    return df

# --- Funktion: Visa formulär för inmatning och uppdatering ---
def visa_form(df: pd.DataFrame) -> pd.DataFrame:
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="bolag_form"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_1 = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_2 = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")
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
            if not bolagsnamn.strip():
                st.error("Bolagsnamn måste anges.")
            else:
                nytt_bolag = {
                    "bolagsnamn": bolagsnamn,
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_forra_aret": vinst_forra_aret,
                    "vinst_i_ar": vinst_i_ar,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "omsattning_forra_aret": omsattning_forra_aret,
                    "omsattningstillvaxt_1": omsattningstillvaxt_1,
                    "omsattningstillvaxt_2": omsattningstillvaxt_2,
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
                st.success(f"Bolag '{bolagsnamn}' sparades/uppdaterades.")
    return df

import numpy as np

# --- Funktion: Beräkna targetkurser och undervärdering ---
def berakna_targetkurser(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Säkerställ att numeriska kolumner är rätt typ
    num_cols = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "nuvarande_kurs",
        "nuvarande_ps", "ps_1", "ps_2",
        "omsattningstillvaxt_1", "omsattningstillvaxt_2"
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs baserat på P/E (medelvärde av pe_1 och pe_2)
    df["targetkurs_pe"] = df.apply(
        lambda row: row["vinst_nasta_ar"] * ((row["pe_1"] + row["pe_2"]) / 2)
        if row["vinst_nasta_ar"] > 0 and (row["pe_1"] + row["pe_2"]) > 0 else 0,
        axis=1,
    )

    # Medel omsättningstillväxt i decimalform
    oms_tillv = ((df["omsattningstillvaxt_1"] + df["omsattningstillvaxt_2"]) / 2) / 100

    # Targetkurs baserat på P/S och omsättningstillväxt
    df["targetkurs_ps"] = df.apply(
        lambda row: ((row["ps_1"] + row["ps_2"]) / 2) * (1 + oms_tillv.loc[row.name]) * row["nuvarande_kurs"]
        if ((row["ps_1"] + row["ps_2"]) > 0) and row["nuvarande_kurs"] > 0 else 0,
        axis=1,
    )

    # Undervärdering i procent (ju högre desto mer undervärderad)
    def undervarderad_procent(row):
        target = max(row["targetkurs_pe"], row["targetkurs_ps"])
        kurs = row["nuvarande_kurs"]
        if kurs > 0 and target > 0:
            return round((target - kurs) / target * 100, 2)
        return 0.0

    df["undervarderad_%"] = df.apply(undervarderad_procent, axis=1)

    # Köpvärd vid 30% rabatt på targetkurs (den högsta av targetkurs_pe och targetkurs_ps)
    df["kopvard_30_pct"] = df.apply(
        lambda row: round(max(row["targetkurs_pe"], row["targetkurs_ps"]) * 0.7, 2), axis=1
    )

    return df

# --- Funktion: Filtrera bolag baserat på undervärdering ---
def filtrera_bolag(df: pd.DataFrame, endast_undervarderade: bool = True) -> pd.DataFrame:
    if df.empty:
        return df
    df = berakna_targetkurser(df)
    if endast_undervarderade:
        df = df[df["undervarderad_%"] >= 30]
    df = df.sort_values(by="undervarderad_%", ascending=False)
    return df

# --- Funktion: Visa tabell med bolag och relevant info ---
def visa_oversikt(df: pd.DataFrame):
    st.header("Översikt av bolag")

    if df.empty:
        st.info("Inga bolag inlagda.")
        return

    visningskolumner = [
        "bolagsnamn",
        "nuvarande_kurs",
        "targetkurs_pe",
        "targetkurs_ps",
        "undervarderad_%",
        "kopvard_30_pct",
        "insatt_datum",
        "senast_andrad",
    ]

    # Kontrollera att kolumner finns
    visningskolumner = [col for col in visningskolumner if col in df.columns]

    tabell_df = df[visningskolumner].copy()
    tabell_df = tabell_df.rename(columns={
        "bolagsnamn": "Bolagsnamn",
        "nuvarande_kurs": "Nuvarande kurs",
        "targetkurs_pe": "Targetkurs P/E",
        "targetkurs_ps": "Targetkurs P/S",
        "undervarderad_%": "Undervärderad %",
        "kopvard_30_pct": "Köpvärd vid 30% rabatt",
        "insatt_datum": "Insatt datum",
        "senast_andrad": "Senast ändrad",
    })

    st.dataframe(tabell_df.style.format({
        "Nuvarande kurs": "{:.2f}",
        "Targetkurs P/E": "{:.2f}",
        "Targetkurs P/S": "{:.2f}",
        "Undervärderad %": "{:.2f}",
        "Köpvärd vid 30% rabatt": "{:.2f}",
    }), use_container_width=True)

# --- Funktion: Visa detaljerad vy och redigera bolag ---
def visa_och_redigera_bolag(df: pd.DataFrame) -> pd.DataFrame:
    st.header("Visa och redigera bolag")

    if df.empty:
        st.info("Inga bolag inlagda.")
        return df

    bolag_lista = df["bolagsnamn"].tolist()
    valt_bolag = st.selectbox("Välj bolag att visa/redigera", bolag_lista)

    if valt_bolag:
        bolagsdata = df[df["bolagsnamn"] == valt_bolag].iloc[0]

        with st.form(key=f"redigera_form_{valt_bolag}"):
            st.write(f"**Bolag:** {valt_bolag}")
            # Visa nuvarande kurs som read-only
            nuvarande_kurs = st.number_input(
                "Nuvarande kurs", value=float(bolagsdata["nuvarande_kurs"]), min_value=0.0, step=0.01
            )
            # Visa övriga fält som input
            vinst_forra_aret = st.number_input(
                "Vinst förra året", value=float(bolagsdata.get("vinst_forra_aret", 0)), step=0.01
            )
            vinst_aktuell_aret = st.number_input(
                "Förväntad vinst i år", value=float(bolagsdata.get("vinst_aktuell_aret", 0)), step=0.01
            )
            vinst_nasta_ar = st.number_input(
                "Förväntad vinst nästa år", value=float(bolagsdata.get("vinst_nasta_ar", 0)), step=0.01
            )
            omsattning_forra_aret = st.number_input(
                "Omsättning förra året", value=float(bolagsdata.get("omsattning_forra_aret", 0)), step=0.01
            )
            omsattningstillvaxt_1 = st.number_input(
                "Omsättningstillväxt i år (%)", value=float(bolagsdata.get("omsattningstillvaxt_1", 0)), step=0.01
            )
            omsattningstillvaxt_2 = st.number_input(
                "Omsättningstillväxt nästa år (%)", value=float(bolagsdata.get("omsattningstillvaxt_2", 0)), step=0.01
            )
            nuvarande_pe = st.number_input(
                "Nuvarande P/E", value=float(bolagsdata.get("nuvarande_pe", 0)), step=0.01
            )
            pe_1 = st.number_input(
                "P/E 1", value=float(bolagsdata.get("pe_1", 0)), step=0.01
            )
            pe_2 = st.number_input(
                "P/E 2", value=float(bolagsdata.get("pe_2", 0)), step=0.01
            )
            pe_3 = st.number_input(
                "P/E 3", value=float(bolagsdata.get("pe_3", 0)), step=0.01
            )
            pe_4 = st.number_input(
                "P/E 4", value=float(bolagsdata.get("pe_4", 0)), step=0.01
            )
            nuvarande_ps = st.number_input(
                "Nuvarande P/S", value=float(bolagsdata.get("nuvarande_ps", 0)), step=0.01
            )
            ps_1 = st.number_input(
                "P/S 1", value=float(bolagsdata.get("ps_1", 0)), step=0.01
            )
            ps_2 = st.number_input(
                "P/S 2", value=float(bolagsdata.get("ps_2", 0)), step=0.01
            )
            ps_3 = st.number_input(
                "P/S 3", value=float(bolagsdata.get("ps_3", 0)), step=0.01
            )
            ps_4 = st.number_input(
                "P/S 4", value=float(bolagsdata.get("ps_4", 0)), step=0.01
            )

            submit = st.form_submit_button("Uppdatera bolag")

        if submit:
            df.loc[df["bolagsnamn"] == valt_bolag, [
                "nuvarande_kurs",
                "vinst_forra_aret",
                "vinst_aktuell_aret",
                "vinst_nasta_ar",
                "omsattning_forra_aret",
                "omsattningstillvaxt_1",
                "omsattningstillvaxt_2",
                "nuvarande_pe",
                "pe_1",
                "pe_2",
                "pe_3",
                "pe_4",
                "nuvarande_ps",
                "ps_1",
                "ps_2",
                "ps_3",
                "ps_4",
                "senast_andrad",
            ]] = [
                nuvarande_kurs,
                vinst_forra_aret,
                vinst_aktuell_aret,
                vinst_nasta_ar,
                omsattning_forra_aret,
                omsattningstillvaxt_1,
                omsattningstillvaxt_2,
                nuvarande_pe,
                pe_1,
                pe_2,
                pe_3,
                pe_4,
                nuvarande_ps,
                ps_1,
                ps_2,
                ps_3,
                ps_4,
                pd.Timestamp.now().strftime("%Y-%m-%d"),
            ]
            st.success(f"Bolaget {valt_bolag} uppdaterades.")
            spara_data(df)

    return df

def main():
    st.set_page_config(page_title="Aktieanalysapp", layout="wide")

    st.title("Aktieanalysapp med undervärderingsanalys")

    df = las_in_data()

    menyval = st.sidebar.radio("Meny", ["Lägg till bolag", "Visa/redigera bolag", "Visa alla bolag"])

    if menyval == "Lägg till bolag":
        df = visa_form(df)
    elif menyval == "Visa/redigera bolag":
        df = visa_och_redigera_bolag(df)
    elif menyval == "Visa alla bolag":
        endast_undervarderade = st.checkbox("Visa endast undervärderade bolag (>30%)", value=False)
        filtrerad_df = filtrera_bolag(df, endast_undervarderade)
        visa_tabell(filtrerad_df)

    spara_data(df)


if __name__ == "__main__":
    main()
