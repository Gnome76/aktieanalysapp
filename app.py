import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "bolag_data.json"

# Läs in data från json-fil
def las_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                return pd.DataFrame(data)
            except json.JSONDecodeError:
                return pd.DataFrame()
    else:
        return pd.DataFrame()

# Spara data till json-fil
def spara_data(df):
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4, default=str)

# Beräkna targetkurser och undervärdering
def berakna_target_och_undervardering(df):
    if df.empty:
        return df
    # Säkerställ att nödvändiga kolumner finns och är numeriska
    for col in ["vinst_nasta_ar", "pe_1", "pe_2", "nuvarande_kurs", "ps_1", "ps_2", "nuvarande_ps"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs baserat på PE
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medel omsättningstillväxt i decimalform
    df["omsattningstillvaxt_medel"] = (
        (pd.to_numeric(df["omsattningstillvaxt_ar"], errors='coerce').fillna(0) +
         pd.to_numeric(df["omsattningstillvaxt_nasta_ar"], errors='coerce').fillna(0)) / 2) / 100

    # Beräkna targetkurs_ps som genomsnitt av P/S * omsättningstillväxt * nuvarande kurs
    df["targetkurs_ps"] = ((df["ps_1"] + df["ps_2"]) / 2) * (1 + df["omsattningstillvaxt_medel"]) * df["nuvarande_kurs"]

    # Undervärdering = max av undervärdering enligt P/E och P/S
    df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]
    df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]

    # Tar högsta undervärdering (för att få konservativt estimat)
    df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    # Rensa eventuella NaN
    df["undervardering"] = df["undervardering"].fillna(0)

    return df

# Funktion för att lägga till eller uppdatera bolag i DataFrame
def lagg_till_eller_uppdatera_bolag(df, data):
    bolagsnamn = data["bolagsnamn"].strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if bolagsnamn == "":
        st.warning("Bolagsnamn får inte vara tomt.")
        return df, False

    # Om df är tom, skapa det med rätt kolumner
    if df.empty:
        df = pd.DataFrame(columns=data.keys())

    # Kontrollera om bolag redan finns
    if bolagsnamn in df["bolagsnamn"].values:
        idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
        for key, value in data.items():
            df.at[idx, key] = value
        df.at[idx, "senast_andrad"] = now
    else:
        data["insatt_datum"] = now
        data["senast_andrad"] = now
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    return df, True

# Funktion för att ta bort bolag från DataFrame
def ta_bort_bolag(df, bolagsnamn):
    if bolagsnamn in df["bolagsnamn"].values:
        df = df[df["bolagsnamn"] != bolagsnamn].reset_index(drop=True)
        st.success(f"Bolaget '{bolagsnamn}' har tagits bort.")
    else:
        st.warning(f"Bolaget '{bolagsnamn}' hittades inte.")
    return df

