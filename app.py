import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktien-Suche Pro", page_icon="🔍", layout="wide")

st.title("🔍 Aktien-Suche nach Name oder Kürzel")
st.markdown("---")

# Eingabefeld für Name oder Ticker
user_input = st.sidebar.text_input("Suche (z.B. Tesla, Apple, Allianz, Gold)", "Tesla")

def get_ticker(search_term):
    try:
        # Sucht bei Yahoo Finance nach dem Begriff
        search = yf.Search(search_term, max_results=1)
        if search.quotes:
            return search.quotes[0]['symbol'], search.quotes[0]['shortname']
        return None, None
    except:
        return None, None

if st.button("Analyse starten"):
    with st.spinner('Suche läuft...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            st.info(f"Gefunden: **{name}** (Kürzel: {symbol})")
            
            # Daten laden (2 Jahre für SMA 200)
            data = yf.download(symbol, period="2y", auto_adjust=True)
            
            if not data.empty:
                # Daten-Bereinigung für Single- und Multi-Index
                if isinstance(data.columns, pd.MultiIndex):
                    close_prices = data['Close'][symbol]
                else:
                    close_prices = data['Close']
                
                # Berechnung
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
                col1.metric("Kurs", f"{current_price:.2f} $")
                col2.metric("SMA 200 (Ø)", f"{current_sma200:.2f} $")
                col3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

                # Empfehlungs-Logik
                st.markdown("### Fazit")
                if current_price > current_sma200 and last_rsi < 40:
                    st.success("🟢 **Kauf-Signal:** Langfristiger Trend ist positiv und die Aktie ist kurzfristig günstig!")
                elif current_price < current_sma200:
                    st.error("🔴 **Trend-Warnung:** Die Aktie ist im Abwärtstrend. Vorsicht geboten.")
                elif last_rsi > 70:
                    st.warning("🟡 **Überhitzt:** Die Aktie ist zu schnell gestiegen. Warte eventuell auf einen Rücksetzer.")
                else:
                    st.info("⚪ **Neutral:** Es liegen aktuell keine extremen Signale vor.")

                # Chart
                st.line_chart(close_prices.tail(252))
            else:
                st.error("Keine Kursdaten für dieses Symbol gefunden.")
        else:
            st.error("Konnte keine Aktie unter diesem Namen finden.")

st.sidebar.markdown("---")
st.sidebar.write("Du kannst Firmennamen wie 'Mercedes' oder 'Microsoft' eingeben.")
