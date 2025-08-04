#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimalist Streamlit Arayüzü - Türk Siyasi Lider Analiz Sistemi V2.0

Kurulum:
pip install streamlit pandas plotly

Çalıştırma:
streamlit run web_interface.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import time
import os
from datetime import datetime

# Ana sistem sınıfını import et
try:
    from political_analyzer import PoliticalAnalysisSystem
except ImportError:
    st.error("❌ political_analyzer.py dosyası bulunamadı!")
    st.stop()

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🇹🇷 Siyasi Analiz Sistemi",
    page_icon="🇹🇷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2E86AB;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }

    .leader-metric {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
    }

    .success-alert {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .info-alert {
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        color: #0d47a1;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .stButton > button {
        width: 100%;
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: #1c5aa3;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 0.875rem;
    }

    .footer-heart {
        color: #ef4444;
        animation: heartbeat 1.5s ease-in-out infinite;
    }

    @keyframes heartbeat {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Minimalist Ana Arayüz"""

    # Başlık
    st.markdown('<h1 class="main-title">🇹🇷 Siyasi Lider Analiz Sistemi</h1>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-alert">
        <strong>RTE</strong> · <strong>ÖÖ</strong> · <strong>MY</strong> · <strong>EI</strong> 
        için otomatik sınıflandırma ve sentiment analizi
    </div>
    """, unsafe_allow_html=True)

    # Ana işlem seçimi
    mode = st.radio(
        "İşlem Türü:",
        ["📝 Tek İçerik Testi", "📊 Toplu Analiz"],
        horizontal=True
    )

    # API Key girişi
    with st.expander("🔑 API Ayarları", expanded=False):
        # Environment'dan varsayılan değer al (opsiyonel)
        default_api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyCklJ6T0IDgjuH7N8fbWl6AQtJuCEGbRA8')

        api_key = st.text_input(
            "Google API Key:",
            type="password",
            value=default_api_key
        )

        col1, col2 = st.columns(2)
        with col1:
            batch_size = st.slider("Batch:", 1, 10, 3)
        with col2:
            rate_limit = st.slider("Rate (s):", 0.5, 3.0, 1.5, 0.1)

    st.divider()

    # Tek İçerik Testi
    if mode == "📝 Tek İçerik Testi":
        st.subheader("Tek İçerik Analizi")

        col1, col2 = st.columns([1, 3])
        with col1:
            account = st.text_input("Hesap:", "@test_user")
        with col2:
            st.empty()  # Spacing

        content = st.text_area(
            "İçerik:",
            "Mansur Yavaş'la harika bir proje yaptık! Desteklerinden dolayı teşekkürler.",
            height=100
        )

        if st.button("🚀 Analiz Et"):
            if not api_key or not content.strip():
                st.error("❌ API key ve içerik gerekli!")
            else:
                with st.spinner("Analiz yapılıyor..."):
                    try:
                        analyzer = PoliticalAnalysisSystem(
                            api_key,
                            batch_size=1,
                            max_workers=1,
                            rate_limit_sec=rate_limit
                        )

                        result = analyzer.process_single_content(account, content)

                        if result:
                            st.success("✅ Analiz tamamlandı!")

                            # Sonuçları kompakt göster
                            leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
                            names = ['R.T. Erdoğan', 'Ö. Özel', 'M. Yavaş', 'E. İmamoğlu']

                            cols = st.columns(4)
                            for i, (leader, name) in enumerate(zip(leaders, names)):
                                with cols[i]:
                                    is_relevant = result.get(f'IS_{leader}', 0)
                                    sentiment = result.get(f'{leader}_SENTIMENT', 0)

                                    if is_relevant == 1:
                                        if sentiment == 1:
                                            st.success(f"**{name}**\n😊 Pozitif")
                                        elif sentiment == -1:
                                            st.error(f"**{name}**\n😠 Negatif")
                                        else:
                                            st.info(f"**{name}**\n😐 Nötr")
                                    else:
                                        st.write(f"**{name}**\n➖ İlgisiz")
                        else:
                            st.error("❌ Analiz başarısız!")

                    except Exception as e:
                        st.error(f"❌ Hata: {str(e)}")

    # Toplu Analiz
    else:
        st.subheader("Toplu CSV Analizi")

        uploaded_file = st.file_uploader(
            "CSV Dosyası Yükle:",
            type=['csv'],
            help="ACCOUNT_NAME ve TEXT sütunları gerekli"
        )

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)

                # Hızlı önizleme
                st.info(f"📄 {len(df)} kayıt yüklendi")

                required_cols = ['ACCOUNT_NAME', 'TEXT']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"❌ Eksik sütunlar: {missing_cols}")
                else:
                    # Önizleme
                    with st.expander("👀 Veri Önizleme"):
                        st.dataframe(df.head(5), use_container_width=True)

                    # Analiz butonu
                    if st.button("🚀 Toplu Analizi Başlat"):
                        if not api_key:
                            st.error("❌ API key gerekli!")
                        else:
                            # Progress tracking
                            progress = st.progress(0)
                            status = st.empty()

                            try:
                                analyzer = PoliticalAnalysisSystem(
                                    api_key,
                                    batch_size=batch_size,
                                    max_workers=2,
                                    rate_limit_sec=rate_limit
                                )

                                # Veriyi işle
                                data_records = df.to_dict('records')
                                results = []
                                total = len(data_records)

                                for i in range(0, total, batch_size):
                                    batch = data_records[i:i + batch_size]

                                    status.text(f"İşleniyor: {i + 1}-{min(i + batch_size, total)}/{total}")

                                    batch_results = analyzer.process_batch_parallel(batch)
                                    results.extend(batch_results)

                                    progress.progress(min((i + batch_size) / total, 1.0))

                                # Sonuçları kaydet
                                st.session_state.results = results
                                status.success("✅ Analiz tamamlandı!")

                                # Özet göster
                                if results:
                                    st.divider()
                                    st.subheader("📊 Sonuç Özeti")

                                    # Basit istatistikler
                                    leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
                                    names = ['R.T. Erdoğan', 'Ö. Özel', 'M. Yavaş', 'E. İmamoğlu']

                                    cols = st.columns(4)
                                    for i, (leader, name) in enumerate(zip(leaders, names)):
                                        with cols[i]:
                                            mentions = sum(1 for r in results if r.get(f'IS_{leader}') == 1)

                                            if mentions > 0:
                                                # Sentiment dağılımı
                                                sentiments = [r.get(f'{leader}_SENTIMENT', 0)
                                                              for r in results if r.get(f'IS_{leader}') == 1]
                                                pos = sum(1 for s in sentiments if s == 1)
                                                neg = sum(1 for s in sentiments if s == -1)

                                                st.metric(
                                                    name,
                                                    mentions,
                                                    f"+{pos} -{neg}"
                                                )
                                            else:
                                                st.metric(name, 0)

                                    # İndirme
                                    st.divider()
                                    results_df = pd.DataFrame(results)
                                    csv = results_df.to_csv(index=False, encoding='utf-8')

                                    st.download_button(
                                        "💾 Sonuçları İndir (CSV)",
                                        csv,
                                        f"analiz_sonuclari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        "text/csv"
                                    )

                            except Exception as e:
                                st.error(f"❌ Analiz hatası: {str(e)}")

            except Exception as e:
                st.error(f"❌ Dosya okuma hatası: {str(e)}")

    # Alt bilgi
    st.divider()
    with st.expander("ℹ️ Sistem Bilgisi"):
        st.markdown("""
        **Liderler:**
        - **RTE**: Recep Tayyip Erdoğan (Cumhurbaşkanı)
        - **ÖÖ**: Özgür Özel (CHP Genel Başkanı)  
        - **MY**: Mansur Yavaş (Ankara Büyükşehir Belediye Başkanı)
        - **EI**: Ekrem İmamoğlu (İstanbul Büyükşehir Belediye Başkanı)

        **Değerler:**
        - İlgisiz liderler: **0** (eski: -1)
        - İlgisiz sentiment: **0** (eski: null)
        - Sentiment: **+1** Pozitif, **0** Nötr, **-1** Negatif
        """)

    # Footer - Baran Can Ercan imzası
    st.markdown("""
    <div class="footer">
        <p>
            Baran Can Ercan tarafından 
            <span class="footer-heart">❤️</span> 
            ile yapılmıştır
        </p>
        <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.5rem;">
            🇹🇷 Türk Siyasi Lider Analiz Sistemi V2.0 · 
            🤖 Google Gemini AI Destekli · 
            🔒 Güvenli & Hızlı
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🇹🇷 Siyasi Analiz Sistemi",
    page_icon="🇹🇷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2E86AB;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }

    .leader-metric {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
    }

    .success-alert {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .info-alert {
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        color: #0d47a1;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .stButton > button {
        width: 100%;
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: #1c5aa3;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Minimalist Ana Arayüz"""

    # Başlık
    st.markdown('<h1 class="main-title">🇹🇷 Siyasi Lider Analiz Sistemi</h1>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-alert">
        <strong>RTE</strong> · <strong>ÖÖ</strong> · <strong>MY</strong> · <strong>EI</strong> 
        için otomatik sınıflandırma ve sentiment analizi
    </div>
    """, unsafe_allow_html=True)

    # Ana işlem seçimi
    mode = st.radio(
        "İşlem Türü:",
        ["📝 Tek İçerik Testi", "📊 Toplu Analiz"],
        horizontal=True
    )

    # API Key girişi
    with st.expander("🔑 API Ayarları"):
        api_key = st.text_input(
            "Google API Key:",
            type="password",
            value="AIzaSyCklJ6T0IDgjuH7N8fbWl6AQtJuCEGbRA8"
        )

        col1, col2 = st.columns(2)
        with col1:
            batch_size = st.slider("Batch:", 1, 10, 3)
        with col2:
            rate_limit = st.slider("Rate (s):", 0.5, 3.0, 1.5, 0.1)

    st.divider()

    # Tek İçerik Testi
    if mode == "📝 Tek İçerik Testi":
        st.subheader("Tek İçerik Analizi")

        col1, col2 = st.columns([1, 3])
        with col1:
            account = st.text_input("Hesap:", "@test_user")
        with col2:
            st.empty()  # Spacing

        content = st.text_area(
            "İçerik:",
            "Mansur Yavaş'la harika bir proje yaptık! Desteklerinden dolayı teşekkürler.",
            height=100
        )

        if st.button("🚀 Analiz Et"):
            if not api_key or not content.strip():
                st.error("❌ API key ve içerik gerekli!")
            else:
                with st.spinner("Analiz yapılıyor..."):
                    try:
                        analyzer = PoliticalAnalysisSystem(
                            api_key,
                            batch_size=1,
                            max_workers=1,
                            rate_limit_sec=rate_limit
                        )

                        result = analyzer.process_single_content(account, content)

                        if result:
                            st.success("✅ Analiz tamamlandı!")

                            # Sonuçları kompakt göster
                            leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
                            names = ['R.T. Erdoğan', 'Ö. Özel', 'M. Yavaş', 'E. İmamoğlu']

                            cols = st.columns(4)
                            for i, (leader, name) in enumerate(zip(leaders, names)):
                                with cols[i]:
                                    is_relevant = result.get(f'IS_{leader}', 0)
                                    sentiment = result.get(f'{leader}_SENTIMENT', 0)

                                    if is_relevant == 1:
                                        if sentiment == 1:
                                            st.success(f"**{name}**\n😊 Pozitif")
                                        elif sentiment == -1:
                                            st.error(f"**{name}**\n😠 Negatif")
                                        else:
                                            st.info(f"**{name}**\n😐 Nötr")
                                    else:
                                        st.write(f"**{name}**\n➖ İlgisiz")
                        else:
                            st.error("❌ Analiz başarısız!")

                    except Exception as e:
                        st.error(f"❌ Hata: {str(e)}")

    # Toplu Analiz
    else:
        st.subheader("Toplu CSV Analizi")

        uploaded_file = st.file_uploader(
            "CSV Dosyası Yükle:",
            type=['csv'],
            help="ACCOUNT_NAME ve TEXT sütunları gerekli"
        )

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)

                # Hızlı önizleme
                st.info(f"📄 {len(df)} kayıt yüklendi")

                required_cols = ['ACCOUNT_NAME', 'TEXT']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"❌ Eksik sütunlar: {missing_cols}")
                else:
                    # Önizleme
                    with st.expander("👀 Veri Önizleme"):
                        st.dataframe(df.head(5), use_container_width=True)

                    # Analiz butonu
                    if st.button("🚀 Toplu Analizi Başlat"):
                        if not api_key:
                            st.error("❌ API key gerekli!")
                        else:
                            # Progress tracking
                            progress = st.progress(0)
                            status = st.empty()

                            try:
                                analyzer = PoliticalAnalysisSystem(
                                    api_key,
                                    batch_size=batch_size,
                                    max_workers=2,
                                    rate_limit_sec=rate_limit
                                )

                                # Veriyi işle
                                data_records = df.to_dict('records')
                                results = []
                                total = len(data_records)

                                for i in range(0, total, batch_size):
                                    batch = data_records[i:i + batch_size]

                                    status.text(f"İşleniyor: {i + 1}-{min(i + batch_size, total)}/{total}")

                                    batch_results = analyzer.process_batch_parallel(batch)
                                    results.extend(batch_results)

                                    progress.progress(min((i + batch_size) / total, 1.0))

                                # Sonuçları kaydet
                                st.session_state.results = results
                                status.success("✅ Analiz tamamlandı!")

                                # Özet göster
                                if results:
                                    st.divider()
                                    st.subheader("📊 Sonuç Özeti")

                                    # Basit istatistikler
                                    leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
                                    names = ['R.T. Erdoğan', 'Ö. Özel', 'M. Yavaş', 'E. İmamoğlu']

                                    cols = st.columns(4)
                                    for i, (leader, name) in enumerate(zip(leaders, names)):
                                        with cols[i]:
                                            mentions = sum(1 for r in results if r.get(f'IS_{leader}') == 1)

                                            if mentions > 0:
                                                # Sentiment dağılımı
                                                sentiments = [r.get(f'{leader}_SENTIMENT', 0)
                                                              for r in results if r.get(f'IS_{leader}') == 1]
                                                pos = sum(1 for s in sentiments if s == 1)
                                                neg = sum(1 for s in sentiments if s == -1)

                                                st.metric(
                                                    name,
                                                    mentions,
                                                    f"+{pos} -{neg}"
                                                )
                                            else:
                                                st.metric(name, 0)

                                    # İndirme
                                    st.divider()
                                    results_df = pd.DataFrame(results)
                                    csv = results_df.to_csv(index=False, encoding='utf-8')

                                    st.download_button(
                                        "💾 Sonuçları İndir (CSV)",
                                        csv,
                                        f"analiz_sonuclari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        "text/csv"
                                    )

                            except Exception as e:
                                st.error(f"❌ Analiz hatası: {str(e)}")

            except Exception as e:
                st.error(f"❌ Dosya okuma hatası: {str(e)}")

    # Alt bilgi
    st.divider()
    with st.expander("ℹ️ Sistem Bilgisi"):
        st.markdown("""
        **Liderler:**
        - **RTE**: Recep Tayyip Erdoğan (Cumhurbaşkanı)
        - **ÖÖ**: Özgür Özel (CHP Genel Başkanı)  
        - **MY**: Mansur Yavaş (Ankara Büyükşehir Belediye Başkanı)
        - **EI**: Ekrem İmamoğlu (İstanbul Büyükşehir Belediye Başkanı)

        **Değerler:**
        - İlgisiz liderler: **0** (eski: -1)
        - İlgisiz sentiment: **0** (eski: null)
        - Sentiment: **+1** Pozitif, **0** Nötr, **-1** Negatif
        """)


if __name__ == "__main__":
    main()