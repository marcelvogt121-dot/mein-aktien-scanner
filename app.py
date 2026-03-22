import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktien-Genie", page_icon="📈")
st.title("🚀 Mein Aktien-Scanner")

ticker = st.text_input("Ticker Symbol (z.B. AAPL, TSLA, BTC-USD)", "AAPL")

if st.button("Analyse starten"):
    data = yf.download(ticker, period="1y")
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        st.metric("Aktueller Kurs", f"{current_price:.2f}")
        st.line_chart(data['Close'])
        
        # RSI Logik (Kaufsignal)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1+rs))
        
        if rsi.iloc[-1] < 30:
            st.success(f"Kaufsignal! RSI ist niedrig ({rsi.iloc[-1]:.2f})")
        else:
            st.info(f"RSI ist bei {rsi.iloc[-1]:.2f}")
    else:
        st.error("Symbol nicht gefunden.")
