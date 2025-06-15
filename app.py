import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Definiera kolumner som appen hanterar
KOLUMNER = [
    "bolagsnamn",
    "nuvarande_kurs",
    "vinst_fjol",
    "vinst_aret",
    "vinst_nasta_ar",
    "omsattning_fjol",
    "omsattningstillvaxt_aret",
    "omsattningstillvaxt_nasta_ar",
    "nuvarande_pe",
    "pe_1",
    "pe_2",
    "pe_3",
    "pe_4",
    "nuvarande_ps",
    "ps_1",
    "ps_2",
    "ps_3",
    "ps_4",
    "insatt_datum",
    "senast_andrad"
]

DATAFIL = "data.json"

def las_data():
    """Läser data från JSON, eller skapar tom DataFrame med rätt kolumner."""
    if os.path.exists(DATAFIL):
        try:
            df = pd.read_json(DATAFIL)
            # Säkerställ att alla kolumner finns
            for col in KOLUMNER:
                if col not in df.columns:
                    df[col] = None
            return df[KOLUMNER]
        except Exception:
            pass
    # Om fil saknas eller fel: skapa tom df med kolumner
    return pd.DataFrame(columns=KOLUMNER)

def lagra_data(df):
    """Sparar DataFrame till JSON."""
    df.to_json(DATAFIL, orient="records", indent=4, force_ascii=False)

