import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

DATA_PATH = "data.json"

# Lista över alla kolumnnamn i korrekt ordning
COLUMNS = [
    "bolagsnamn",
    "nuvarande_kurs",
    "vinst_fjol",
    "vinst_i_ar",
    "vinst_nasta_ar",
    "omsattning_fjol",
    "omsattningstillvaxt_ar",
    "omsattningstillvaxt_nasta_ar",
    "pe_nuvarande",
    "pe_1",
    "pe_2",
    "pe_3",
    "pe_4",
    "ps_nuvarande",
    "ps_1",
    "ps_2",
    "ps_3",
    "ps_4",
    "insatt_datum",
    "senast_andrad"
]

def las_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            # Säkerställ alla kolumner finns, lägg till tomma om saknas
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = None
            return df[COLUMNS]
    else:
        return pd.DataFrame(columns=COLUMNS)

def spara_data(df):
    df.to_json(DATA_PATH, orient="records", force_ascii=False, indent=2)

def berakna_target_och_undervardering(df):
    # Beräkna targetkurs_pe och targetkurs_ps enligt formeln från överenskommelsen
    # För att undvika keyerror om tom df:
    if df.empty:
        return df
    # Gör om kolumner till numeriska (om inte redan)
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "nuvarande_kurs",
                "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    omsattningstillvaxt_genomsnitt = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100
    omsattningstillvaxt_genomsnitt = omsattningstillvaxt_genomsnitt.fillna(0)
    ps_medel = (df["ps_1"] + df["ps_2"]) / 2

    df["targetkurs_ps"] = ps_medel * (1 + omsattningstillvaxt_genomsnitt) * df["omsattning_fjol"]

    df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]

    # Ta största undervärdering
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)
    df["undervardering"] = df["undervardering"].fillna(0)
    return df

def hamta_input_varden(existerande=None):
    """Returnerar dict med input-värden, använder session_state för att behålla data"""
    def valfilt(key, dtype=float):
        # Prioritera session_state, sedan existerande data, annars default
        if key in st.session_state:
            return st.session_state[key]
        if existerande is not None and existerande.get(key) is not None:
            return existerande[key]
        return 0.0 if dtype==float else ""

    data = {}
    data["nuvarande_kurs"] = st.number_input("Nuvarande kurs", value=valfilt("nuvarande_kurs"), key="nuvarande_kurs")
    data["vinst_fjol"] = st.number_input("Vinst förra året", value=valfilt("vinst_fjol"), key="vinst_fjol")
    data["vinst_i_ar"] = st.number_input("Förväntad vinst i år", value=valfilt("vinst_i_ar"), key="vinst_i_ar")
    data["vinst_nasta_ar"] = st.number_input("Förväntad vinst nästa år", value=valfilt("vinst_nasta_ar"), key="vinst_nasta_ar")
    data["omsattning_fjol"] = st.number_input("Omsättning förra året", value=valfilt("omsattning_fjol"), key="omsattning_fjol")
    data["omsattningstillvaxt_ar"] = st.number_input("Förväntad omsättningstillväxt i år %", value=valfilt("omsattningstillvaxt_ar"), key="omsattningstillvaxt_ar")
    data["omsattningstillvaxt_nasta_ar"] = st.number_input("Förväntad omsättningstillväxt nästa år %", value=valfilt("omsattningstillvaxt_nasta_ar"), key="omsattningstillvaxt_nasta_ar")
    data["pe_nuvarande"] = st.number_input("Nuvarande P/E", value=valfilt("pe_nuvarande"), key="pe_nuvarande")
    data["pe_1"] = st.number_input("P/E 1", value=valfilt("pe_1"), key="pe_1")
    data["pe_2"] = st.number_input("P/E 2", value=valfilt("pe_2"), key="pe_2")
    data["pe_3"] = st.number_input("P/E 3", value=valfilt("pe_3"), key="pe_3")
    data["pe_4"] = st.number_input("P/E 4", value=valfilt("pe_4"), key="pe_4")
    data["ps_nuvarande"] = st.number_input("Nuvarande P/S", value=valfilt("ps_nuvarande"), key="ps_nuvarande")
    data["ps_1"] = st.number_input("P/S 1", value=valfilt("ps_1"), key="ps_1")
    data["ps_2"] = st.number_input("P/S 2", value=valfilt("ps_2"), key="ps_2")
    data["ps_3"] = st.number_input("P/S 3", value=valfilt("ps_3"), key="ps_3")
    data["ps_4"] = st.number_input("P/S 4", value=valfilt("ps_4"), key="ps_4")
    return data

