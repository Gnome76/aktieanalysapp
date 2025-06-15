import streamlit as st
import pandas as pd
import json
import os

FILNAMN = "bolag.json"

def las_data():
    if os.path.exists(FILNAMN):
        try:
            with open(FILNAMN, "r", encoding="utf-8") as f:
                data = json.load(f)
                return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def spara_data(df):
    with open(FILNAMN, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

def berakna_target_och_undervardering(df):
    if df.empty:
        return df

    kolumner = [
        "vinst_nasta_ar", "pe_1", "pe_2", "kurs", "ps_1", "ps_2"
    ]
    for kol in kolumner:
        if kol not in df.columns:
            df[kol] = pd.NA

    for kol in kolumner:
        df[kol] = pd.to_numeric(df[kol], errors="coerce")

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * df["kurs"]

    underv_pe = (df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"]
    underv_ps = (df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"]

    df["undervardering"] = pd.concat([underv_pe, underv_ps], axis=1).max(axis=1)
    df["undervardering"] = df["undervardering"].fillna(0)
    df.loc[df["undervardering"] < 0, "undervardering"] = 0

    return df

def visa_undervarderade(df):
    st.subheader("Undervärderade bolag (minst 30% rabatt)")
    if df.empty:
        st.info("Inga bolag inlagda ännu.")
        return

    df_vis = df[df["undervardering"] >= 0.3].copy()
    if df_vis.empty:
        st.info("Inga bolag är undervärderade med minst 30%.")
        return

    df_vis = df_vis.sort_values(by="undervardering", ascending=False).reset_index(drop=True)

    if "idx" not in st.session_state:
        st.session_state.idx = 0

    def prev_bolag():
        if st.session_state.idx > 0:
            st.session_state.idx -= 1

    def next_bolag():
        if st.session_state.idx < len(df_vis) - 1:
            st.session_state.idx += 1

    bolag = df_vis.iloc[st.session_state.idx]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Föregående", on_click=prev_bolag)
    with col2:
        st.markdown(f"### {bolag['bolagsnamn']}")
        st.write(f"- Nuvarande kurs: {bolag['kurs']:.2f}")
        st.write(f"- Targetkurs P/E: {bolag['targetkurs_pe']:.2f}")
        st.write(f"- Targetkurs P/S: {bolag['targetkurs_ps']:.2f}")
        st.write(f"- Undervärdering: {bolag['undervardering']*100:.1f} %")
    with col3:
        st.button("Nästa →", on_click=next_bolag)

def bolagsform(df):
    st.subheader("Lägg till eller redigera bolag")

    val = ["-- Nytt bolag --"] + sorted(df["bolagsnamn"].tolist()) if not df.empty else ["-- Nytt bolag --"]
    valt_bolag = st.selectbox("Välj bolag att redigera", val)

    if valt_bolag == "-- Nytt bolag --":
        data = {
            "bolagsnamn": "",
            "kurs": "",
            "vinst_fjol": "",
            "vinst_i_ar": "",
            "vinst_nasta_ar": "",
            "omsattning_fjol": "",
            "omsattningstillvaxt_i_ar_procent": "",
            "omsattningstillvaxt_nasta_ar_procent": "",
            "pe_nuvarande": "",
            "pe_1": "",
            "pe_2": "",
            "pe_3": "",
            "pe_4": "",
            "ps_nuvarande": "",
            "ps_1": "",
            "ps_2": "",
            "ps_3": "",
            "ps_4": "",
        }
    else:
        data_row = df[df["bolagsnamn"] == valt_bolag].iloc[0]
        data = data_row.to_dict()

    col1, col2 = st.columns(2)
    with col1:
        bolagsnamn = st.text_input("Bolagsnamn", value=data.get("bolagsnamn", ""))
        kurs = st.text_input("Nuvarande kurs", value=str(data.get("kurs", "")))
        vinst_fjol = st.text_input("Vinst förra året", value=str(data.get("vinst_fjol", "")))
        vinst_i_ar = st.text_input("Förväntad vinst i år", value=str(data.get("vinst_i_ar", "")))
        vinst_nasta_ar = st.text_input("Förväntad vinst nästa år", value=str(data.get("vinst_nasta_ar", "")))
        omsattning_fjol = st.text_input("Omsättning förra året", value=str(data.get("omsattning_fjol", "")))
        omsattningstillvaxt_i_ar_procent = st.text_input("Omsättningstillväxt i år %", value=str(data.get("omsattningstillvaxt_i_ar_procent", "")))
    with col2:
        omsattningstillvaxt_nasta_ar_procent = st.text_input("Omsättningstillväxt nästa år %", value=str(data.get("omsattningstillvaxt_nasta_ar_procent", "")))
        pe_nuvarande = st.text_input("Nuvarande P/E", value=str(data.get("pe_nuvarande", "")))
        pe_1 = st.text_input("P/E 1", value=str(data.get("pe_1", "")))
        pe_2 = st.text_input("P/E 2", value=str(data.get("pe_2", "")))
        pe_3 = st.text_input("P/E 3", value=str(data.get("pe_3", "")))
        pe_4 = st.text_input("P/E 4", value=str(data.get("pe_4", "")))
        ps_nuvarande = st.text_input("Nuvarande P/S", value=str(data.get("ps_nuvarande", "")))
        ps_1 = st.text_input("P/S 1", value=str(data.get("ps_1", "")))
        ps_2 = st.text_input("P/S 2", value=str(data.get("ps_2", "")))
        ps_3 = st.text_input("P/S 3", value=str(data.get("ps_3", "")))
        ps_4 = st.text_input("P/S 4", value=str(data.get("ps_4", "")))

    if st.button("Spara bolag"):
        if not bolagsnamn.strip():
            st.error("Bolagsnamn kan inte vara tomt!")
            return df

        ny_rad = {
            "bolagsnamn": bolagsnamn.strip(),
            "kurs": kurs,
            "vinst_fjol": vinst_fjol,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_fjol": omsattning_fjol,
            "omsattningstillvaxt_i_ar_procent": omsattningstillvaxt_i_ar_procent,
            "omsattningstillvaxt_nasta_ar_procent": omsattningstillvaxt_nasta_ar_procent,
            "pe_nuvarande": pe_nuvarande,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "pe_3": pe_3,
            "pe_4": pe_4,
            "ps_nuvarande": ps_nuvarande,
            "ps_1": ps_1,
            "ps_2": ps_2,
            "ps_3": ps_3,
            "ps_4": ps_4,
        }

        # Uppdatera eller lägg till
        if valt_bolag == "-- Nytt bolag --":
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
        else:
            idx = df.index[df["bolagsnamn"] == valt_bolag][0]
            df.loc[idx] = ny_rad

        spara_data(df)
        st.success(f"Bolaget '{bolagsnamn}' sparat!")
        st.experimental_rerun()

    return df

def main():
    st.title("Aktieanalysapp")

    df = las_data()
    df = berakna_target_och_undervardering(df)

    df = bolagsform(df)

    visa_undervarderade(df)

if __name__ == "__main__":
    main()
