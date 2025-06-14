import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "bolag_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
st.title("📈 Aktieanalysapp – Inmatning, analys och filtrering")

# Välj/redigera bolag
valda_bolag = list(data.keys())
val = st.selectbox("Välj ett bolag att redigera eller skriv nytt namn:", [""] + valda_bolag)
nytt_bolagsnamn = st.text_input("Bolagsnamn", value=val if val else "")
info = data.get(nytt_bolagsnamn, {})

# Inmatningsfält
kurs = st.number_input("Nuvarande kurs", value=info.get("kurs", 0.0), step=0.01)
vinst_fjol = st.number_input("Vinst förra året", value=info.get("vinst_fjol", 0.0), step=0.01)
vinst_1 = st.number_input("Förväntad vinst i år", value=info.get("vinst_1", 0.0), step=0.01)
vinst_2 = st.number_input("Förväntad vinst nästa år", value=info.get("vinst_2", 0.0), step=0.01)
oms_fjol = st.number_input("Omsättning förra året", value=info.get("oms_fjol", 0.0), step=0.01)
oms_tillv_1 = st.number_input("Omsättningstillväxt i år (%)", value=info.get("oms_tillv_1", 0.0), step=0.1)
oms_tillv_2 = st.number_input("Omsättningstillväxt nästa år (%)", value=info.get("oms_tillv_2", 0.0), step=0.1)

pe_nu = st.number_input("Nuvarande P/E", value=info.get("pe_nu", 0.0), step=0.1)
pe1 = st.number_input("P/E 1", value=info.get("pe1", 0.0), step=0.1)
pe2 = st.number_input("P/E 2", value=info.get("pe2", 0.0), step=0.1)
pe3 = st.number_input("P/E 3", value=info.get("pe3", 0.0), step=0.1)
pe4 = st.number_input("P/E 4", value=info.get("pe4", 0.0), step=0.1)

ps_nu = st.number_input("Nuvarande P/S", value=info.get("ps_nu", 0.0), step=0.1)
ps1 = st.number_input("P/S 1", value=info.get("ps1", 0.0), step=0.1)
ps2 = st.number_input("P/S 2", value=info.get("ps2", 0.0), step=0.1)
ps3 = st.number_input("P/S 3", value=info.get("ps3", 0.0), step=0.1)
ps4 = st.number_input("P/S 4", value=info.get("ps4", 0.0), step=0.1)

