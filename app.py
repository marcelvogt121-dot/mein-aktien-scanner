import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktien-Profi-Scanner", page_icon="📈", layout="wide")

st.title("📈 Mein Profi-Scanner: Trends & Volumen")
st.markdown("---")

# Seitenleiste
st.sidebar.header("Suche & Filter")
user_input = st.sidebar.text_input("Name oder Kürzel der Aktie", "TSLA")
zeitraum = st.sidebar.selectbox("Zeitraum für Chart", ["1y", "2y", "5y", "max"], index=0)

def get_ticker(search_term):
    try:
        search = yf.Search(search_term, max_results=1)
        if search.quotes:
            return search.quotes[0]['symbol'], search.quotes[0]['shortname']
        return None, None
    except:
        return None, None

if st.sidebar.button("Analyse starten"):
    with st.spinner('Analysiere Marktdaten...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            st.subheader(f"Analyse für: {name} ({symbol})")
            
            # Daten laden (genug für SMA 200)
            data = yf.download(symbol, period="5y", auto_adjust=True)
            
            if not data.empty:
                # Spalten-Handling
                if isinstance(data.columns, pd.MultiIndex):
                    close_prices = data['Close'][symbol]
                    volume_data = data['Volume'][symbol]
                else:
                    close_prices = data['Close']
                    volume_data = data['Volume']
                
                # Indikatoren
                current_price = float(close_prices.iloc[-1])
                sma200 = close_prices.rolling(window=200).mean()
                current_sma200 = float(sma200.iloc[-1])
                
                # RSI
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                last_rsi = float(rsi.iloc[-1])

                # Layout Spalten
                c1, c2, c3 = st.columns(3)
                c1.metric("Kurs", f"{current_price:.2f} $")
                c2.metric("SMA 200 (1J-Schnitt)", f"{current_sma200:.2f} $")
                c3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

                # Handelsvolumen Check
                avg_vol = volume_data.tail(20).mean()
                last_vol = volume_data.iloc[-1]
                vol_status = "Normal"
                if last_vol > avg_vol * 1.5:
                    vol_status = "HOCH 🔥"
                    st.warning(f"Achtung: Das Handelsvolumen ist aktuell {vol_status}! Viel Bewegung im Markt.")

                # Chart-Bereich
                if zeitraum == "1y": plot_data = close_prices.tail(252); vol_plot = volume_data.tail(252)
                elif zeitraum == "2y": plot_data = close_prices.tail(504); vol_plot = volume_data.tail(504)
                elif zeitraum == "5y": plot_data = close_prices.tail(1260); vol_plot = volume_data.tail(1260)
                else: plot_data = close_prices; vol_plot = volume_data

                # Preis-Chart
                st.write("### Preisverlauf & SMA 200")
                st.line_chart(pd.DataFrame({"Preis": plot_data, "SMA 200": sma200.loc[plot_data.index]}))
                
                # Volumen-Chart (Balken)
                st.write("### Handelsvolumen (Balken)")
                st.bar_chart(vol_plot)

                # Fazit-Box
                st.markdown("---")
                if current_price > current_sma200 and last_rsi < 35:
                    st.success("✅ **Top-Signal:** Trendstark und kurzfristig überverkauft!")
                elif current_price < current_sma200:
                    st.error("🔴 **Abwärtstrend:** Kurs unter SMA 200. Bei FMC wäre das erst ein Kauf, wenn die Linie bricht.")
                else:
                    st.info("⚖️ **Abwarten:** Aktuell keine extremen Signale.")

            else:
                st.error("Keine Daten gefunden.")
        else:
            st.error("Aktie nicht gefunden.")

st.sidebar.markdown("---")
st.sidebar.write("📖 **Volumen-Info:** Hohe Balken bedeuten, dass viele Aktien den Besitzer gewechselt haben. Oft ein Zeichen für Wendepunkte!")