def rensa_session_state_keys():
    # Ta bort alla input-relaterade nycklar från session_state efter spar
    keys = [
        "bolagsnamn",
        "nuvarande_kurs",
        "vinst_fjol",
        "vinst_i_ar",
        "vinst_nasta_ar",
        "omsattning_fjol",
        "omsattningstillvaxt_ar",
        "omsattningstillvaxt_nasta_ar",
        "pe_nuvarande",
        "pe_1",
        "pe_2",
        "pe_3",
        "pe_4",
        "ps_nuvarande",
        "ps_1",
        "ps_2",
        "ps_3",
        "ps_4"
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

def bolagsform(df):
    st.header("Lägg till eller uppdatera bolag")

    # Välj bolag att redigera eller nytt bolag
    bolagslista = sorted(df["bolagsnamn"].dropna().unique()) if not df.empty else []
    valt_bolag = st.selectbox("Välj bolag att redigera eller skriv nytt", [""] + bolagslista, index=0, key="bolagsnamn")

    existerande_data = None
    if valt_bolag and valt_bolag in df["bolagsnamn"].values:
        existerande_data = df.loc[df["bolagsnamn"] == valt_bolag].iloc[0].to_dict()

    # Visa fält och fyll med existerande data eller session_state
    with st.form(key="bolagsformulär"):
        bolagsnamn = st.text_input("Bolagsnamn", value=valt_bolag if valt_bolag else "", key="bolagsnamn_input")

        # Hämta eller visa inputfält
        input_data = hamta_input_varden(existerande_data)

        # Spara-knapp
        spara = st.form_submit_button("Spara")

    if spara:
        if not bolagsnamn.strip():
            st.error("Ange ett bolagsnamn.")
            return df

        # Kolla om bolaget redan finns
        idx = df.index[df["bolagsnamn"] == bolagsnamn.strip()]
        nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if len(idx) > 0:
            # Uppdatera existerande bolag
            df.loc[idx[0], "nuvarande_kurs"] = input_data["nuvarande_kurs"]
            df.loc[idx[0], "vinst_fjol"] = input_data["vinst_fjol"]
            df.loc[idx[0], "vinst_i_ar"] = input_data["vinst_i_ar"]
            df.loc[idx[0], "vinst_nasta_ar"] = input_data["vinst_nasta_ar"]
            df.loc[idx[0], "omsattning_fjol"] = input_data["omsattning_fjol"]
            df.loc[idx[0], "omsattningstillvaxt_ar"] = input_data["omsattningstillvaxt_ar"]
            df.loc[idx[0], "omsattningstillvaxt_nasta_ar"] = input_data["omsattningstillvaxt_nasta_ar"]
            df.loc[idx[0], "pe_nuvarande"] = input_data["pe_nuvarande"]
            df.loc[idx[0], "pe_1"] = input_data["pe_1"]
            df.loc[idx[0], "pe_2"] = input_data["pe_2"]
            df.loc[idx[0], "pe_3"] = input_data["pe_3"]
            df.loc[idx[0], "pe_4"] = input_data["pe_4"]
            df.loc[idx[0], "ps_nuvarande"] = input_data["ps_nuvarande"]
            df.loc[idx[0], "ps_1"] = input_data["ps_1"]
            df.loc[idx[0], "ps_2"] = input_data["ps_2"]
            df.loc[idx[0], "ps_3"] = input_data["ps_3"]
            df.loc[idx[0], "ps_4"] = input_data["ps_4"]
            df.loc[idx[0], "senast_andrad"] = nu
        else:
            # Lägg till nytt bolag
            ny_rad = {
                "bolagsnamn": bolagsnamn.strip(),
                "nuvarande_kurs": input_data["nuvarande_kurs"],
                "vinst_fjol": input_data["vinst_fjol"],
                "vinst_i_ar": input_data["vinst_i_ar"],
                "vinst_nasta_ar": input_data["vinst_nasta_ar"],
                "omsattning_fjol": input_data["omsattning_fjol"],
                "omsattningstillvaxt_ar": input_data["omsattningstillvaxt_ar"],
                "omsattningstillvaxt_nasta_ar": input_data["omsattningstillvaxt_nasta_ar"],
                "pe_nuvarande": input_data["pe_nuvarande"],
                "pe_1": input_data["pe_1"],
                "pe_2": input_data["pe_2"],
                "pe_3": input_data["pe_3"],
                "pe_4": input_data["pe_4"],
                "ps_nuvarande": input_data["ps_nuvarande"],
                "ps_1": input_data["ps_1"],
                "ps_2": input_data["ps_2"],
                "ps_3": input_data["ps_3"],
                "ps_4": input_data["ps_4"],
                "insatt_datum": nu,
                "senast_andrad": nu
            }
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)

        spara_data(df)
        rensa_session_state_keys()
        st.success(f"Bolag '{bolagsnamn.strip()}' sparat.")
    return df

def ta_bort_bolag(df):
    st.header("Ta bort bolag")

    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df

    bolagslista = sorted(df["bolagsnamn"].dropna().unique())
    valt_bolag = st.selectbox("Välj bolag att ta bort", bolagslista)

    if st.button("Ta bort bolag"):
        df = df[df["bolagsnamn"] != valt_bolag].reset_index(drop=True)
        spara_data(df)
        st.success(f"Bolaget '{valt_bolag}' har tagits bort.")
        st.experimental_rerun()

    return df


