import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_PATH = "aktiedata.json"

def las_in_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            if not df.empty:
                df["insatt_datum"] = pd.to_datetime(df["insatt_datum"])
                df["senast_andrad"] = pd.to_datetime(df["senast_andrad"])
            return df
    else:
        # Skapa tom DataFrame med rätt kolumner om fil saknas
        kolumner = [
            "bolagsnamn", "kurs", "vinst_fjol", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_ar_1", "omsattningstillvaxt_ar_2",
            "pe_aktuell", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_aktuell", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=kolumner)

def spara_data(df):
    # Konvertera datum till str innan sparande
    df_spara = df.copy()
    df_spara["insatt_datum"] = df_spara["insatt_datum"].astype(str)
    df_spara["senast_andrad"] = df_spara["senast_andrad"].astype(str)
    with open(DATA_PATH, "w") as f:
        json.dump(df_spara.to_dict(orient="records"), f, indent=2)

def lagg_till_eller_uppdatera_bolag(df, nytt_bolag):
    bolagsnamn_ny = nytt_bolag["bolagsnamn"].lower()
    # Kontrollera om bolaget redan finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()

    nu = datetime.now()

    if idx:
        # Uppdatera befintligt bolag
        i = idx[0]
        for key, value in nytt_bolag.items():
            df.at[i, key] = value
        df.at[i, "senast_andrad"] = nu
    else:
        # Lägg till nytt bolag
        nytt_bolag["insatt_datum"] = nu
        nytt_bolag["senast_andrad"] = nu
        df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)
    return df

def berakna_targetkurser(df):
    if df.empty:
        return df

    def calc_target_pe(row):
        try:
            return row["vinst_nasta_ar"] * ((row["pe_1"] + row["pe_2"]) / 2)
        except Exception:
            return None

    def calc_target_ps(row):
        try:
            ps_avg = (row["ps_1"] + row["ps_2"]) / 2
            tillvaxt_avg = (row["omsattningstillvaxt_ar_1"] + row["omsattningstillvaxt_ar_2"]) / 2 / 100
            return ps_avg * (1 + tillvaxt_avg) * row["kurs"]
        except Exception:
            return None

    df["targetkurs_pe"] = df.apply(calc_target_pe, axis=1)
    df["targetkurs_ps"] = df.apply(calc_target_ps, axis=1)

    # Beräkna undervärdering i procent
    def calc_undervardering(row):
        try:
            underv_pe = (row["targetkurs_pe"] - row["kurs"]) / row["targetkurs_pe"] * 100 if row["targetkurs_pe"] else None
            underv_ps = (row["targetkurs_ps"] - row["kurs"]) / row["targetkurs_ps"] * 100 if row["targetkurs_ps"] else None
            if underv_pe is None and underv_ps is None:
                return None
            elif underv_pe is None:
                return underv_ps
            elif underv_ps is None:
                return underv_pe
            else:
                return max(underv_pe, underv_ps)
        except Exception:
            return None

    df["undervarderad_procent"] = df.apply(calc_undervardering, axis=1)
    df["kopvard_30procent"] = df["targetkurs_pe"] * 0.7

    return df

import os
import json

DATA_PATH = "aktiedata.json"

