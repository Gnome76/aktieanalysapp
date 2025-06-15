import streamlit as st
import pandas as pd
import json
from datetime import datetime

DATAFIL = "data.json"

def ladda_data():
    try:
        with open(DATAFIL, "r") as f:
            return pd.DataFrame(json.load(f))
    except:
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs", "vinst_forra", "vinst_iar", "vinst_nasta_ar",
            "oms_forra", "oms_tillv_iar", "oms_tillv_nasta_ar",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ])

def spara_data(df):
    with open(DATAFIL, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

def berakna_target_undervardering(df):
    if df.empty:
        return df
    df = df.copy()
    try:
        df["targetkurs_pe"] = df["vinst_nasta_ar"].astype(float) * ((df["pe_1"].astype(float) + df["pe_2"].astype(float)) / 2)
        tillv_oms = ((df["oms_tillv_iar"].astype(float) + df["oms_tillv_nasta_ar"].astype(float)) / 2) / 100
        df["targetkurs_ps"] = df["ps_1"].astype(float).add(df["ps_2"].astype(float)).div(2).mul(tillv_oms.add(1)).mul(df["nuvarande_kurs"].astype(float))
        underv_pe = 1 - df["nuvarande_kurs"].astype(float) / df["targetkurs_pe"]
        underv_ps = 1 - df["nuvarande_kurs"].astype(float) / df["targetkurs_ps"]
        df["undervardering"] = pd.concat([underv_pe, underv_ps], axis=1).max(axis=1)
    except Exception as e:
        st.error(f"Fel vid berÃ¤kningar: {e}")
    return df

def bolagsform(df):
    with st.form("lÃ¤gg_till_eller_redigera"):
        st.subheader("LÃ¤gg till eller redigera bolag")
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", step=0.1)
        vinst_forra = st.number_input("Vinst fÃ¶rra Ã¥ret", step=0.1)
        vinst_iar = st.number_input("FÃ¶rvÃ¤ntad vinst i Ã¥r", step=0.1)
        vinst_nasta_ar = st.number_input("FÃ¶rvÃ¤ntad vinst nÃ¤sta Ã¥r", step=0.1)
        oms_forra = st.number_input("OmsÃ¤ttning fÃ¶rra Ã¥ret", step=0.1)
        oms_tillv_iar = st.number_input("OmsÃ¤ttningstillvÃ¤xt i Ã¥r (%)", step=0.1)
        oms_tillv_nasta_ar = st.number_input("OmsÃ¤ttningstillvÃ¤xt nÃ¤sta Ã¥r (%)", step=0.1)
        pe_nu = st.number_input("Nuvarande P/E", step=0.1)
        pe_1 = st.number_input("P/E 1", step=0.1)
        pe_2 = st.number_input("P/E 2", step=0.1)
        pe_3 = st.number_input("P/E 3", step=0.1)
        pe_4 = st.number_input("P/E 4", step=0.1)
        ps_nu = st.number_input("Nuvarande P/S", step=0.1)
        ps_1 = st.number_input("P/S 1", step=0.1)
        ps_2 = st.number_input("P/S 2", step=0.1)
        ps_3 = st.number_input("P/S 3", step=0.1)
        ps_4 = st.number_input("P/S 4", step=0.1)
        submitted = st.form_submit_button("Spara")

        if submitted and bolagsnamn:
            ny_rad = {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra": vinst_forra,
                "vinst_iar": vinst_iar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "oms_forra": oms_forra,
                "oms_tillv_iar": oms_tillv_iar,
                "oms_tillv_nasta_ar": oms_tillv_nasta_ar,
                "pe_nu": pe_nu,
                "pe_1": pe_1, "pe_2": pe_2, "pe_3": pe_3, "pe_4": pe_4,
                "ps_nu": ps_nu,
                "ps_1": ps_1, "ps_2": ps_2, "ps_3": ps_3, "ps_4": ps_4,
                "senast_andrad": datetime.now().isoformat(),
                "insatt_datum": datetime.now().isoformat(),
            }
            if bolagsnamn in df["bolagsnamn"].values:
                df.loc[df["bolagsnamn"] == bolagsnamn] = ny_rad
            else:
                df.loc[len(df)] = ny_rad
            spara_data(df)
            st.session_state["refresh"] = True
            st.stop()
    return df

def visa_undervarderade(df):
    st.subheader("UndervÃ¤rderade bolag")
    if "undervardering" not in df.columns:
        st.warning("Inga berÃ¤kningar Ã¤nnu")
        return

    visningslista = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)
    if visningslista.empty:
        st.info("Inga undervÃ¤rderade bolag just nu")
        return

    if "index" not in st.session_state:
        st.session_state["index"] = 0

    bolag = visningslista.iloc[st.session_state["index"]]
    st.markdown(f"### {bolag['bolagsnamn']}")
    st.metric("Nuvarande kurs", f"{bolag['nuvarande_kurs']} kr")
    st.metric("Targetkurs P/E", f"{bolag['targetkurs_pe']:.2f} kr")
    st.metric("Targetkurs P/S", f"{bolag['targetkurs_ps']:.2f} kr")
    st.metric("UndervÃ¤rdering", f"{bolag['undervardering']*100:.1f} %")

    kol1, kol2 = st.columns(2)
    with kol1:
        if st.button("FÃ¶regÃ¥ende") and st.session_state["index"] > 0:
            st.session_state["index"] -= 1
            st.stop()
    with kol2:
        if st.button("NÃ¤sta") and st.session_state["index"] < len(visningslista) - 1:
            st.session_state["index"] += 1
            st.stop()

def main():
    st.set_page_config(page_title="Aktieanalys", layout="centered")
    st.title("ð Aktieanalysapp")
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    df = ladda_data()
    df = berakna_target_undervardering(df)
    df = bolagsform(df)
    visa_undervarderade(df)

if __name__ == "__main__":
    main()
