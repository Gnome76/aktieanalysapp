import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

# --- Funktioner för att läsa och spara data ---
def las_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att alla kolumner finns (om filen tom eller inkomplett)
        expected_cols = [
            "bolagsnamn", "kurs", "vinst_forra_aret", "vinst_aret", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_aret",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad",
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        return df[expected_cols]
    else:
        # Tom DataFrame med rätt kolumner
        return pd.DataFrame(columns=[
            "bolagsnamn", "kurs", "vinst_forra_aret", "vinst_aret", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_aret",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad",
        ])

def lagra_data(df):
    df = df.fillna("")  # Undvik NaN i JSON
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# --- Funktion för att beräkna targetkurser och undervärdering ---
def berakna_target_och_undervardering(df):
    # Om tom df, returnera direkt
    if df.empty:
        return df

    # Säkerställ numeriska typer
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "kurs",
                "ps_1", "ps_2", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_aret"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs PE = vinst_nasta_ar * medelvärdet av PE 1 och 2
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medelvärde omsättningstillväxt
    oms_tillv = (df["omsattningstillvaxt_aret"] + df["omsattningstillvaxt_nasta_aret"]) / 2 / 100

    # Targetkurs PS = medelvärde av PS 1 och 2 * medel omsättningstillväxt * kurs nu (för skalning)
    # Notera: Vi tolkar PS som P/S * omsättningstillväxt * kurs
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + oms_tillv) * df["kurs"]

    # Undervärdering - max rabatt mellan PE och PS target jämfört med kurs
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"]
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    # Köp-värd vid 30% rabatt
    df["kopvard"] = df["undervardering"] >= 0.3

    # Hantera ev. oändligheter och NaN
    df.replace([float('inf'), -float('inf')], 0, inplace=True)
    df["undervardering"] = df["undervardering"].fillna(0)

    return df

# --- Funktion för att lägga till eller uppdatera ett bolag ---
def lagg_till_eller_uppdatera_bolag(df, ny_bolag):
    ny_bolag_namn = ny_bolag["bolagsnamn"].strip().lower()
    if ny_bolag_namn == "":
        st.warning("Bolagsnamn kan inte vara tomt.")
        return df

    # Kontrollera om bolaget redan finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == ny_bolag_namn]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if len(idx) > 0:
        # Uppdatera existerande rad
        i = idx[0]
        for key, value in ny_bolag.items():
            df.at[i, key] = value
        df.at[i, "senast_andrad"] = now_str
    else:
        # Lägg till nytt bolag
        ny_bolag["insatt_datum"] = now_str
        ny_bolag["senast_andrad"] = now_str
        df = pd.concat([df, pd.DataFrame([ny_bolag])], ignore_index=True)

    return df

# --- Funktion för att ta bort bolag ---
def ta_bort_bolag(df, bolag_namn):
    bolag_namn = bolag_namn.strip().lower()
    idx = df.index[df["bolagsnamn"].str.lower() == bolag_namn]
    if len(idx) > 0:
        df = df.drop(idx[0]).reset_index(drop=True)
        st.success(f"Bolaget '{bolag_namn}' borttaget.")
    else:
        st.warning(f"Bolaget '{bolag_namn}' hittades inte.")
    return df

# --- Funktion för att visa och hantera inmatningsformulär ---
def visa_form(df):
    st.header("Lägg till / Uppdatera bolag")

    with st.form(key="bolagsform"):
        bolagsnamn = st.text_input("Bolagsnamn")
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_aret = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_aret = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
        omsattningstillvaxt_nasta_aret = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
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

        skickaknapp = st.form_submit_button("Spara")

    if skickaknapp:
        ny_bolag = {
            "bolagsnamn": bolagsnamn,
            "kurs": kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_aret": vinst_aret,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_forra_aret": omsattning_forra_aret,
            "omsattningstillvaxt_aret": omsattningstillvaxt_aret,
            "omsattningstillvaxt_nasta_aret": omsattningstillvaxt_nasta_aret,
            "pe_nu": pe_nu,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "pe_3": pe_3,
            "pe_4": pe_4,
            "ps_nu": ps_nu,
            "ps_1": ps_1,
            "ps_2": ps_2,
            "ps_3": ps_3,
            "ps_4": ps_4,
        }
        df = lagg_till_eller_uppdatera_bolag(df, ny_bolag)
        lagra_data(df)
        st.success(f"Bolaget '{bolagsnamn}' har sparats.")
        # Uppdatera sidans tillstånd utan att starta om appen
        st.experimental_rerun()

    return df

