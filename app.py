import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.set_page_config(page_title="Aktieanalysapp", layout="wide")

DATA_PATH = "bolag.json"


def las_data() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            # Säkerställ att alla kolumner finns
            kolumner = [
                "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_i_ar", "vinst_nasta_ar",
                "omsattning_fjol", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
                "pe_nuvarande", "pe_1", "pe_2", "pe_3", "pe_4",
                "ps_nuvarande", "ps_1", "ps_2", "ps_3", "ps_4",
                "insatt_datum", "senast_andrad"
            ]
            for k in kolumner:
                if k not in df.columns:
                    df[k] = None
            return df[kolumner]
        except Exception as e:
            st.error(f"Fel vid inläsning av data: {e}")
            return pd.DataFrame(columns=[
                "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_i_ar", "vinst_nasta_ar",
                "omsattning_fjol", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
                "pe_nuvarande", "pe_1", "pe_2", "pe_3", "pe_4",
                "ps_nuvarande", "ps_1", "ps_2", "ps_3", "ps_4",
                "insatt_datum", "senast_andrad"
            ])
    else:
        # Om filen inte finns, returnera tom df med rätt kolumner
        return pd.DataFrame(columns=[
            "bolagsnamn", "nuvarande_kurs", "vinst_fjol", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_fjol", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
            "pe_nuvarande", "pe_1", "pe_2", "pe_3", "pe_4",
            "ps_nuvarande", "ps_1", "ps_2", "ps_3", "ps_4",
            "insatt_datum", "senast_andrad"
        ])


def spara_data(df: pd.DataFrame):
    df.to_json(DATA_PATH, orient="records", indent=2, force_ascii=False)

