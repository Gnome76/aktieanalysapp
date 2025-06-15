import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATAFIL = "aktier.json"

KOLUMNER = [
    "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
    "oms_forra_aret", "oms_tillv_i_ar", "oms_tillv_nasta_ar",
    "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
    "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
    "insatt_datum", "senast_andrad"
]

# -------- Datahantering --------

def ladda_data():
    if os.path.exists(DATAFIL):
        try:
            with open(DATAFIL, "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            for col in KOLUMNER:
                if col not in df.columns:
                    df[col] = ""
            return df[KOLUMNER]
        except Exception:
            pass
    return pd.DataFrame(columns=KOLUMNER)

def spara_data(df):
    with open(DATAFIL, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# -------- Beräkningar --------

def berakna_target_undervardering(df):
    if df.empty:
        return df
    # Säkerställ numeriska typer
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "pe_nu", "ps_nu",
                "oms_tillv_i_ar", "oms_tillv_nasta_ar", "nuvarande_kurs"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    oms_tillv_medel = (df["oms_tillv_i_ar"] + df["oms_tillv_nasta_ar"]) / 2 / 100
    p_s_medel = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = p_s_medel * (1 + oms_tillv_medel) * df["nuvarande_kurs"]

    df["undervardering_pe"] = 1 - df["nuvarande_kurs"] / df["targetkurs_pe"]
    df["undervardering_ps"] = 1 - df["nuvarande_kurs"] / df["targetkurs_ps"]
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    df["undervardering"].fillna(0, inplace=True)
    df["undervardering_pe"].fillna(0, inplace=True)
    df["undervardering_ps"].fillna(0, inplace=True)
    return df

# -------- UI-funktioner --------

def visa_undervardering(df, index):
    if df.empty or index >= len(df):
        st.info("Inga bolag att visa.")
        return
    row = df.iloc[index]

    st.markdown(f"### {row['bolagsnamn']}")
    st.write(f"**Nuvarande kurs:** {row['nuvarande_kurs']:.2f}")
    st.write(f"**Targetkurs P/E:** {row['targetkurs_pe']:.2f}")
    st.write(f"**Targetkurs P/S:** {row['targetkurs_ps']:.2f}")

    underv = row["undervardering"]
    if underv > 0.3:
        emoji = "🟢"
        färg = "green"
    elif underv > 0.1:
        emoji = "🟡"
        färg = "orange"
    else:
        emoji = "🔴"
        färg = "red"

    procent = underv * 100
    st.markdown(f"<h3 style='color:{färg};'>{emoji} Undervärdering: {procent:.1f}%</h3>", unsafe_allow_html=True)
    st.progress(min(max(procent / 100, 0), 1))

def bolagsform(df):
    st.header("Lägg till / uppdatera bolag")

    with st.form("bolagsform", clear_on_submit=False):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.text_input("Nuvarande kurs")
        vinst_forra_aret = st.text_input("Vinst förra året")
        vinst_i_ar = st.text_input("Förväntad vinst i år")
        vinst_nasta_ar = st.text_input("Förväntad vinst nästa år")
        oms_forra_aret = st.text_input("Omsättning förra året")
        oms_tillv_i_ar = st.text_input("Förväntad omsättningstillväxt i år (%)")
        oms_tillv_nasta_ar = st.text_input("Förväntad omsättningstillväxt nästa år (%)")
        pe_nu = st.text_input("Nuvarande P/E")
        pe_1 = st.text_input("P/E 1")
        pe_2 = st.text_input("P/E 2")
        pe_3 = st.text_input("P/E 3")
        pe_4 = st.text_input("P/E 4")
        ps_nu = st.text_input("Nuvarande P/S")
        ps_1 = st.text_input("P/S 1")
        ps_2 = st.text_input("P/S 2")
        ps_3 = st.text_input("P/S 3")
        ps_4 = st.text_input("P/S 4")

        submitted = st.form_submit_button("Spara / Uppdatera")

        if submitted:
            if not bolagsnamn:
                st.error("Bolagsnamn måste anges.")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if bolagsnamn in df["bolagsnamn"].values:
                    idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
                    df.loc[idx] = [
                        bolagsnamn, nuvarande_kurs, vinst_forra_aret, vinst_i_ar, vinst_nasta_ar,
                        oms_forra_aret, oms_tillv_i_ar, oms_tillv_nasta_ar,
                        pe_nu, pe_1, pe_2, pe_3, pe_4,
                        ps_nu, ps_1, ps_2, ps_3, ps_4,
                        df.at[idx, "insatt_datum"], now
                    ]
                    st.success(f"Bolag '{bolagsnamn}' uppdaterat.")
                else:
                    ny_rad = {
                        "bolagsnamn": bolagsnamn,
                        "nuvarande_kurs": nuvarande_kurs,
                        "vinst_forra_aret": vinst_forra_aret,
                        "vinst_i_ar": vinst_i_ar,
                        "vinst_nasta_ar": vinst_nasta_ar,
                        "oms_forra_aret": oms_forra_aret,
                        "oms_tillv_i_ar": oms_tillv_i_ar,
                        "oms_tillv_nasta_ar": oms_tillv_nasta_ar,
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
                        "insatt_datum": now,
                        "senast_andrad": now,
                    }
                    df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
                    st.success(f"Bolag '{bolagsnamn}' tillagt.")
            spara_data(df)
            st.session_state["update_flag"] = True

    return df

def ta_bort_bolag(df):
    st.header("Ta bort bolag")
    if df.empty:
        st.info("Inga bolag sparade.")
        return df

    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())

    if st.button("Ta bort"):
        df = df[df["bolagsnamn"] != bolag_att_ta_bort]
        spara_data(df)
        st.success(f"Bolag '{bolag_att_ta_bort}' borttaget.")
        st.session_state["update_flag"] = True
    return df

def redigera_bolag(df):
    st.header("Redigera bolag")

    if df.empty:
        st.info("Inga bolag sparade.")
        return df

    val = st.selectbox("Välj bolag att redigera", options=df["bolagsnamn"].tolist())
    if val:
        idx = df.index[df["bolagsnamn"] == val][0]
        row = df.loc[idx]

        with st.form("redigera_form"):
            nuvarande_kurs = st.text_input("Nuvarande kurs", value=str(row["nuvarande_kurs"]))
            vinst_forra_aret = st.text_input("Vinst förra året", value=str(row["vinst_forra_aret"]))
            vinst_i_ar = st.text_input("Förväntad vinst i år", value=str(row["vinst_i_ar"]))
            vinst_nasta_ar = st.text_input("Förväntad vinst nästa år", value=str(row["vinst_nasta_ar"]))
            oms_forra_aret = st.text_input("Omsättning förra året", value=str(row["oms_forra_aret"]))
            oms_tillv_i_ar = st.text_input("Omsättningstillväxt i år (%)", value=str(row["oms_tillv_i_ar"]))
            oms_tillv_nasta_ar = st.text_input("Omsättningstillväxt nästa år (%)", value=str(row["oms_tillv_nasta_ar"]))
            pe_nu = st.text_input("Nuvarande P/E", value=str(row["pe_nu"]))
            pe_1 = st.text_input("P/E 1", value=str(row["pe_1"]))
            pe_2 = st.text_input("P/E 2", value=str(row["pe_2"]))
            pe_3 = st.text_input("P/E 3", value=str(row["pe_3"]))
            pe_4 = st.text_input("P/E 4", value=str(row["pe_4"]))
            ps_nu = st.text_input("Nuvarande P/S", value=str(row["ps_nu"]))
            ps_1 = st.text_input("P/S 1", value=str(row["ps_1"]))
            ps_2 = st.text_input("P/S 2", value=str(row["ps_2"]))
            ps_3 = st.text_input("P/S 3", value=str(row["ps_3"]))
            ps_4 = st.text_input("P/S 4", value=str(row["ps_4"]))

            submitted = st.form_submit_button("Uppdatera")

            if submitted:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[idx] = [
                    val,
                    nuvarande_kurs, vinst_forra_aret, vinst_i_ar, vinst_nasta_ar,
                    oms_forra_aret, oms_tillv_i_ar, oms_tillv_nasta_ar,
                    pe_nu, pe_1, pe_2, pe_3, pe_4,
                    ps_nu, ps_1, ps_2, ps_3, ps_4,
                    df.at[idx, "insatt_datum"], now
                ]
                spara_data(df)
                st.success(f"Bolag '{val}' uppdaterat.")
                st.session_state["update_flag"] = True

    return df

# -------- Huvudfunktion --------

def main():
    st.title("Aktieanalysapp")

    # Ladda data
    if "data" not in st.session_state:
        st.session_state["data"] = ladda_data()

    if "update_flag" not in st.session_state:
        st.session_state["update_flag"] = False

    # Sidor i appen
    menyval = st.sidebar.selectbox("Meny", ["Visa alla bolag", "Visa undervärderade", "Lägg till / uppdatera", "Redigera bolag", "Ta bort bolag"])

    df = st.session_state["data"]

    if menyval == "Visa alla bolag":
        df = berakna_target_undervardering(df)
        df_visning = df.copy()
        df_visning = df_visning.sort_values(by="undervardering", ascending=False)
        if df_visning.empty:
            st.info("Inga bolag sparade.")
        else:
            st.dataframe(df_visning[[
                "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering"
            ]])

    elif menyval == "Visa undervärderade":
        df = berakna_target_undervardering(df)
        undervarde_grans = st.slider("Minsta undervärdering (%)", min_value=0, max_value=100, value=30) / 100
        df_ud = df[df["undervardering"] >= undervarde_grans].sort_values(by="undervardering", ascending=False)
        if df_ud.empty:
            st.info("Inga undervärderade bolag enligt vald gräns.")
        else:
            # Visa ett i taget med bläddringsknappar
            if "visningsindex" not in st.session_state:
                st.session_state["visningsindex"] = 0

            col1, col2, col3 = st.columns([1,3,1])
            with col1:
                if st.button("← Föregående"):
                    st.session_state["visningsindex"] = max(0, st.session_state["visningsindex"] - 1)
            with col3:
                if st.button("Nästa →"):
                    st.session_state["visningsindex"] = min(len(df_ud)-1, st.session_state["visningsindex"] + 1)

            visa_undervardering(df_ud.reset_index(drop=True), st.session_state["visningsindex"])

    elif menyval == "Lägg till / uppdatera":
        df = bolagsform(df)

    elif menyval == "Redigera bolag":
        df = redigera_bolag(df)

    elif menyval == "Ta bort bolag":
        df = ta_bort_bolag(df)

    # Uppdatera sessionstate-data om något ändrats
    if st.session_state["update_flag"]:
        st.session_state["data"] = df
        st.session_state["update_flag"] = False

if __name__ == "__main__":
    main()