def berakna_target_och_undervardering(df):
    if df.empty:
        return df

    # Säkerställ att alla kolumner finns och är numeriska
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "nuvarande_kurs", "ps_nuvarande", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Beräkna targetkurs_pe enligt ny formel
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medelvärde omsättningstillväxt år 1 och 2 (i decimalform)
    omsattningstillvaxt_medel = ((df["omsattningstillvaxt_ar"] / 100) + (df["omsattningstillvaxt_nasta_ar"] / 100)) / 2

    # Medelvärde av P/S 1 och 2
    ps_medel = (df["ps_1"] + df["ps_2"]) / 2

    # Beräkna targetkurs_ps enligt ny formel
    df["targetkurs_ps"] = ps_medel * omsattningstillvaxt_medel * df["nuvarande_kurs"]

    # Undervärdering som max av procentuell rabatt på targetkurs_pe och targetkurs_ps
    def räkna_undervardering(row):
        target_pe = row["targetkurs_pe"]
        target_ps = row["targetkurs_ps"]
        kurs = row["nuvarande_kurs"]
        underv_pe = (target_pe - kurs) / target_pe if target_pe > 0 else 0
        underv_ps = (target_ps - kurs) / target_ps if target_ps > 0 else 0
        return max(underv_pe, underv_ps, 0)

    df["undervardering"] = df.apply(räkna_undervardering, axis=1)

    return df


def visa_aktier_en_i_taget(df):
    st.header("Undervärderade bolag – en i taget")

    if df.empty:
        st.info("Inga bolag att visa.")
        return

    # Filtrera undervärderade (minst 30% undervärderade)
    undervard_df = df[df["undervardering"] >= 0.3]

    if undervard_df.empty:
        st.info("Inga bolag är minst 30% undervärderade.")
        return

    # Index för bläddring sparas i session_state
    if "aktie_index" not in st.session_state:
        st.session_state.aktie_index = 0

    # Visa valt bolag
    aktie = undervard_df.iloc[st.session_state.aktie_index]

    st.subheader(aktie["bolagsnamn"])
    st.write(f"Nuvarande kurs: {aktie['nuvarande_kurs']:.2f} SEK")
    st.write(f"Targetkurs P/E: {aktie['targetkurs_pe']:.2f} SEK")
    st.write(f"Targetkurs P/S: {aktie['targetkurs_ps']:.2f} SEK")
    st.write(f"Undervärdering: {aktie['undervardering']*100:.1f} %")

    # Visa övriga nyckeltal i tabellform
    nyckeltal = {
        "Vinst förra året": aktie["vinst_fjol"],
        "Förväntad vinst i år": aktie["vinst_i_ar"],
        "Förväntad vinst nästa år": aktie["vinst_nasta_ar"],
        "Omsättning förra året": aktie["omsattning_fjol"],
        "Omsättningstillväxt i år %": aktie["omsattningstillvaxt_ar"],
        "Omsättningstillväxt nästa år %": aktie["omsattningstillvaxt_nasta_ar"],
        "Nuvarande P/E": aktie["pe_nuvarande"],
        "P/E 1": aktie["pe_1"],
        "P/E 2": aktie["pe_2"],
        "P/E 3": aktie["pe_3"],
        "P/E 4": aktie["pe_4"],
        "Nuvarande P/S": aktie["ps_nuvarande"],
        "P/S 1": aktie["ps_1"],
        "P/S 2": aktie["ps_2"],
        "P/S 3": aktie["ps_3"],
        "P/S 4": aktie["ps_4"]
    }

    st.table(pd.DataFrame.from_dict(nyckeltal, orient="index", columns=["Värde"]))

    # Navigeringsknappar
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("Föregående"):
            st.session_state.aktie_index = (st.session_state.aktie_index - 1) % len(undervard_df)
    with col3:
        if st.button("Nästa"):
            st.session_state.aktie_index = (st.session_state.aktie_index + 1) % len(undervard_df)

def main():
    st.title("Aktieanalysapp - Undervärderade bolag")

    # Läs in data från json
    df = las_data()

    # Menyval
    meny = st.sidebar.radio("Välj funktion", ["Visa alla bolag", "Lägg till/uppdatera bolag", "Ta bort bolag", "Visa undervärderade en i taget"])

    if meny == "Visa alla bolag":
        if df.empty:
            st.info("Inga bolag sparade än.")
        else:
            df = berakna_target_och_undervardering(df)
            visa_df = df.copy()
            visa_df["undervardering %"] = (visa_df["undervardering"] * 100).round(1)
            visa_df = visa_df.sort_values(by="undervardering", ascending=False)
            st.dataframe(visa_df[["bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering %"]])

    elif meny == "Lägg till/uppdatera bolag":
        df = lagg_till_eller_uppdatera_bolag(df)

    elif meny == "Ta bort bolag":
        df = ta_bort_bolag(df)

    elif meny == "Visa undervärderade en i taget":
        df = berakna_target_och_undervardering(df)
        visa_aktier_en_i_taget(df)

if __name__ == "__main__":
    main()
