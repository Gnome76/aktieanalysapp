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
    nödvändiga = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "omsattning_forra_aret", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
        "ps_1", "ps_2", "nuvarande_kurs"
    ]
    for kol in nödvändiga:
        if kol not in df.columns:
            df[kol] = 0

    df["vinst_nasta_ar"] = pd.to_numeric(df["vinst_nasta_ar"], errors="coerce").fillna(0)
    df["pe_1"] = pd.to_numeric(df["pe_1"], errors="coerce").fillna(0)
    df["pe_2"] = pd.to_numeric(df["pe_2"], errors="coerce").fillna(0)
    df["omsattning_forra_aret"] = pd.to_numeric(df["omsattning_forra_aret"], errors="coerce").fillna(0)
    df["omsattningstillvaxt_ar"] = pd.to_numeric(df["omsattningstillvaxt_ar"], errors="coerce").fillna(0)
    df["omsattningstillvaxt_nasta_ar"] = pd.to_numeric(df["omsattningstillvaxt_nasta_ar"], errors="coerce").fillna(0)
    df["ps_1"] = pd.to_numeric(df["ps_1"], errors="coerce").fillna(0)
    df["ps_2"] = pd.to_numeric(df["ps_2"], errors="coerce").fillna(0)
    df["nuvarande_kurs"] = pd.to_numeric(df["nuvarande_kurs"], errors="coerce").fillna(0)

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    oms_tillv = ((df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2) / 100 + 1
    medel_ps = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = df["omsattning_forra_aret"] * oms_tillv * medel_ps

    pe_diff = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"].replace(0, pd.NA)
    ps_diff = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"].replace(0, pd.NA)

    df["undervardering"] = pe_diff.combine(ps_diff, max).fillna(0)
    return df

def main():
    st.title("Aktieanalysapp")

    df = las_data()
    df = berakna_target_undervardering(df)

    st.header("Lägg till / uppdatera bolag")

    with st.form("inmatningsform"):
        bolagsnamn = st.text_input("Bolagsnamn")
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

        skickaknapp = st.form_submit_button("Spara bolag")

        if skickaknapp:
            if bolagsnamn.strip() == "":
                st.warning("Fyll i bolagsnamn.")
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

                # Uppdatera om bolaget finns, annars lägg till nytt
                if bolagsnamn in df["bolagsnamn"].values:
                    idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
                    df.loc[idx] = ny_rad
                    st.success(f"Bolag '{bolagsnamn}' uppdaterat!")
                else:
                    df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
                    st.success(f"Bolag '{bolagsnamn}' tillagt!")

                spara_data(df)
                df = berakna_target_undervardering(df)

    st.header("Undervärderade bolag (mer än 30%)")

    undervarderade = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)

    if len(undervarderade) == 0:
        st.info("Inga bolag är just nu undervärderade med mer än 30%.")
    else:
        if "index_bolag" not in st.session_state:
            st.session_state["index_bolag"] = 0

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Föregående") and st.session_state["index_bolag"] > 0:
                st.session_state["index_bolag"] -= 1
        with col3:
            if st.button("Nästa ➡️") and st.session_state["index_bolag"] < len(undervarderade) - 1:
                st.session_state["index_bolag"] += 1

        idx = st.session_state["index_bolag"]
        bolag = undervarderade.iloc[idx]

        st.markdown(f"### {bolag['bolagsnamn']}")

        st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} SEK")
        st.write(f"Targetkurs (P/E): {bolag['targetkurs_pe']:.2f} SEK")
        st.write(f"Targetkurs (P/S): {bolag['targetkurs_ps']:.2f} SEK")
        st.write(f"Undervärdering: {bolag['undervardering']*100:.1f} %")

        nyckeltal = {
            "Vinst förra året": bolag["vinst_forra_aret"],
            "Vinst i år": bolag["vinst_i_ar"],
            "Vinst nästa år": bolag["vinst_nasta_ar"],
            "Omsättning förra året": bolag["omsattning_forra_aret"],
            "Omsättningstillväxt i år (%)": bolag["omsattningstillvaxt_ar"],
            "Omsättningstillväxt nästa år (%)": bolag["omsattningstillvaxt_nasta_ar"],
            "Nuvarande P/E": bolag["nuvarande_pe"],
            "P/E 1": bolag["pe_1"],
            "P/E 2": bolag["pe_2"],
            "P/E 3": bolag["pe_3"],
            "P/E 4": bolag["pe_4"],
            "Nuvarande P/S": bolag["nuvarande_ps"],
            "P/S 1": bolag["ps_1"],
            "P/S 2": bolag["ps_2"],
            "P/S 3": bolag["ps_3"],
            "P/S 4": bolag["ps_4"],
        }
        st.write(nyckeltal)

if __name__ == "__main__":
    main()
