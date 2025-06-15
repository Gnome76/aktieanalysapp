import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_PATH = "aktie_data.json"

# --- Funktion: Ladda data från JSON ---
def las_in_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Säkerställ att kolumner finns
        expected_cols = [
            "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_ars", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_ars", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        return df[expected_cols]
    else:
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_ars", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_ars", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ])

# --- Funktion: Spara data till JSON ---
def spara_data(df):
    with open(DATA_PATH, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# --- Funktion: Beräkna targetkurser och undervärdering ---
def berakna_targetkurser(df):
    if df.empty:
        return df

    # Säkerställ att kolumner är numeriska för beräkning
    num_cols = [
        "vinst_nasta_ar", "pe_1", "pe_2",
        "ps_1", "ps_2",
        "nuvarande_kurs", "nuvarande_pe", "nuvarande_ps"
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Beräkna targetkurs_pe
    def calc_target_pe(row):
        if pd.notnull(row["vinst_nasta_ar"]) and pd.notnull(row["pe_1"]) and pd.notnull(row["pe_2"]):
            return row["vinst_nasta_ar"] * ((row["pe_1"] + row["pe_2"]) / 2)
        else:
            return None

    df["targetkurs_pe"] = df.apply(calc_target_pe, axis=1)

    # Beräkna genomsnittlig omsättningstillväxt
    def genoms_omsattningstillvaxt(row):
        vals = []
        for val in [row["omsattningstillvaxt_ars"], row["omsattningstillvaxt_nasta_ar"]]:
            try:
                if pd.notnull(val):
                    vals.append(float(val))
            except:
                pass
        if vals:
            return sum(vals)/len(vals)/100  # Procent till decimal
        else:
            return None

    df["genoms_omsattningstillvaxt"] = df.apply(genoms_omsattningstillvaxt, axis=1)

    # Beräkna targetkurs_ps
    def calc_target_ps(row):
        if pd.notnull(row["ps_1"]) and pd.notnull(row["ps_2"]) and pd.notnull(row["genoms_omsattningstillvaxt"]):
            medel_ps = (row["ps_1"] + row["ps_2"]) / 2
            return medel_ps * (1 + row["genoms_omsattningstillvaxt"]) * row["nuvarande_kurs"]
        else:
            return None

    df["targetkurs_ps"] = df.apply(calc_target_ps, axis=1)

    # Beräkna undervärdering % (lägst av P/E och P/S)
    def calc_undervardering(row):
        if pd.notnull(row["targetkurs_pe"]) and pd.notnull(row["nuvarande_kurs"]) and row["targetkurs_pe"] > 0:
            underv_pe = (row["targetkurs_pe"] - row["nuvarande_kurs"]) / row["targetkurs_pe"] * 100
        else:
            underv_pe = None
        if pd.notnull(row["targetkurs_ps"]) and pd.notnull(row["nuvarande_kurs"]) and row["targetkurs_ps"] > 0:
            underv_ps = (row["targetkurs_ps"] - row["nuvarande_kurs"]) / row["targetkurs_ps"] * 100
        else:
            underv_ps = None

        undervarderingar = [v for v in [underv_pe, underv_ps] if v is not None]
        if undervarderingar:
            return max(undervarderingar)
        else:
            return None

    df["undervardering_pct"] = df.apply(calc_undervardering, axis=1)

    # Köp värd vid 30% rabatt (targetkurs * 0.7)
    df["kopvard_30pct_pe"] = df["targetkurs_pe"] * 0.7
    df["kopvard_30pct_ps"] = df["targetkurs_ps"] * 0.7

    return df

# --- Del 3: Funktioner för att lägga till, uppdatera och visa bolag ---

def lagg_till_eller_uppdatera_bolag(df, nytt_bolag):
    bolagsnamn_ny = nytt_bolag["bolagsnamn"].strip().lower()
    if "bolagsnamn" not in df.columns:
        df = pd.DataFrame(columns=nytt_bolag.keys())

    # Rensa index om df är tom
    if df.empty:
        df = pd.DataFrame(columns=nytt_bolag.keys())

    # Kontrollera om bolaget redan finns (case insensitive)
    if "bolagsnamn" in df.columns:
        # Säkerställ att alla bolagsnamn är strängar
        df["bolagsnamn"] = df["bolagsnamn"].astype(str)

        idx = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()
        if idx:
            i = idx[0]
            for key, value in nytt_bolag.items():
                df.at[i, key] = value
            df.at[i, "senast_andrad"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' uppdaterat.")
        else:
            nytt_bolag["insatt_datum"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nytt_bolag["senast_andrad"] = ""
            df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)
            st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' tillagt.")
    else:
        # Om "bolagsnamn" saknas, lägg till hela raden
        nytt_bolag["insatt_datum"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nytt_bolag["senast_andrad"] = ""
        df = pd.concat([df, pd.DataFrame([nytt_bolag])], ignore_index=True)
        st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' tillagt.")
    return df

def visa_form(df):
    with st.form(key="form_add_bolag"):
        st.header("Lägg till eller uppdatera bolag")

        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_foregaende_ar = st.number_input("Vinst förra året", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_foregaende_ar = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")

        pe_0 = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f")

        ps_0 = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f")

        submit_button = st.form_submit_button(label="Spara bolag")

    if submit_button:
        nytt_bolag = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_foregaende_ar": vinst_foregaende_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_foregaende_ar": omsattning_foregaende_ar,
            "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
            "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
            "pe_0": pe_0,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "pe_3": pe_3,
            "pe_4": pe_4,
            "ps_0": ps_0,
            "ps_1": ps_1,
            "ps_2": ps_2,
            "ps_3": ps_3,
            "ps_4": ps_4,
        }
        df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
        spara_data(df)
    return df

# --- Del 4: Beräkning av targetkurser och filtrering av bolag ---

def berakna_targetkurser(df):
    # Försök räkna ut targetkurser och undervärdering, hantera saknade värden försiktigt
    def safe_mean(values):
        valid = [v for v in values if v is not None and v > 0]
        return sum(valid) / len(valid) if valid else None

    # Targetkurs baserad på P/E
    def targetkurs_pe(row):
        pe_vals = [row.get("pe_1"), row.get("pe_2")]
        pe_med = safe_mean(pe_vals)
        if pe_med is None or row.get("vinst_nasta_ar") is None:
            return None
        return row["vinst_nasta_ar"] * pe_med

    # Targetkurs baserad på P/S
    def targetkurs_ps(row):
        ps_vals = [row.get("ps_1"), row.get("ps_2")]
        ps_med = safe_mean(ps_vals)
        oms_tillv_vals = [row.get("omsattningstillvaxt_ar"), row.get("omsattningstillvaxt_nasta_ar")]
        oms_tillv_med = safe_mean(oms_tillv_vals)
        omsattning = row.get("omsattning_foregaende_ar")
        if None in (ps_med, oms_tillv_med, omsattning):
            return None
        oms_tillv_factor = 1 + oms_tillv_med / 100
        return ps_med * omsattning * oms_tillv_factor

    df = df.copy()

    df["targetkurs_pe"] = df.apply(lambda row: targetkurs_pe(row), axis=1)
    df["targetkurs_ps"] = df.apply(lambda row: targetkurs_ps(row), axis=1)

    # Undervärdering i procent jämfört med nuvarande kurs
    def undervarderingsprocent(row):
        kurs = row.get("nuvarande_kurs")
        targets = [row.get("targetkurs_pe"), row.get("targetkurs_ps")]
        targets = [t for t in targets if t is not None and t > 0]
        if kurs is None or kurs == 0 or not targets:
            return None
        max_target = max(targets)
        return (max_target - kurs) / max_target * 100

    df["undervarderingsprocent"] = df.apply(undervarderingsprocent, axis=1)

    # Köpvärd kurs vid 30% rabatt på max targetkurs
    def kopvard_kurs(row):
        targets = [row.get("targetkurs_pe"), row.get("targetkurs_ps")]
        targets = [t for t in targets if t is not None and t > 0]
        if not targets:
            return None
        max_target = max(targets)
        return max_target * 0.7

    df["kopvard_kurs_30"] = df.apply(kopvard_kurs, axis=1)

    return df

def filtrera_bolag(df, endast_undervarderade):
    df = berakna_targetkurser(df)

    if endast_undervarderade:
        # Filtrera bolag med minst 30% undervärdering
        df = df[df["undervarderingsprocent"] >= 30]

    # Sortera på mest undervärderade först (störst procent)
    df = df.sort_values(by="undervarderingsprocent", ascending=False, na_position="last")
    df = df.reset_index(drop=True)
    return df

# --- Del 5: Visning, inmatning, redigering och borttagning av bolag ---

def visa_bolag(df):
    st.subheader("Översikt av sparade bolag")
    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return

    # Visa bolagstabell med utvalda kolumner
    visningskolumner = [
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps",
        "undervarderingsprocent", "kopvard_kurs_30"
    ]
    df_vis = df[visningskolumner].copy()
    df_vis["undervarderingsprocent"] = df_vis["undervarderingsprocent"].map(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
    )
    df_vis["targetkurs_pe"] = df_vis["targetkurs_pe"].map(
        lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
    )
    df_vis["targetkurs_ps"] = df_vis["targetkurs_ps"].map(
        lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
    )
    df_vis["kopvard_kurs_30"] = df_vis["kopvard_kurs_30"].map(
        lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
    )
    st.dataframe(df_vis, use_container_width=True)

def lagg_till_bolag(df):
    st.subheader("Lägg till nytt bolag")

    with st.form("form_lagg_till_bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_foregaende_ar = st.number_input("Vinst förra året", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_foregaende_ar = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Lägg till bolag")

    if submitted:
        nytt_bolag = {
            "bolagsnamn": bolagsnamn.strip(),
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_foregaende_ar": vinst_foregaende_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_foregaende_ar": omsattning_foregaende_ar,
            "omsattningstillvaxt_ar": omsattningstillvaxt_ar,
            "omsattningstillvaxt_nasta_ar": omsattningstillvaxt_nasta_ar,
            "pe_1": pe_1,
            "pe_2": pe_2,
            "ps_1": ps_1,
            "ps_2": ps_2,
        }

        if not nytt_bolag["bolagsnamn"]:
            st.error("Bolagsnamn får inte vara tomt.")
        else:
            df = lagg_till_eller_uppdatera_bolag(df, nytt_bolag)
            st.success(f"Bolag '{nytt_bolag['bolagsnamn']}' har lagts till eller uppdaterats.")
            spara_data(df)
            st.experimental_rerun()

    return df

def lagg_till_eller_uppdatera_bolag(df, bolag_dict):
    bolagsnamn_ny = bolag_dict["bolagsnamn"].lower()
    df = df.copy()

    # Kontrollera om bolaget finns redan (case-insensitivt)
    if "bolagsnamn" in df.columns:
        idx_list = df.index[df["bolagsnamn"].str.lower() == bolagsnamn_ny].tolist()
    else:
        idx_list = []

    if idx_list:
        idx = idx_list[0]
        # Uppdatera existerande rad
        for key, value in bolag_dict.items():
            df.at[idx, key] = value
        df.at[idx, "senast_andrad"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Lägg till nytt bolag som ny rad
        bolag_dict["insatt_datum"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        bolag_dict["senast_andrad"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        df = pd.concat([df, pd.DataFrame([bolag_dict])], ignore_index=True)

    return df

def ta_bort_bolag(df):
    st.subheader("Ta bort bolag")
    if df.empty:
        st.info("Inga bolag att ta bort.")
        return df

    bolag_lista = df["bolagsnamn"].tolist()
    valt_bolag = st.selectbox("Välj bolag att ta bort", options=bolag_lista)

    if st.button("Ta bort valt bolag"):
        df = df[df["bolagsnamn"] != valt_bolag]
        spara_data(df)
        st.success(f"Bolag '{valt_bolag}' har tagits bort.")
        st.experimental_rerun()

    return df

# --- Del 6: Huvudfunktion och appstart ---

def main():
    st.title("Aktieanalysapp - Undervärderade Bolag")

    # Läs in data
    df = las_in_data()

    # Checkbox för att visa endast undervärderade bolag
    endast_undervarderade = st.checkbox("Visa endast minst 30% undervärderade bolag", value=False)

    # Beräkna targetkurser och undervärdering
    df = beräkna_targetkurser(df)

    # Filtrera bolag enligt checkbox
    filtrerad_df = filtrera_bolag(df, endast_undervarderade)

    # Visa bolagstabell
    visa_bolag(filtrerad_df)

    # Lägga till nytt bolag
    df = lagg_till_bolag(df)

    # Ta bort bolag
    df = ta_bort_bolag(df)

if __name__ == "__main__":
    main()
