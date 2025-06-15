import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATAFIL = "aktiedata.json"

# --- Datahantering ---

def las_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att kolumner har rätt datatyper
        df = df.astype({
            "nuvarande_kurs": float,
            "vinst_forra_aret": float,
            "vinst_i_ar": float,
            "vinst_nasta_ar": float,
            "omsattning_forra_aret": float,
            "omsattningstillvaxt_ar": float,
            "omsattningstillvaxt_nasta_ar": float,
            "nuvarande_pe": float,
            "pe_1": float,
            "pe_2": float,
            "pe_3": float,
            "pe_4": float,
            "nuvarande_ps": float,
            "ps_1": float,
            "ps_2": float,
            "ps_3": float,
            "ps_4": float,
        })
        # Datumfält
        for date_col in ["insatt_datum", "senast_andrad"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            else:
                df[date_col] = pd.NaT
        return df
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn",
            "nuvarande_kurs",
            "vinst_forra_aret",
            "vinst_i_ar",
            "vinst_nasta_ar",
            "omsattning_forra_aret",
            "omsattningstillvaxt_ar",
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
        ])

def spara_data(df):
    # Konvertera datetime till str för json-serialisering
    df_copy = df.copy()
    for col in ["insatt_datum", "senast_andrad"]:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    with open(DATAFIL, "w", encoding="utf-8") as f:
        json.dump(df_copy.to_dict(orient="records"), f, ensure_ascii=False, indent=2)


# --- Funktion: Lägg till eller uppdatera bolag ---

def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    bolagsnamn_ny = bolag_ny["bolagsnamn"].strip().lower()
    if "bolagsnamn" not in df.columns:
        df["bolagsnamn"] = []
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny]
    now = pd.Timestamp.now()
    if len(idx) > 0:
        # Uppdatera befintlig rad
        i = idx[0]
        for key, val in bolag_ny.items():
            df.at[i, key] = val
        df.at[i, "senast_andrad"] = now
    else:
        # Lägg till nytt bolag
        bolag_ny["insatt_datum"] = now
        bolag_ny["senast_andrad"] = now
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)
    return df.reset_index(drop=True)


# --- Funktion: Beräkna targetkurser och undervärdering ---

def berakna_targetkurser(df):
    if df.empty:
        return df
    # Skydda mot division med noll eller saknade värden
    df = df.copy()

    # Targetkurs P/E: genomsnitt av pe_1 och pe_2 * vinst_nasta_ar
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Targetkurs P/S: medelvärde av ps_1 och ps_2 * omsattningstillvaxt medel * nuvarande kurs
    oms_tillv_med = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100  # omvandla % till dec
    ps_med = (df["ps_1"] + df["ps_2"]) / 2

    # Targetkurs P/S beräknas som: ps_med * oms_tillv_med * nuvarande_kurs
    # (Alternativt: ps_med * omsattningstillvaxt_med * nuvarande_kurs, men ofta targetkurs = ps_med * omsattning)
    df["targetkurs_ps"] = ps_med * oms_tillv_med * df["nuvarande_kurs"]

    # Undervärdering % jämfört med nuvarande kurs
    df["undervärdering_pe_%"] = 100 * (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]
    df["undervärdering_ps_%"] = 100 * (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]

    # Hantera NaN och infinit
    df["undervärdering_pe_%"] = df["undervärdering_pe_%"].fillna(0).clip(lower=-100, upper=100)
    df["undervärdering_ps_%"] = df["undervärdering_ps_%"].fillna(0).clip(lower=-100, upper=100)

    # Max undervärdering per bolag (den mest intressanta)
    df["max_undervärdering_%"] = df[["undervärdering_pe_%", "undervärdering_ps_%"]].max(axis=1)

    # Köpvärd vid minst 30% rabatt på targetkurs (sant/falskt)
    df["kopvard"] = ((df["max_undervärdering_%"] >= 30) | (df["undervärdering_pe_%"] >= 30) | (df["undervärdering_ps_%"] >= 30))

    return df

# --- Del 2: Visning och filtrering av bolag ---

