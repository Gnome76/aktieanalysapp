import streamlit as st
import pandas as pd
import json
import os

FILNAMN = "aktier.json"

def las_data():
    kolumner = [
        "bolagsnamn", "nuvarande_kurs",
        "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
        "omsattning_forra_aret", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
        "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
        "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4"
    ]
    if os.path.exists(FILNAMN):
        with open(FILNAMN, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        for kol in kolumner:
            if kol not in df.columns:
                df[kol] = pd.NA
        df = df[kolumner]
        return df
    else:
        return pd.DataFrame(columns=kolumner)

def spara_data(df):
    with open(FILNAMN, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

def berakna_target_undervardering(df):
    # Säkerställ att nödvändiga kolumner finns och är numeriska
    nödvändiga = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "omsattning_forra_aret", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
        "ps_1", "ps_2", "nuvarande_kurs"
    ]
    for kol in nödvändiga:
        if kol not in df.columns:
            df[kol] = 0
    for kol in nödvändiga:
        df[kol] = pd.to_numeric(df[kol], errors="coerce").fillna(0)

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    oms_tillv = ((df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2) / 100 + 1
    medel_ps = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = df["omsattning_forra_aret"] * oms_tillv * medel_ps

    pe_diff = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"].replace(0, pd.NA)
    ps_diff = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"].replace(0, pd.NA)

    df["undervardering"] = pe_diff.combine(ps_diff, max).fillna(0)
    return df

def visa_undervarderade_bolag(df):
    underv = df[df["undervardering"] > 0.3].copy()
    if underv.empty:
        st.info("Inga bolag är undervärderade med minst 30% just nu.")
        return
    underv = underv.sort_values("undervardering", ascending=False).reset_index(drop=True)
    index = st.session_state.get("underv_index", 0)

    bolag = underv.iloc[index]

    st.markdown(f"### {bolag['bolagsnamn']}")
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} SEK")
    st.write(f"Targetkurs P/E: {bolag['targetkurs_pe']:.2f} SEK")
    st.write(f"Targetkurs P/S: {bolag['targetkurs_ps']:.2f} SEK")
    st.write(f"Undervärdering: {bolag['undervardering']*100:.1f} %")

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Föregående") and index > 0:
            st.session_state["underv_index"] = index - 1
    with col3:
        if st.button("Nästa") and index < len(underv) - 1:
            st.session_state["underv_index"] = index + 1

def main():
    st.title("Aktieanalysapp")

    df = las_data()
    df = berakna_target_undervardering(df)

    st.header("Lägg till nytt bolag")
    with st.form("nytt_bolag_form"):
        bolagsnamn = st.text_input("Bolagsnamn (nytt bolag)")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")
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

        lagg_till_knapp = st.form_submit_button("Lägg till bolag")

        if lagg_till_knapp:
            if bolagsnamn.strip() == "":
                st.warning("Fyll i bolagsnamn.")
            elif bolagsnamn in df["bolagsnamn"].values:
                st.warning("Bolaget finns redan. Använd redigeringssektionen för att uppdatera.")
            else:
                ny_rad = {
                    "bolagsnamn": bolagsnamn.strip(),
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_forra_aret": vinst_forra_aret,
                    "vinst_i_ar": vinst_i_ar,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "omsattning_forra_aret": omsattning_forra_aret,
                    "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                    "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
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
                df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
                spara_data(df)
                st.success(f"Bolag '{bolagsnamn}' tillagt!")

    st.header("Redigera eller ta bort befintligt bolag")

    if len(df) == 0:
        st.info("Inga bolag finns sparade ännu.")
    else:
        valt_bolag = st.selectbox("Välj bolag att redigera eller ta bort", df["bolagsnamn"].tolist())

        if valt_bolag:
            idx = df.index[df["bolagsnamn"] == valt_bolag][0]
            bolag = df.loc[idx]

            with st.form("redigera_bolag_form"):
                st.markdown(f"### Redigera bolag: {valt_bolag}")

                # Visa nuvarande kurs alltid
                nuvarande_kurs = st.number_input("Nuvarande kurs", value=float(bolag["nuvarande_kurs"]), format="%.2f")

                # Vill du visa alla fält? Checkbox för att visa dolda fält
                visa_fler = st.checkbox("Visa fler nyckeltal att redigera")

                if visa_fler:
                    vinst_forra_aret = st.number_input("Vinst förra året", value=float(bolag["vinst_forra_aret"]), format="%.2f")
                    vinst_i_ar = st.number_input("Förväntad vinst i år", value=float(bolag["vinst_i_ar"]), format="%.2f")
                    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", value=float(bolag["vinst_nasta_ar"]), format="%.2f")
                    omsattning_forra_aret = st.number_input("Omsättning förra året", value=float(bolag["omsattning_forra_aret"]), format="%.2f")
                    omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", value=float(bolag["omsattningstillvaxt_ar"]), format="%.2f")
                    omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", value=float(bolag["omsattningstillvaxt_nasta_ar"]), format="%.2f")
                    nuvarande_pe = st.number_input("Nuvarande P/E", value=float(bolag["nuvarande_pe"]), format="%.2f")
                    pe_1 = st.number_input("P/E 1", value=float(bolag["pe_1"]), format="%.2f")
                    pe_2 = st.number_input("P/E 2", value=float(bolag["pe_2"]), format="%.2f")
                    pe_3 = st.number_input("P/E 3", value=float(bolag["pe_3"]), format="%.2f")
                    pe_4 = st.number_input("P/E 4", value=float(bolag["pe_4"]), format="%.2f")
                    nuvarande_ps = st.number_input("Nuvarande P/S", value=float(bolag["nuvarande_ps"]), format="%.2f")
                    ps_1 = st.number_input("P/S 1", value=float(bolag["ps_1"]), format="%.2f")
                    ps_2 = st.number_input("P/S 2", value=float(bolag["ps_2"]), format="%.2f")
                    ps_3 = st.number_input("P/S 3", value=float(bolag["ps_3"]), format="%.2f")
                    ps_4 = st.number_input("P/S 4", value=float(bolag["ps_4"]), format="%.2f")
                else:
                    # Behåll gamla värden för dessa fält
                    vinst_forra_aret = bolag["vinst_forra_aret"]
                    vinst_i_ar = bolag["vinst_i_ar"]
                    vinst_nasta_ar = bolag["vinst_nasta_ar"]
                    omsattning_forra_aret = bolag["omsattning_forra_aret"]
                    omsattningstillvaxt_ar = bolag["omsattningstillvaxt_ar"]
                    omsattningstillvaxt_nasta_ar = bolag["omsattningstillvaxt_nasta_ar"]
                    nuvarande_pe = bolag["nuvarande_pe"]
                    pe_1 = bolag["pe_1"]
                    pe_2 = bolag["pe_2"]
                    pe_3 = bolag["pe_3"]
                    pe_4 = bolag["pe_4"]
                    nuvarande_ps = bolag["nuvarande_ps"]
                    ps_1 = bolag["ps_1"]
                    ps_2 = bolag["ps_2"]
                    ps_3 = bolag["ps_3"]
                    ps_4 = bolag["ps_4"]

                uppdatera_knapp = st.form_submit_button("Uppdatera bolag")
                ta_bort_knapp = st.form_submit_button("Ta bort bolag")

                if uppdatera_knapp:
                    df.at[idx, "nuvarande_kurs"] = nuvarande_kurs
                    df.at[idx, "vinst_forra_aret"] = vinst_forra_aret
                    df.at[idx, "vinst_i_ar"] = vinst_i_ar
                    df.at[idx, "vinst_nasta_ar"] = vinst_nasta_ar
                    df.at[idx, "omsattning_forra_aret"] = omsattning_forra_aret
                    df.at[idx, "omsattningstillvaxt_ar"] = omsattningstillvaxt_ar
                    df.at[idx, "omsattningstillvaxt_nasta_ar"] = omsattningstillvaxt_nasta_ar
                    df.at[idx, "nuvarande_pe"] = nuvarande_pe
                    df.at[idx, "pe_1"] = pe_1
                    df.at[idx, "pe_2"] = pe_2
                    df.at[idx, "pe_3"] = pe_3
                    df.at[idx, "pe_4"] = pe_4
                    df.at[idx, "nuvarande_ps"] = nuvarande_ps
                    df.at[idx, "ps_1"] = ps_1
                    df.at[idx, "ps_2"] = ps_2
                    df.at[idx, "ps_3"] = ps_3
                    df.at[idx, "ps_4"] = ps_4
                    spara_data(df)
                    st.success(f"Bolaget '{valt_bolag}' uppdaterat!")
                    st.experimental_rerun()

                if ta_bort_knapp:
                    df = df.drop(idx).reset_index(drop=True)
                    spara_data(df)
                    st.success(f"Bolaget '{valt_bolag}' borttaget!")
                    st.experimental_rerun()

    st.header("Undervärderade bolag (minst 30 %)")
    visa_undervarderade_bolag(df)

if __name__ == "__main__":
    if "underv_index" not in st.session_state:
        st.session_state["underv_index"] = 0
    main()
