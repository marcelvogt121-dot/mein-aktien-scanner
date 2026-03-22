import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go # Neu für fortgeschrittene Charts
from plotly.subplots import make_subplots # Neu für Subplots

st.set_page_config(page_title="Aktien-Volumen-Chart", page_icon="📈", layout="wide")

st.title("📈 Profi-Chart: Preis, SMA 200 & Volumen integriert")
st.markdown("---")

# Seitenleiste
st.sidebar.header("Suche & Zeitraum")
user_input = st.sidebar.text_input("Name oder Kürzel", "TSLA")
zeitraum = st.sidebar.selectbox("Zeitraum", ["1y", "2y", "5y", "max"], index=0)

def get_ticker(search_term):
    try:
        search = yf.Search(search_term, max_results=1)
        if search.quotes:
            return search.quotes[0]['symbol'], search.quotes[0]['shortname']
        return None, None
    except:
        return None, None

if st.sidebar.button("Analyse starten"):
    with st.spinner('Marktdaten werden geladen...'):
        symbol, name = get_ticker(user_input)
        
        if symbol:
            st.subheader(f"Analyse für: {name} ({symbol})")
            
            # Daten laden (immer genug für SMA 200)
            data = yf.download(symbol, period="5y", auto_adjust=True)
            
            if not data.empty:
                # Daten-Extraktion
                if isinstance(data.columns, pd.MultiIndex):
                    close_prices = data['Close'][symbol]
                    volume_data = data['Volume'][symbol]
                else:
                    close_prices = data['Close']
                    volume_data = data['Volume']
                
                # Berechnung
                current_price = float(close_prices.iloc[-1])
                sma200 = close_prices.rolling(window=200).mean()
                current_sma200 = float(sma200.iloc[-1])
                
                # Filterung für den gewählten Zeitraum
                if zeitraum == "1y": plot_data = close_prices.tail(252); vol_data = volume_data.tail(252)
                elif zeitraum == "2y": plot_data = close_prices.tail(504); vol_data = volume_data.tail(504)
                elif zeitraum == "5y": plot_data = close_prices.tail(1260); vol_data = volume_data.tail(1260)
                else: plot_data = close_prices; vol_data = volume_data
                
                sma200_filtered = sma200.loc[plot_data.index]

                # --- KOMBINEIRTER CHART MIT PLOTLY ---
                st.write("### Kursverlauf mit integriertem Volumen")
                
                # Erstelle Subplots: Preis oben (größer), Volumen unten (kleiner)
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                   vertical_spacing=0.03, subplot_titles=(f'{zeitraum}-Chart', 'Volumen'), 
                                   row_heights=[0.7, 0.3])

                # 1. Preis-Linie (Row 1)
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data, name='Preis', 
                                         line=dict(color='blue', width=2)), row=1, col=1)
                
                # 2. SMA 200-Linie (Row 1)
                fig.add_trace(go.Scatter(x=sma200_filtered.index, y=sma200_filtered, name='SMA 200', 
                                         line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)

                # 3. Volumen-Balken (Row 2) - Farbe je nach Preisbewegung
                colors = ['green' if plot_data.iloc[i] >= plot_data.iloc[i-1] else 'red' for i in range(1, len(plot_data))]
                colors.insert(0, 'gray') # Erste Farbe
                
                fig.add_trace(go.Bar(x=vol_data.index, y=vol_data, name='Volumen', 
                                     marker=dict(color=colors)), row=2, col=1)

                # Layout-Anpassungen (Achsenbeschriftungen, Hover-Effekte)
                fig.update_layout(xaxis2_title='Datum', yaxis1_title='Preis ($)', yaxis2_title='Volumen',
                                  hovermode='x unified', height=600)
                
                st.plotly_chart(fig, use_container_width=True)

                # --- METRIKEN ---
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.metric("Kurs aktuell", f"{current_price:.2f} $")
                col2.metric("SMA 200 (Durchschnitt)", f"{current_sma200:.2f} $")
                col3.metric("Trend", "Aufwärts ✅" if current_price > current_sma200 else "Abwärts 🔴")

                # --- FAZIT-BOX ---
                st.subheader("💡 Fazit")
                if current_price > current_sma200:
                    st.success(f"🟢 **Trend Folger:** {name} ist im Aufwärtstrend (über SMA 200).")
                else:
                    st.error(f"🔴 **VORSICHT:** Die Aktie notiert unter ihrem Jahresdurchschnitt (Abwärtstrend).")

            else:
                st.error("Keine Daten gefunden.")
        else:
            st.error("Aktie wurde nicht gefunden.")

st.sidebar.markdown("---")
st.sidebar.write("📖 **Profi-Tipp:** Steigt der Kurs bei **hohem Volumen** (grüne Balken), ist das ein starkes Kaufsignal. Fällt er bei hohem Volumen (rote Balken), ist Vorsicht geboten.")
