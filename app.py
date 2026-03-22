# --- NEWS SEKTION (REPARIERT & FORMATEIERT) ---
                st.markdown("---")
                st.subheader(f"📰 Aktuelle Marktdaten & News")
                
                try:
                    news_list = ticker_obj.news
                    if news_list and len(news_list) > 0:
                        for item in news_list[:5]:
                            title = item.get('title', 'Kein Titel verfügbar')
                            link = item.get('link', '#')
                            publisher = item.get('publisher', 'Finanz-News')
                            
                            with st.expander(f"{publisher}: {title}"):
                                if link != '#':
                                    st.write(f"🔗 [Vollständigen Artikel lesen]({link})")
                                else:
                                    st.write("Kein Link verfügbar.")
                    else:
                        st.warning("Keine direkten News verfügbar.")
                        st.info(f"💡 [Direkt zu Yahoo Finance](https://finance.yahoo.com/quote/{symbol}/news)")
                except Exception as e:
                    st.error("News-Fehler")