def berakna_target_och_undervardering(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Säkerställ numeriska kolumner
    num_cols = [
        "vinst_nasta_ar", "pe_1", "pe_2", "ps_1", "ps_2",
        "nuvarande_kurs", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
        "ps_nuvarande"
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Targetkurs P/E
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Medel omsättningstillväxt
    oms_tillvxt_medel = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100  # % till decimal

    # Targetkurs P/S
    ps_medel = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = ps_medel * (1 + oms_tillvxt_medel) * df["nuvarande_kurs"]

    # Undervärdering baserat på lägsta av undervärdering mellan P/E och P/S mål jämfört med nuvarande kurs
    undervard_pe = (df["targetkurs_pe"] - df["nuvarande_kurs"]) / df["targetkurs_pe"]
    undervard_ps = (df["targetkurs_ps"] - df["nuvarande_kurs"]) / df["targetkurs_ps"]
    df["undervardering"] = pd.concat([undervard_pe, undervard_ps], axis=1).max(axis=1) * 100  # i procent

    # Rensa ev negativa och NaN undervärderingar
    df["undervardering"] = df["undervardering"].fillna(0)
    df.loc[df["undervardering"] < 0, "undervardering"] = 0

    return df


def visa_oversikt(df: pd.DataFrame):
    st.header("Översikt över sparade bolag")

    if df.empty:
        st.info("Inga bolag sparade ännu.")
        return

    visa_undervard = st.checkbox("Visa endast bolag med minst 30% undervärdering", value=False)

    df_visning = df.copy()
    if visa_undervard:
        df_visning = df_visning[df_visning["undervardering"] >= 30]

    df_visning = df_visning.sort_values(by="undervardering", ascending=False)

    if df_visning.empty:
        st.info("Inga bolag matchar filtreringen.")
        return

    # Visa tabell med utvalda kolumner
    kolumner_visning = [
        "bolagsnamn", "nuvarande_kurs", "targetkurs_pe", "targetkurs_ps", "undervardering",
        "insatt_datum", "senast_andrad"
    ]

    st.dataframe(df_visning[kolumner_visning].style.format({
        "nuvarande_kurs": "{:.2f}",
        "targetkurs_pe": "{:.2f}",
        "targetkurs_ps": "{:.2f}",
        "undervardering": "{:.1f} %",
    }), use_container_width=True)

def bolagsform(df: pd.DataFrame) -> pd.DataFrame:
    st.header("Lägg till / Redigera bolag")

    val = st.radio("Välj åtgärd", ["Lägg till nytt bolag", "Redigera befintligt bolag"])

    if val == "Lägg till nytt bolag":
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        if st.button("Spara nytt bolag"):
            if not bolagsnamn:
                st.error("Bolagsnamn krävs.")
            elif bolagsnamn in df["bolagsnamn"].values:
                st.error("Bolaget finns redan. Välj 'Redigera befintligt bolag'.")
            else:
                ny_rad = {"bolagsnamn": bolagsnamn}
                ny_rad.update(hamta_input_varden())
                nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ny_rad["insatt_datum"] = nu
                ny_rad["senast_andrad"] = nu
                df = df.append(ny_rad, ignore_index=True)
                spara_data(df)
                st.success(f"Bolaget '{bolagsnamn}' sparades!")
                st.session_state["refresh"] = True
                st.experimental_rerun()

    else:
        if df.empty:
            st.info("Inga bolag att redigera.")
            return df

        val_bolag = st.selectbox("Välj bolag att redigera", df["bolagsnamn"].tolist())

        if val_bolag:
            idx = df.index[df["bolagsnamn"] == val_bolag][0]
            rad = df.loc[idx]

            nya_varden = hamta_input_varden(rad)

            if st.button("Uppdatera bolag"):
                for key, val in nya_varden.items():
                    df.at[idx, key] = val
                df.at[idx, "senast_andrad"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                spara_data(df)
                st.success(f"Bolaget '{val_bolag}' uppdaterades!")
                st.session_state["refresh"] = True
                st.experimental_rerun()

        if st.button("Ta bort valt bolag"):
            if val_bolag:
                df = df[df["bolagsnamn"] != val_bolag].reset_index(drop=True)
               

def hamta_input_varden(existerande=None) -> dict:
    """Hämtar inputvärden från formulärfält, existerande är en serie med tidigare värden (för redigering)."""
    def valfilt(key, dtype=float):
        if existerande is not None and pd.notna(existerande.get(key)):
            return dtype(existerande[key])
        return None

    return {
        "nuvarande_kurs": st.number_input("Nuvarande kurs", value=valfilt("nuvarande_kurs") or 0.0, min_value=0.0, format="%.2f"),
        "vinst_fjol": st.number_input("Vinst förra året", value=valfilt("vinst_fjol") or 0.0, format="%.2f"),
        "vinst_i_ar": st.number_input("Förväntad vinst i år", value=valfilt("vinst_i_ar") or 0.0, format="%.2f"),
        "vinst_nasta_ar": st.number_input("Förväntad vinst nästa år", value=valfilt("vinst_nasta_ar") or 0.0, format="%.2f"),
        "omsattning_fjol": st.number_input("Omsättning förra året", value=valfilt("omsattning_fjol") or 0.0, format="%.2f"),
        "omsattningstillvaxt_ar": st.number_input("Förväntad omsättningstillväxt i år (%)", value=valfilt("omsattningstillvaxt_ar") or 0.0, format="%.2f"),
        "omsattningstillvaxt_nasta_ar": st.number_input("Förväntad omsättningstillväxt nästa år (%)", value=valfilt("omsattningstillvaxt_nasta_ar") or 0.0, format="%.2f"),
        "pe_nuvarande": st.number_input("Nuvarande P/E", value=valfilt("pe_nuvarande") or 0.0, format="%.2f"),
        "pe_1": st.number_input("P/E 1", value=valfilt("pe_1") or 0.0, format="%.2f"),
        "pe_2": st.number_input("P/E 2", value=valfilt("pe_2") or 0.0, format="%.2f"),
        "pe_3": st.number_input("P/E 3", value=valfilt("pe_3") or 0.0, format="%.2f"),
        "pe_4": st.number_input("P/E 4", value=valfilt("pe_4") or 0.0, format="%.2f"),
        "ps_nuvarande": st.number_input("Nuvarande P/S", value=valfilt("ps_nuvarande") or 0.0, format="%.2f"),
        "ps_1": st.number_input("P/S 1", value=valfilt("ps_1") or 0.0, format="%.2f"),
        "ps_2": st.number_input("P/S 2", value=valfilt("ps_2") or 0.0, format="%.2f"),
        "ps_3": st.number_input("P/S 3", value=valfilt("ps_3") or 0.0, format="%.2f"),
        "ps_4": st.number_input("P/S 4", value=valfilt("ps_4") or 0.0, format="%.2f"),
    }


def bolagsform(df: pd.DataFrame) -> pd.DataFrame:
    st.header("Lägg till / Redigera bolag")

    val = st.radio("Välj åtgärd", ["Lägg till nytt bolag", "Redigera befintligt bolag"])

    if val == "Lägg till nytt bolag":
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        if st.button("Spara nytt bolag"):
            if not bolagsnamn:
                st.error("Bolagsnamn krävs.")
            elif bolagsnamn in df["bolagsnamn"].values:
                st.error("Bolaget finns redan. Välj 'Redigera befintligt bolag'.")
            else:
                ny_rad = {"bolagsnamn": bolagsnamn}
                ny_rad.update(hamta_input_varden())
                nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ny_rad["insatt_datum"] = nu
                ny_rad["senast_andrad"] = nu
                df = df.append(ny_rad, ignore_index=True)
                spara_data(df)
                st.success(f"Bolaget '{bolagsnamn}' sparades!")
                st.session_state["refresh"] = True
                st.experimental_rerun()

    else:
        if df.empty:
            st.info("Inga bolag att redigera.")
            return df

        val_bolag = st.selectbox("Välj bolag att redigera", df["bolagsnamn"].tolist())

        if val_bolag:
            idx = df.index[df["bolagsnamn"] == val_bolag][0]
            rad = df.loc[idx]

            st.markdown(f"**Redigera bolag: {val_bolag}**")

            nya_varden = hamta_input_varden(rad)

            if st.button("Uppdatera bolag"):
                for key, val in nya_varden.items():
                    df.at[idx, key] = val
                df.at[idx, "senast_andrad"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                spara_data(df)
                st.success(f"Bolaget '{val_bolag}' uppdaterades!")
                st.session_state["refresh"] = True
                st.experimental_rerun()

        if st.button("Ta bort valt bolag"):
            if val_bolag:
                df = df[df["bolagsnamn"] != val_bolag].reset_index(drop=True)
                spara_data(df)
                st.success(f"Bolaget '{val_bolag}' togs bort!")
                st.session_state["refresh"] = True
                st.experimental_rerun()

    return df

def main():
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    df = las_data()

    df = berakna_target_och_undervardering(df)

    col1, col2 = st.columns([2, 1])

    with col1:
        visa_oversikt(df)

    with col2:
        df = bolagsform(df)

    if st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.experimental_rerun()


if __name__ == "__main__":
    main()