# --- Funktion för att beräkna targetkurser och undervärdering ---
def berakna_target_och_undervardering(df):
    # Beräkna medelvärde för P/E 1-4 och P/S 1-4 för target
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df[["pe_1", "pe_2", "pe_3", "pe_4"]].mean(axis=1)))
    omsattningstillvaxt_mean = df[["omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_aret"]].mean(axis=1) / 100
    df["targetkurs_ps"] = ((df[["ps_1", "ps_2", "ps_3", "ps_4"]].mean(axis=1)) *
                          (1 + omsattningstillvaxt_mean) * df["omsattning_forra_aret"])

    # Undervärdering % beräknas som (target - kurs) / target
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"]

    # Högsta undervärdering av P/E eller P/S
    df["undervardering_max"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    # Köpbar om minst 30% undervärderad (30% rabatt)
    df["kopvard"] = df["undervardering_max"] >= 0.3

    return df

# --- Funktion för att visa bolag i tabell med filter och borttagning ---
def visa_oversikt(df):
    st.header("Översikt över bolag")

    visa_enda_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)

    if visa_enda_undervarderade:
        visad_df = df[df["kopvard"] == True].copy()
    else:
        visad_df = df.copy()

    if visad_df.empty:
        st.info("Inga bolag att visa med valt filter.")
        return

    visad_df = visad_df.sort_values(by="undervardering_max", ascending=False)

    # Visa tabell utan index och med rundade värden
    tabell_df = visad_df[[
        "bolagsnamn", "kurs",
        "targetkurs_pe", "targetkurs_ps",
        "undervardering_pe", "undervardering_ps", "undervardering_max", "kopvard"
    ]].round(2)

    st.dataframe(tabell_df, use_container_width=True)

    # Ta bort bolag via selectbox
    st.subheader("Ta bort bolag")
    bolag_till_borttagning = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].sort_values())
    if st.button("Ta bort valt bolag"):
        df = ta_bort_bolag(df, bolag_till_borttagning)
        lagra_data(df)
        st.experimental_rerun()

    return df

# --- Huvudfunktion ---
def main():
    st.title("Aktieanalysapp")

    df = las_data()

    df = berakna_target_och_undervardering(df)

    df = visa_form(df)

    df = visa_oversikt(df)

    lagra_data(df)

if __name__ == "__main__":
    main()

# --- Funktion för att ta bort bolag från DataFrame ---
def ta_bort_bolag(df, bolagsnamn):
    if bolagsnamn in df["bolagsnamn"].values:
        df = df[df["bolagsnamn"] != bolagsnamn].reset_index(drop=True)
        st.success(f"Bolaget '{bolagsnamn}' har tagits bort.")
    else:
        st.warning(f"Bolaget '{bolagsnamn}' hittades inte.")
    return df

# --- Funktion för att läsa data från json ---
def las_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att alla kolumner finns
        for col in kolumner:
            if col not in df.columns:
                df[col] = np.nan
        return df
    except FileNotFoundError:
        # Om fil inte finns, skapa tom df med rätt kolumner
        return pd.DataFrame(columns=kolumner)

# --- Funktion för att lagra data till json ---
def lagra_data(df):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

# --- Kolumnlista för data ---
kolumner = [
    "bolagsnamn", "kurs",
    "vinst_forra_aret", "vinst_aret", "vinst_nasta_ar",
    "omsattning_forra_aret", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_aret",
    "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
    "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4"
]

if __name__ == "__main__":
    main()
