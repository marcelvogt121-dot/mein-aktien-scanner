import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Aktien-Ampel Pro", page_icon="🚥", layout="wide")

st.title("🚥 Aktien-Scanner mit Analysten-Ampel")
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
    with st.spinner('Lade Marktdaten...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            ticker_obj = yf.Ticker(symbol)
            # 1. Kursdaten laden
            data = ticker_obj.history(period="5y")
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                sma200 = data['Close'].rolling(window=200).mean().iloc[-1]
                
                st.subheader(f"Analyse für: {name} ({symbol})")
                
                # --- DIE NEUE AMPEL LOGIK (SICHERER) ---
                st.markdown("### 🚦 Analysten-Ampel")
                
                # Wir versuchen die Empfehlung aus den 'info' Daten zu lesen
                try:
                    info = ticker_obj.info
                    rec_key = info.get('recommendationKey', 'Keine Daten').replace('_', ' ').title()
                    target_price = info.get('targetMeanPrice', 'N/A')
                    
                    col_a, col_b = st.columns(2)
                    
                    # Farbauswahl für die Ampel
                    if "Buy" in rec_key:
                        st.success(f"🟢 **Empfehlung: {rec_key}**")
                    elif "Sell" in rec_key:
                        st.error(f"🔴 **Empfehlung: {rec_key}**")
                    else:
                        st.warning(f"🟡 **Empfehlung: {rec_key}**")
                        
                    st.write(f"Durchschnittliches Kursziel der Profis: **{target_price} $**")
                except:
                    st.info("Analysten-Zusammenfassung aktuell nicht verfügbar.")

                # --- DER CHART ---
                plot_data = data['Close'].tail(252 if zeitraum == "1y" else 504 if zeitraum == "2y" else 1260)
                vol_data = data['Volume'].loc[plot_data.index]
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data, name='Preis', line=dict(color='#1f77b4')), row=1, col=1)
                fig.add_trace(go.Bar(x=plot_data.index, y=vol_data, name='Volumen', marker_color='#d3d3d3'), row=2, col=1)
                
                fig.update_layout(height=600, template="plotly_white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                # --- TREND-CHECK ---
                st.markdown("---")
                if current_price > sma200:
                    st.success(f"📈 **Trend:** Die Aktie ist im Aufwärtstrend (über SMA 200 von {sma200:.2f} $)")
                else:
                    st.error(f"📉 **Trend:** Die Aktie ist im Abwärtstrend (unter SMA 200 von {sma200:.2f} $)")

            else:
                st.error("Keine Kursdaten gefunden.")
        else:
            st.error("Aktie wurde nicht gefunden.")
