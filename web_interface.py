#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Web Arayüzü - Türk Siyasi Lider Analiz Sistemi V2.0
Excel ve CSV Destekli Versiyon

Kurulum:
pip install streamlit pandas plotly openpyxl

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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS Tasarım
st.markdown("""
<style>
    /* Ana sayfa stil */
    .main > div {
        padding-top: 2rem;
    }

    /* Başlık */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .main-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        font-weight: 400;
    }

    /* Kartlar */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }

    .leader-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        text-align: center;
    }

    .leader-card.relevant {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-color: #3b82f6;
    }

    .leader-card.positive {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-color: #22c55e;
    }

    .leader-card.negative {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-color: #ef4444;
    }

    /* Butonlar */
    .stButton > button {
        width: 100%;
        height: 3rem;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }

    /* Form elemanları */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 1rem;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Metrikler */
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
        min-width: 120px;
    }

    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }

    /* Alert'ler */
    .success-alert {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border: 1px solid #22c55e;
        color: #15803d;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .info-alert {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #3b82f6;
        color: #1d4ed8;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .error-alert {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        color: #dc2626;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    /* File type badge */
    .file-type-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }

    .file-type-csv {
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #22c55e;
    }

    .file-type-excel {
        background: #dbeafe;
        color: #1d4ed8;
        border: 1px solid #3b82f6;
    }

    /* Download buttons */
    .download-buttons {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }

    .download-buttons .stDownloadButton > button {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .download-csv {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
    }

    .download-excel {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }

    .download-json {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 6px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* File uploader */
    .stFileUploader > div > button {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        background: #f8fafc;
        color: #374151;
        font-weight: 600;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 1rem;
        margin-top: 4rem;
        border-top: 1px solid #e5e7eb;
        background: #f8fafc;
    }

    .footer-text {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .footer-heart {
        color: #ef4444;
        animation: heartbeat 2s ease-in-out infinite;
    }

    @keyframes heartbeat {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    /* Responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }

        .card {
            padding: 1rem;
        }

        .metric-container {
            flex-direction: column;
            gap: 1rem;
        }

        .download-buttons {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)


def get_api_key():
    """API key'i environment veya secrets'tan al"""
    # Önce environment variable'ı kontrol et
    env_key = os.getenv('GOOGLE_API_KEY', '')
    if env_key:
        return env_key

    # Sonra Streamlit secrets'ı kontrol et (güvenli şekilde)
    try:
        if hasattr(st, 'secrets') and st.secrets and 'GOOGLE_API_KEY' in st.secrets:
            return st.secrets['GOOGLE_API_KEY']
    except Exception:
        # Secrets bulunamadı, sorun değil
        pass

    # Son olarak .env dosyasını kontrol et
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv('GOOGLE_API_KEY', '')
    except ImportError:
        # python-dotenv yüklü değil
        pass

    # Hiçbiri bulunamadı, boş string döndür
    return ''


def read_file(uploaded_file):
    """
    CSV veya Excel dosyasını oku

    Args:
        uploaded_file: Streamlit file uploader nesnesi

    Returns:
        pandas DataFrame
    """
    try:
        # Dosya türünü belirle
        file_extension = uploaded_file.name.lower().split('.')[-1]

        if file_extension == 'csv':
            # CSV dosyası
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        elif file_extension in ['xlsx', 'xls']:
            # Excel dosyası
            df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_extension}")

        # Sütun isimlerini temizle
        df.columns = df.columns.str.strip()

        # Boş satırları temizle
        df = df.dropna(subset=['TEXT'])
        df = df[df['TEXT'].str.strip() != '']

        return df, file_extension

    except Exception as e:
        raise Exception(f"Dosya okuma hatası: {str(e)}")


def create_excel_file(df):
    """
    DataFrame'i Excel formatında in-memory dosya olarak oluştur

    Args:
        df: pandas DataFrame

    Returns:
        bytes: Excel dosyası bytes
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl', mode='wb') as writer:
        # Ana sonuçlar sayfası
        df.to_excel(writer, sheet_name='Analiz Sonuçları', index=False)

        # Özet istatistikler sayfası
        leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
        leader_names = ['R.T. Erdoğan', 'Ö. Özel', 'M. Yavaş', 'E. İmamoğlu']

        summary_data = []
        for leader_code, leader_name in zip(leaders, leader_names):
            mentions = len(df[df[f'IS_{leader_code}'] == 1])

            if mentions > 0:
                sentiments = df[df[f'IS_{leader_code}'] == 1][f'{leader_code}_SENTIMENT']
                positive = len(sentiments[sentiments == 1])
                negative = len(sentiments[sentiments == -1])
                neutral = len(sentiments[sentiments == 0])

                summary_data.append({
                    'Lider': leader_name,
                    'Kod': leader_code,
                    'Toplam Bahsetme': mentions,
                    'Pozitif': positive,
                    'Nötr': neutral,
                    'Negatif': negative,
                    'Pozitif %': round((positive / mentions) * 100, 1) if mentions > 0 else 0,
                    'Negatif %': round((negative / mentions) * 100, 1) if mentions > 0 else 0
                })
            else:
                summary_data.append({
                    'Lider': leader_name,
                    'Kod': leader_code,
                    'Toplam Bahsetme': 0,
                    'Pozitif': 0,
                    'Nötr': 0,
                    'Negatif': 0,
                    'Pozitif %': 0,
                    'Negatif %': 0
                })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Özet İstatistikler', index=False)

        # Metadata sayfası
        metadata = {
            'Analiz Tarihi': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Toplam Kayıt': [len(df)],
            'Sistem Versiyonu': ['2.0'],
            'AI Model': ['Google Gemini 1.5 Flash']
        }
        metadata_df = pd.DataFrame(metadata)
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

    return output.getvalue()


def render_leader_result(leader_code, leader_name, result):
    """Lider sonucunu kart olarak render et"""
    is_relevant = result.get(f'IS_{leader_code}', 0)
    sentiment = result.get(f'{leader_code}_SENTIMENT', 0)

    # Kart class'ını belirle
    card_class = "leader-card"
    icon = "➖"
    status = "İlgisiz"

    if is_relevant == 1:
        card_class += " relevant"
        if sentiment == 1:
            card_class += " positive"
            icon = "😊"
            status = "Pozitif"
        elif sentiment == -1:
            card_class += " negative"
            icon = "😠"
            status = "Negatif"
        else:
            icon = "😐"
            status = "Nötr"

    st.markdown(f"""
    <div class="{card_class}">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">{leader_name}</div>
        <div style="color: #6b7280; font-size: 0.9rem;">{status}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Ana uygulama"""

    # Başlık
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🇹🇷 Siyasi Lider Analiz Sistemi</h1>
        <p class="main-subtitle">AI destekli otomatik sınıflandırma ve sentiment analizi</p>
        <p style="color: #6b7280; font-size: 0.9rem; margin-top: 0.5rem;">
            📄 CSV ve 📊 Excel desteği ile
        </p>
    </div>
    """, unsafe_allow_html=True)

    # API Key kontrolü
    api_key = get_api_key()

    if not api_key:
        st.markdown("""
        <div class="error-alert">
            <strong>⚠️ API Anahtarı Gerekli</strong><br>
            Lütfen Google Gemini API anahtarınızı girin veya environment/secrets'ta ayarlayın.
        </div>
        """, unsafe_allow_html=True)

        api_key = st.text_input(
            "Google API Key:",
            type="password",
            placeholder="AIzaSyAWOHLAA4dj9lNfNGB8oScs-c2aHrjFnsE"
        )

        if not api_key:
            st.stop()

    # Lider bilgileri
    leaders_info = {
        'RTE': 'Recep Tayyip Erdoğan',
        'ÖÖ': 'Özgür Özel',
        'MY': 'Mansur Yavaş',
        'EI': 'Ekrem İmamoğlu'
    }

    # Ana tab'lar
    tab1, tab2 = st.tabs(["🧪 Tek İçerik Testi", "📊 Toplu Analiz"])

    # Tab 1: Tek İçerik Testi
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("### 🧪 Tek İçerik Analizi")
        st.markdown("Sosyal medya içeriğinizi test edin ve anlık sonuç alın.")

        col1, col2 = st.columns([1, 3])
        with col1:
            test_account = st.text_input(
                "Hesap Adı:",
                value="@test_user",
                placeholder="@ornek_hesap"
            )

        test_text = st.text_area(
            "İçerik Metni:",
            value="Mansur Yavaş'la harika bir proje yaptık! Desteklerinden dolayı teşekkürler.",
            height=120,
            placeholder="Analiz edilecek sosyal medya içeriğini buraya yazın..."
        )

        # Analiz butonu
        if st.button("🚀 Analiz Et", key="single_analyze"):
            if not test_text.strip():
                st.error("❌ Lütfen analiz edilecek içeriği girin!")
            else:
                with st.spinner("🔄 Analiz yapılıyor..."):
                    try:
                        analyzer = PoliticalAnalysisSystem(
                            api_key,
                            batch_size=1,
                            max_workers=1,
                            rate_limit_sec=1.5
                        )

                        result = analyzer.process_single_content(test_account, test_text)

                        if result:
                            st.markdown("""
                            <div class="success-alert">
                                <strong>✅ Analiz tamamlandı!</strong>
                            </div>
                            """, unsafe_allow_html=True)

                            # Sonuçları göster
                            st.markdown("#### 📊 Analiz Sonuçları")

                            cols = st.columns(4)
                            for i, (leader_code, leader_name) in enumerate(leaders_info.items()):
                                with cols[i]:
                                    render_leader_result(leader_code, leader_name, result)
                        else:
                            st.error("❌ Analiz başarısız! Lütfen tekrar deneyin.")

                    except Exception as e:
                        st.error(f"❌ Hata oluştu: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Toplu Analiz
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("### 📊 Toplu Dosya Analizi")
        st.markdown("CSV veya Excel dosyalarınızı yükleyip toplu analiz yapın.")

        # Dosya yükleme
        uploaded_file = st.file_uploader(
            "Dosya Seçin:",
            type=['csv', 'xlsx', 'xls'],
            help="ACCOUNT_NAME ve TEXT sütunları içeren CSV veya Excel dosyası"
        )

        if uploaded_file is not None:
            try:
                df, file_type = read_file(uploaded_file)

                # Dosya türü badge'i
                badge_class = "file-type-csv" if file_type == 'csv' else "file-type-excel"
                badge_text = "CSV" if file_type == 'csv' else "Excel"
                badge_icon = "📄" if file_type == 'csv' else "📊"

                st.markdown(f"""
                <div class="info-alert">
                    <strong>{badge_icon} Dosya Yüklendi:</strong> {len(df):,} kayıt bulundu
                    <span class="file-type-badge {badge_class}">{badge_text}</span>
                </div>
                """, unsafe_allow_html=True)

                # Sütun kontrolü
                required_cols = ['ACCOUNT_NAME', 'TEXT']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.markdown(f"""
                    <div class="error-alert">
                        <strong>❌ Eksik Sütunlar:</strong> {', '.join(missing_cols)}<br>
                        <small>Dosyanızda şu sütunlar bulunmalı: ACCOUNT_NAME, TEXT</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Veri önizleme
                    with st.expander("👀 Veri Önizleme"):
                        st.dataframe(df.head(10), use_container_width=True)

                    # Ayarlar
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        batch_size = st.selectbox("Batch Boyutu:", [1, 3, 5, 10], index=1)
                    with col2:
                        max_workers = st.selectbox("Paralel İşlem:", [1, 2, 3], index=1)
                    with col3:
                        rate_limit = st.selectbox("Rate Limit (s):", [1.0, 1.5, 2.0, 3.0], index=1)

                    # Analiz butonu
                    if st.button("🚀 Toplu Analizi Başlat", key="batch_analyze"):
                        # Progress tracking
                        progress_container = st.container()

                        with progress_container:
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            try:
                                analyzer = PoliticalAnalysisSystem(
                                    api_key,
                                    batch_size=batch_size,
                                    max_workers=max_workers,
                                    rate_limit_sec=rate_limit
                                )

                                data_records = df.to_dict('records')
                                results = []
                                total_items = len(data_records)

                                # Batch'ler halinde işle
                                for i in range(0, total_items, batch_size):
                                    batch = data_records[i:i + batch_size]
                                    current_end = min(i + batch_size, total_items)

                                    status_text.text(f"İşleniyor: {i + 1}-{current_end}/{total_items}")

                                    batch_results = analyzer.process_batch_parallel(batch)
                                    results.extend(batch_results)

                                    progress = current_end / total_items
                                    progress_bar.progress(progress)

                                    time.sleep(0.1)  # UI güncelleme için

                                # Sonuçları session state'e kaydet
                                st.session_state.analysis_results = results
                                st.session_state.analysis_df = pd.DataFrame(results)

                                status_text.success("✅ Analiz tamamlandı!")
                                time.sleep(1)

                                # Sonuç sayfasına yönlendir
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Analiz hatası: {str(e)}")

            except Exception as e:
                st.error(f"❌ Dosya okuma hatası: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Sonuçları göster (eğer varsa)
        if 'analysis_results' in st.session_state:
            results = st.session_state.analysis_results

            if results:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### 📈 Analiz Sonuçları")

                # Özet metrikler
                total_processed = len(results)

                # Lider istatistikleri
                leader_stats = {}
                for leader_code in leaders_info.keys():
                    mentions = sum(1 for r in results if r.get(f'IS_{leader_code}') == 1)

                    sentiments = [r.get(f'{leader_code}_SENTIMENT', 0)
                                  for r in results if r.get(f'IS_{leader_code}') == 1]

                    positive = sum(1 for s in sentiments if s == 1)
                    negative = sum(1 for s in sentiments if s == -1)
                    neutral = sum(1 for s in sentiments if s == 0)

                    leader_stats[leader_code] = {
                        'name': leaders_info[leader_code],
                        'mentions': mentions,
                        'positive': positive,
                        'negative': negative,
                        'neutral': neutral
                    }

                # Metrik kartları
                cols = st.columns(4)
                for i, (leader_code, stats) in enumerate(leader_stats.items()):
                    with cols[i]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-number">{stats['mentions']}</div>
                            <div class="metric-label">{stats['name']}</div>
                            <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.25rem;">
                                +{stats['positive']} -{stats['negative']} ={stats['neutral']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Görselleştirme
                if any(stats['mentions'] > 0 for stats in leader_stats.values()):
                    st.markdown("#### 📊 Görsel Analiz")

                    # Bahsetme grafiği
                    mentions_data = [stats['mentions'] for stats in leader_stats.values()]
                    leader_names = [stats['name'] for stats in leader_stats.values()]

                    fig = px.bar(
                        x=leader_names,
                        y=mentions_data,
                        title="Lider Bahsetme Sayıları",
                        color=mentions_data,
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(
                        title_font_size=16,
                        xaxis_title="Liderler",
                        yaxis_title="Bahsetme Sayısı",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # İndirme bölümü
                st.markdown("#### 💾 Sonuçları İndir")
                st.markdown("Analiz sonuçlarınızı farklı formatlarda indirebilirsiniz:")

                results_df = st.session_state.analysis_df

                # Dosya adı için timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                # CSV data
                csv_data = results_df.to_csv(index=False, encoding='utf-8')

                # Excel data
                excel_data = create_excel_file(results_df)

                # JSON data
                json_data = json.dumps(results, ensure_ascii=False, indent=2)

                # İndirme butonları
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.download_button(
                        "📄 CSV İndir",
                        csv_data,
                        f"siyasi_analiz_{timestamp}.csv",
                        "text/csv",
                        use_container_width=True,
                        help="Virgül ile ayrılmış değer formatı"
                    )

                with col2:
                    st.download_button(
                        "📊 Excel İndir",
                        excel_data,
                        f"siyasi_analiz_{timestamp}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        help="Excel formatı - 3 sayfa: Sonuçlar, Özet, Metadata"
                    )

                with col3:
                    st.download_button(
                        "📋 JSON İndir",
                        json_data,
                        f"siyasi_analiz_{timestamp}.json",
                        "application/json",
                        use_container_width=True,
                        help="JSON formatı - programatik kullanım için"
                    )

                # İndirme bilgilendirme
                st.markdown("""
                <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin-top: 1rem;">
                    <strong>📋 Dosya Format Bilgileri:</strong><br>
                    • <strong>CSV:</strong> Temel tablo formatı, Excel'de açılabilir<br>
                    • <strong>Excel:</strong> Çoklu sayfa - Sonuçlar + Özet istatistikler + Metadata<br>
                    • <strong>JSON:</strong> Programlama ve API entegrasyonu için
                </div>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

    # Kullanım rehberi
    with st.expander("📚 Kullanım Rehberi", expanded=False):
        st.markdown("""
        ### 📁 Dosya Formatları

        **Desteklenen Dosya Türleri:**
        - 📄 **CSV** (Comma Separated Values)
        - 📊 **Excel** (.xlsx, .xls)

        **Gerekli Sütunlar:**
        - `ACCOUNT_NAME`: Sosyal medya hesap adı (@username)
        - `TEXT`: Analiz edilecek içerik metni

        ### 📊 Çıktı Formatları

        **CSV İndirme:**
        - Basit tablo formatı
        - Tüm spreadsheet uygulamalarında açılabilir
        - Programatik işleme uygun

        **Excel İndirme:**
        - **Sayfa 1:** Detaylı analiz sonuçları
        - **Sayfa 2:** Özet istatistikler ve yüzdeler
        - **Sayfa 3:** Metadata (tarih, versiyon, model bilgisi)
        - Profesyonel raporlama için ideal

        **JSON İndirme:**
        - API entegrasyonu için
        - Programlama dillerinde kolay işleme
        - Veri yapısını korur

        ### 🎯 Lider Kodları

        - **RTE**: Recep Tayyip Erdoğan (Cumhurbaşkanı)
        - **ÖÖ**: Özgür Özel (CHP Genel Başkanı)
        - **MY**: Mansur Yavaş (Ankara Büyükşehir Belediye Başkanı)
        - **EI**: Ekrem İmamoğlu (İstanbul Büyükşehir Belediye Başkanı)

        ### 📈 Değer Anlamları

        **Sınıflandırma (IS_XXX):**
        - `1`: İçerik bu liderle ilgili
        - `0`: İçerik bu liderle ilgisiz

        **Sentiment (XXX_SENTIMENT):**
        - `1`: Pozitif (övgü, destek)
        - `0`: Nötr (tarafsız bahsetme)
        - `-1`: Negatif (eleştiri, olumsuz)
        - `null`: Lider ilgili değilse boş

        ### ⚙️ Performans Ayarları

        - **Batch Boyutu**: Aynı anda işlenecek kayıt sayısı (1-10)
        - **Paralel İşlem**: Eşzamanlı thread sayısı (1-3)
        - **Rate Limit**: API çağrıları arası bekleme süresi (1-3 saniye)

        ### 💡 İpuçları

        1. **Küçük testler**: İlk önce 10-50 kayıtlık küçük dosyalarla test edin
        2. **Excel formatı**: Profesyonel raporlar için Excel indirmeyi tercih edin
        3. **Batch ayarları**: Büyük dosyalar için batch boyutunu küçük tutun
        4. **API limitleri**: Rate limit'i düşük tutarak hata riskini azaltın
        """)

    # Footer
    st.markdown("""
    <div class="footer">
        <div class="footer-text">
            Baran Can Ercan tarafından <span class="footer-heart">❤️</span> ile yapılmıştır
        </div>
        <div style="font-size: 0.8rem; color: #9ca3af;">
            🇹🇷 Türk Siyasi Lider Analiz Sistemi V2.0 · Google Gemini AI Destekli
        </div>
        <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;">
            📄 CSV & 📊 Excel Desteği · 🚀 Yüksek Performans · 🔒 Güvenli
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()