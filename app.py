import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

def las_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return pd.DataFrame(data)
    else:
        # Returnera tom DataFrame med kolumner om fil inte finns
        kolumner = [
            "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar",
            "vinst_nasta_ar", "omsattning_forra_aret", "omsattningstillvaxt_i_ar_procent",
            "omsattningstillvaxt_nasta_ar_procent", "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4", "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=kolumner)

def lagra_data(df):
    df.to_json(DATA_FILE, orient="records", indent=2, force_ascii=False)

def berakna_target_och_undervardering(df):
    # Beräkna targetkurs baserat på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"].astype(float) * ((df["pe_1"].astype(float) + df["pe_2"].astype(float)) / 2)
    # Beräkna genomsnittlig omsättningstillväxt (decimalform)
    oms_tillv_1 = df["omsattningstillvaxt_i_ar_procent"].astype(float) / 100
    oms_tillv_2 = df["omsattningstillvaxt_nasta_ar_procent"].astype(float) / 100
    oms_tillv_medel = (oms_tillv_1 + oms_tillv_2) / 2
    # Beräkna genomsnittligt P/S för år 1 och 2
    ps_medel = (df["ps_1"].astype(float) + df["ps_2"].astype(float)) / 2
    # Targetkurs P/S
    df["targetkurs_ps"] = ps_medel * (1 + oms_tillv_medel) * df["nuvarande_kurs"].astype(float)
    # Undervärdering: max av (targetkurs - nuvarande kurs)/targetkurs
    underv_pe = (df["targetkurs_pe"] - df["nuvarande_kurs"].astype(float)) / df["targetkurs_pe"]
    underv_ps = (df["targetkurs_ps"] - df["nuvarande_kurs"].astype(float)) / df["targetkurs_ps"]
    df["undervardering"] = underv_pe.combine(underv_ps, max)
    # Rensa negativa undervärderingar (övervärderade bolag) till 0
    df.loc[df["undervardering"] < 0, "undervardering"] = 0
    return df

def lagg_till_eller_uppdatera_bolag(df):
    st.subheader("Lägg till eller uppdatera bolag")
    with st.form("bolagsform"):
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        oms_tillv_i_ar = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
        oms_tillv_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
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

        skickaknapp = st.form_submit_button("Spara bolag")

    if skickaknapp:
        if bolagsnamn == "":
            st.error("Bolagsnamn måste fyllas i!")
            return df
        nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Kontrollera om bolaget redan finns
        if bolagsnamn in df["bolagsnamn"].values:
            # Uppdatera existerande bolag
            df.loc[df["bolagsnamn"] == bolagsnamn, :] = [
                bolagsnamn, nuvarande_kurs, vinst_forra_aret, vinst_i_ar, vinst_nasta_ar,
                omsattning_forra_aret, oms_tillv_i_ar, oms_tillv_nasta_ar, nuvarande_pe,
                pe_1, pe_2, pe_3, pe_4, nuvarande_ps, ps_1, ps_2, ps_3, ps_4,
                df.loc[df["bolagsnamn"] == bolagsnamn, "insatt_datum"].values[0], nu
            ]
            st.success(f"Bolaget {bolagsnamn} uppdaterades.")
        else:
            # Lägg till nytt bolag
            ny_rad = {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_forra_aret": vinst_forra_aret,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "omsattning_forra_aret": omsattning_forra_aret,
                "omsattningstillvaxt_i_ar_procent": oms_tillv_i_ar,
                "omsattningstillvaxt_nasta_ar_procent": oms_tillv_nasta_ar,
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
                "insatt_datum": nu,
                "senast_andrad": nu
            }
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            st.success(f"Bolaget {bolagsnamn} tillagt.")
        lagra_data(df)
        # Uppdatera sidan utan st.experimental_rerun (Streamlit Cloud-vanligt workaround)
        st.session_state["refresh"] = True
        st.experimental_rerun()
    return df

def ta_bort_bolag(df):
    st.subheader("Ta bort bolag")
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
    if st.button("Ta bort valt bolag"):
        df = df[df["bolagsnamn"] != bolag_att_ta_bort].reset_index(drop=True)
        lagra_data(df)
        st.success(f"Bolaget {bolag_att_ta_bort} togs bort.")
        st.session_state["refresh"] = True
        st.experimental_rerun()
    return df

def visa_och_filtrera_bolag(df):
    st.subheader("Visa bolag")

    if df.empty:
        st.info("Inga bolag inlagda ännu.")
        return

    df = berakna_target_och_undervardering(df)

    visa_endast_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering")

    if visa_endast_undervarderade:
        df_vis = df[df["undervardering"] >= 0.30].copy()
        if df_vis.empty:
            st.warning("Inga bolag uppfyller kravet på minst 30% undervärdering.")
            return
    else:
        df_vis = df.copy()

    # Sortera på undervärdering, högst först
    df_vis = df_vis.sort_values(by="undervardering", ascending=False).reset_index(drop=True)

    # Visa översiktstabell
    kolumner_att_visa = [
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering"
    ]
    df_ovrigt = df_vis[kolumner_att_visa].copy()
    df_ovrigt["undervardering"] = (df_ovrigt["undervardering"] * 100).round(2).astype(str) + " %"

    st.dataframe(df_ovrigt, use_container_width=True)

    # Visa ett bolag i taget med navigering
    st.markdown("---")
    st.write("### Bläddra mellan bolag")

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Föregående"):
            if st.session_state.current_index > 0:
                st.session_state.current_index -= 1
    with col3:
        if st.button("Nästa"):
            if st.session_state.current_index < len(df_vis) - 1:
                st.session_state.current_index += 1

    bolag = df_vis.iloc[st.session_state.current_index]

    # Visa detaljer för valt bolag
    st.markdown(f"#### {bolag['bolagsnamn']}")
    detaljer = {
        "Nuvarande kurs": bolag["nuvarande_kurs"],
        "Vinst förra året": bolag["vinst_forra_aret"],
        "Förväntad vinst i år": bolag["vinst_i_ar"],
        "Förväntad vinst nästa år": bolag["vinst_nasta_ar"],
        "Omsättning förra året": bolag["omsattning_forra_aret"],
        "Omsättningstillväxt i år %": bolag["omsattningstillvaxt_i_ar_procent"],
        "Omsättningstillväxt nästa år %": bolag["omsattningstillvaxt_nasta_ar_procent"],
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
        "Targetkurs P/E": round(bolag["targetkurs_pe"], 2),
        "Targetkurs P/S": round(bolag["targetkurs_ps"], 2),
        "Undervärdering": f"{round(bolag['undervardering']*100, 2)} %"
    }

    for nyckel, varde in detaljer.items():
        st.write(f"**{nyckel}:** {varde}")

def main():
    st.title("Aktieanalysapp med Nyckeltal och Targetkurser")

    # Läs in data vid start
    df = las_data()

    # Formulär för att lägga till eller uppdatera bolag
    df = bolagsform(df)

    # Visa och filtrera bolag
    visa_och_filtrera_bolag(df)

    # Spara data
    lagra_data(df)

    # Kontroll för att uppdatera sidan vid ändringar (ersätter st.experimental_rerun())
    if st.session_state.get("refresh", False):
        st.session_state["refresh"] = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
