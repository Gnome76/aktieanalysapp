import streamlit as st
import pandas as pd
import os
import json

FILNAMN = "bolag_data.json"

# Läs in data från json-fil
def las_data():
    if os.path.exists(FILNAMN):
        with open(FILNAMN, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        kolumner = [
            "bolagsnamn", "nuvarande_kurs",
            "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
            "omsattning_forra_aret", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
            "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
            "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4"
        ]
        return pd.DataFrame(columns=kolumner)

# Spara data till json-fil
def spara_data(df):
    with open(FILNAMN, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

# Beräkna targetkurser och undervärdering
def berakna_target_undervardering(df):
    # Targetkurs P/E baserat på medelvärde av pe_1 och pe_2 gånger vinst nästa år
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"].astype(float) + df["pe_2"].astype(float)) / 2)
    # Targetkurs P/S baserat på medelvärde av ps_1 och ps_2 gånger omsättningstillväxt gånger nuvarande kurs
    oms_tillv = ((df["omsattningstillvaxt_ar"].astype(float) + df["omsattningstillvaxt_nasta_ar"].astype(float)) / 2) / 100 + 1
    medel_ps = (df["ps_1"].astype(float) + df["ps_2"].astype(float)) / 2
    df["targetkurs_ps"] = df["omsattning_forra_aret"].astype(float) * oms_tillv * medel_ps
    # Undervärdering: högsta skillnad (targetkurs - nuvarande kurs)/nuvarande kurs
    pe_diff = (df["targetkurs_pe"] - df["nuvarande_kurs"].astype(float)) / df["nuvarande_kurs"].astype(float)
    ps_diff = (df["targetkurs_ps"] - df["nuvarande_kurs"].astype(float)) / df["nuvarande_kurs"].astype(float)
    df["undervardering"] = pe_diff.combine(ps_diff, max).fillna(0)
    return df

def main():
    st.title("Aktieanalysapp med undervärderingsbläddring")

    df = las_data()
    df = berakna_target_undervardering(df)

    # Lägg till nytt bolag
    with st.expander("Lägg till eller uppdatera bolag"):
        bolagsnamn = st.text_input("Bolagsnamn")
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        oms_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        oms_tillv_ar = st.number_input("Förväntad omsättningstillväxt i år (%)", format="%.2f")
        oms_tillv_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år (%)", format="%.2f")
        nuvarande_pe = st.number_input("Nuvarande P/E", format="%.2f")
        pe_1 = st.number_input("P/E 1", format="%.2f")
        pe_2 = st.number_input("P/E 2", format="%.2f")
        pe_3 = st.number_input("P/E 3", format="%.2f")
        pe_4 = st.number_input("P/E 4", format="%.2f")
        nuvarande_ps = st.number_input("Nuvarande P/S", format="%.2f")
        ps_1 = st.number_input("P/S 1", format="%.2f")
        ps_2 = st.number_input("P/S 2", format="%.2f")
        ps_3 = st.number_input("P/S 3", format="%.2f")
        ps_4 = st.number_input("P/S 4", format="%.2f")

        if st.button("Spara/uppdatera bolag"):
            if bolagsnamn.strip() == "":
                st.error("Ange bolagsnamn!")
            else:
                ny_rad = {
                    "bolagsnamn": bolagsnamn.strip(),
                    "nuvarande_kurs": nuvarande_kurs,
                    "vinst_forra_aret": vinst_forra_aret,
                    "vinst_i_ar": vinst_i_ar,
                    "vinst_nasta_ar": vinst_nasta_ar,
                    "omsattning_forra_aret": oms_forra_aret,
                    "omsattningstillvaxt_ar": oms_tillv_ar,
                    "omsattningstillvaxt_nasta_ar": oms_tillv_nasta_ar,
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
                if bolagsnamn in df["bolagsnamn"].values:
                    idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
                    df.loc[idx] = ny_rad
                    st.success(f"Bolaget '{bolagsnamn}' uppdaterat.")
                else:
                    df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
                    st.success(f"Bolaget '{bolagsnamn}' tillagt.")
                df = berakna_target_undervardering(df)
                spara_data(df)

    # Visa undervärderade bolag
    if not df.empty:
        df = berakna_target_undervardering(df)
        df_undervard = df[df["undervardering"] > 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)

        if df_undervard.empty:
            st.info("Inga bolag med minst 30% undervärdering.")
        else:
            st.subheader("Undervärderade bolag (minst 30%)")
            if "index_undervard" not in st.session_state:
                st.session_state["index_undervard"] = 0

            col1, col2, col3 = st.columns([1,2,1])
            with col1:
                if st.button("⬅️ Föregående"):
                    if st.session_state["index_undervard"] > 0:
                        st.session_state["index_undervard"] -= 1
            with col3:
                if st.button("Nästa ➡️"):
                    if st.session_state["index_undervard"] < len(df_undervard) - 1:
                        st.session_state["index_undervard"] += 1

            i = st.session_state["index_undervard"]
            bolag = df_undervard.iloc[i]
            st.markdown(f"### {bolag['bolagsnamn']} ({i+1} av {len(df_undervard)})")
            underv = bolag["undervardering"] * 100
            if underv > 50:
                emoji = "🚀"
            elif underv > 30:
                emoji = "🔥"
            else:
                emoji = "✨"
            st.markdown(f"**Undervärdering:** {underv:.1f}% {emoji}")

            # Progressbar för undervärdering (max 100%)
            undervardering_norm = min(underv / 100, 1.0)
            st.progress(undervardering_norm)

            st.write("**Nuvarande kurs:**", bolag["nuvarande_kurs"])
            st.write("**Targetkurs P/E:**", f"{bolag['targetkurs_pe']:.2f}")
            st.write("**Targetkurs P/S:**", f"{bolag['targetkurs_ps']:.2f}")

            # Visa nyckeltal tabell
            nyckeltal = {
                "Vinst förra året": bolag["vinst_forra_aret"],
                "Vinst i år": bolag["vinst_i_ar"],
                "Vinst nästa år": bolag["vinst_nasta_ar"],
                "Omsättning förra året": bolag["omsattning_forra_aret"],
                "Omsättningstillväxt i år (%)": bolag["omsattningstillvaxt_ar"],
                "Omsättningstillväxt nästa år (%)": bolag["omsattningstillvaxt_nasta_ar"],
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
            }
            st.table(pd.DataFrame.from_dict(nyckeltal, orient="index", columns=["Värde"]))

    else:
        st.info("Ingen data tillgänglig. Lägg till bolag ovan.")

if __name__ == "__main__":
    main()
