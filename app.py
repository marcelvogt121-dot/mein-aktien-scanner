import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Seite konfigurieren
st.set_page_config(page_title="Aktien-Scanner Pro", page_icon="🚥", layout="wide")

# Initialisierung der Favoritenliste im Sitzungsspeicher (Session State)
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = []

st.title("🚥 Aktien-Check: Trend, RSI & Favoriten")
st.markdown("---")

# --- SEITENLEISTE ---
st.sidebar.header("Suche & Einstellungen")
user_input = st.sidebar.text_input("Name oder Kürzel der Aktie", "TSLA")
zeitraum = st.sidebar.selectbox("Zeitraum für Chart", ["1y", "2y", "5y"], index=0)

# Favoriten-Funktionen
st.sidebar.markdown("---")
st.sidebar.header("⭐ Meine Favoriten")

# Button zum Hinzufügen des aktuellen Inputs
if st.sidebar.button("Zu Favoriten hinzufügen"):
    symbol_to_add = user_input.upper()
    if symbol_to_add not in st.session_state['favorites']:
        st.session_state['favorites'].append(symbol_to_add)
        st.sidebar.success(f"{symbol_to_add} gespeichert!")

# Favoritenliste anzeigen und klickbar machen
if st.session_state['favorites']:
    selected_fav = st.sidebar.selectbox("Gespeicherte Aktien auswählen:", st.session_state['favorites'])
    if st.sidebar.button("Favorit laden"):
        user_input = selected_fav # Setzt den Input auf den Favoriten

if st.sidebar.button("Favoritenliste leeren"):
    st.session_state['favorites'] = []
    st.rerun()

st.sidebar.markdown("---")

def get_ticker(search_term):
    try:
        search = yf.Search(search_term, max_results=1)
        if search.quotes:
            return search.quotes[0]['symbol'], search.quotes[0]['shortname']
        return None, None
    except:
        return None, None

# Haupt-Logik startet bei Button-Klick
if st.sidebar.button("Analyse starten"):
    with st.spinner('Daten werden analysiert...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            ticker_obj = yf.Ticker(symbol)
            data = ticker_obj.history(period="5y")
            
            if not data.empty:
                # --- BERECHNUNGEN ---
                close_prices = data['Close']
                volume_data = data['Volume']
                current_price = float(close_prices.iloc[-1])
                sma200 = close_prices.rolling(window=200).mean()
                current_sma200 = float(sma200.iloc[-1])
                
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi_series = 100 - (100 / (1 + (gain / loss)))
                last_rsi = float(rsi_series.iloc[-1])
                
                # Panik-Logik
                avg_volume = volume_data.rolling(window=20).mean()
                is_panic = (volume_data.iloc[-1] > avg_volume.iloc[-1] * 1.5) and (close_prices.iloc[-1] < close_prices.iloc[-2])

                st.subheader(f"Analyse für: {name} ({symbol})")
                
                # Analysten-Empfehlung
                try:
                    info = ticker_obj.info
                    rec_key = info.get('recommendationKey', 'N/A').replace('_', ' ').title()
                    target_price = info.get('targetMeanPrice', 'N/A')
                    
                    st.markdown("### 🚦 Analysten-Meinung")
                    if "Buy" in rec_key:
                        st.success(f"🟢 Empfehlung: **{rec_key}** | Kursziel: **{target_price} $**")
                    elif "Sell" in rec_key:
                        st.error(f"🔴 Empfehlung: **{rec_key}** | Kursziel: **{target_price} $**")
                    else:
                        st.warning(f"🟡 Empfehlung: **{rec_key}** | Kursziel: **{target_price} $**")
                except:
                    st.info("Analysten-Daten aktuell nicht verfügbar.")

                st.markdown("---")

                # Metriken
                m1, m2, m3 = st.columns(3)
                m1.metric("Aktueller Kurs", f"{current_price:.2f} $")
                m2.metric("SMA 200 (Trend)", f"{current_sma200:.2f} $")
                m3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

                if is_panic:
                    st.error("⚠️ ACHTUNG: Hohes Verkaufsvolumen erkannt! Mögliche Panik im Markt.")

                # Chart
                limit = 252 if zeitraum == "1y" else 504 if zeitraum == "2y" else 1260
                p_data = close_prices.tail(limit)
                s_data = sma200.tail(limit)
                v_data = volume_data.tail(limit)
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig.add_trace(go.Scatter(x=p_data.index, y=p_data, name='Preis', line=dict(color='#1f77b4', width=2)), row=1, col=1)
                fig.add_trace(go.Scatter(x=s_data.index, y=s_data, name='SMA 200', line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)
                
                # Farblogik Volumen
                v_avg_plot = avg_volume.loc[v_data.index]
                colors = []
                for i in range(len(v_data)):
                    if v_data.iloc[i] > v_avg_plot.iloc[i] * 1.5 and (i > 0 and p_data.iloc[i] < p_data.iloc[i-1]):
                        colors.append('red')
                    else:
                        colors.append('lightgray')
                
                fig.add_trace(go.Bar(x=v_data.index, y=v_data, name='Volumen', marker_color=colors), row=2, col=1)
                fig.update_layout(height=600, template="plotly_white", hovermode='x unified', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                # Fazit
                st.markdown("---")
                if current_price > current_sma200:
                    st.write("✅ **Trend:** Die Aktie ist im langfristigen Aufwärtstrend.")
                else:
                    st.write("❌ **Trend:** Die Aktie ist im langfristigen Abwärtstrend.")
            else:
                st.error("Keine Daten gefunden.")
        else:
            st.error("Aktie wurde nicht gefunden.")
