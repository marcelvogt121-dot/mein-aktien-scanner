import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktien-Suche Pro", page_icon="🔍", layout="wide")

st.title("🔍 Aktien-Analyse mit Zeitraum-Wahl")
st.markdown("---")

# Eingaben in der Seitenleiste
st.sidebar.header("Einstellungen")
user_input = st.sidebar.text_input("Suche (Name oder Kürzel)", "Tesla")
zeitraum = st.sidebar.selectbox("Zeitraum für den Chart", ["1y", "2y", "5y", "max"], index=0)

def get_ticker(search_term):
    try:
        search = yf.Search(search_term, max_results=1)
        if search.quotes:
            return search.quotes[0]['symbol'], search.quotes[0]['shortname']
        return None, None
    except:
        return None, None

if st.sidebar.button("Analyse starten"):
    with st.spinner('Daten werden geladen...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            st.subheader(f"Ergebnis: {name} ({symbol})")
            
            # Wir laden immer genug Daten für den SMA 200 (mind. 2 Jahre), 
            # zeigen aber im Chart nur den gewählten Zeitraum.
            data = yf.download(symbol, period="5y", auto_adjust=True)
            
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    close_prices = data['Close'][symbol]
                else:
                    close_prices = data['Close']
                
                # Berechnungen (immer aktuell)
                current_price = float(close_prices.iloc[-1])
                sma200 = close_prices.rolling(window=200).mean()
                current_sma200 = float(sma200.iloc[-1])
                
                # RSI Berechnung
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                last_rsi = float(rsi.iloc[-1])

                # Layout Anzeigen
                col1, col2, col3 = st.columns(3)
                col1.metric("Kurs aktuell", f"{current_price:.2f} $")
                col2.metric("SMA 200 (Schnitt)", f"{current_sma200:.2f} $")
                col3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

                # Empfehlungs-Logik
                st.markdown("---")
                if current_price > current_sma200 and last_rsi < 40:
                    st.success("🟢 **Signal:** Langfristiger Trend ist positiv und die Aktie ist kurzfristig günstig (Kauf-Zone).")
                elif current_price < current_sma200:
                    st.error("🔴 **Trend-Warnung:** Die Aktie ist im Abwärtstrend. Vorsicht geboten.")
                elif last_rsi > 70:
                    st.warning("🟡 **Überhitzt:** Die Aktie ist zu schnell gestiegen. Hohes Rückschlagrisiko.")
                else:
                    st.info("⚪ **Neutral:** Keine extremen Signale.")

                # Chart Filterung basierend auf Auswahl
                if zeitraum == "1y":
                    plot_data = close_prices.tail(252)
                elif zeitraum == "2y":
                    plot_data = close_prices.tail(504)
                elif zeitraum == "5y":
                    plot_data = close_prices.tail(1260)
                else:
                    plot_data = close_prices
                
                st.line_chart(plot_data)
            else:
                st.error("Keine Kursdaten gefunden.")
        else:
            st.error("Konnte keine Aktie unter diesem Namen finden.")

st.sidebar.info("Tipp: Der SMA 200 zeigt dir den 'fairen' Durchschnittspreis des letzten Jahres.")
