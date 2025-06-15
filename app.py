import streamlit as st
from forms import input_form, edit_form
from utils import (
    calculate_targetkurs_pe,
    calculate_targetkurs_ps,
    calculate_undervardering,
)
from data_handler import load_data, save_data, delete_company

st.set_page_config(page_title="Aktieanalysapp", layout="wide")
st.title("📈 Aktieanalysapp")

# Ladda data
data = load_data()

st.header("➕ Lägg till nytt bolag")

with st.form("nytt_bolag_form"):
    nytt_bolag = input_form()
    submit_nytt = st.form_submit_button("Lägg till bolag")

if submit_nytt and nytt_bolag:
    data.append(nytt_bolag)
    save_data(data)
    st.success(f"Bolaget **{nytt_bolag['bolagsnamn']}** har lagts till.")
    st.experimental_rerun()

st.header("✏️ Redigera eller ta bort bolag")

if data:
    bolagslista = [b["bolagsnamn"] for b in data]
    valt_bolag = st.selectbox("Välj ett bolag att redigera eller ta bort", bolagslista)

    if valt_bolag:
        bolag_data = hitta_bolag(data, valt_bolag)

        if bolag_data:
            with st.form("redigera_bolag_form"):
                redigerat = edit_form(bolag_data)
                uppdatera = st.form_submit_button("Uppdatera bolag")

            if uppdatera and redigerat:
                for i, b in enumerate(data):
                    if b["bolagsnamn"] == valt_bolag:
                        redigerat["senast_andrad"] = datetime.now().isoformat()
                        data[i] = redigerat
                        save_data(data)
                        st.success(f"{valt_bolag} uppdaterat.")
                        st.experimental_rerun()

        if st.button("🗑️ Ta bort bolag"):
            data = ta_bort_bolag(data, valt_bolag)
            save_data(data)
            st.success(f"{valt_bolag} har tagits bort.")
            st.experimental_rerun()

st.header("📈 Översikt och undervärdering")

visa_endast_undervarderade = st.checkbox("Visa endast bolag med minst 30 % undervärdering")

visa_data = []
for bolag in data:
    pe_target = calculate_targetkurs_pe(bolag)
    ps_target = calculate_targetkurs_ps(bolag)
    kurs = bolag.get("nuvarande_kurs", 0)

    underv_pe = calculate_undervardering(kurs, pe_target)
    underv_ps = calculate_undervardering(kurs, ps_target)
    bolag["undervardering_pct"] = max(underv_pe or 0, underv_ps or 0)
    bolag["target_pe"] = round(pe_target or 0, 2)
    bolag["target_ps"] = round(ps_target or 0, 2)

    if not visa_endast_undervarderade or bolag["undervardering_pct"] >= 30:
        visa_data.append(bolag)

visa_data.sort(key=lambda x: x.get("undervardering_pct", 0), reverse=True)

if visa_data:
    st.subheader("📃 Undervärderade bolag (mest intressant först)")
    index = st.number_input("Visa bolag", min_value=0, max_value=len(visa_data) - 1, step=1, key="bolagsindex")
    bolag = visa_data[index]

    st.markdown(f"### {bolag['bolagsnamn']}")
    st.markdown(f"- **Nuvarande kurs:** {bolag['nuvarande_kurs']}")
    st.markdown(f"- **Targetkurs P/E:** {bolag['target_pe']}")
    st.markdown(f"- **Targetkurs P/S:** {bolag['target_ps']}")
    st.markdown(f"- **Undervärdering:** {round(bolag['undervardering_pct'], 1)} %")

    if bolag['undervardering_pct'] >= 30:
        st.success("📌 Köpvärd (minst 30 % rabatt)")
else:
    st.info("Inga bolag att visa enligt dina filter.")

if __name__ == "__main__":
    main()
