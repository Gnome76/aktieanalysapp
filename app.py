import streamlit as st
import pandas as pd

# Initiera session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "bolagsnamn", "nuvarande_kurs", "vinst_forra_aret", "vinst_i_ar", "vinst_nasta_ar",
        "omsattning_forra_aret", "omsattningstillvaxt_ar", "omsattningstillvaxt_nasta_ar",
        "nuvarande_pe", "pe_1", "pe_2", "pe_3", "pe_4",
        "nuvarande_ps", "ps_1", "ps_2", "ps_3", "ps_4",
        "insatt_datum", "senast_andrad"
    ])

def berakna_targetkurs(df):
    # Target P/E = vinst_nasta_ar * ( (pe_1 + pe_2)/2 )
    df["targetkurs_pe"] = df["vinst_nasta_ar"] * ((df["pe_1"] + df["pe_2"]) / 2)

    # Target P/S = ( (ps_1 + ps_2)/2 ) * omsättningstillväxt * nuvarande kurs
    oms_tillv_avg = (df["omsattningstillvaxt_ar"] + df["omsattningstillvaxt_nasta_ar"]) / 2 / 100
    ps_avg = (df["ps_1"] + df["ps_2"]) / 2
    df["targetkurs_ps"] = ps_avg * (1 + oms_tillv_avg) * df["nuvarande_kurs"]

    # Beräkna undervärdering som högsta rabatt av P/E och P/S metoder
    rabatt_pe = 1 - (df["nuvarande_kurs"] / df["targetkurs_pe"])
    rabatt_ps = 1 - (df["nuvarande_kurs"] / df["targetkurs_ps"])
    df["undervardering"] = rabatt_pe.combine(rabatt_ps, max)
    df["undervardering"] = df["undervardering"].clip(lower=0)

    return df

def lagg_till_bolag():
    st.header("Lägg till / Uppdatera bolag")
    with st.form("lagg_till_form"):
        bolagsnamn = st.text_input("Bolagsnamn").strip()
        nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")
        vinst_forra_aret = st.number_input("Vinst förra året", format="%.2f")
        vinst_i_ar = st.number_input("Förväntad vinst i år", format="%.2f")
        vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", format="%.2f")
        omsattning_forra_aret = st.number_input("Omsättning förra året", format="%.2f")
        omsattningstillvaxt_ar = st.number_input("Förväntad omsättningstillväxt i år %", format="%.2f")
        omsattningstillvaxt_nasta_ar = st.number_input("Förväntad omsättningstillväxt nästa år %", format="%.2f")
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

        submitted = st.form_submit_button("Spara bolag")

        if submitted:
            if bolagsnamn == "":
                st.error("Bolagsnamn måste fyllas i.")
                return
            df = st.session_state.df
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if bolagsnamn in df["bolagsnamn"].values:
                # Uppdatera befintligt bolag
                idx = df.index[df["bolagsnamn"] == bolagsnamn][0]
                df.loc[idx] = [
                    bolagsnamn, nuvarande_kurs, vinst_forra_aret, vinst_i_ar, vinst_nasta_ar,
                    omsattning_forra_aret, omsattningstillvaxt_ar, omsattningstillvaxt_nasta_ar,
                    nuvarande_pe, pe_1, pe_2, pe_3, pe_4,
                    nuvarande_ps, ps_1, ps_2, ps_3, ps_4,
                    df.loc[idx, "insatt_datum"],  # bevara original datum
                    now  # nytt ändrat datum
                ]
                st.success(f"Bolaget '{bolagsnamn}' uppdaterat.")
            else:
                # Lägg till nytt bolag
                ny_rad = pd.DataFrame([[
                    bolagsnamn, nuvarande_kurs, vinst_forra_aret, vinst_i_ar, vinst_nasta_ar,
                    omsattning_forra_aret, omsattningstillvaxt_ar, omsattningstillvaxt_nasta_ar,
                    nuvarande_pe, pe_1, pe_2, pe_3, pe_4,
                    nuvarande_ps, ps_1, ps_2, ps_3, ps_4,
                    now, now
                ]], columns=df.columns)
                st.session_state.df = pd.concat([df, ny_rad], ignore_index=True)
                st.success(f"Bolaget '{bolagsnamn}' lagt till.")

def visa_undervarderade():
    st.header("Undervärderade bolag")
    df = st.session_state.df.copy()
    df = berakna_targetkurs(df)

    undervard_df = df[df["undervardering"] >= 0.3].sort_values("undervardering", ascending=False).reset_index(drop=True)

    if undervard_df.empty:
        st.info("Inga bolag är tillräckligt undervärderade (>= 30%).")
        return

    # Bläddra mellan bolag
    if "idx" not in st.session_state:
        st.session_state.idx = 0

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("⬅️ Föregående"):
            st.session_state.idx = max(st.session_state.idx - 1, 0)
    with col3:
        if st.button("Nästa ➡️"):
            st.session_state.idx = min(st.session_state.idx + 1, len(undervard_df) -1)

    bolag = undervard_df.iloc[st.session_state.idx]

    st.subheader(f"{bolag['bolagsnamn']} ({st.session_state.idx +1}/{len(undervard_df)})")
    st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']:.2f} SEK")

    undervard = bolag["undervardering"]
    procent = int(undervard * 100)
    emoji = "🟢" if procent >= 50 else "🟡" if procent >= 30 else "🔴"

    st.write(f"Undervärdering: {emoji} **{procent}%**")

    # Progress bar med färg (grönt till rött)
    st.progress(min(procent / 100, 1.0))

    # Visa nyckeltal
    nyckeltal = {
        "Vinst förra året": bolag["vinst_forra_aret"],
        "Förväntad vinst i år": bolag["vinst_i_ar"],
        "Förväntad vinst nästa år": bolag["vinst_nasta_ar"],
        "Omsättning förra året": bolag["omsattning_forra_aret"],
        "Omsättningstillväxt i år %": bolag["omsattningstillvaxt_ar"],
        "Omsättningstillväxt nästa år %": bolag["omsattningstillvaxt_nasta_ar"],
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

    for k, v in nyckeltal.items():
        st.write(f"**{k}:** {v:.2f}")

def visa_alla_bolag():
    st.header("Alla bolag")
    df = st.session_state.df.copy()
    df = berakna_targetkurs(df)
    st.dataframe(df[[
        "bolagsnamn", "nuvarande_kurs", "undervardering", "targetkurs_pe", "targetkurs_ps"
    ]].sort_values("undervardering", ascending=False).style.format({
        "nuvarande_kurs": "{:.2f}",
        "undervardering": "{:.2%}",
        "targetkurs_pe": "{:.2f}",
        "targetkurs_ps": "{:.2f}"
    }))

def main():
    st.title("Aktieanalysapp")

    menyval = st.sidebar.radio("Navigera", ["Lägg till / uppdatera bolag", "Visa undervärderade bolag", "Visa alla bolag"])

    if menyval == "Lägg till / uppdatera bolag":
        lagg_till_bolag()
    elif menyval == "Visa undervärderade bolag":
        visa_undervarderade()
    elif menyval == "Visa alla bolag":
        visa_alla_bolag()

if __name__ == "__main__":
    main()
