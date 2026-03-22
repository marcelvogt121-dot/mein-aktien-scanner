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
    with st.spinner('Lade Marktdaten & Analysten-Meinungen...'):
        symbol, name = get_ticker(user_input)
        ticker_obj = yf.Ticker(symbol)
        
        if symbol:
            # 1. Kursdaten laden
            data = ticker_obj.history(period="5y")
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                sma200 = data['Close'].rolling(window=200).mean().iloc[-1]
                
                # 2. Analysten-Empfehlungen abrufen
                rec = ticker_obj.recommendations
                
                st.subheader(f"Analyse für: {name} ({symbol})")
                
                # --- DIE AMPEL LOGIK ---
                st.markdown("### 🚦 Analysten-Ampel")
                if rec is not None and not rec.empty:
                    # Wir nehmen die aktuellste Zeile der Empfehlungen
                    latest_rec = rec.iloc[-1]
                    buy = latest_rec.get('strongBuy', 0) + latest_rec.get('buy', 0)
                    hold = latest_rec.get('hold', 0)
                    sell = latest_rec.get('sell', 0) + latest_rec.get('strongSell', 0)
                    
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Kaufen", f"{buy} Profis")
                    col_b.metric("Halten", f"{hold} Profis")
                    col_c.metric("Verkaufen", f"{sell} Profis")

                    if buy > sell and buy > hold:
                        st.success("🟢 **AMPELEMPFEHLUNG: KAUFEN** - Die Mehrheit der Analysten ist optimistisch.")
                    elif sell > buy:
                        st.error("🔴 **AMPELEMPFEHLUNG: VERKAUFEN** - Die Experten raten zur Vorsicht.")
                    else:
                        st.warning("🟡 **AMPELEMPFEHLUNG: HALTEN** - Es gibt aktuell keine klare Richtung.")
                else:
                    st.info("Keine aktuellen Analysten-Daten für dieses Symbol verfügbar.")

                # --- DER CHART ---
                plot_data = data['Close'].tail(252 if zeitraum == "1y" else 504 if zeitraum == "2y" else 1260)
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data, name='Preis'), row=1, col=1)
                fig.add_trace(go.Bar(x=plot_data.index, y=data['Volume'].loc[plot_data.index], name='Volumen'), row=2, col=1)
                fig.update_layout(height=500, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                # --- FAZIT ---
                st.markdown("---")
                if current_price > sma200:
                    st.write("✅ **Trend-Check:** Die Aktie notiert über ihrem Jahresdurchschnitt (Aufwärtstrend).")
                else:
                    st.write("❌ **Trend-Check:** Die Aktie notiert unter ihrem Jahresdurchschnitt (Abwärtstrend).")

            else:
                st.error("Keine Daten gefunden.")
