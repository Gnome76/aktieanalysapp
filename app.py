import streamlit as st
import pandas as pd
import json
import os

DATA_PATH = "aktier.json"

def las_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret",
            "vinst_i_ar", "vinst_nasta_ar", "oms_forra_aret",
            "oms_tillv_i_ar", "oms_tillv_nasta_ar",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4"
        ])

def spara_data(df):
    with open(DATA_PATH, "w") as f:
        f.write(df.to_json(orient="records", indent=4)) 
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

DATAFIL = "data.json"

def las_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs", "vinst_ifjol", "vinst_i_ar", "vinst_nasta_ar",
            "oms_ifjol", "oms_tillv_i_ar", "oms_tillv_nasta_ar",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ])

def spara_data(df):
    with open(DATAFIL, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4)

def berakna_target_och_undervardering(df):
    df = df.copy()
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    gen_oms_tillv = ((df["oms_tillv_i_ar"] + df["oms_tillv_nasta_ar"]) / 2) / 100
    df["targetkurs_ps"] = df["ps_nu"] * gen_oms_tillv * df["nuvarande_kurs"]

    df["undervärdering_pe_%"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"] * 100
    df["undervärdering_ps_%"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"] * 100
    return df

def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="bolagsform_unik"):
        kol1, kol2 = st.columns(2)

        with kol1:
            bolagsnamn = st.text_input("Bolagsnamn").strip()
            nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, step=0.01)
            vinst_ifjol = st.number_input("Vinst förra året", step=0.01)
            vinst_i_ar = st.number_input("Förväntad vinst i år", step=0.01)
            vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", step=0.01)
            oms_ifjol = st.number_input("Omsättning förra året", step=0.01)
            oms_tillv_i_ar = st.number_input("Förväntad Omsättningstillväxt i år %", step=0.1)
            oms_tillv_nasta_ar = st.number_input("Förväntad Omsättningstillväxt nästa år %", step=0.1)

        with kol2:
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

        submit = st.form_submit_button("Spara bolag")

    if submit:
        if bolagsnamn == "":
            st.error("Bolagsnamn krävs.")
            return df

        ny_bolag = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_ifjol": vinst_ifjol,
            "vinst_i_ar": vinst_i_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "oms_ifjol": oms_ifjol,
            "oms_tillv_i_ar": oms_tillv_i_ar,
            "oms_tillv_nasta_ar": oms_tillv_nasta_ar,
            "pe_nu": pe_nu, "pe_1": pe_1, "pe_2": pe_2, "pe_3": pe_3, "pe_4": pe_4,
            "ps_nu": ps_nu, "ps_1": ps_1, "ps_2": ps_2, "ps_3": ps_3, "ps_4": ps_4,
            "insatt_datum": datetime.today().strftime("%Y-%m-%d"),
            "senast_andrad": datetime.today().strftime("%Y-%m-%d")
        }

        df = lagg_till_eller_uppdatera_bolag(df, ny_bolag)
        spara_data(df)
        st.success(f"{bolagsnamn} har sparats.")
    return df

def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    idx = df.index[df["bolagsnamn"].str.lower() == bolag_ny["bolagsnamn"].lower()]
    if not idx.empty:
        bolag_ny["insatt_datum"] = df.loc[idx[0], "insatt_datum"]
        bolag_ny["senast_andrad"] = datetime.today().strftime("%Y-%m-%d")
        df.loc[idx[0]] = bolag_ny
    else:
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)
    return df

def berakna_targetkurser(df):
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    
    genomsnittlig_tillv = (df["oms_tillv_i_ar"] + df["oms_tillv_nasta_ar"]) / 2
    genomsnittlig_ps = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = df["nuvarande_kurs"] * (1 + genomsnittlig_tillv / 100) * genomsnittlig_ps / df["ps_nu"]

    df["undervärdering_pe_%"] = ((df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]) * 100
    df["undervärdering_ps_%"] = ((df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]) * 100
    df["max_undervärdering"] = df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)
    return df


def visa_bolag(df):
    st.header("📊 Bolagsanalyser")

    df = berakna_targetkurser(df)
    visa_endast_undervard = st.checkbox("Visa endast undervärderade bolag (>30%)", value=True)

    filtrerat_df = df.copy()
    if visa_endast_undervard:
        filtrerat_df = filtrerat_df[filtrerat_df["max_undervärdering"] >= 30]

    filtrerat_df = filtrerat_df.sort_values(by="max_undervärdering", ascending=False).reset_index(drop=True)

    if filtrerat_df.empty:
        st.info("Inga bolag med över 30% undervärdering hittades.")
        return df

    if "bolagsindex" not in st.session_state:
        st.session_state["bolagsindex"] = 0

    if st.button("⬅️ Föregående") and st.session_state["bolagsindex"] > 0:
        st.session_state["bolagsindex"] -= 1
    if st.button("➡️ Nästa") and st.session_state["bolagsindex"] < len(filtrerat_df) - 1:
        st.session_state["bolagsindex"] += 1

    bolag = filtrerat_df.iloc[st.session_state["bolagsindex"]]

    st.subheader(f"{bolag['bolagsnamn']}")
    st.metric("Nuvarande kurs", f"{bolag['nuvarande_kurs']:.2f} kr")
    st.metric("Targetkurs P/E", f"{bolag['targetkurs_pe']:.2f} kr")
    st.metric("Targetkurs P/S", f"{bolag['targetkurs_ps']:.2f} kr")
    st.metric("Undervärdering P/E", f"{bolag['undervärdering_pe_%']:.1f} %")
    st.metric("Undervärdering P/S", f"{bolag['undervärdering_ps_%']:.1f} %")

    if bolag["max_undervärdering"] >= 30:
        st.success("📈 Köpvärd! Mer än 30 % undervärderad mot targetkurs.")

    if st.button("❌ Ta bort detta bolag"):
        df = df[df["bolagsnamn"].str.lower() != bolag["bolagsnamn"].lower()].reset_index(drop=True)
        spara_data(df)
        st.session_state["bolagsindex"] = 0
        st.success("Bolaget har tagits bort.")
        st.experimental_rerun()

    return df

def main():
    st.title("📈 Aktieanalysapp - Undervärderade Bolag")

    df = las_data()

    df = visa_form(df)  # Formulär för nytt/uppdaterat bolag

    df = visa_bolag(df)  # Visa bolag och undervärdering

    spara_data(df)  # Spara data efter eventuella ändringar


if __name__ == "__main__":
    main()
