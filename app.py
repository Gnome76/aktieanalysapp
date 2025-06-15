import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_PATH = "data.json"

def las_in_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs",
            "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_ar_1_pct", "omsattningstillvaxt_ar_2_pct",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad",
        ])
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Säkerställ rätt datatyper
    df["nuvarande_kurs"] = pd.to_numeric(df["nuvarande_kurs"], errors="coerce")
    df["vinst_forra_aret"] = pd.to_numeric(df["vinst_forra_aret"], errors="coerce")
    df["vinst_i_ar"] = pd.to_numeric(df["vinst_i_ar"], errors="coerce")
    df["vinst_nasta_ar"] = pd.to_numeric(df["vinst_nasta_ar"], errors="coerce")
    df["omsattning_forra_aret"] = pd.to_numeric(df["omsattning_forra_aret"], errors="coerce")
    df["omsattningstillvaxt_ar_1_pct"] = pd.to_numeric(df["omsattningstillvaxt_ar_1_pct"], errors="coerce")
    df["omsattningstillvaxt_ar_2_pct"] = pd.to_numeric(df["omsattningstillvaxt_ar_2_pct"], errors="coerce")
    df["nuvarande_pe"] = pd.to_numeric(df["nuvarande_pe"], errors="coerce")
    df["pe_1"] = pd.to_numeric(df["pe_1"], errors="coerce")
    df["pe_2"] = pd.to_numeric(df["pe_2"], errors="coerce")
    df["pe_3"] = pd.to_numeric(df["pe_3"], errors="coerce")
    df["pe_4"] = pd.to_numeric(df["pe_4"], errors="coerce")
    df["nuvarande_ps"] = pd.to_numeric(df["nuvarande_ps"], errors="coerce")
    df["ps_1"] = pd.to_numeric(df["ps_1"], errors="coerce")
    df["ps_2"] = pd.to_numeric(df["ps_2"], errors="coerce")
    df["ps_3"] = pd.to_numeric(df["ps_3"], errors="coerce")
    df["ps_4"] = pd.to_numeric(df["ps_4"], errors="coerce")
    df["insatt_datum"] = pd.to_datetime(df["insatt_datum"], errors="coerce")
    df["senast_andrad"] = pd.to_datetime(df["senast_andrad"], errors="coerce")
    return df

def spara_data(df: pd.DataFrame):
    data = df.fillna("").to_dict(orient="records")
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, default=str)

def berakna_targetkurser(df: pd.DataFrame) -> pd.DataFrame:
    # Säkerställ att det finns rader och nödvändiga kolumner
    if df.empty:
        return df

    def calc_target_pe(row):
        try:
            return row["vinst_nasta_ar"] * ((row["pe_1"] + row["pe_2"]) / 2)
        except Exception:
            return None

    def calc_target_ps(row):
        try:
            oms_vt_avg = (row["omsattningstillvaxt_ar_1_pct"] + row["omsattningstillvaxt_ar_2_pct"]) / 2 / 100
            ps_avg = (row["ps_1"] + row["ps_2"]) / 2
            return ps_avg * (1 + oms_vt_avg) * row["nuvarande_kurs"]
        except Exception:
            return None

    df["targetkurs_pe"] = df.apply(calc_target_pe, axis=1)
    df["targetkurs_ps"] = df.apply(calc_target_ps, axis=1)

    # Undervärdering i procent (större är mer undervärderad)
    df["undervarderad_pe_pct"] = ((df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]) * 100
    df["undervarderad_ps_pct"] = ((df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]) * 100

    # Ta högsta undervärdering mellan P/E och P/S
    df["undervarderad_pct"] = df[["undervarderad_pe_pct", "undervarderad_ps_pct"]].max(axis=1)
    return df

def filtrera_bolag(df: pd.DataFrame, endast_undervarderade: bool) -> pd.DataFrame:
    df = berakna_targetkurser(df)
    if endast_undervarderade:
        df = df[df["undervarderad_pct"] >= 30]
    df = df.sort_values(by="undervarderad_pct", ascending=False)
    return df.reset_index(drop=True)