def visa_bolag(df):
    st.header("Översikt av sparade bolag")

    if df.empty:
        st.info("Inga bolag inlagda ännu.")
        return df

    df = berakna_targetkurser(df)

    # Checkbox för att visa endast köpvärda bolag (minst 30% undervärdering)
    visa_endast_kopvard = st.checkbox("Visa endast köpvärda bolag (minst 30% undervärdering)", value=False)

    if visa_endast_kopvard:
        df_vis = df[df["kopvard"] == True].copy()
    else:
        df_vis = df.copy()

    if df_vis.empty:
        st.warning("Inga bolag matchar filtreringen.")
        return df

    # Sortera efter max undervärdering % (fallande)
    df_vis = df_vis.sort_values(by="max_undervärdering_%", ascending=False)

    # Skapa en presentationstabell med önskade kolumner
    vis_df = pd.DataFrame()
    vis_df["Bolagsnamn"] = df_vis["bolagsnamn"]
    vis_df["Nuvarande kurs"] = df_vis["nuvarande_kurs"].map("{:.2f} kr".format)
    vis_df["Targetkurs P/E"] = df_vis["targetkurs_pe"].map("{:.2f} kr".format)
    vis_df["Targetkurs P/S"] = df_vis["targetkurs_ps"].map("{:.2f} kr".format)
    # Visa högsta undervärdering i %
    vis_df["Undervärdering %"] = df_vis["max_undervärdering_%"].map("{:.1f} %".format)
    # Köpvärd?
    vis_df["Köp värd vid 30% rabatt"] = df_vis["kopvard"].map({True: "✅", False: ""})

    # Visa tabellen med bredare kolumner för bättre läsbarhet
    st.dataframe(vis_df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)

    return df

# --- Del 3: Formulär för inmatning, redigering och borttagning av bolag ---

