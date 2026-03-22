# --- NEWS SEKTION (VERBESSERT) ---
                st.markdown("---")
                st.subheader(f"📰 Aktuelle Marktdaten & News")
                
                try:
                    # Wir holen die News direkt vom Ticker-Objekt
                    news_list = ticker_obj.news
                    
                    if news_list and len(news_list) > 0:
                        for item in news_list[:5]:
                            # Sicherer Zugriff auf die Felder
                            title = item.get('title', 'Kein Titel verfügbar')
                            link = item.get('link', '#')
                            publisher = item.get('publisher', 'Finanz-News')
                            
                            with st.expander(f"{publisher}: {title}"):
                                if link != '#':
                                    st.write(f"🔗 [Vollständigen Artikel lesen]({link})")
                                else:
                                    st.write("Kein Link verfügbar.")
                    else:
                        st.warning("Yahoo Finance liefert gerade keine direkten News-Links. Das passiert oft bei kleineren Firmen oder Wartungsarbeiten.")
                        st.info(f"💡 [Klicke hier für die News-Suche zu {name} auf Yahoo Finance](https://finance.yahoo.com/quote/{symbol}/news)")
                
                except Exception as e:
                    st.error("Der News-Feed konnte aufgrund einer technischen Änderung bei Yahoo nicht geladen werden.")
                    st.info(f"Suche manuell nach: [Google News Suche für {name}](https://www.google.com/search?q={name}+Aktie+News&tbm=nws)")