def visa_inmatningsformulär(df: pd.DataFrame):
    st.header("Lägg till eller uppdatera bolag")
    with st.form(key="form_lagg_till_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar_1_pct = st.number_input("Omsättningstillväxt år 1 (%)", format="%.2f")
        omsattningstillvaxt_ar_2_pct = st.number_input("Omsättningstillväxt år 2 (%)", format="%.2f")

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

        skickaknapp = st.form_submit_button("Spara")

    if skickaknapp:
        if bolagsnamn == "":
            st.error("Bolagsnamn måste anges!")
            return df

        # Kolla om bolaget redan finns
        idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn.lower()]
        tidpunkt = datetime.now()

        ny_rad = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_forra_aret": vinst_forra_aret,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_forra_aret": omsattning_forra_aret,
            "omsattningstillvaxt_ar_1_pct": omsattningstillvaxt_ar_1_pct,
            "omsattningstillvaxt_ar_2_pct": omsattningstillvaxt_ar_2_pct,
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
            "insatt_datum": tidpunkt if idx.empty else df.loc[idx[0], "insatt_datum"],
            "senast_andrad": tidpunkt,
        }

        if idx.empty:
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            st.success(f"Bolag '{bolagsnamn}' tillagt!")
        else:
            # Uppdatera befintlig rad
            df.loc[idx[0]] = ny_rad
            st.success(f"Bolag '{bolagsnamn}' uppdaterat!")

        spara_data(df)
    return df


def visa_borttagning(df: pd.DataFrame):
    st.header("Ta bort bolag")
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
    if st.button("Ta bort"):
        df = df[df["bolagsnamn"] != bolag_att_ta_bort].reset_index(drop=True)
        spara_data(df)
        st.success(f"Bolag '{bolag_att_ta_bort}' har tagits bort.")
    return df

def beräkna_targetkurser(df: pd.DataFrame) -> pd.DataFrame:
    # Säkerställ att nödvändiga kolumner finns och är numeriska, annars fyll med 0
    for col in [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "nuvarande_kurs",
        "nuvarande_ps", "ps_1", "ps_2",
        "omsattningstillvaxt_ar_1_pct", "omsattningstillvaxt_ar_2_pct",
    ]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Beräkna targetkurs baserat på P/E
    df["targetkurs_pe"] = df.apply(
        lambda row: row["vinst_nasta_ar"] * ((row["pe_1"] + row["pe_2"]) / 2)
        if (row["pe_1"] > 0 and row["pe_2"] > 0 and row["vinst_nasta_ar"] > 0) else 0,
        axis=1
    )

    # Genomsnittlig omsättningstillväxt som faktor (från % till decimal)
    df["omsattningstillvaxt_genomsnitt"] = ((df["omsattningstillvaxt_ar_1_pct"] + df["omsattningstillvaxt_ar_2_pct"]) / 2) / 100

    # Beräkna targetkurs baserat på P/S (genomsnitt P/S * genomsnitt omsättningstillväxt * nuvarande kurs)
    df["targetkurs_ps"] = df.apply(
        lambda row: ((row["ps_1"] + row["ps_2"]) / 2) * row["omsattningstillvaxt_genomsnitt"] * row["nuvarande_kurs"]
        if (row["ps_1"] > 0 and row["ps_2"] > 0 and row["omsattningstillvaxt_genomsnitt"] > 0 and row["nuvarande_kurs"] > 0) else 0,
        axis=1
    )

    # Undervärdering i procent för P/E och P/S
    df["undervarderad_pe_pct"] = df.apply(
        lambda row: max(0, (row["targetkurs_pe"] - row["nuvarande_kurs"]) / row["targetkurs_pe"] * 100) if row["targetkurs_pe"] > 0 else 0,
        axis=1
    )

    df["undervarderad_ps_pct"] = df.apply(
        lambda row: max(0, (row["targetkurs_ps"] - row["nuvarande_kurs"]) / row["targetkurs_ps"] * 100) if row["targetkurs_ps"] > 0 else 0,
        axis=1
    )

    # Total undervärdering = max av undervärdering p/e och p/s
    df["undervarderad_pct"] = df[["undervarderad_pe_pct", "undervarderad_ps_pct"]].max(axis=1)

    # Köp-värd kurs vid 30% rabatt (targetkurs * 0.7)
    df["kopvard_kurs_pe"] = df["targetkurs_pe"] * 0.7
    df["kopvard_kurs_ps"] = df["targetkurs_ps"] * 0.7

    return df