def berakna_target_och_undervardering(df):
    """Beräknar targetkurser och undervärdering, lägger till kolumner."""
    if df.empty:
        return df

    # Säkerställ numeriska typer för beräkningar
    for col in [
        "vinst_nasta_ar",
        "pe_1", "pe_2",
        "ps_1", "ps_2",
        "nuvarande_kurs",
        "nuvarande_pe",
        "nuvarande_ps",
        "omsattningstillvaxt_aret",
        "omsattningstillvaxt_nasta_ar",
        "omsattning_fjol"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Targetkurs baserat på PE
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Targetkurs baserat på PS, med omsättningstillväxt medel
    omsattningstillvxt_medel = (df["omsattningstillvaxt_aret"].fillna(0) + df["omsattningstillvaxt_nasta_ar"].fillna(0)) / 2
    medel_ps = (df["ps_1"].fillna(0) + df["ps_2"].fillna(0)) / 2
    omsattningstillvxt_decimal = omsattningstillvxt_medel / 100  # om det är i procentform
    omsattning = df["omsattning_fjol"].fillna(0)

    df["targetkurs_ps"] = omsattning * (1 + omsattningstillvxt_decimal) * medel_ps

    # Undervärdering - baserat på max rabatt mellan pe och ps målkurser
    df["undervardering_pe"] = 1 - (df["nuvarande_kurs"] / df["targetkurs_pe"])
    df["undervardering_ps"] = 1 - (df["nuvarande_kurs"] / df["targetkurs_ps"])

    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    # Rensa negativa undervärderingar till 0 (inte undervärderade)
    df.loc[df["undervardering"] < 0, "undervardering"] = 0

    return df

def main():
    st.title("Aktieanalysapp")

    # Läs data med fixad kolumnstruktur
    df = las_data()

    # Beräkna targetkurser och undervärdering
    df = berakna_target_och_undervardering(df)

    # Här fortsätter vi i nästa del med UI och formulär osv

if __name__ == "__main__":
    main()

def lagg_till_eller_uppdatera_bolag(df, ny_bolag):
    """Lägger till nytt bolag eller uppdaterar befintligt baserat på bolagsnamn."""
    bolagsnamn_ny = ny_bolag["bolagsnamn"].strip().lower()
    if bolagsnamn_ny == "":
        return df  # tomt namn, gör inget

    # Kontrollera om bolag redan finns (case insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny]

    nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ny_bolag["senast_andrad"] = nu

    if len(idx) > 0:
        # Uppdatera existerande rad
        for col in ny_bolag:
            df.at[idx[0], col] = ny_bolag[col]
        # Uppdatera insatt_datum om den saknas
        if pd.isna(df.at[idx[0], "insatt_datum"]) or df.at[idx[0], "insatt_datum"] == "":
            df.at[idx[0], "insatt_datum"] = nu
    else:
        # Lägg till nytt bolag
        ny_bolag["insatt_datum"] = nu
        df = pd.concat([df, pd.DataFrame([ny_bolag])], ignore_index=True)

    return df

def ta_bort_bolag(df, bolagsnamn):
    """Tar bort bolag från df baserat på bolagsnamn."""
    bolagsnamn = bolagsnamn.strip().lower()
    df = df[df["bolagsnamn"].str.lower() != bolagsnamn].reset_index(drop=True)
    return df

def visa_form(df):
    """Visar formulär för inmatning och uppdatering av bolag."""
    st.header("Lägg till eller uppdatera bolag")

    with st.form("bolagsform"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_fjol = st.number_input("Vinst förra året", format="%.2f")
        vinst_aret = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_fjol = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_aret = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
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
        ny_bolag = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_fjol": vinst_fjol,
            "vinst_aret": vinst_aret,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_fjol": omsattning_fjol,
            "omsattningstillvaxt_aret": omsattningstillvaxt_aret,
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
        df = lagg_till_eller_uppdatera_bolag(df, ny_bolag)
        lagra_data(df)
        st.success(f"Bolaget '{bolagsnamn}' har sparats/uppdaterats.")
        # Uppdatera sidan utan st.experimental_rerun (streamlitcloud)
        st.session_state["refresh"] = True
        st.stop()

    return df

def sidebar_val(df):
    st.sidebar.header("Bolagsval")
    val = st.sidebar.selectbox("Välj bolag att ta bort", options=["--Ingen--"] + sorted(df["bolagsnamn"].tolist()))
    if val != "--Ingen--":
        if st.sidebar.button(f"Ta bort '{val}'"):
            df = ta_bort_bolag(df, val)
            lagra_data(df)
            st.sidebar.success(f"Bolaget '{val}' är borttaget.")
            st.session_state["refresh"] = True
            st.stop()
    return df

def berakna_targetkurser(df):
    """Beräkna targetkurser baserat på P/E och P/S enligt dina regler."""
    # Targetkurs baserad på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)
    # Medelvärde av P/S * medelvärde av omsättningstillväxt * nuvarande kurs
    omsattningstillvaxt_medel = (df["omsattningstillvaxt_aret"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100
    ps_medel = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = ps_medel * (1 + omsattningstillvaxt_medel) * df["nuvarande_kurs"]

    # Beräkna undervärdering i procent för P/E och P/S (negativ betyder undervärderad)
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"] * 100
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"] * 100

    # Skapa en kolumn med max undervärdering av P/E eller P/S (för sortering/filter)
    df["max_undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    return df

def filtrera_undervarderade(df, min_rabatt=30):
    """Filtrera fram bolag som är undervärderade minst min_rabatt procent."""
    df = df[df["max_undervardering"] >= min_rabatt]
    return df

def visa_oversikt(df):
    """Visa tabell med bolagsdata och targetkurser."""
    st.header("Översikt över bolag")

    if df.empty:
        st.info("Inga bolag sparade.")
        return

    vis_df = df.copy()
    # Sortera på max undervärdering, högst först
    vis_df = vis_df.sort_values(by="max_undervardering", ascending=False)

    # Visa utvalda kolumner
    kolumner = [
        "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_aret", "vinst_nasta_ar",
        "omsattning_fjol", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_ar",
        "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
        "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
        "targetkurs_pe", "targetkurs_ps", "undervardering_pe", "undervardering_ps", "max_undervardering"
    ]
    st.dataframe(vis_df[kolumner].reset_index(drop=True))

def visa_bolag_ett_i_taget(df):
    """Visa ett bolag i taget med navigering, mobilvänligt."""
    st.header("Undervärderade bolag - ett i taget")

    if df.empty:
        st.info("Inga undervärderade bolag att visa.")
        return

    # Initiera index i session_state
    if "idx" not in st.session_state:
        st.session_state.idx = 0

    # Visa bolag på aktuellt index
    bolag = df.iloc[st.session_state.idx]

    st.subheader(bolag["bolagsnamn"])
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} SEK")
    st.write(f"Targetkurs (P/E): {bolag['targetkurs_pe']:.2f} SEK")
    st.write(f"Targetkurs (P/S): {bolag['targetkurs_ps']:.2f} SEK")
    st.write(f"Undervärdering max: {bolag['max_undervardering']:.2f} %")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Föregående"):
            if st.session_state.idx > 0:
                st.session_state.idx -= 1
    with col2:
        if st.button("Nästa"):
            if st.session_state.idx < len(df) - 1:
                st.session_state.idx += 1

import streamlit as st
import pandas as pd
import json
import os

DATAFIL = "aktier.json"

def las_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r", encoding="utf-8") as f:
            data = json.load(f)
            return pd.DataFrame(data)
    else:
        kolumner = [
            "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_aret", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4"
        ]
        return pd.DataFrame(columns=kolumner)

def lagra_data(df):
    with open(DATAFIL, "w", encoding="utf-8") as f:
        f.write(df.to_json(orient="records", force_ascii=False))

def lagg_till_eller_uppdatera_bolag(df, ny_bolag):
    # Kontrollera om bolaget redan finns (case insensitive)
    if df.empty:
        df = pd.DataFrame([ny_bolag])
    else:
        idx = df.index[df["bolagsnamn"].str.lower() == ny_bolag["bolagsnamn"].lower()]
        if len(idx) > 0:
            # Uppdatera befintligt bolag
            for kol in ny_bolag:
                df.at[idx[0], kol] = ny_bolag[kol]
        else:
            # Lägg till nytt bolag
            df = pd.concat([df, pd.DataFrame([ny_bolag])], ignore_index=True)
    return df

def ta_bort_bolag(df, bolagsnamn):
    if not df.empty:
        df = df[df["bolagsnamn"].str.lower() != bolagsnamn.lower()]
    return df

def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")
    with st.form("bolagsform", clear_on_submit=True):
        bolagsnamn = st.text_input("Bolagsnamn", key="inp_bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", key="inp_nuvarande_kurs")
        vinst_fjol = st.number_input("Vinst förra året", key="inp_vinst_fjol")
        vinst_aret = st.number_input("Förväntad vinst i år", key="inp_vinst_aret")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", key="inp_vinst_nasta_ar")
        omsattning_fjol = st.number_input("Omsättning förra året", key="inp_omsattning_fjol")
        omsattningstillvaxt_aret = st.number_input("Förväntad omsättningstillväxt i år %", key="inp_omsattningstillvaxt_aret")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år %", key="inp_omsattningstillvaxt_nasta_ar")
        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f", key="inp_nuvarande_pe")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f", key="inp_pe_1")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f", key="inp_pe_2")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f", key="inp_pe_3")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f", key="inp_pe_4")
        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f", key="inp_nuvarande_ps")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f", key="inp_ps_1")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f", key="inp_ps_2")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f", key="inp_ps_3")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f", key="inp_ps_4")

        skickaknapp = st.form_submit_button("Spara/uppdatera")

        if skickaknapp:
            if bolagsnamn.strip() == "":
                st.warning("Bolagsnamn måste fyllas i.")
            else:
                ny_bolag = {
                    "bolagsnamn": bolagsnamn.strip(),
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_fjol": vinst_fjol,
                    "vinst_aret": vinst_aret,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "omsattning_fjol": omsattning_fjol,
                    "omsattningstillvaxt_aret": omsattningstillvaxt_aret,
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
                    "ps_4": ps_4
                }
                df = lagg_till_eller_uppdatera_bolag(df, ny_bolag)
                lagra_data(df)
                st.success(f"Bolag '{bolagsnamn}' sparat/uppdaterat.")
                # Uppdatera session_state så listan visas korrekt
                st.session_state["refresh"] = True
                st.experimental_rerun()
    return df

