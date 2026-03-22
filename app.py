import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktien-Genie", page_icon="📈")
st.title("🚀 Mein Aktien-Scanner")

ticker = st.text_input("Ticker Symbol (z.B. AAPL, TSLA, BTC-USD)", "AAPL")

if st.button("Analyse starten"):
    # Wir fügen 'auto_adjust=True' hinzu, um Fehler zu vermeiden
    data = yf.download(ticker, period="1y", auto_adjust=True)
    
    if not data.empty:
        # Sicherstellen, dass wir die 'Close' Spalte richtig erwischen
        # Manchmal nennt yfinance sie 'Close', manchmal ist sie verschachtelt
        if isinstance(data.columns, pd.MultiIndex):
            close_prices = data['Close'][ticker]
        else:
            close_prices = data['Close']
            
        current_price = float(close_prices.iloc[-1])
        st.metric(f"Aktueller Kurs ({ticker})", f"{current_price:.2f}")
        st.line_chart(close_prices)
        
        # RSI Logik
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1+rs))
        last_rsi = float(rsi.iloc[-1])
        
        if last_rsi < 30:
            st.success(f"🔥 KAUFSIGNAL: RSI ist bei {last_rsi:.2f} (Überverkauft)")
        elif last_rsi > 70:
            st.warning(f"❄️ VERKAUFSIGNAL: RSI ist bei {last_rsi:.2f} (Überkauft)")
        else:
            st.info(f"Neutral: RSI liegt bei {last_rsi:.2f}")
    else:
        st.error("Symbol nicht gefunden oder keine Daten verfügbar.")