def filtrera_bolag(df: pd.DataFrame, endast_undervarderade: bool = True) -> pd.DataFrame:
    df = beräkna_targetkurser(df)

    if endast_undervarderade:
        df = df[df["undervarderad_pct"] >= 30]

    df = df.sort_values(by="undervarderad_pct", ascending=False).reset_index(drop=True)
    return df

def visa_aktie_info(df: pd.DataFrame, index: int) -> None:
    if df.empty:
        st.write("Inga bolag att visa.")
        return

    row = df.iloc[index]
    st.subheader(f"Bolag: {row['bolagsnamn']}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Nuvarande kurs:** {row['nuvarande_kurs']:.2f} SEK")
        st.markdown(f"**Vinst nästa år:** {row['vinst_nasta_ar']:.2f} SEK")
        st.markdown(f"**Nuvarande P/E:** {row['nuvarande_pe']:.2f}")
        st.markdown(f"**P/E 1:** {row['pe_1']:.2f}")
        st.markdown(f"**P/E 2:** {row['pe_2']:.2f}")
        st.markdown(f"**Targetkurs (P/E):** {row['targetkurs_pe']:.2f} SEK")
        st.markdown(f"**Köpvärd kurs (P/E, 30% rabatt):** {row['kopvard_kurs_pe']:.2f} SEK")

    with col2:
        st.markdown(f"**Nuvarande P/S:** {row['nuvarande_ps']:.2f}")
        st.markdown(f"**P/S 1:** {row['ps_1']:.2f}")
        st.markdown(f"**P/S 2:** {row['ps_2']:.2f}")
        st.markdown(f"**Targetkurs (P/S):** {row['targetkurs_ps']:.2f} SEK")
        st.markdown(f"**Köpvärd kurs (P/S, 30% rabatt):** {row['kopvard_kurs_ps']:.2f} SEK")
        st.markdown(f"**Undervärdering:** {row['undervarderad_pct']:.2f} %")

    st.markdown("---")

def navigering(df: pd.DataFrame):
    if "aktie_index" not in st.session_state:
        st.session_state["aktie_index"] = 0

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Föregående") and st.session_state["aktie_index"] > 0:
            st.session_state["aktie_index"] -= 1
    with col3:
        if st.button("Nästa") and st.session_state["aktie_index"] < len(df) - 1:
            st.session_state["aktie_index"] += 1

    st.write(f"Visar bolag {st.session_state['aktie_index'] + 1} av {len(df)}")
    visa_aktie_info(df, st.session_state["aktie_index"])

