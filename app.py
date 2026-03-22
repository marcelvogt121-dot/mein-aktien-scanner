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

# Der Button triggert die gesamte Berechnung neu
if st.sidebar.button("Analyse starten"):
    with st.spinner('Marktdaten werden frisch geladen...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            st.subheader(f"Analyse für: {name} ({symbol})")
            
            # Wichtig: 'period' auf 5y lassen, damit SMA 200 immer berechnet werden kann
            data = yf.download(symbol, period="5y", auto_adjust=True)
            
            if not data.empty:
                # Daten-Extraktion
                if isinstance(data.columns, pd.MultiIndex):
                    close_prices = data['Close'][symbol]
                    volume_data = data['Volume'][symbol]
                else:
                    close_prices = data['Close']
                    volume_data = data['Volume']
                
                # Aktuelle Werte
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

                # Metriken in Echtzeit
                c1, c2, c3 = st.columns(3)
                c1.metric("Kurs", f"{current_price:.2f} $")
                c2.metric("SMA 200 (1J-Schnitt)", f"{current_sma200:.2f} $")
                c3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

                # Chart-Bereich (Filterung je nach Auswahl)
                if zeitraum == "1y": plot_data = close_prices.tail(252)
                elif zeitraum == "2y": plot_data = close_prices.tail(504)
                elif zeitraum == "5y": plot_data = close_prices.tail(1260)
                else: plot_data = close_prices
                
                st.write("### Preisverlauf & SMA 200")
                # Wir zeigen den Preis und den gleitenden Durchschnitt im selben Chart
                st.line_chart(pd.DataFrame({
                    "Preis": plot_data, 
                    "SMA 200": sma200.loc[plot_data.index]
                }))
                
                st.write("### Handelsvolumen")
                st.bar_chart(volume_data.loc[plot_data.index])

                # DAS FAZIT (Jetzt fest in der Schleife)
                st.markdown("---")
                st.subheader("💡 Fazit der Analyse")
                
                if current_price > current_sma200:
                    if last_rsi < 35:
                        st.success(f"✅ **STARKES SIGNAL:** {name} ist im Aufwärtstrend (über SMA 200), aber gerade kurzfristig extrem günstig (RSI: {last_rsi:.1f}).")
                    elif last_rsi > 70:
                        st.warning(f"⚠️ **ÜBERHITZT:** Der Trend ist zwar positiv, aber die Aktie ist aktuell zu teuer (RSI: {last_rsi:.1f}). Warte auf einen Rücksetzer.")
                    else:
                        st.info(f"⚖️ **TREND FOLGEN:** Die Aktie ist stabil im Aufwärtstrend. Kein extremes RSI-Signal.")
                else:
                    if last_rsi < 30:
                        st.error(f"🔴 **VORSICHT (FALLING KNIFE):** Der RSI ist zwar sehr niedrig ({last_rsi:.1f}), aber die Aktie ist im Abwärtstrend (unter SMA 200). Ein Einstieg ist riskant!")
                    else:
                        st.error(f"🔴 **ABWÄRTSTREND:** Keine Kaufempfehlung. Die Aktie notiert unter ihrem Jahresdurchschnitt.")

            else:
                st.error("Konnte keine Daten für dieses Symbol finden.")
        else:
            st.error("Aktie wurde nicht gefunden. Probiere es mit dem Kürzel (z.B. TSLA).")

st.sidebar.markdown("---")
st.sidebar.write("Die Empfehlung basiert auf der Kombination von Trend (SMA 200) und Dynamik (RSI).")
