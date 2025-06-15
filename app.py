import json
import os

DATA_FILE = "bolag_data.json"

def load_data():
    """Läser in data från JSON-fil. Returnerar lista med bolag."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []

def save_data(data):
    """Sparar data (lista med bolag) till JSON-fil."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def delete_company(data, bolagsnamn):
    """
    Tar bort bolag med angivet bolagsnamn från data-listan.
    Sparar uppdaterad lista och returnerar den.
    """
    updated_data = [b for b in data if b.get("bolagsnamn") != bolagsnamn]
    save_data(updated_data)
    return updated_data

# Del 2: Hantera ny inmatning av bolag

nytt_bolag = input_form()

if nytt_bolag:
    # Lägg till nytt bolag i session_state och spara i fil
    st.session_state["all_data"].append(nytt_bolag)
    save_data(st.session_state["all_data"])
    st.success(f'Bolag "{nytt_bolag["bolagsnamn"]}" har lagts till.')

# Fortsättning av app.py

# Visa vald bolagsdata och redigera
if valt_bolag is not None:
    # Hitta bolagets data i listan
    bolag = next((b for b in st.session_state["all_data"] if b["bolagsnamn"] == valt_bolag), None)
    if bolag:
        st.subheader(f"Detaljer för {bolag['bolagsnamn']}")
        st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']}")
        # Visa övriga nyckeltal
        st.write("Nyckeltal och prognoser:")
        st.json(bolag)

        # Redigeringsformulär
        uppdaterat_bolag = edit_form(bolag)
        if uppdaterat_bolag:
            # Uppdatera listan med redigerade data
            idx = next((i for i, b in enumerate(st.session_state["all_data"]) if b["bolagsnamn"] == uppdaterat_bolag["bolagsnamn"]), None)
            if idx is not None:
                st.session_state["all_data"][idx] = uppdaterat_bolag
                save_data(st.session_state["all_data"])
                st.success(f"Bolaget {uppdaterat_bolag['bolagsnamn']} uppdaterades.")

        # Ta bort bolag
        if st.button(f"Ta bort {bolag['bolagsnamn']}"):
            st.session_state["all_data"] = delete_company(st.session_state["all_data"], bolag["bolagsnamn"])
            save_data(st.session_state["all_data"])
            st.success(f"Bolaget {bolag['bolagsnamn']} togs bort.")
            # Uppdatera valt bolag i session state
            st.session_state["valt_bolag"] = None

# Fortsättning av app.py

# Visa vald bolagsdata och redigera
if valt_bolag is not None:
    # Hitta bolagets data i listan
    bolag = next((b for b in st.session_state["all_data"] if b["bolagsnamn"] == valt_bolag), None)
    if bolag:
        st.subheader(f"Detaljer för {bolag['bolagsnamn']}")
        st.write(f"Nuvarande kurs: {bolag['nuvarande_kurs']}")
        # Visa övriga nyckeltal
        st.write("Nyckeltal och prognoser:")
        st.json(bolag)

        # Redigeringsformulär
        uppdaterat_bolag = edit_form(bolag)
        if uppdaterat_bolag:
            # Uppdatera listan med redigerade data
            idx = next((i for i, b in enumerate(st.session_state["all_data"]) if b["bolagsnamn"] == uppdaterat_bolag["bolagsnamn"]), None)
            if idx is not None:
                st.session_state["all_data"][idx] = uppdaterat_bolag
                save_data(st.session_state["all_data"])
                st.success(f"Bolaget {uppdaterat_bolag['bolagsnamn']} uppdaterades.")

        # Ta bort bolag
        if st.button(f"Ta bort {bolag['bolagsnamn']}"):
            st.session_state["all_data"] = delete_company(st.session_state["all_data"], bolag["bolagsnamn"])
            save_data(st.session_state["all_data"])
            st.success(f"Bolaget {bolag['bolagsnamn']} togs bort.")
            # Uppdatera valt bolag i session state
            st.session_state["valt_bolag"] = None
