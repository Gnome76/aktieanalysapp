import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

DATA_PATH = "/mnt/data/aktier.json"  # Anpassa för Streamlit Cloud

# --- Del 1: Datahantering och hjälpfunktioner ---

def las_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            # Säkerställ kolumntyper
            if "bolagsnamn" in df.columns:
                df["bolagsnamn"] = df["bolagsnamn"].fillna("").astype(str)
            else:
                df["bolagsnamn"] = ""
            # Konvertera datum till datetime
            for col in ["insatt_datum", "senast_andrad"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            return df
    else:
        # Skapa tom DataFrame med alla nödvändiga kolumner
        kolumner = [
            "bolagsnamn", "kurs_nu", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_i_ar", "omsattningstillvaxt_nasta_ar",
            "pe_nu", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nu", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        df = pd.DataFrame(columns=kolumner)
        df["bolagsnamn"] = df["bolagsnamn"].astype(str)
        return df

def spara_data(df):
    # Konvertera datetime till str för json
    df_to_save = df.copy()
    for col in ["insatt_datum", "senast_andrad"]:
        if col in df_to_save.columns:
            df_to_save[col] = df_to_save[col].apply(lambda x: x.isoformat() if pd.notnull(x) else "")
    with open(DATA_PATH, "w") as f:
        json.dump(df_to_save.to_dict(orient="records"), f, indent=2)

def berakna_targetkurser(df):
    # Säkerställ att kolumner finns och är numeriska
    for col in ["vinst_nasta_ar", "pe_1", "pe_2"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["ps_1", "ps_2", "omsattningstillvaxt_i_ar", "omsattningstillvaxt_nasta_ar"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Targetkurs PE = vinst_nasta_ar * medelvärde av pe_1 och pe_2
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Targetkurs PS = medelvärde av ps_1 och ps_2 * genomsnittlig omsättningstillväxt * kurs_nu
    omsattningstillvaxt_medel = ((df["omsattningstillvaxt_i_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2) / 100
    ps_medel = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = ps_medel * omsattningstillvaxt_medel * df["kurs_nu"]

    # Undervärdering i procent (negativ om övervärderad)
    df["undervardering_pe_%"] = ((df["targetkurs_pe"] - df["kurs_nu"]) / df["targetkurs_pe"] * 100).round(2)
    df["undervardering_ps_%"] = ((df["targetkurs_ps"] - df["kurs_nu"]) / df["targetkurs_ps"] * 100).round(2)

    # Max undervärdering
    df["max_undervardering_%"] = df[["undervardering_pe_%", "undervardering_ps_%"]].max(axis=1)

    # Köp-värd vid 30% rabatt på targetkurser (True/False)
    df["kopvard_pe"] = df["undervardering_pe_%"] >= 30
    df["kopvard_ps"] = df["undervardering_ps_%"] >= 30

    return df

# --- Del 2: Visa bolag och undervärdering samt navigering ---

def visa_bolag(df):
    df = berakna_targetkurser(df)

    st.header("Bolagslista och Undervärdering")

    visa_alla = st.checkbox("Visa alla bolag (avmarkera för endast undervärderade ≥30%)", value=True)

    if not visa_alla:
        # Filtrera undervärderade (max undervärdering ≥30%)
        df = df[df["max_undervardering_%"] >= 30]

    # Sortera på max undervärdering, högst först
    df = df.sort_values(by="max_undervardering_%", ascending=False)

    if df.empty:
        st.info("Inga bolag att visa.")
        return df

    # Visa i tabell med relevanta kolumner
    tabell_kolumner = [
        "bolagsnamn",
        "kurs_nu",
        "targetkurs_pe",
        "targetkurs_ps",
        "max_undervardering_%",
        "kopvard_pe",
        "kopvard_ps",
        "insatt_datum",
        "senast_andrad"
    ]
    tabell = df[tabell_kolumner].copy()

    # Format för procent och bool
    tabell["max_undervardering_%"] = tabell["max_undervardering_%"].map("{:.2f}%".format)
    tabell["kopvard_pe"] = tabell["kopvard_pe"].map({True: "Ja", False: "Nej"})
    tabell["kopvard_ps"] = tabell["kopvard_ps"].map({True: "Ja", False: "Nej"})

    st.dataframe(tabell, use_container_width=True)

    # Bläddra ett bolag i taget (mobilvänligt)
    st.subheader("Visa bolag ett i taget")

    if "index" not in st.session_state:
        st.session_state["index"] = 0

    col1, col2, col3 = st.columns([1, 2, 1])

    def prev():
        if st.session_state["index"] > 0:
            st.session_state["index"] -= 1

    def next():
        if st.session_state["index"] < len(df) - 1:
            st.session_state["index"] += 1

    with col1:
        st.button("Föregående", on_click=prev)
    with col3:
        st.button("Nästa", on_click=next)

    idx = st.session_state["index"]
    if idx >= len(df):
        st.session_state["index"] = 0
        idx = 0

    bolag = df.iloc[idx]

    st.markdown(f"### {bolag['bolagsnamn']}")
    st.write(f"- Nuvarande kurs: {bolag['kurs_nu']}")
    st.write(f"- Targetkurs P/E: {bolag['targetkurs_pe']:.2f}")
    st.write(f"- Targetkurs P/S: {bolag['targetkurs_ps']:.2f}")
    st.write(f"- Max undervärdering: {bolag['max_undervardering_%']:.2f}%")
    st.write(f"- Köpvärd vid 30% rabatt P/E: {'Ja' if bolag['kopvard_pe'] else 'Nej'}")
    st.write(f"- Köpvärd vid 30% rabatt P/S: {'Ja' if bolag['kopvard_ps'] else 'Nej'}")

    return df

# --- Del 3: Formulär, inmatning och uppdatering av bolag ---

def lagg_till_eller_uppdatera_bolag(df, nytt_bolag):
    bolagsnamn_ny = nytt_bolag["bolagsnamn"].strip().lower()

    if "bolagsnamn" not in df.columns:
        # Om df är tom eller ej rätt format, skapa kolumner
        df = pd.DataFrame(columns=nytt_bolag.keys())

    # Se till att 'bolagsnamn' är strängar (för .str metoder)
    df["bolagsnamn"] = df["bolagsnamn"].astype(str)

    # Kolla om bolaget redan finns (case-insensitive)
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()

    if idx:
        # Uppdatera befintlig rad
        index = idx[0]
        for key, value in nytt_bolag.items():
            df.at[index, key] = value
        df.at[index, "senast_andrad"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Lägg till nytt bolag med insatt_datum och senast_andrad
        nytt_bolag["insatt_datum"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nytt_bolag["senast_andrad"] = ""
        df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)

    return df


def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="form_lagg_till_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn", key="form_bolagsnamn")
        kurs_nu = st.number_input("Nuvarande kurs", min_value=0.0, format="%.4f", key="form_kurs_nu")

        # Fler inmatningsfält för alla fält
        vinst_forra_ar = st.number_input("Vinst förra året", format="%.4f", key="form_vinst_forra_ar")
        vinst_nasta_ar = st.number_input("Vinst nästa år (förväntad)", format="%.4f", key="form_vinst_nasta_ar")

        omsattning_forra_ar = st.number_input("Omsättning förra året", format="%.4f", key="form_omsattning_forra_ar")
        omsattningstillvaxt_ar1 = st.number_input("Omsättningstillväxt år 1 (%)", format="%.2f", key="form_omsattningstillvaxt_ar1")
        omsattningstillvaxt_ar2 = st.number_input("Omsättningstillväxt år 2 (%)", format="%.2f", key="form_omsattningstillvaxt_ar2")

        pe_nu = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f", key="form_pe_nu")
        pe_1 = st.number_input("P/E år 1", min_value=0.0, format="%.2f", key="form_pe_1")
        pe_2 = st.number_input("P/E år 2", min_value=0.0, format="%.2f", key="form_pe_2")
        pe_3 = st.number_input("P/E år 3", min_value=0.0, format="%.2f", key="form_pe_3")
        pe_4 = st.number_input("P/E år 4", min_value=0.0, format="%.2f", key="form_pe_4")

        ps_nu = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f", key="form_ps_nu")
        ps_1 = st.number_input("P/S år 1", min_value=0.0, format="%.2f", key="form_ps_1")
        ps_2 = st.number_input("P/S år 2", min_value=0.0, format="%.2f", key="form_ps_2")
        ps_3 = st.number_input("P/S år 3", min_value=0.0, format="%.2f", key="form_ps_3")
        ps_4 = st.number_input("P/S år 4", min_value=0.0, format="%.2f", key="form_ps_4")

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            if not bolagsnamn:
                st.error("Bolagsnamn måste anges!")
            else:
                nytt_bolag = {
                    "bolagsnamn": bolagsnamn,
                    "kurs_nu": kurs_nu,
                    "vinst_forra_ar": vinst_forra_ar,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "omsattning_forra_ar": omsattning_forra_ar,
                    "omsattningstillvaxt_ar1": omsattningstillvaxt_ar1,
                    "omsattningstillvaxt_ar2": omsattningstillvaxt_ar2,
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
                }

                df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
                st.success(f"Bolag '{bolagsnamn}' har sparats.")
                spara_data(df)
                st.experimental_rerun()

    return df

# --- Del 4: Visa bolag, beräkna targetkurser, filtrering och borttagning ---

def berakna_targetkurser(df):
    # Kontrollera att nödvändiga kolumner finns
    nödvändiga = ["vinst_nasta_ar", "pe_1", "pe_2", "kurs_nu", 
                  "ps_1", "ps_2", "omsattningstillvaxt_ar1", "omsattningstillvaxt_ar2"]
    for col in nödvändiga:
        if col not in df.columns:
            df[col] = 0.0

    # Fyll ev. NaN med 0
    df.fillna(0, inplace=True)

    # Beräkna targetkurs_pe som medel av pe_1 och pe_2 gånger vinst_nasta_ar
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Genomsnittlig omsättningstillväxt år 1 och 2 i decimalform
    oms_tillvxt_dec = ((df["omsattningstillvaxt_ar1"] + df["omsattningstillvaxt_ar2"]) / 2) / 100

    # Beräkna targetkurs_ps som medel av ps_1 och ps_2 * genomsn omsättningstillväxt * kurs_nu
    # En rimligare formel är (ps * omsättningstillväxt) * omsättning (eller kurs) - anpassa efter din logik
    # Här gör vi: targetkurs_ps = genomsnitt(ps_1, ps_2) * (1 + genomsnittlig omsättningstillväxt) * kurs_nu

    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + oms_tillvxt_dec) * df["kurs_nu"]

    # Undervärdering i % = (targetkurs - kurs_nu) / kurs_nu * 100
    df["undervardering_pe"] = ((df["targetkurs_pe"] - df["kurs_nu"]) / df["kurs_nu"]) * 100
    df["undervardering_ps"] = ((df["targetkurs_ps"] - df["kurs_nu"]) / df["kurs_nu"]) * 100

    # Köp-värd = True om undervärdering minst 30% (på pe eller ps)
    df["kopvard"] = ((df["undervardering_pe"] >= 30) | (df["undervardering_ps"] >= 30))

    # Rensa eventuella oändligheter eller NaN
    df.replace([np.inf, -np.inf], 0, inplace=True)
    df.fillna(0, inplace=True)

    return df


def visa_bolag(df):
    st.header("Översikt över bolag och värdering")

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    df = berakna_targetkurser(df)

    # Sortera på högsta undervärdering (pe eller ps)
    df["max_undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)
    df = df.sort_values(by="max_undervardering", ascending=False)

    # Checkbox: Visa endast undervärderade bolag
    visa_endast_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)

    if visa_endast_undervarderade:
        df_vis = df[df["kopvard"] == True]
    else:
        df_vis = df

    if df_vis.empty:
        st.warning("Inga bolag uppfyller kriterierna för visning.")
        return df

    # Visa tabell med valda kolumner
    kolumner = [
        "bolagsnamn", "kurs_nu", "targetkurs_pe", "targetkurs_ps",
        "undervardering_pe", "undervardering_ps", "kopvard"
    ]

    # Formatera procent och decimalsiffror
    df_vis_display = df_vis[kolumner].copy()
    df_vis_display["kurs_nu"] = df_vis_display["kurs_nu"].map("{:.2f}".format)
    df_vis_display["targetkurs_pe"] = df_vis_display["targetkurs_pe"].map("{:.2f}".format)
    df_vis_display["targetkurs_ps"] = df_vis_display["targetkurs_ps"].map("{:.2f}".format)
    df_vis_display["undervardering_pe"] = df_vis_display["undervardering_pe"].map("{:.1f}%".format)
    df_vis_display["undervardering_ps"] = df_vis_display["undervardering_ps"].map("{:.1f}%".format)
    df_vis_display["kopvard"] = df_vis_display["kopvard"].map({True: "Ja", False: "Nej"})

    st.dataframe(df_vis_display.reset_index(drop=True), use_container_width=True)

    # Möjlighet att ta bort bolag via selectbox
    st.markdown("---")
    st.subheader("Ta bort bolag")

    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df

    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
    if st.button("Ta bort valt bolag"):
        df = ta_bort_bolag(df, bolag_att_ta_bort)
        st.success(f"Bolag '{bolag_att_ta_bort}' har tagits bort.")
        spara_data(df)
        st.experimental_rerun()

    return df


def ta_bort_bolag(df, bolagsnamn):
    if bolagsnamn in df["bolagsnamn"].values:
        df = df[df["bolagsnamn"] != bolagsnamn].reset_index(drop=True)
    return df

# --- Del 5: Huvudfunktion och appstart ---

def main():
    st.set_page_config(page_title="Aktieanalysapp", layout="wide")
    st.title("Aktieanalysapp med värdering och redigering")

    # Läs in data från fil eller starta tom df
    df = las_data()

    # Visa formulär för inmatning/redigering av bolag
    df = visa_form(df)

    # Visa bolagstabell, undervärdering, och borttagning
    df = visa_bolag(df)

    # Spara data vid varje ändring
    spara_data(df)


if __name__ == "__main__":
    main()
