import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "aktie_data.json"

def las_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            return df
    else:
        columns = [
            "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_i_ar_pct", "omsattningstillvaxt_nasta_ar_pct",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=columns)

def spara_data(df):
    df = df.fillna("")
    data = df.to_dict(orient="records")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    bolagsnamn_ny = bolag_ny["bolagsnamn"].strip().lower()
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if len(idx) > 0:
        # Uppdatera existerande rad
        i = idx[0]
        for key, value in bolag_ny.items():
            df.at[i, key] = value
        df.at[i, "senast_andrad"] = now_str
    else:
        # Lägg till ny rad
        bolag_ny["insatt_datum"] = now_str
        bolag_ny["senast_andrad"] = now_str
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)

    return df

def berakna_targetkurser(df):
    # Säkerställ att nödvändiga kolumner finns och är numeriska
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "nuvarande_kurs", "nuvarande_pe", "nuvarande_ps",
                "omsattning_forra_aret", "omsattningstillvaxt_i_ar_pct", "omsattningstillvaxt_nasta_ar_pct"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs baserat på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medel omsättningstillväxt i decimalform
    oms_tillvaxt_medel = ((df["omsattningstillvaxt_i_ar_pct"] + df["omsattningstillvaxt_nasta_ar_pct"]) / 2) / 100

    # Targetkurs baserat på P/S
    ps_medel = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = ps_medel * (1 + oms_tillvaxt_medel) * df["omsattning_forra_aret"]

    # Undervärdering i procent
    df["undervärdering_pe_pct"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"] * 100
    df["undervärdering_ps_pct"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"] * 100

    # Max undervärdering (den högsta av pe och ps)
    df["max_undervärdering"] = df[["undervärdering_pe_pct", "undervärdering_ps_pct"]].max(axis=1)

    # Köp-rekommendation (minst 30% undervärdering)
    df["kopvard"] = df["max_undervärdering"] >= 30

    return df

def visa_form(df):
    with st.form(key="form_lagg_till_bolag", clear_on_submit=True):
        st.header("Lägg till eller uppdatera bolag")

        bolagsnamn = st.text_input("Bolagsnamn", key="input_bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", key="input_nuvarande_kurs")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f", key="input_vinst_forra_aret")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f", key="input_vinst_i_ar")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f", key="input_vinst_nasta_ar")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f", key="input_omsattning_forra_aret")
        oms_tillvaxt_i_ar_pct = st.number_input("Förväntad omsättningstillväxt i år %", min_value=0.0, max_value=100.0, format="%.2f", key="input_oms_tillvaxt_i_ar")
        oms_tillvaxt_nasta_ar_pct = st.number_input("Förväntad omsättningstillväxt nästa år %", min_value=0.0, max_value=100.0, format="%.2f", key="input_oms_tillvaxt_nasta_ar")
        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f", key="input_nuvarande_pe")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f", key="input_pe_1")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f", key="input_pe_2")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f", key="input_pe_3")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f", key="input_pe_4")
        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f", key="input_nuvarande_ps")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f", key="input_ps_1")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f", key="input_ps_2")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f", key="input_ps_3")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f", key="input_ps_4")

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            if not bolagsnamn.strip():
                st.error("Bolagsnamn måste anges.")
            else:
                nytt_bolag = {
                    "bolagsnamn": bolagsnamn.strip(),
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_forra_aret": vinst_forra_aret,
                    "vinst_i_ar": vinst_i_ar,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "omsattning_forra_aret": omsattning_forra_aret,
                    "omsattningstillvaxt_i_ar_pct": oms_tillvaxt_i_ar_pct,
                    "omsattningstillvaxt_nasta_ar_pct": oms_tillvaxt_nasta_ar_pct,
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
                st.session_state["refresh"] = True
                st.experimental_rerun()

    return df

# --- Del 4: Visa bolag, filtrering, beräkningar och borttagning ---

import streamlit as st
import pandas as pd
from datetime import datetime

def berakna_targetkurser(df):
    # Kontrollera att nödvändiga kolumner finns innan beräkning
    pe_cols = ["pe_1", "pe_2"]
    ps_cols = ["ps_1", "ps_2"]
    for col in pe_cols + ps_cols + ["vinst_nasta_ar", "kurs"]:
        if col not in df.columns:
            df[col] = 0

    # Räkna targetkurs baserat på medelvärde av P/E 1 och 2 gånger förväntad vinst nästa år
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    
    # Räkna targetkurs baserat på medelvärde av P/S 1 och 2 gånger omsättningstillväxt och kurs
    # Omsättningstillväxt % måste vara i decimalform för korrekt beräkning
    df["omsättningstillväxt_medel"] = df[["omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar"]].mean(axis=1) / 100
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + df["omsättningstillväxt_medel"]) * df["kurs"]

    # Undervärdering i procent
    df["undervärdering_pe_%"] = (df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"] * 100
    df["undervärdering_ps_%"] = (df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"] * 100

    # Max undervärdering mellan P/E och P/S
    df["max_undervärdering"] = df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)

    # Lägg till kolumn för köpvärd (ja/nej) om max undervärdering är minst 30%
    df["kopvard"] = df["max_undervärdering"].apply(lambda x: "Ja" if x >= 30 else "Nej")

    return df

def visa_bolag(df):
    st.header("Visa bolag och undervärdering")

    visa_endast_undervarderade = st.checkbox("Visa endast undervärderade bolag (minst 30 % rabatt)")

    df = berakna_targetkurser(df)

    if visa_endast_undervarderade:
        filtrerat_df = df[df["max_undervärdering"] >= 30].copy()
    else:
        filtrerat_df = df.copy()

    if filtrerat_df.empty:
        st.info("Inga bolag att visa med valt filter.")
        return df

    # Sortera efter max undervärdering (störst först)
    filtrerat_df = filtrerat_df.sort_values(by="max_undervärdering", ascending=False)

    # Visa i tabell
    st.dataframe(filtrerat_df[[
        "bolagsnamn", "kurs", "vinst_forra_ar", "vinst_i_ar", "vinst_nasta_ar",
        "omsattning_forra_ar", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
        "pe_1", "pe_2", "pe_3", "pe_4",
        "ps_1", "ps_2", "ps_3", "ps_4",
        "targetkurs_pe", "targetkurs_ps", "undervärdering_pe_%", "undervärdering_ps_%", "max_undervärdering", "kopvard"
    ]])

    # Möjlighet att ta bort bolag
    ta_bort_bolag = st.selectbox("Välj bolag att ta bort", options=["--"] + filtrerat_df["bolagsnamn"].tolist())
    if ta_bort_bolag != "--":
        if st.button(f"Ta bort {ta_bort_bolag}"):
            df = df[df["bolagsnamn"].str.lower() != ta_bort_bolag.lower()]
            st.success(f"Bolaget {ta_bort_bolag} togs bort.")
            spara_data(df)  # Spara efter borttagning
            st.experimental_rerun()

    return df

# --- Del 5: Formulär, redigering, inmatning och sparfunktioner ---

import streamlit as st
import pandas as pd
from datetime import datetime

def las_data():
    """Läser in data från JSON-fil."""
    try:
        df = pd.read_json("data.json")
    except Exception:
        df = pd.DataFrame(columns=[
            "bolagsnamn", "kurs", "vinst_forra_ar", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_ar", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
            "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ])
    return df

def spara_data(df):
    """Sparar data till JSON-fil."""
    df.to_json("data.json", orient="records", indent=2)

def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    bolagsnamn_ny = bolag_ny["bolagsnamn"].strip().lower()
    if bolagsnamn_ny == "":
        st.warning("Bolagsnamn kan inte vara tomt.")
        return df

    # Kolla om bolaget redan finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if len(idx) > 0:
        # Uppdatera befintligt bolag
        i = idx[0]
        for key, value in bolag_ny.items():
            df.at[i, key] = value
        df.at[i, "senast_andrad"] = now_str
        st.success(f"Bolaget '{bolag_ny['bolagsnamn']}' uppdaterades.")
    else:
        # Lägg till nytt bolag
        bolag_ny["insatt_datum"] = now_str
        bolag_ny["senast_andrad"] = now_str
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)
        st.success(f"Bolaget '{bolag_ny['bolagsnamn']}' lades till.")

    return df

def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="form_lagg_till_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn", max_chars=50)
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_ar = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år (förväntad)", format="%.2f")
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

        submit_button = st.form_submit_button(label="Spara bolag")

    if submit_button:
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
            "ps_4": ps_4
        }
        df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
        spara_data(df)
        st.experimental_rerun()

    return df

def main():
    st.title("Aktieanalysapp - Komplett")

    df = las_data()

    # Visa formulär för inmatning/redigering
    df = visa_form(df)

    # Visa bolag och undervärdering med filter och möjlighet till borttagning
    df = visa_bolag(df)

    # Spara data om det ändrats (exempelvis från borttagning)
    spara_data(df)

if __name__ == "__main__":
    main()