def ta_bort_form(df):
    st.header("Ta bort bolag")
    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
    if st.button("Ta bort valt bolag"):
        df = ta_bort_bolag(df, bolag_att_ta_bort)
        lagra_data(df)
        st.success(f"Bolag '{bolag_att_ta_bort}' borttaget.")
        st.session_state["refresh"] = True
        st.experimental_rerun()
    return df

def main():
    st.title("Aktieanalysapp")

    df = las_data()

    # Beräkna targetkurser och undervärdering
    if not df.empty:
        df = berakna_targetkurser(df)

    # Visa formulär för inmatning/uppdatering
    df = visa_form(df)

    # Visa formulär för borttagning
    df = ta_bort_form(df)

    # Checkbox för att filtrera undervärderade bolag
    visa_undervard = st.checkbox("Visa endast undervärderade bolag (>30% rabatt)", value=False)

    if visa_undervard:
        undervard_df = filtrera_undervarderade(df, min_rabatt=30)
        if undervard_df.empty:
            st.info("Inga bolag uppfyller kriteriet för undervärdering.")
        else:
            # Visa ett bolag i taget (mobilvy)
            visa_bolag_ett_i_taget(undervard_df)
    else:
        # Visa alla bolag i tabellvy
        visa_oversikt(df)

if __name__ == "__main__":
    main()
