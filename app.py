import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Seite konfigurieren
st.set_page_config(page_title="Aktien-Scanner Pro", page_icon="🚥", layout="wide")

st.title("🚥 Profi-Check: Trend & Panik-Indikator")
st.markdown("---")

# Seitenleiste für Eingaben
st.sidebar.header("Suche & Einstellungen")
user_input = st.sidebar.text_input("Name oder Kürzel der Aktie", "TSLA")
zeitraum = st.sidebar.selectbox("Zeitraum für Chart", ["1y", "2y", "5y"], index=0)

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
    with st.spinner('Marktdaten werden analysiert...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            ticker_obj = yf.Ticker(symbol)
            # 5 Jahre laden für präzisen SMA 200
            data = ticker_obj.history(period="5y")
            
            if not data.empty:
                # --- BERECHNUNGEN ---
                close_prices = data['Close']
                volume_data = data['Volume']
                current_price = float(close_prices.iloc[-1])
                
                # SMA 200 (Trend-Linie)
                sma200 = close_prices.rolling(window=200).mean()
                current_sma200 = float(sma200.iloc[-1])
                
                # RSI (Stimmung)
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi_series = 100 - (100 / (1 + (gain / loss)))
                last_rsi = float(rsi_series.iloc[-1])
                
                # --- PANIK-LOGIK (VOLUMEN-SIGNAL) ---
                avg_volume = volume_data.rolling(window=20).mean()
                # Signal, wenn Volumen 150% über dem Schnitt liegt UND Preis fällt
                is_panic = (volume_data.iloc[-1] > avg_volume.iloc[-1] * 1.5) and (close_prices.iloc[-1] < close_prices.iloc[-2])

                st.subheader(f"Analyse für: {name} ({symbol})")
                
                # Metriken anzeigen
                m1, m2, m3 = st.columns(3)
                m1.metric("Aktueller Kurs", f"{current_price:.2f} $")
                m2.metric("SMA 200 (Trend)", f"{current_sma200:.2f} $")
                m3.metric("RSI (Stimmung)", f"{last_rsi:.2f}")

                if is_panic:
                    st.error("⚠️ ACHTUNG: Hohes Verkaufsvolumen erkannt! Panik-Verkäufe möglich.")

                # --- CHART ERSTELLEN ---
                limit = 252 if zeitraum == "1y" else 504 if zeitraum == "2y" else 1260
                p_data = close_prices.tail(limit)
                s_data = sma200.tail(limit)
                v_data = volume_data.tail(limit)
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                
                # Preis & SMA
                fig.add_trace(go.Scatter(x=p_data.index, y=p_data, name='Preis', line=dict(color='#1f77b4', width=2)), row=1, col=1)
                fig.add_trace(go.Scatter(x=s_data.index, y=s_data, name='SMA 200', line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)
                
                # Volumen-Balken mit Farblogik
                colors = []
                for i in range(len(v_data)):
                    # Wenn Volumen > 150% vom Schnitt und Preis sinkt -> Knallrot
                    current_idx = v_data.index[i]
                    if v_data.iloc[i] > avg_volume.loc[current_idx] * 1.5 and (i > 0 and p_data.iloc[i] < p_data.iloc[i-1]):
                        colors.append('red')
                    else:
                        colors.append('lightgray')
                
                fig.add_trace(go.Bar(x=v_data.index, y=v_data, name='Volumen', marker_color=colors), row=2, col=1)
                
                fig.update_layout(height=600, template="plotly_white", hovermode='x unified', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                # --- NEWS ---
                st.markdown("---")
                st.subheader("📰 Aktuelle Schlagzeilen")
                try:
                    news = ticker_obj.news
                    if news:
                        for item in news[:5]:
                            with st.expander(item.get('title', 'Nachricht')):
                                st.write(f"Quelle: {item.get('publisher')}")
                                st.write(f"[Link zum Artikel]({item.get('link')})")
                    else:
                        st.write("Keine News verfügbar.")
                except:
                    st.write("News-Schnittstelle momentan nicht erreichbar.")

            else:
                st.error("Konnte keine Daten für dieses Symbol finden.")
        else:
            st.error("Aktie wurde nicht gefunden.")
