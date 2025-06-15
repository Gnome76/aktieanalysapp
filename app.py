import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Filnamn för datalagring i Streamlit Cloud
DATA_FILE = "/mnt/data/aktie_data.json"

def las_data():
    """Läser data från JSON-fil, returnerar DataFrame."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        # Returnera tom DataFrame med rätt kolumner om fil saknas
        columns = [
            "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_aret", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=columns)

def lagra_data(df):
    """Sparar DataFrame som JSON-fil."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

def berakna_target_och_undervardering(df):
    """Beräknar targetkurser och undervärdering."""
    if df.empty:
        return df

    # Säkerställ numeriska värden för beräkningarna, fyll NaN med 0
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "nuvarande_kurs",
                "nuvarande_pe", "nuvarande_ps", "omsattning_fjol", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_ar"]:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs baserat på P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medel omsättningstillväxt
    df["medel_omsattningstillvaxt"] = ((df["omsattningstillvaxt_aret"] + df["omsattningstillvaxt_nasta_ar"]) / 2) / 100

    # Medel P/S
    df["medel_ps"] = (df["ps_1"] + df["ps_2"]) / 2

    # Targetkurs baserat på P/S och omsättningstillväxt
    df["targetkurs_ps"] = df["medel_ps"] * df["omsattning_fjol"] * (1 + df["medel_omsattningstillvaxt"])

    # Undervärdering i procent baserat på lägsta targetkurs
    df["min_targetkurs"] = df[["targetkurs_pe", "targetkurs_ps"]].min(axis=1)
    df["undervardering"] = ((df["min_targetkurs"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]) * 100

    # Runda till två decimaler
    df["undervardering"] = df["undervardering"].round(2)
    df["targetkurs_pe"] = df["targetkurs_pe"].round(2)
    df["targetkurs_ps"] = df["targetkurs_ps"].round(2)

    return df

def lagg_till_eller_uppdatera_bolag(df, ny_bolag):
    """Lägger till eller uppdaterar ett bolag i DataFrame."""
    bolagsnamn = ny_bolag["bolagsnamn"]
    nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if bolagsnamn in df["bolagsnamn"].values:
        # Uppdatera befintligt bolag
        idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
        ny_bolag["insatt_datum"] = df.at[idx, "insatt_datum"]  # Behåll ursprungligt insatt datum
        ny_bolag["senast_andrad"] = nu
        df.loc[idx] = ny_bolag
    else:
        # Lägg till nytt bolag
        ny_bolag["insatt_datum"] = nu
        ny_bolag["senast_andrad"] = nu
        df = pd.concat([df, pd.DataFrame([ny_bolag])], ignore_index=True)

    return df

def visa_form(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form("bolagsform", clear_on_submit=False):
        bolagsnamn = st.text_input("Bolagsnamn", max_chars=50)
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

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            if bolagsnamn.strip() == "":
                st.error("Bolagsnamn måste fyllas i!")
                return df
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
                "ps_4": ps_4,
            }
            df = lagg_till_eller_uppdatera_bolag(df, ny_bolag)
            lagra_data(df)
            st.success(f"Bolag '{bolagsnamn}' har sparats/uppdaterats!")
            st.experimental_rerun()

    return df

def visa_bolagslista(df):
    st.header("Sparade bolag")

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    # Sortera på undervärdering, visa högst undervärderade först
    df = berakna_target_och_undervardering(df)
    df_visning = df.sort_values(by="undervardering", ascending=False)

    # Checkbox för filtrering undervärderade minst 30%
    filtrera = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)
    if filtrera:
        df_visning = df_visning[df_visning["undervardering"] >= 30]

    # Visa som tabell med relevanta kolumner
    st.dataframe(df_visning[[
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering",
        "insatt_datum", "senast_andrad"
    ]].reset_index(drop=True))

    # Möjlighet att ta bort bolag
    ta_bort = st.selectbox("Välj bolag att ta bort", options=[""] + list(df["bolagsnamn"]))
    if ta_bort and ta_bort != "":
        if st.button(f"Ta bort '{ta_bort}'"):
            df = df[df["bolagsnamn"] != ta_bort]
            lagra_data(df)
            st.success(f"Bolag '{ta_bort}' har tagits bort.")
            st.experimental_rerun()

    return df