# Formulär för inmatning/uppdatering av bolag
def bolagsform(df):
    st.header("Lägg till eller uppdatera bolag")

    with st.form("bolagsform"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_fjol = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_fjol = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
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
            ny_data = {
                "bolagsnamn": bolagsnamn,
                "nuvarande_kurs": nuvarande_kurs,
                "vinst_fjol": vinst_fjol,
                "vinst_i_ar": vinst_i_ar,
                "vinst_nasta_ar": vinst_nasta_ar,
                "omsattning_fjol": omsattning_fjol,
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
            }
            df, success = lagg_till_eller_uppdatera_bolag(df, ny_data)
            if success:
                spara_data(df)
                st.success(f"Bolaget '{bolagsnamn}' sparades/uppdaterades.")
                # För att uppdatera vy utan experimental_rerun:
                st.experimental_set_query_params(refresh="true")
                st.experimental_rerun()

    return df

# Funktion för att lägga till eller uppdatera bolag i DataFrame
def lagg_till_eller_uppdatera_bolag(df, ny_data):
    bolagsnamn = ny_data["bolagsnamn"]
    if bolagsnamn in df["bolagsnamn"].values:
        # Uppdatera existerande bolag
        idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
        for key, value in ny_data.items():
            df.at[idx, key] = value
        df.at[idx, "senast_andrad"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        success = True
    else:
        # Lägg till nytt bolag
        ny_data["insatt_datum"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        ny_data["senast_andrad"] = ny_data["insatt_datum"]
        df = df.append(ny_data, ignore_index=True)
        success = True
    return df, success

# Funktion för att beräkna targetkurser och undervärdering
def berakna_target_och_undervardering(df):
    if df.empty:
        return df
    try:
        # Targetkurs baserat på vinst_nasta_ar och medelvärde av PE1 och PE2
        df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

        # Targetkurs PS baserat på P/S 1 och 2, och omsättningstillväxten (medelvärde)
        omsattningstillvaxt_mean = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100  # omvandlat till decimal
        ps_mean = (df["ps_1"] + df["ps_2"]) / 2
        omsattning_nu = df["omsattning_fjol"]
        df["targetkurs_ps"] = ps_mean * omsattning_nu * (1 + omsattningstillvaxt_mean)

        # Undervärdering - beräkna skillnad mellan nuvarande kurs och targetkurser i %
        df["undervardering_pe"] = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]
        df["undervardering_ps"] = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["nuvarande_kurs"]

        # Samlad undervärdering: ta max undervärdering av pe eller ps
        df["undervardering"] = df[["undervardering_pe", "undervardering_ps"]].max(axis=1)

    except Exception as e:
        st.error(f"Fel vid beräkning av targetkurser eller undervärdering: {e}")
    return df

# Funktion för att visa bolagsdata i tabell med filtrering
def visa_och_filtrera_bolag(df):
    st.header("Bolagslista och filtrering")

    visa_alla = st.checkbox("Visa alla bolag (inkl. icke-undervärderade)", value=True)
    procent_grans = st.slider("Minsta undervärdering (%)", min_value=0, max_value=100, value=30)

    if not visa_alla:
        df_visning = df[df["undervardering"] >= procent_grans / 100]
    else:
        df_visning = df.copy()

    if not df_visning.empty:
        df_visning = df_visning.sort_values(by="undervardering", ascending=False)
        df_visning_display = df_visning[[
            "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps",
            "undervardering_pe", "undervardering_ps", "undervardering",
            "insatt_datum", "senast_andrad"
        ]].copy()

        # Visa med snyggare procentformat
        for col in ["undervardering_pe", "undervardering_ps", "undervardering"]:
            df_visning_display[col] = (df_visning_display[col] * 100).map("{:.1f}%".format)

        st.dataframe(df_visning_display.reset_index(drop=True))
    else:
        st.info("Inga bolag matchar filtreringen.")

def ta_bort_bolag(df):
    st.header("Ta bort bolag")
    if df.empty:
        st.info("Inga bolag sparade.")
        return df
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", options=df["bolagsnamn"].tolist())
    if st.button("Ta bort valt bolag"):
        df = df[df["bolagsnamn"] != bolag_att_ta_bort].reset_index(drop=True)
        st.success(f"Bolaget '{bolag_att_ta_bort}' har tagits bort.")
    return df

def main():
    st.title("Aktieanalysapp")

    # Initiera session_state för data
    if "df" not in st.session_state:
        st.session_state.df = las_data()

    df = st.session_state.df

    # Formulär för nytt/uppdatera bolag
    with st.form("bolagsform"):
        bolagsnamn = st.text_input("Bolagsnamn", key="bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", key="nuvarande_kurs")
        vinst_fjol = st.number_input("Vinst förra året", format="%.2f", key="vinst_fjol")
        vinst_ar = st.number_input("Förväntad vinst i år", format="%.2f", key="vinst_ar")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f", key="vinst_nasta_ar")
        omsattning_fjol = st.number_input("Omsättning förra året", format="%.2f", key="omsattning_fjol")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", min_value=0.0, max_value=100.0, format="%.2f", key="omsattningstillvaxt_ar")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", min_value=0.0, max_value=100.0, format="%.2f", key="omsattningstillvaxt_nasta_ar")

        nuvarande_pe = st.number_input("Nuvarande P/E", min_value=0.0, format="%.2f", key="nuvarande_pe")
        pe_1 = st.number_input("P/E 1", min_value=0.0, format="%.2f", key="pe_1")
        pe_2 = st.number_input("P/E 2", min_value=0.0, format="%.2f", key="pe_2")
        pe_3 = st.number_input("P/E 3", min_value=0.0, format="%.2f", key="pe_3")
        pe_4 = st.number_input("P/E 4", min_value=0.0, format="%.2f", key="pe_4")

        nuvarande_ps = st.number_input("Nuvarande P/S", min_value=0.0, format="%.2f", key="nuvarande_ps")
        ps_1 = st.number_input("P/S 1", min_value=0.0, format="%.2f", key="ps_1")
        ps_2 = st.number_input("P/S 2", min_value=0.0, format="%.2f", key="ps_2")
        ps_3 = st.number_input("P/S 3", min_value=0.0, format="%.2f", key="ps_3")
        ps_4 = st.number_input("P/S 4", min_value=0.0, format="%.2f", key="ps_4")

        submitted = st.form_submit_button("Lägg till / Uppdatera bolag")

    if submitted:
        ny_data = {
            "bolagsnamn": bolagsnamn,
            "nuvarande_kurs": nuvarande_kurs,
            "vinst_fjol": vinst_fjol,
            "vinst_ar": vinst_ar,
            "vinst_nasta_ar": vinst_nasta_ar,
            "omsattning_fjol": omsattning_fjol,
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
        }
        df, success = lagg_till_eller_uppdatera_bolag(df, ny_data)
        if success:
            st.success(f"Bolaget '{bolagsnamn}' sparades/uppdaterades.")
            lagra_data(df)
            st.session_state.df = df

    # Beräkna targetkurser och undervärdering
    df = berakna_target_och_undervardering(df)
    st.session_state.df = df

    # Visa tabell med filtrering
    visa_och_filtrera_bolag(df)

    # Ta bort bolag
    df = ta_bort_bolag(df)
    st.session_state.df = df
    lagra_data(df)


if __name__ == "__main__":
    main()
