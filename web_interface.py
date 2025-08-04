#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Web Arayüzü - Türk Siyasi Lider Analiz Sistemi

Kurulum:
pip install streamlit pandas plotly

Çalıştırma:
streamlit run web_interface.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import time
from datetime import datetime
import sys
import os

# Ana sistem sınıfını import et
try:
    from political_analyzer import PoliticalAnalysisSystem
except ImportError:
    st.error("❌ political_analyzer.py dosyası bulunamadı!")
    st.stop()

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🇹🇷 Türk Siyasi Lider Analiz Sistemi",
    page_icon="🇹🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }

    .leader-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }

    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Ana web arayüzü"""

    # Başlık
    st.markdown('<h1 class="main-header">🇹🇷 Türk Siyasi Lider Analiz Sistemi</h1>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>ℹ️ Sistem Hakkında:</strong><br>
        Bu sistem sosyal medya içeriklerini analiz ederek 4 siyasi lidere göre kategorize eder 
        ve sentiment analizi yapar: <strong>RTE, ÖÖ, MY, EI</strong>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Konfigürasyon
    with st.sidebar:
        st.header("⚙️ Konfigürasyon")

        api_key = st.text_input(
            "Google API Key",
            type="password",
            value="AIzaSyCklJ6T0IDgjuH7N8fbWl6AQtJuCEGbRA8",
            help="Google Gemini API anahtarınızı girin"
        )

        st.subheader("📊 İleri Ayarlar")
        batch_size = st.slider("Batch Boyutu", 1, 10, 3)
        max_workers = st.slider("Paralel İşlem", 1, 5, 2)
        rate_limit = st.slider("Rate Limit (saniye)", 0.5, 5.0, 1.5, 0.1)

        st.subheader("📈 Lider Bilgileri")
        leaders_info = {
            'RTE': 'Recep Tayyip Erdoğan',
            'ÖÖ': 'Özgür Özel',
            'MY': 'Mansur Yavaş',
            'EI': 'Ekrem İmamoğlu'
        }

        for code, name in leaders_info.items():
            st.text(f"{code}: {name}")

    # Ana içerik - Tab'lar
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧪 Tek İçerik Testi",
        "📁 Toplu Analiz",
        "📊 Sonuçlar",
        "📋 Kullanım Kılavuzu"
    ])

    # Tab 1: Tek İçerik Testi
    with tab1:
        st.header("🧪 Tek İçerik Analizi")

        col1, col2 = st.columns([1, 1])

        with col1:
            test_account = st.text_input(
                "Hesap Adı",
                value="@burcukoksal03",
                placeholder="@ornek_hesap"
            )

        with col2:
            st.empty()  # Boşluk için

        test_text = st.text_area(
            "İçerik Metni",
            value="Ata tohumlarımızı hasat ettik! 11 Ekim'de Ankara Büyükşehir Belediye Başkanımız Mansur Yavaş'la birlikte ektiğimiz arpa, buğday ve çörek otunun bereketini topladık. Desteklerinden dolayı Mansur Başkanımıza teşekkür ediyorum. @mansuryavas06",
            height=150,
            placeholder="Analiz edilecek sosyal medya içeriğini yazın..."
        )

        if st.button("🚀 Analiz Et", type="primary"):
            if not api_key:
                st.error("❌ Lütfen API anahtarını girin!")
            elif not test_text.strip():
                st.error("❌ Lütfen analiz edilecek içeriği girin!")
            else:
                with st.spinner("🔄 Analiz yapılıyor..."):
                    try:
                        analyzer = PoliticalAnalysisSystem(
                            api_key,
                            batch_size=1,
                            max_workers=1,
                            rate_limit_sec=rate_limit
                        )

                        result = analyzer.process_single_content(test_account, test_text)

                        if result:
                            st.success("✅ Analiz tamamlandı!")

                            # Sonuçları göster
                            col1, col2 = st.columns([1, 1])

                            with col1:
                                st.subheader("👥 Lider Sınıflandırması")
                                leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
                                for leader in leaders:
                                    value = result.get(f'IS_{leader}', -1)
                                    if value == 1:
                                        st.success(f"✅ {leader}: İlgili (+1)")
                                    else:
                                        st.info(f"➖ {leader}: İlgisiz (-1)")

                            with col2:
                                st.subheader("😊 Sentiment Analizi")
                                for leader in leaders:
                                    sentiment_key = f'{leader}_SENTIMENT'
                                    sentiment = result.get(sentiment_key)

                                    if sentiment is not None:
                                        if sentiment == 1:
                                            st.success(f"😊 {leader}: Pozitif (+1)")
                                        elif sentiment == 0:
                                            st.info(f"😐 {leader}: Nötr (0)")
                                        elif sentiment == -1:
                                            st.error(f"😠 {leader}: Negatif (-1)")
                                    else:
                                        st.text(f"➖ {leader}: Analiz yok")

                            # Detaylı sonuç
                            st.subheader("📄 Detaylı Sonuç")
                            st.json(result)

                        else:
                            st.error("❌ Analiz başarısız!")

                    except Exception as e:
                        st.error(f"❌ Hata oluştu: {str(e)}")

    # Tab 2: Toplu Analiz
    with tab2:
        st.header("📁 Toplu CSV Analizi")

        # Dosya yükleme
        uploaded_file = st.file_uploader(
            "CSV Dosyası Seçin",
            type=['csv'],
            help="ACCOUNT_NAME ve TEXT sütunları içeren CSV dosyası yükleyin"
        )

        if uploaded_file is not None:
            try:
                # CSV'yi önizle
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Dosya yüklendi: {len(df)} kayıt")

                # Veri önizleme
                st.subheader("👀 Veri Önizleme")
                st.dataframe(df.head(10))

                # Sütun kontrolü
                required_cols = ['ACCOUNT_NAME', 'TEXT']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"❌ Eksik sütunlar: {missing_cols}")
                else:
                    st.success("✅ Gerekli sütunlar mevcut")

                    # İşlem başlat butonu
                    col1, col2, col3 = st.columns([1, 1, 1])

                    with col2:
                        if st.button("🚀 Toplu Analizi Başlat", type="primary"):
                            if not api_key:
                                st.error("❌ Lütfen API anahtarını girin!")
                            else:
                                # Session state'de analiz durumunu takip et
                                if 'analysis_running' not in st.session_state:
                                    st.session_state.analysis_running = False

                                if not st.session_state.analysis_running:
                                    st.session_state.analysis_running = True

                                    # Progress bar ve durum
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()

                                    try:
                                        analyzer = PoliticalAnalysisSystem(
                                            api_key,
                                            batch_size=batch_size,
                                            max_workers=max_workers,
                                            rate_limit_sec=rate_limit
                                        )

                                        # Veriyi hazırla
                                        data_records = df.to_dict('records')
                                        results = []

                                        total_items = len(data_records)

                                        # Batch'ler halinde işle
                                        for i in range(0, total_items, batch_size):
                                            batch = data_records[i:i + batch_size]

                                            status_text.text(
                                                f"İşleniyor: {i + 1}-{min(i + batch_size, total_items)}/{total_items}")

                                            # Batch işle
                                            batch_results = analyzer.process_batch_parallel(batch)
                                            results.extend(batch_results)

                                            # Progress güncelle
                                            progress = min((i + batch_size) / total_items, 1.0)
                                            progress_bar.progress(progress)

                                            time.sleep(0.1)  # UI güncellemesi için

                                        # Sonuçları session state'e kaydet
                                        st.session_state.analysis_results = results
                                        st.session_state.analysis_completed = True

                                        status_text.success("✅ Analiz tamamlandı!")

                                    except Exception as e:
                                        st.error(f"❌ Analiz hatası: {str(e)}")

                                    finally:
                                        st.session_state.analysis_running = False

                                else:
                                    st.warning("⚠️ Analiz zaten devam ediyor...")

            except Exception as e:
                st.error(f"❌ Dosya okuma hatası: {str(e)}")

    # Tab 3: Sonuçlar
    with tab3:
        st.header("📊 Analiz Sonuçları")

        if 'analysis_results' in st.session_state:
            results = st.session_state.analysis_results

            if results:
                # Özet istatistikler
                st.subheader("📈 Özet İstatistikler")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Toplam İşlenen", len(results))

                total_mentions = sum(
                    1 for r in results
                    if any(r.get(f'IS_{leader}') == 1 for leader in ['RTE', 'ÖÖ', 'MY', 'EI'])
                )
                with col2:
                    st.metric("Toplam Bahsetme", total_mentions)

                # Sentiment dağılımları hesapla
                all_sentiments = []
                for r in results:
                    for leader in ['RTE', 'ÖÖ', 'MY', 'EI']:
                        sentiment = r.get(f'{leader}_SENTIMENT')
                        if sentiment is not None:
                            all_sentiments.append(sentiment)

                avg_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0

                with col3:
                    st.metric("Ortalama Sentiment", f"{avg_sentiment:.2f}")

                with col4:
                    success_rate = (len(results) / len(results)) * 100 if results else 0
                    st.metric("Başarı Oranı", f"{success_rate:.1f}%")

                # Lider bazlı analiz
                st.subheader("👥 Lider Bazlı Analiz")

                leader_data = []
                for leader_code in ['RTE', 'ÖÖ', 'MY', 'EI']:
                    leader_name = leaders_info[leader_code]

                    mentions = sum(1 for r in results if r.get(f'IS_{leader_code}') == 1)

                    sentiments = [r.get(f'{leader_code}_SENTIMENT') for r in results
                                  if r.get(f'{leader_code}_SENTIMENT') is not None]

                    positive = sum(1 for s in sentiments if s == 1)
                    neutral = sum(1 for s in sentiments if s == 0)
                    negative = sum(1 for s in sentiments if s == -1)

                    leader_data.append({
                        'Lider': leader_name,
                        'Kod': leader_code,
                        'Bahsetme': mentions,
                        'Pozitif': positive,
                        'Nötr': neutral,
                        'Negatif': negative,
                        'Toplam Sentiment': len(sentiments)
                    })

                # Lider tablosu
                leader_df = pd.DataFrame(leader_data)
                st.dataframe(leader_df, use_container_width=True)

                # Görselleştirmeler
                st.subheader("📊 Görselleştirmeler")

                # Bahsetme grafiği
                fig_mentions = px.bar(
                    leader_df,
                    x='Lider',
                    y='Bahsetme',
                    title='Lider Bahsetme Sayıları',
                    color='Bahsetme',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_mentions, use_container_width=True)

                # Sentiment dağılımı
                fig_sentiment = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=[f"{row['Lider']} ({row['Kod']})" for _, row in leader_df.iterrows()],
                    specs=[[{"type": "pie"}, {"type": "pie"}],
                           [{"type": "pie"}, {"type": "pie"}]]
                )

                colors = ['#ff4444', '#ffaa00', '#44ff44']  # Negatif, Nötr, Pozitif

                for i, (_, row) in enumerate(leader_df.iterrows()):
                    if row['Toplam Sentiment'] > 0:
                        pie_row = (i // 2) + 1
                        pie_col = (i % 2) + 1

                        fig_sentiment.add_trace(
                            go.Pie(
                                labels=['Negatif', 'Nötr', 'Pozitif'],
                                values=[row['Negatif'], row['Nötr'], row['Pozitif']],
                                marker_colors=colors,
                                showlegend=(i == 0)
                            ),
                            row=pie_row, col=pie_col
                        )

                fig_sentiment.update_layout(title_text="Lider Sentiment Dağılımları")
                st.plotly_chart(fig_sentiment, use_container_width=True)

                # Sonuçları indir
                st.subheader("💾 Sonuçları İndir")

                # CSV oluştur
                results_df = pd.DataFrame(results)
                csv_buffer = io.StringIO()
                results_df.to_csv(csv_buffer, index=False, encoding='utf-8')
                csv_string = csv_buffer.getvalue()

                # JSON oluştur
                json_string = json.dumps(results, ensure_ascii=False, indent=2)

                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="📄 CSV İndir",
                        data=csv_string,
                        file_name=f"siyasi_analiz_sonuclari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

                with col2:
                    st.download_button(
                        label="📋 JSON İndir",
                        data=json_string,
                        file_name=f"siyasi_analiz_sonuclari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

            else:
                st.info("ℹ️ Henüz analiz sonucu bulunmuyor.")
        else:
            st.info("ℹ️ Önce analiz yapın, sonuçlar burada görünecek.")

    # Tab 4: Kullanım Kılavuzu
    with tab4:
        st.header("📋 Kullanım Kılavuzu")

        st.markdown("""
        ## 🎯 Sistem Özellikleri

        ### Agent 1: Lider Sınıflandırma
        - **RTE**: Recep Tayyip Erdoğan (AK Parti, Cumhurbaşkanı)
        - **ÖÖ**: Özgür Özel (CHP Genel Başkanı)
        - **MY**: Mansur Yavaş (Ankara Büyükşehir Belediye Başkanı)
        - **EI**: Ekrem İmamoğlu (İstanbul Büyükşehir Belediye Başkanı)

        ### Agent 2: Sentiment Analizi
        - **+1**: Pozitif (övgü, destek, beğeni)
        - **0**: Nötr (tarafsız bahsetme, objektif)
        - **-1**: Negatif (eleştiri, saldırı, olumsuz)

        ## 📊 CSV Format Gereksinimleri

        ### Girdi CSV'niz şu sütunları içermelidir:
        ```
        ACCOUNT_NAME,TEXT
        @user1,"İçerik metni 1"
        @user2,"İçerik metni 2"
        ```

        ### Çıktı CSV formatı:
        ```
        ACCOUNT_NAME,TEXT,IS_RTE,IS_ÖÖ,IS_MY,IS_EI,RTE_SENTIMENT,ÖÖ_SENTİMENT,MY_SENTIMENT,EI_SENTIMENT
        ```

        ## 🚀 Hızlı Başlangıç

        1. **API Anahtarı**: Google Gemini API anahtarınızı yan panele girin
        2. **Tek Test**: "Tek İçerik Testi" sekmesinde hızlı test yapın
        3. **Toplu Analiz**: CSV dosyanızı yükleyip toplu analiz başlatın
        4. **Sonuçlar**: "Sonuçlar" sekmesinde detaylı analizi görün

        ## ⚙️ Performans Ayarları

        - **Batch Boyutu**: Aynı anda işlenecek kayıt sayısı (1-10)
        - **Paralel İşlem**: Eş zamanlı worker sayısı (1-5)
        - **Rate Limit**: API çağrıları arası bekleme süresi (0.5-5 saniye)

        ## 💡 İpuçları

        - Küçük veri setleri için batch boyutunu artırabilirsiniz
        - API limitlerini aşmamak için rate limit'i ayarlayın
        - İşlem sırasında sayfayı kapatmayın
        - Büyük dosyalar için komut satırı versiyonunu tercih edin

        ## 🛠️ Komut Satırı Kullanımı

        Büyük veri setleri için terminal kullanın:
        ```bash
        pip install requests pandas tqdm colorama
        python political_analyzer.py input.csv output.csv YOUR_API_KEY
        ```

        ## 📞 Destek

        - Sistem hataları için log dosyalarını kontrol edin
        - API limitleri için Google Cloud Console'u kontrol edin
        - Büyük dosyalar için komut satırı versiyonunu kullanın
        """)


if __name__ == "__main__":
    main()