def redigera_bolag(df: pd.DataFrame) -> pd.DataFrame:
    bolag_list = df["bolagsnamn"].tolist()
    valt_bolag = st.selectbox("Välj bolag att redigera", bolag_list, key="edit_select")

    if valt_bolag:
        idx = df.index[df["bolagsnamn"] == valt_bolag][0]
        bolag_data = df.loc[idx]

        with st.form(key="redigera_form"):
            nuvarande_kurs = st.number_input("Nuvarande kurs", value=float(bolag_data["nuvarande_kurs"]))
            vinst_nasta_ar = st.number_input("Vinst nästa år", value=float(bolag_data["vinst_nasta_ar"]))
            nuvarande_pe = st.number_input("Nuvarande P/E", value=float(bolag_data["nuvarande_pe"]))
            pe_1 = st.number_input("P/E 1", value=float(bolag_data["pe_1"]))
            pe_2 = st.number_input("P/E 2", value=float(bolag_data["pe_2"]))
            nuvarande_ps = st.number_input("Nuvarande P/S", value=float(bolag_data["nuvarande_ps"]))
            ps_1 = st.number_input("P/S 1", value=float(bolag_data["ps_1"]))
            ps_2 = st.number_input("P/S 2", value=float(bolag_data["ps_2"]))

            submit = st.form_submit_button("Uppdatera bolag")

        if submit:
            df.at[idx, "nuvarande_kurs"] = nuvarande_kurs
            df.at[idx, "vinst_nasta_ar"] = vinst_nasta_ar
            df.at[idx, "nuvarande_pe"] = nuvarande_pe
            df.at[idx, "pe_1"] = pe_1
            df.at[idx, "pe_2"] = pe_2
            df.at[idx, "nuvarande_ps"] = nuvarande_ps
            df.at[idx, "ps_1"] = ps_1
            df.at[idx, "ps_2"] = ps_2
            df.at[idx, "senast_andrad"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            st.success(f"Bolaget '{valt_bolag}' uppdaterades.")
            df = beräkna_targetkurser(df)
            spara_data(df)

    return df

def ta_bort_bolag(df: pd.DataFrame) -> pd.DataFrame:
    bolag_list = df["bolagsnamn"].tolist()
    valt_bolag = st.selectbox("Välj bolag att ta bort", bolag_list, key="remove_select")

    if valt_bolag:
        if st.button("Ta bort bolag"):
            df = df[df["bolagsnamn"] != valt_bolag].reset_index(drop=True)
            st.success(f"Bolaget '{valt_bolag}' har tagits bort.")
            spara_data(df)
            # Reset navigation index om nödvändigt
            st.session_state["aktie_index"] = 0

    return df

def spara_data(df: pd.DataFrame):
    with open(DATA_PATH, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4)

def main():
    st.title("Aktieanalysapp med Undervärdering")

    df = las_in_data()

    meny = ["Visa bolag", "Lägg till bolag", "Redigera bolag", "Ta bort bolag"]
    val = st.sidebar.radio("Meny", meny)

    if val == "Lägg till bolag":
        df = lagg_till_bolag(df)
    elif val == "Redigera bolag":
        df = redigera_bolag(df)
    elif val == "Ta bort bolag":
        df = ta_bort_bolag(df)

    # Visa bolag med filtrering och navigering
    if val == "Visa bolag":
        endast_undervarderade = st.checkbox("Visa endast undervärderade bolag (≥30%)", key="filter_checkbox")
        df = beräkna_targetkurser(df)
        filtrerad_df = filtrera_bolag(df, endast_undervarderade)

        if filtrerad_df.empty:
            st.warning("Inga bolag att visa med aktuellt filter.")
            return

        # Navigation: visa ett bolag i taget
        if "aktie_index" not in st.session_state:
            st.session_state["aktie_index"] = 0

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Föregående"):
                if st.session_state["aktie_index"] > 0:
                    st.session_state["aktie_index"] -= 1
        with col3:
            if st.button("Nästa"):
                if st.session_state["aktie_index"] < len(filtrerad_df) - 1:
                    st.session_state["aktie_index"] += 1

        bolag = filtrerad_df.iloc[st.session_state["aktie_index"]]
        st.subheader(f"{bolag['bolagsnamn']}")

        st.markdown(f"**Nuvarande kurs:** {bolag['nuvarande_kurs']:.2f} SEK")
        st.markdown(f"**Targetkurs P/E:** {bolag['targetkurs_pe']:.2f} SEK")
        st.markdown(f"**Targetkurs P/S:** {bolag['targetkurs_ps']:.2f} SEK")

        undervarderad_pct = bolag["undervarderad_pct"]
        st.markdown(f"**Undervärdering (%):** {undervarderad_pct:.2f}%")

        kopvard_pris = bolag["targetkurs_pe"] * 0.7  # 30% rabatt på targetkurs P/E
        st.markdown(f"**Köpvärd vid 30% rabatt:** {kopvard_pris:.2f} SEK")

        st.markdown("---")
        st.markdown("### Nyckeltal")
        nyckeltal_text = f"""
        - Nuvarande P/E: {bolag['nuvarande_pe']:.2f}
        - P/E 1: {bolag['pe_1']:.2f}
        - P/E 2: {bolag['pe_2']:.2f}
        - Nuvarande P/S: {bolag['nuvarande_ps']:.2f}
        - P/S 1: {bolag['ps_1']:.2f}
        - P/S 2: {bolag['ps_2']:.2f}
        - Vinst nästa år: {bolag['vinst_nasta_ar']:.2f} MSEK
        """
        st.markdown(nyckeltal_text)

if __name__ == "__main__":
    main()