def lagg_till_eller_uppdatera_bolag(df, bolag_ny):
    # Kolla om bolaget finns
    idx = df.index[df["bolagsnamn"].str.lower() == bolag_ny["bolagsnamn"].lower()]
    if len(idx) > 0:
        # Uppdatera befintligt bolag
        i = idx[0]
        for key, value in bolag_ny.items():
            df.at[i, key] = value
        df.at[i, "senast_andrad"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Lägg till nytt bolag
        bolag_ny["insatt_datum"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        bolag_ny["senast_andrad"] = ""
        df = pd.concat([df, pd.DataFrame([bolag_ny])], ignore_index=True)
    return df

def lagra_data(df, filnamn="aktier_data.json"):
    try:
        df.to_json(filnamn, orient="records", indent=2)
    except Exception as e:
        st.error(f"Fel vid sparande av data: {e}")

def las_data(filnamn="aktier_data.json"):
    try:
        df = pd.read_json(filnamn)
        return df
    except Exception:
        # Om fil saknas eller läsning misslyckas, returnera tom DataFrame
        columns = [
            "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_aret", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_aret", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ]
        return pd.DataFrame(columns=columns)

def main():
    st.title("Aktieanalysapp - Streamlit Cloud")

    df = las_data()

    # Visa lista med bolag, möjlighet ta bort
    df = visa_bolagslista(df)

    # Visa form för att lägga till/uppdatera bolag
    df = visa_form(df)

    # Spara data automatiskt efter ändringar
    lagra_data(df)


if __name__ == "__main__":
    main()

def berakna_target_och_undervardering(df):
    # Säkerställ att kolumner finns och är numeriska för beräkningar
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2", "nuvarande_ps", "nuvarande_pe"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs PE
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medel omsättningstillväxt i decimalform
    df["oms_tillv_medel"] = ((df["omsattningstillvaxt_aret"] + df["omsattningstillvaxt_nasta_ar"]) / 2) / 100

    # Medel P/S för år 1 och 2
    df["ps_medel"] = (df["ps_1"] + df["ps_2"]) / 2

    # Targetkurs PS
    df["targetkurs_ps"] = df["ps_medel"] * (1 + df["oms_tillv_medel"]) * df["nuvarande_ps"]

    # Undervärdering, högsta procentvisa skillnad från nuvarande kurs mot targetkurserna
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]

    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    return df

def visa_bolagslista(df):
    st.header("Sparade bolag")
    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return df

    # Uppdatera beräkningar
    df = berakna_target_och_undervardering(df)

    # Sortera på undervärdering
    df = df.sort_values(by="undervardering", ascending=False)

    # Filtrera undervärderade bolag
    visa_endast_undervarderade = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)
    if visa_endast_undervarderade:
        df_vis = df[df["undervardering"] >= 0.3]
    else:
        df_vis = df.copy()

    # Visa tabell
    st.dataframe(df_vis[[
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering"
    ]])

    # Ta bort bolag
    ta_bort_bolag = st.selectbox("Ta bort bolag", options=[""] + df["bolagsnamn"].tolist())
    if ta_bort_bolag:
        if st.button(f"Ta bort {ta_bort_bolag}"):
            df = df[df["bolagsnamn"] != ta_bort_bolag]
            st.experimental_rerun()
    return df

def visa_form(df):
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

        submitted = st.form_submit_button("Spara bolag")

    if submitted:
        if not bolagsnamn:
            st.error("Ange ett bolagsnamn.")
        else:
            bolag_ny = {
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
            df = lagg_till_eller_uppdatera_bolag(df, bolag_ny)
            st.success(f"Bolag '{bolagsnamn}' sparat/uppdaterat.")
            st.experimental_rerun()

    return df
