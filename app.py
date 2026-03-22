import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktien-Genie Pro", page_icon="📊", layout="wide")

st.title("📊 Mein intelligenter Aktien-Check")
st.markdown("---")

# Eingabe
ticker = st.sidebar.text_input("Ticker Symbol", "TSLA").upper()
zeitraum = st.sidebar.selectbox("Zeitraum für Chart", ["1y", "2y", "5y"], index=0)

if st.button("Analyse starten"):
    data = yf.download(ticker, period="2y", auto_adjust=True) # 2 Jahre für SMA200 nötig
    
    if not data.empty:
        # Daten-Bereinigung
        if isinstance(data.columns, pd.MultiIndex):
            close_prices = data['Close'][ticker]
        else:
            close_prices = data['Close']
            
        # Indikatoren berechnen
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

        # Metriken anzeigen
        col1, col2, col3 = st.columns(3)
        col1.metric("Aktueller Kurs", f"{current_price:.2f} $")
        col2.metric("SMA 200 (1 Jahr Ø)", f"{current_sma200:.2f} $", f"{(current_price - current_sma200):.2f} $ Differenz")
        col3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

        st.markdown("---")
        
        # Logik-Check (Die "Empfehlung")
        if current_price > current_sma200 and last_rsi < 40:
            st.success("✅ STARKES SIGNAL: Aktie im Aufwärtstrend, aber kurzfristig günstig (RSI niedrig).")
        elif current_price < current_sma200:
            st.error("⚠️ VORSICHT: Aktie befindet sich im langfristigen Abwärtstrend (unter SMA 200).")
        elif last_rsi > 70:
            st.warning("🔥 ÜBERHITZT: Die Aktie ist kurzfristig zu schnell gestiegen (RSI hoch).")
        else:
            st.info("⚖️ NEUTRAL: Keine extremen Signale aktuell.")

        # Chart mit SMA 200
        chart_data = pd.DataFrame({
            'Kurs': close_prices,
            'Durchschnitt (SMA 200)': sma200
        }).tail(252) # Zeige nur das letzte Jahr im Chart
        
        st.subheader(f"Chart-Analyse: {ticker}")
        st.line_chart(chart_data)
        
    else:
        st.error("Fehler: Ticker nicht gefunden.")

st.sidebar.markdown("---")
st.sidebar.write("💡 **Tipp:** Wenn der Kurs weit über der blauen Linie (SMA 200) liegt, ist die Aktie historisch gesehen 'teuer'.")
