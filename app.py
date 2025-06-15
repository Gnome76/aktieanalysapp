import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "bolag_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn",
            "kurs",
            "vinst_forra_aret",
            "vinst_i_ar",
            "vinst_nasta_ar",
            "omsattning_forra_aret",
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
        ])

def save_data(df):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

def berakna_target_och_undervardering(df):
    if df.empty:
        return df
    cols = ["vinst_nasta_ar","pe_1","pe_2","ps_1","ps_2","kurs","omsattningstillvaxt_ar","omsattningstillvaxt_nasta_ar"]
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    oms_tillvxt = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100
    ps_medeltal = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = ps_medeltal * (1 + oms_tillvxt) * df["kurs"]

    df["undervardering_pe"] = (df["targetkurs_pe"] - df["kurs"]) / df["targetkurs_pe"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["kurs"]) / df["targetkurs_ps"]
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)
    df.loc[df["undervardering"] < 0, "undervardering"] = 0

    return df

def bolagsform(df):
    st.subheader("Lägg till eller uppdatera bolag")
    with st.form("bolagsformulär", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            bolagsnamn = st.text_input("Bolagsnamn").strip()
            kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
            vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
            vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
            vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
            omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
            omsattningstillvaxt_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f")
            omsattningstillvaxt_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f")
        with col2:
            pe_nuvarande = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
            pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
            pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
            pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
            pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")
            ps_nuvarande = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
            ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
            ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
            ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
            ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Spara / Uppdatera")

    if submitted:
        if not bolagsnamn:
            st.warning("Ange bolagsnamn!")
            return df

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if bolagsnamn in df["bolagsnamn"].values:
            idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
            df.loc[idx, ["kurs","vinst_forra_aret","vinst_i_ar","vinst_nasta_ar",
                         "omsattning_forra_aret","omsattningstillvaxt_ar","omsattningstillvaxt_nasta_ar",
                         "pe_nuvarande","pe_1","pe_2","pe_3","pe_4",
                         "ps_nuvarande","ps_1","ps_2","ps_3","ps_4"]] = [
                kurs,vinst_forra_aret,vinst_i_ar,vinst_nasta_ar,
                omsattning_forra_aret,omsattningstillvaxt_ar,omsattningstillvaxt_nasta_ar,
                pe_nuvarande,pe_1,pe_2,pe_3,pe_4,
                ps_nuvarande,ps_1,ps_2,ps_3,ps_4
            ]
            df.loc[idx, "senast_andrad"] = now_str
            st.success(f"Bolag '{bolagsnamn}' uppdaterat.")
        else:
            ny_rad = {
                "bolagsnamn": bolagsnamn,
                "kurs": kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
                "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
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
                "insatt_datum": now_str,
                "senast_andrad": now_str
            }
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            st.success(f"Bolag '{bolagsnamn}' tillagt.")

        df = berakna_target_och_undervardering(df)
        save_data(df)
        st.session_state["refresh"] = True
        st.stop()

    return df

def visa_alla_bolag(df):
    st.subheader("Alla bolag")
    if df.empty:
        st.info("Inga bolag sparade.")
        return
    df_vis = df.copy()
    df_vis = df_vis.sort_values(by="undervardering", ascending=False).reset_index(drop=True)
    st.dataframe(df_vis[[
        "bolagsnamn","kurs","targetkurs_pe","targetkurs_ps","undervardering",
        "insatt_datum","senast_andrad"
    ]])

def ta_bort_bolag(df):
    st.subheader("Ta bort bolag")
    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df
    bolag = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
    if st.button("Ta bort"):
        df = df[df["bolagsnamn"] != bolag].reset_index(drop=True)
        save_data(df)
        st.success(f"Bolag '{bolag}' borttaget.")
        st.session_state["refresh"] = True
        st.stop()
    return df

def undervarderade_vy(df):
    st.subheader("Undervärderade bolag (minst 30% rabatt)")
    df_u = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)
    if df_u.empty:
        st.info("Inga undervärderade bolag med minst 30% rabatt.")
        return

    if "index_undervard" not in st.session_state:
        st.session_state["index_undervard"] = 0

    col1, col2, col3 = st.columns([1,6,1])
    with col1:
        if st.button("⬅️ Föregående"):
            st.session_state["index_undervard"] = max(0, st.session_state["index_undervard"] - 1)
    with col3:
        if st.button("Nästa ➡️"):
            st.session_state["index_undervard"] = min(len(df_u)-1, st.session_state["index_undervard"] + 1)

    idx = st.session_state["index_undervard"]
    bolag = df_u.iloc[idx]
    st.markdown(f"### {bolag['bolagsnamn']}")
    st.write(bolag[[
        "kurs","targetkurs_pe","targetkurs_ps","undervardering",
        "insatt_datum","senast_andrad"
    ]])

def main():
    st.title("Aktieanalysapp")

    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    df = load_data()
    df = berakna_target_och_undervardering(df)

    menyval = st.sidebar.radio("Välj vy", ["Lägg till/Uppdatera bolag", "Visa alla bolag", "Ta bort bolag", "Undervärderade bolag"])

    if menyval == "Lägg till/Uppdatera bolag":
        df = bolagsform(df)
    elif menyval == "Visa alla bolag":
        visa_alla_bolag(df)
    elif menyval == "Ta bort bolag":
        df = ta_bort_bolag(df)
    elif menyval == "Undervärderade bolag":
        undervarderade_vy(df)

    if st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
