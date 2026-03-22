import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Aktien-Scanner Pro", page_icon="🚥", layout="wide")

st.title("🚥 Aktien-Check: Analyse & News")
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
    with st.spinner('Lade Daten...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            ticker_obj = yf.Ticker(symbol)
            data = ticker_obj.history(period="5y")
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                sma200 = data['Close'].rolling(window=200).mean().iloc[-1]
                
                st.subheader(f"Analyse für: {name} ({symbol})")
                
                # --- ANALYSTEN AMPEL ---
                try:
                    info = ticker_obj.info
                    rec_key = info.get('recommendationKey', 'N/A').replace('_', ' ').title()
                    st.markdown(f"**Analysten-Meinung:** {rec_key}")
                except:
                    st.info("Keine Empfehlungs-Daten.")

                # --- CHART ---
                plot_data = data['Close'].tail(252 if zeitraum == "1y" else 504 if zeitraum == "2y" else 1260)
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data, name='Preis'), row=1, col=1)
                fig.add_trace(go.Bar(x=plot_data.index, y=data['Volume'].loc[plot_data.index], name='Volumen', marker_color='lightgray'), row=2, col=1)
                fig.update_layout(height=500, template="plotly_white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                # --- NEWS SEKTION ---
                st.markdown("---")
                st.subheader(f"📰 Aktuelle News zu {name}")
                news = ticker_obj.news
                if news:
                    for item in news[:5]: # Zeige die Top 5 News
                        with st.expander(item['title']):
                            st.write(f"**Quelle:** {item['publisher']}")
                            st.write(f"**Link:** [Zum Artikel]({item['link']})")
                else:
                    st.write("Keine aktuellen News gefunden.")
            else:
                st.error("Keine Kursdaten gefunden.")