# Spara bolag
if st.button("💾 Spara bolag"):
    if nytt_bolagsnamn.strip() == "":
        st.warning("Bolagsnamn krävs.")
    else:
        data[nytt_bolagsnamn] = {
            "kurs": kurs,
            "vinst_fjol": vinst_fjol,
            "vinst_1": vinst_1,
            "vinst_2": vinst_2,
            "oms_fjol": oms_fjol,
            "oms_tillv_1": oms_tillv_1,
            "oms_tillv_2": oms_tillv_2,
            "pe_nu": pe_nu,
            "pe1": pe1,
            "pe2": pe2,
            "pe3": pe3,
            "pe4": pe4,
            "ps_nu": ps_nu,
            "ps1": ps1,
            "ps2": ps2,
            "ps3": ps3,
            "ps4": ps4,
            "senast_andrad": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_data(data)
        st.success("Bolaget har sparats!")
        st.session_state["refresh"] = True
        st.stop()

if val and nytt_bolagsnamn in data:
    st.markdown(f"📅 Senast uppdaterad: **{data[nytt_bolagsnamn].get('senast_andrad', 'okänt')}**")

# Översikt
st.header("📋 Översikt – sparade bolag")

if data:
    tabell = []
    for namn, info in data.items():
        tabell.append({
            "Bolag": namn,
            "Kurs": info["kurs"],
            "Vinst 1": info["vinst_1"],
            "Vinst 2": info["vinst_2"],
            "Oms tillv 1 (%)": info["oms_tillv_1"],
            "Oms tillv 2 (%)": info["oms_tillv_2"],
            "P/E snitt": round(sum([info.get(f"pe{i}", 0) for i in range(1, 5)]) / 4, 2),
            "P/S snitt": round(sum([info.get(f"ps{i}", 0) for i in range(1, 5)]) / 4, 2),
            "Uppdaterad": info.get("senast_andrad", "")
        })
    st.dataframe(tabell, use_container_width=True)
else:
    st.info("Inga bolag sparade än.")

# Targetkurser & checkboxfiltrering
st.header("🎯 Targetkurser & värdering")

visa_endast_undervard = st.checkbox("Visa endast bolag med minst 30 % rabatt", value=False)

targetdata = []

for namn, info in data.items():
    try:
        pe_snitt = sum([info.get(f"pe{i}", 0) for i in range(1, 5)]) / 4
        ps_snitt = sum([info.get(f"ps{i}", 0) for i in range(1, 5)]) / 4

        target_pe = info["vinst_2"] * pe_snitt
        target_ps = ps_snitt * info["kurs"]

        aktuell_kurs = info["kurs"]
        rabatt_pe = round(100 * (1 - aktuell_kurs / target_pe), 1) if target_pe else 0
        rabatt_ps = round(100 * (1 - aktuell_kurs / target_ps), 1) if target_ps else 0

        targetdata.append({
            "Bolag": namn,
            "Kurs": aktuell_kurs,
            "Target P/E": round(target_pe, 2),
            "Target P/S": round(target_ps, 2),
            "Rabatt P/E (%)": rabatt_pe,
            "Rabatt P/S (%)": rabatt_ps,
        })
    except Exception as e:
        st.warning(f"Fel i beräkning för {namn}: {e}")

if visa_endast_undervard:
    targetdata = [
        row for row in targetdata
        if row["Rabatt P/E (%)"] >= 30 or row["Rabatt P/S (%)"] >= 30
    ]

if targetdata:
    targetdata = sorted(targetdata, key=lambda x: min(x["Rabatt P/E (%)"], x["Rabatt P/S (%)"]), reverse=True)
    st.dataframe(targetdata, use_container_width=True)
else:
    st.info("Inga bolag matchar filtreringen just nu.")

# Mobilvy ett bolag i taget
st.header("📱 Enkelt bolag-i-taget-läge")

visningslista = targetdata.copy()

if visningslista:
    if "bolag_index" not in st.session_state:
        st.session_state.bolag_index = 0

    index = st.session_state.bolag_index
    bolag = visningslista[index]

    st.subheader(bolag["Bolag"])
    st.metric("Aktuell kurs", f"{bolag['Kurs']:.2f} kr")
    st.metric("Target P/E", f"{bolag['Target P/E']:.2f} kr", delta=f"{bolag['Rabatt P/E (%)']:.1f}% rabatt")
    st.metric("Target P/S", f"{bolag['Target P/S']:.2f} kr", delta=f"{bolag['Rabatt P/S (%)']:.1f}% rabatt")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Föregående", use_container_width=True) and index > 0:
            st.session_state.bolag_index -= 1
            st.experimental_rerun()
    with col2:
        if st.button("Nästa ➡️", use_container_width=True) and index < len(visningslista) - 1:
            st.session_state.bolag_index += 1
            st.experimental_rerun()
else:
    st.info("Inget bolag att visa här.")

# Ta bort bolag
st.header("🗑️ Ta bort bolag")

if valda_bolag:
    bolag_att_ta_bort = st.selectbox("Välj bolag att ta bort", valda_bolag)
    if st.button("Radera valt bolag"):
        if bolag_att_ta_bort in data:
            del data[bolag_att_ta_bort]
            save_data(data)
            st.success(f"{bolag_att_ta_bort} har raderats.")
            st.session_state["refresh"] = True
            st.stop()
else:
    st.info("Inga bolag att radera.")
