import streamlit as st
import json
from datetime import datetime
import os

DATA_PATH = "data/aktie_data.json"

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def display_stock_details(stock):
    st.subheader(f"Detaljer för {stock['Bolagsnamn']}")
    st.write(f"Nuvarande kurs: {stock['Nuvarande kurs']:.2f} kr")

    with st.expander("Visa/redigera fler detaljer"):
        stock['Vinst förra året'] = st.number_input("Vinst förra året", value=stock['Vinst förra året'], format="%.2f")
        stock['Förväntad vinst i år'] = st.number_input("Förväntad vinst i år", value=stock['Förväntad vinst i år'], format="%.2f")
        stock['Förväntad vinst nästa år'] = st.number_input("Förväntad vinst nästa år", value=stock['Förväntad vinst nästa år'], format="%.2f")
        stock['Omsättning förra året'] = st.number_input("Omsättning förra året", value=stock['Omsättning förra året'], format="%.2f")
        stock['Förväntad Omsättningstillväxt i år %'] = st.number_input("Omsättningstillväxt i år %", value=stock['Förväntad Omsättningstillväxt i år %'], format="%.2f")
        stock['Förväntad Omsättningstillväxt nästa år %'] = st.number_input("Omsättningstillväxt nästa år %", value=stock['Förväntad Omsättningstillväxt nästa år %'], format="%.2f")
        stock['Nuvarande p/e'] = st.number_input("Nuvarande P/E", value=stock['Nuvarande p/e'], format="%.2f")
        stock['P/e 1'] = st.number_input("P/E 1", value=stock['P/e 1'], format="%.2f")
        stock['P/e 2'] = st.number_input("P/E 2", value=stock['P/e 2'], format="%.2f")
        stock['P/e 3'] = st.number_input("P/E 3", value=stock['P/e 3'], format="%.2f")
        stock['P/e 4'] = st.number_input("P/E 4", value=stock['P/e 4'], format="%.2f")
        stock['Nuvarande p/s'] = st.number_input("Nuvarande P/S", value=stock['Nuvarande p/s'], format="%.2f")
        stock['P/s 1'] = st.number_input("P/S 1", value=stock['P/s 1'], format="%.2f")
        stock['P/s 2'] = st.number_input("P/S 2", value=stock['P/s 2'], format="%.2f")
        stock['P/s 3'] = st.number_input("P/S 3", value=stock['P/s 3'], format="%.2f")
        stock['P/s 4'] = st.number_input("P/S 4", value=stock['P/s 4'], format="%.2f")
        stock['Senast uppdaterad'] = st.date_input("Senast uppdaterad", value=datetime.strptime(stock.get('Senast uppdaterad', datetime.today().date().isoformat()), "%Y-%m-%d").date())
def main():
    st.title("Aktieanalysapp")

    # Ladda data
    data = load_data()
    if 'data' not in st.session_state:
        st.session_state.data = data

    # Inmatning av nytt eller redigering
    val = st.selectbox("Välj bolag att redigera eller nytt bolag", options=["Nytt bolag"] + list(st.session_state.data.keys()))
    
    if val == "Nytt bolag":
        nytt_bolagsnamn = st.text_input("Bolagsnamn")
        if nytt_bolagsnamn:
            if nytt_bolagsnamn in st.session_state.data:
                st.warning("Bolaget finns redan. Välj det i rullistan för att redigera.")
            else:
                ny_post = {
                    'Bolagsnamn': nytt_bolagsnamn,
                    'Nuvarande kurs': 0.0,
                    'Vinst förra året': 0.0,
                    'Förväntad vinst i år': 0.0,
                    'Förväntad vinst nästa år': 0.0,
                    'Omsättning förra året': 0.0,
                    'Förväntad Omsättningstillväxt i år %': 0.0,
                    'Förväntad Omsättningstillväxt nästa år %': 0.0,
                    'Nuvarande p/e': 0.0,
                    'P/e 1': 0.0,
                    'P/e 2': 0.0,
                    'P/e 3': 0.0,
                    'P/e 4': 0.0,
                    'Nuvarande p/s': 0.0,
                    'P/s 1': 0.0,
                    'P/s 2': 0.0,
                    'P/s 3': 0.0,
                    'P/s 4': 0.0,
                    'Senast uppdaterad': datetime.today().date().isoformat()
                }
                st.session_state.data[nytt_bolagsnamn] = ny_post
                st.success(f"Nytt bolag {nytt_bolagsnamn} tillagt. Välj det i rullistan för redigering.")
    else:
        stock = st.session_state.data[val]
        display_stock_details(stock)
        if st.button("Uppdatera"):
            stock['Senast uppdaterad'] = datetime.today().date().isoformat()
            st.session_state.data[val] = stock
            save_data(st.session_state.data)
            st.success(f"{val} uppdaterat!")

    # Sortera bolag efter undervärdering (skillnad mellan target P/E och nuvarande kurs)
    stocks_list = list(st.session_state.data.values())

    def undervärdering(stock):
        pe_snitt = 0
        try:
            pe_värden = [stock[k] for k in ['P/e 1','P/e 2','P/e 3','P/e 4']]
            pe_värden = [v for v in pe_värden if v > 0]
            if pe_värden:
                pe_snitt = sum(pe_värden)/len(pe_värden)
            target_pe = stock['Förväntad vinst i år'] * pe_snitt
            return target_pe - stock['Nuvarande kurs']
        except:
            return 0

    stocks_list.sort(key=undervärdering, reverse=True)

    st.subheader("Bolag sorterade efter undervärdering (target P/E)")

    for stock in stocks_list:
        underv = undervärdering(stock)
        st.write(f"{stock['Bolagsnamn']} — Nuvarande kurs: {stock['Nuvarande kurs']:.2f} kr — Undervärdering: {underv:.2f} kr")

if __name__ == "__main__":
    main()