def las_in_data():
    if not os.path.exists(DATA_PATH):
        # Returnera tom DataFrame med rätt kolumner om filen inte finns
        kolumner = [
            "bolagsnamn", "kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_ar_1", "omsattningstillvaxt_ar_2",
            "pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=kolumner)
    else:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Konvertera datumfält till datetime
        if "insatt_datum" in df.columns:
            df["insatt_datum"] = pd.to_datetime(df["insatt_datum"], errors="coerce")
        if "senast_andrad" in df.columns:
            df["senast_andrad"] = pd.to_datetime(df["senast_andrad"], errors="coerce")
        # Säkerställ numeriska kolumner är rätt typ
        num_cols = [
            "kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_ar_1", "omsattningstillvaxt_ar_2",
            "pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps", "ps_1", "ps_2", "ps_3", "ps_4"
        ]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

def spara_data(df):
    # Om datumfält finns, konvertera till str för JSON
    df_skriv = df.copy()
    for col in ["insatt_datum", "senast_andrad"]:
        if col in df_skriv.columns:
            df_skriv[col] = df_skriv[col].astype(str)
    with open(DATA_PATH, "w") as f:
        f.write(df_skriv.to_json(orient="records", force_ascii=False))

def formatera_datum(dt):
    if pd.isna(dt):
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M")

from datetime import datetime

def lagg_till_eller_uppdatera_bolag(df, nytt_bolag):
    bolagsnamn_ny = nytt_bolag["bolagsnamn"].strip().lower()
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()

    now = datetime.now()

    if idx:
        # Uppdatera befintligt bolag
        i = idx[0]
        for nyckel, varde in nytt_bolag.items():
            df.at[i, nyckel] = varde
        df.at[i, "senast_andrad"] = now
    else:
        # Lägg till nytt bolag
        nytt_bolag["insatt_datum"] = now
        nytt_bolag["senast_andrad"] = now
        df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)
    return df

def beräkna_targetkurser(df):
    if df.empty:
        return df

    def safe_mean(vals):
        vals = [v for v in vals if pd.notna(v)]
        if not vals:
            return None
        return sum(vals) / len(vals)

    # Targetkurs baserad på P/E
    df["targetkurs_pe"] = df.apply(
        lambda row: row["vinst_nasta_ar"] * safe_mean([row.get("pe_1"), row.get("pe_2")])
        if pd.notna(row["vinst_nasta_ar"]) and safe_mean([row.get("pe_1"), row.get("pe_2")]) else None,
        axis=1,
    )

    # Targetkurs baserad på P/S, beräknas som medelvärde av P/S * medel omsättningstillväxt * omsättning förra året
    df["targetkurs_ps"] = df.apply(
        lambda row: (
            row["omsattning_forra_aret"]
            * safe_mean([row.get("ps_1"), row.get("ps_2")])
            * (1 + safe_mean([row.get("omsattningstillvaxt_ar_1"), row.get("omsattningstillvaxt_ar_2")]) / 100)
            if pd.notna(row["omsattning_forra_aret"]) and safe_mean([row.get("ps_1"), row.get("ps_2")]) and safe_mean([row.get("omsattningstillvaxt_ar_1"), row.get("omsattningstillvaxt_ar_2")]) is not None
            else None
        ),
        axis=1,
    )

    # Undervärdering i procent baserat på lägsta targetkurs av P/E och P/S
    def undervarderad_pct(row):
        if pd.isna(row["kurs"]) or (pd.isna(row["targetkurs_pe"]) and pd.isna(row["targetkurs_ps"])):
            return None
        target_min = min(filter(pd.notna, [row["targetkurs_pe"], row["targetkurs_ps"]]), default=None)
        if target_min is None or target_min == 0:
            return None
        return round((target_min - row["kurs"]) / target_min * 100, 2)

    df["undervarderad_pct"] = df.apply(undervarderad_pct, axis=1)

    # Köp vid 30% rabatt (målpris = targetkurs * 0.7)
    def kopvard_pris(row):
        target_min = min(filter(pd.notna, [row.get("targetkurs_pe"), row.get("targetkurs_ps")]), default=None)
        if target_min is None:
            return None
        return round(target_min * 0.7, 2)

    df["kopvard_30"] = df.apply(kopvard_pris, axis=1)

    return df

def filtrera_bolag(df, endast_undervarderade):
    df = beräkna_targetkurser(df)
    if endast_undervarderade:
        df = df[df["undervarderad_pct"] >= 30]
    # Sortera på undervärdering (fallande)
    df = df.sort_values(by="undervarderad_pct", ascending=False)
    return df.reset_index(drop=True)

import streamlit as st

def ta_bort_bolag(df, bolagsnamn):
    bolagsnamn = bolagsnamn.strip().lower()
    df = df[~(df["bolagsnamn"].str.lower() == bolagsnamn)].reset_index(drop=True)
    return df

