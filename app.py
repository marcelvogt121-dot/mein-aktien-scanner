import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Aktien-Scanner Pro", page_icon="🚥", layout="wide")

st.title("🚥 Profi-Check: Preis, Trend (SMA) & RSI")
st.markdown("---")

# Seitenleiste
st.sidebar.header("Suche")
user_input = st.sidebar.text_input("Name oder Kürzel", "TSLA")
zeitraum = st.sidebar.selectbox("Zeitraum", ["1y", "2y", "5y"], index=0)

def get_ticker(search_term):
    try:
        search = yf.Search(search_term, max_results=1)
        if search.quotes:
            return search.quotes[0]['symbol'], search.quotes[0]['shortname']
        return None, None
    except:
        return None, None

if st.sidebar.button("Analyse starten"):
    with st.spinner('Berechne Indikatoren...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            ticker_obj = yf.Ticker(symbol)
            # Wir laden 5 Jahre, um den SMA 200 immer präzise berechnen zu können
            data = ticker_obj.history(period="5y")
            
            if not data.empty:
                # --- BERECHNUNGEN ---
                close_prices = data['Close']
                current_price = float(close_prices.iloc[-1])
                
                # SMA 200 (Gleitender Durchschnitt)
                sma200 = close_prices.rolling(window=200).mean()
                current_sma200 = float(sma200.iloc[-1])
                
                # RSI (Relative Strength Index)
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi_series = 100 - (100 / (1 + (gain / loss)))
                last_rsi = float(rsi_series.iloc[-1])
                
                st.subheader(f"Analyse für: {name} ({symbol})")
                
                # --- METRIKEN ANZEIGEN ---
                m1, m2, m3 = st.columns(3)
                m1.metric("Kurs", f"{current_price:.2f} $")
                m2.metric("SMA 200", f"{current_sma200:.2f} $", f"{(current_price - current_sma200):.2f} $ Diff")
                m3.metric("RSI (14 Tage)", f"{last_rsi:.2f}")

                # --- DER KOMBINIERTE CHART ---
                # Zeitraum für den Plot zuschneiden
                limit = 252 if zeitraum == "1y" else 504 if zeitraum == "2y" else 1260
                plot_data = close_prices.tail(limit)
                sma_plot = sma200.tail(limit)
                vol_plot = data['Volume'].tail(limit)
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                
                # Preis-Linie
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data, name='Preis', line=dict(color='#1f77b4', width=2)), row=1, col=1)
                
                # SMA 200-Linie (Orange gestrichelt)
                fig.add_trace(go.Scatter(x=sma_plot.index, y=sma_plot, name='SMA 200', line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)
                
                # Volumen-Balken
                fig.add_trace(go.Bar(x=vol_plot.index, y=vol_plot, name='Volumen', marker_color='lightgray'), row=2, col=1)
                
                fig.update_layout(height=600, template="plotly_white", hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)

                # --- FAZIT-AMPEL ---
                st.markdown("### 💡 Einschätzung")
                if current_price > current_sma200:
                    if last_rsi < 35:
                        st.success(f"🟢 **SIGNAL:** Aufwärtstrend bestätigt & RSI niedrig ({last_rsi:.1f}). Eventuell ein guter Einstieg!")
                    else:
                        st.info("⚖️ **Trend:** Stabil über SMA 200. Kein extremes RSI-Signal.")
                else:
                    st.error(f"🔴 **WARNUNG:** Abwärtstrend (unter SMA 200). Der RSI von {last_rsi:.1f} allein reicht hier nicht für einen Kauf.")

                # --- NEWS ---
                st.markdown("---")
                st.subheader("📰 Aktuelle News")
                try:
                    for item in ticker_obj.news[:5]:
                        with st.expander(item.get('title', 'News')):
                            st.write(f"Quelle: {item.get('publisher')}")
                            st.write(f"[Link zum Artikel]({item.get('link')})")
                except:
                    st.write("News derzeit nicht verfügbar.")
            else:
                st.error("Daten konnten nicht geladen werden.")