def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form(key="bolagsform_add_update"):
        bolagsnamn = st.text_input("Bolagsnamn", max_chars=50)
        nuvarande_kurs = st.number_input("Nuvarande kurs (kr)", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året (kr)", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år (kr)", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år (kr)", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året (kr)", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")
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

        submitted = st.form_submit_button("Lägg till / Uppdatera bolag")

    if submitted:
        if not bolagsnamn:
            st.error("Ange ett bolagsnamn.")
            return df

        nytt_bolag = {
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
            "insatt_datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "senast_andrad": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
        st.success(f"Bolaget '{bolagsnamn}' har lagts till eller uppdaterats.")

    st.markdown("---")
    st.header("Ta bort bolag")

    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df

    with st.form(key="bolagsform_delete"):
        bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
        raderad = st.form_submit_button("Ta bort valt bolag")

    if raderad:
        df = ta_bort_bolag(df, bolag_att_ta_bort)
        st.success(f"Bolaget '{bolag_att_ta_bort}' har tagits bort.")

    return df


def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    bolagsnamn_ny = bolag_ny["bolagsnamn"].lower()
    if "bolagsnamn" not in df.columns:
        df["bolagsnamn"] = []

    # Kontrollera om bolaget redan finns
    idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()
    if idx:
        # Uppdatera befintlig rad
        idx = idx[0]
        for nyckel, varde in bolag_ny.items():
            df.at[idx, nyckel] = varde
    else:
        # Lägg till nytt bolag
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)

    return df


def ta_bort_bolag(df, bolagsnamn):
    if "bolagsnamn" not in df.columns:
        return df
    df = df[df["bolagsnamn"].str.lower() != bolagsnamn.lower()]
    df = df.reset_index(drop=True)
    return df

# --- Del 4: Beräkningar och visning av bolag ---

def berakna_targetkurser(df):
    if df.empty:
        return df

    # Säkerställ att kolumner finns innan beräkning
    for kolumn in ["vinst_nasta_ar", "pe_1", "pe_2", "nuvarande_kurs", 
                   "nuvarande_pe", "nuvarande_ps", "ps_1", "ps_2",
                   "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
                   "ps_1", "ps_2"]:
        if kolumn not in df.columns:
            df[kolumn] = 0

    # Targetkurs P/E baserat på vinst nästa år och medel P/E 1 & 2
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medel omsättningstillväxt (års1 och års2)
    df["omsattningstillvaxt_medel"] = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100

    # Targetkurs P/S baserat på medelvärde P/S * omsättningstillväxt * omsättning förra året
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * df["omsattning_forra_aret"] * (1 + df["omsattningstillvaxt_medel"])

    # Undervärdering i % relativt nuvarande kurs (mål minus kurs) / kurs * 100
    df["undervardering_pe_%"] = ((df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]) * 100
    df["undervardering_ps_%"] = ((df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]) * 100

    # Max undervärdering av P/E och P/S för sortering och presentation
    df["max_undervardering_%"] = df[["undervardering_pe_%", "undervardering_ps_%"]].max(axis=1)

    # Köp-värd: True om max undervärdering är minst 30%
    df["kopvard"] = df["max_undervardering_%"] >= 30

    return df


def visa_bolag(df):
    st.header("Bolagsöversikt")

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    df = berakna_targetkurser(df)

    # Checkbox för att visa endast köpvärda bolag (>30% undervärdering)
    endast_kopvard = st.checkbox("Visa endast köpvärda bolag (minst 30% undervärdering)")

    if endast_kopvard:
        filtrerat_df = df[df["kopvard"]].copy()
    else:
        filtrerat_df = df.copy()

    if filtrerat_df.empty:
        st.warning("Inga bolag matchar filtreringen.")
        return df

    # Sortera på max undervärdering högst först
    filtrerat_df = filtrerat_df.sort_values(by="max_undervardering_%", ascending=False)

    # Välj vilka kolumner som ska visas
    visningskolumner = [
        "bolagsnamn",
        "nuvarande_kurs",
        "targetkurs_pe",
        "targetkurs_ps",
        "undervardering_pe_%",
        "undervardering_ps_%",
        "max_undervardering_%",
        "kopvard",
        "insatt_datum",
        "senast_andrad",
    ]

    # Runda siffror för bättre läsbarhet
    filtrerat_df["nuvarande_kurs"] = filtrerat_df["nuvarande_kurs"].round(2)
    filtrerat_df["targetkurs_pe"] = filtrerat_df["targetkurs_pe"].round(2)
    filtrerat_df["targetkurs_ps"] = filtrerat_df["targetkurs_ps"].round(2)
    filtrerat_df["undervardering_pe_%"] = filtrerat_df["undervardering_pe_%"].round(1)
    filtrerat_df["undervardering_ps_%"] = filtrerat_df["undervardering_ps_%"].round(1)
    filtrerat_df["max_undervardering_%"] = filtrerat_df["max_undervardering_%"].round(1)

    # Anpassa kolumnnamn för presentation
    filtrerat_df = filtrerat_df.rename(columns={
        "bolagsnamn": "Bolagsnamn",
        "nuvarande_kurs": "Nuvarande kurs",
        "targetkurs_pe": "Targetkurs P/E",
        "targetkurs_ps": "Targetkurs P/S",
        "undervardering_pe_%": "Undervärdering P/E (%)",
        "undervardering_ps_%": "Undervärdering P/S (%)",
        "max_undervardering_%": "Max undervärdering (%)",
        "kopvard": "Köpvärd (≥30%)",
        "insatt_datum": "Insatt datum",
        "senast_andrad": "Senast ändrad",
    })

    st.dataframe(filtrerat_df[visningskolumner], use_container_width=True)

    return df

# --- Del 5: Huvudfunktion, datahantering och appstart ---

import streamlit as st
import pandas as pd
import json
from datetime import datetime

DATAFIL = "aktiedata.json"

def las_data():
    try:
        with open(DATAFIL, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att datumfält är datetime
        if "insatt_datum" in df.columns:
            df["insatt_datum"] = pd.to_datetime(df["insatt_datum"], errors='coerce')
        if "senast_andrad" in df.columns:
            df["senast_andrad"] = pd.to_datetime(df["senast_andrad"], errors='coerce')
        return df
    except Exception:
        # Om fil saknas eller är tom, returnera tom DataFrame med kolumner definierade
        kolumner = [
            "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=kolumner)


def spara_data(df):
    try:
        # Konvertera datetime till str för JSON
        df_spar = df.copy()
        for kol in ["insatt_datum", "senast_andrad"]:
            if kol in df_spar.columns:
                df_spar[kol] = df_spar[kol].astype(str)
        with open(DATAFIL, "w") as f:
            json.dump(df_spar.to_dict(orient="records"), f, indent=4)
    except Exception as e:
        st.error(f"Fel vid sparande av data: {e}")


def main():
    st.title("Aktieanalysapp")

    # Läs data från fil
    df = las_data()

    # Visa bolagslista och beräkningar
    df = visa_bolag(df)

    # Formulär för tillägg och redigering
    df = visa_form(df)

    # Spara data
    spara_data(df)


if __name__ == "__main__":
    main()