def visa_oversikt_tabell(df):
    if df.empty:
        st.info("Inga bolag att visa.")
        return
    st.dataframe(df[[
        "bolagsnamn", "kurs", "targetkurs_pe", "targetkurs_ps", "undervarderad_pct", "kopvard_30"
    ]].style.format({
        "kurs": "{:.2f}",
        "targetkurs_pe": "{:.2f}",
        "targetkurs_ps": "{:.2f}",
        "undervarderad_pct": "{:.2f} %",
        "kopvard_30": "{:.2f}",
    }))

def visa_enskild_bolagsvy(df, index):
    if df.empty or index >= len(df) or index < 0:
        st.info("Inget bolag valt eller index utanför intervall.")
        return

    bolag = df.iloc[index]

    st.subheader(f"Bolag: {bolag['bolagsnamn']}")
    st.markdown(f"**Nuvarande kurs:** {bolag['kurs']:.2f} SEK")
    st.markdown(f"**Targetkurs P/E:** {bolag['targetkurs_pe']:.2f} SEK")
    st.markdown(f"**Targetkurs P/S:** {bolag['targetkurs_ps']:.2f} SEK")
    st.markdown(f"**Undervärdering:** {bolag['undervarderad_pct']:.2f} %")
    st.markdown(f"**Köpvärd vid 30% rabatt:** {bolag['kopvard_30']:.2f} SEK")

    # Visa övriga nyckeltal
    nyckeltal = {
        "Vinst förra året": bolag.get("vinst_forra_aret", "N/A"),
        "Vinst nästa år": bolag.get("vinst_nasta_ar", "N/A"),
        "Omsättning förra året": bolag.get("omsattning_forra_aret", "N/A"),
        "Omsättningstillväxt år 1 (%)": bolag.get("omsattningstillvaxt_ar_1", "N/A"),
        "Omsättningstillväxt år 2 (%)": bolag.get("omsattningstillvaxt_ar_2", "N/A"),
        "P/E nuvarande": bolag.get("pe_nuvarande", "N/A"),
        "P/E 1": bolag.get("pe_1", "N/A"),
        "P/E 2": bolag.get("pe_2", "N/A"),
        "P/S nuvarande": bolag.get("ps_nuvarande", "N/A"),
        "P/S 1": bolag.get("ps_1", "N/A"),
        "P/S 2": bolag.get("ps_2", "N/A"),
        "Insatt datum": bolag.get("insatt_datum", "N/A"),
        "Senast ändrad": bolag.get("senast_andrad", "N/A"),
    }
    for nyckel, varde in nyckeltal.items():
        st.markdown(f"**{nyckel}:** {varde}")

def huvudmeny(df):
    st.sidebar.title("Aktieanalysapp")
    menyval = st.sidebar.radio("Välj vy", ["Visa översikt", "Lägg till / Uppdatera bolag", "Ta bort bolag", "Visa bolag enskilt"])
    return menyval

import streamlit as st

def main():
    st.title("Aktieanalysapp")

    df = las_in_data()

    menyval = huvudmeny(df)

    if menyval == "Visa översikt":
        endast_undervarderade = st.checkbox("Visa endast undervärderade bolag (minst 30 % rabatt)", value=False)
        filtrerad_df = filtrera_bolag(df, endast_undervarderade)
        visa_oversikt_tabell(filtrerad_df)

    elif menyval == "Lägg till / Uppdatera bolag":
        df = visa_form(df)
        spara_data(df)
        st.success("Bolagsdata uppdaterad och sparad.")

    elif menyval == "Ta bort bolag":
        bolagslista = df["bolagsnamn"].tolist()
        vald_bolag = st.selectbox("Välj bolag att ta bort", bolagslista)
        if st.button("Ta bort valt bolag"):
            df = ta_bort_bolag(df, vald_bolag)
            spara_data(df)
            st.success(f"Bolag '{vald_bolag}' borttaget.")

    elif menyval == "Visa bolag enskilt":
        if df.empty:
            st.info("Ingen data att visa.")
            return
        index = st.number_input("Ange bolagsindex att visa (0-bas)", min_value=0, max_value=len(df)-1, value=0, step=1)
        visa_enskild_bolagsvy(df, index)

    # Säkerställ att session state uppdateras korrekt utan st.experimental_rerun()
    if "refresh" in st.session_state and st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
