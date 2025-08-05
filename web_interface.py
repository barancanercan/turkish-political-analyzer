#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Güvenli Web Arayüzü - Türk Siyasi Lider Analiz Sistemi V2.0
Minimalist tasarım, dark mode uyumlu, güvenli API yönetimi

Kurulum:
pip install streamlit pandas plotly openpyxl python-dotenv

Çalıştırma:
streamlit run web_interface.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import io
import time
import os
from datetime import datetime
from pathlib import Path

# Güvenli API key yönetimi
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Ana sistem sınıfını import et
try:
    from political_analyzer import PoliticalAnalysisSystem
except ImportError:
    st.error("❌ political_analyzer.py dosyası bulunamadı!")
    st.stop()

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🇹🇷 Siyasi Analiz",
    page_icon="🇹🇷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern minimalist CSS - Light theme
st.markdown("""
<style>
    /* Ana tema - Beyaz tema */
    .stApp {
        background: #ffffff;
        color: #1f2937;
    }

    /* Başlık */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 2rem;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }

    .developer-credit {
        color: #9ca3af;
        font-size: 0.9rem;
        font-style: italic;
        font-weight: 300;
    }

    /* Kartlar */
    .card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* Lider sonuç kartları */
    .leader-result {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .leader-result.neutral {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #64748b;
    }

    .leader-result.positive {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #22c55e;
    }

    .leader-result.negative {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }

    .leader-result.relevant {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #3b82f6;
    }

    .leader-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .leader-name {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }

    .leader-status {
        font-size: 0.8rem;
        opacity: 0.8;
    }

    /* Butonlar - Dark mode uyumlu */
    .stButton > button {
        width: 100%;
        height: 2.8rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Form elemanları */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        background: #ffffff;
        color: #1f2937;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }

    /* Form label'ları siyah yap */
    .stTextArea > label,
    .stTextInput > label,
    .stSelectbox > label,
    .stFileUploader > label,
    label[data-testid="stWidgetLabel"] {
        color: #1f2937 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }

    /* Form label içindeki div'ler */
    .stTextArea > label > div,
    .stTextInput > label > div,
    .stSelectbox > label > div,
    .stFileUploader > label > div {
        color: #1f2937 !important;
    }

    /* Metrikler */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e5e7eb;
    }

    .metric-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }

    .metric-detail {
        font-size: 0.7rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }

    /* Alertler */
    .alert {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }

    .alert-success {
        background: rgba(34, 197, 94, 0.1);
        border-left-color: #22c55e;
        color: #1f2937;
    }

    .alert-info {
        background: rgba(59, 130, 246, 0.1);
        border-left-color: #3b82f6;
        color: #1f2937;
    }

    .alert-error {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
        color: #1f2937;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* File uploader */
    [data-testid="stFileUploader"] > div > button {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        background: #f9fafb;
        color: #374151;
        padding: 2rem;
    }

    /* Radio buttons - Basit ve temiz yaklaşım */
    .stRadio {
        display: flex;
        justify-content: center;
        margin: 1.5rem 0;
    }

    .stRadio > div {
        display: flex !important;
        justify-content: center !important;
        gap: 1rem !important;
        padding: 1rem !important;
        background: #f8fafc !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        flex-direction: row !important;
    }

    .stRadio label {
        background: #ffffff !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        color: #1f2937 !important;
        min-width: 140px !important;
        text-align: center !important;
        font-size: 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stRadio label:hover {
        border-color: #667eea !important;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-1px) !important;
    }

    .stRadio input[type="radio"]:checked + label,
    .stRadio label[data-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
    }

    .stRadio input[type="radio"] {
        display: none !important;
    }

    /* JavaScript ile temizlenecek elementler için işaretleme */
    .stRadio label:empty,
    .stRadio label:not(:has(div:not(:empty))):not(:has(span:not(:empty))):not(:has(input)) {
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -9999px !important;
    }
</style>

<script>
// DOM temizliği için JavaScript
function cleanupEmptyElements() {
    // Radio group içindeki boş label'ları bul ve kaldır
    const radioGroups = document.querySelectorAll('.stRadio > div');
    radioGroups.forEach(group => {
        const labels = group.querySelectorAll('label');
        labels.forEach(label => {
            // Boş label'ları kontrol et
            const hasContent = label.querySelector('div:not(:empty)') || 
                             label.querySelector('span:not(:empty)') || 
                             label.querySelector('input') ||
                             label.textContent.trim().length > 0;

            if (!hasContent) {
                label.style.display = 'none';
                label.style.visibility = 'hidden';
                label.style.position = 'absolute';
                label.style.left = '-9999px';
                label.style.width = '0';
                label.style.height = '0';
                label.style.margin = '0';
                label.style.padding = '0';
                label.remove(); // Tamamen kaldır
            }
        });
    });

    // Boş tooltip'leri temizle
    const tooltipLabels = document.querySelectorAll('label.st-emotion-cache-1whk732');
    tooltipLabels.forEach(label => {
        const hasRealContent = label.querySelector('input') || 
                              label.querySelector('span:not(:empty)') ||
                              (label.textContent && label.textContent.trim().length > 0);

        if (!hasRealContent) {
            label.remove();
        }
    });
}

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', cleanupEmptyElements);

// Streamlit güncellemelerinden sonra çalıştır
const observer = new MutationObserver(cleanupEmptyElements);
observer.observe(document.body, { childList: true, subtree: true });

// Periyodik temizlik (son çare)
setInterval(cleanupEmptyElements, 1000);
</script>

<style>

    /* Text içinde ki div'ler için */
    .stRadio label div {
        color: inherit !important;
        font-weight: inherit !important;
        font-size: inherit !important;
    }

    /* Boş elementleri gizle - En agresif yaklaşım */
    label:empty,
    div:empty:not([class*="stProgress"]):not([class*="stSpinner"]):not([data-testid*="stEmpty"]) {
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
        position: absolute !important;
        left: -9999px !important;
    }

    /* Radio group içindeki boş label'lar - çok spesifik */
    .stRadio > div > label:empty,
    .stRadio > div > label:not(:has(*)),
    .stRadio > div > label:not(:has(div:not(:empty))):not(:has(span:not(:empty))):not(:has(input)),
    .stRadio label:first-child:empty,
    .stRadio label:first-child:not(:has(input)):not(:has(span)):not(:has(div:not(:empty))) {
        display: none !important;
        visibility: hidden !important;
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
        z-index: -1000 !important;
    }

    /* Streamlit radio container temizliği */
    .stRadio > div > *:empty {
        display: none !important;
    }

    /* Streamlit'in oluşturduğu boş label'lar - daha spesifik */
    .st-emotion-cache-1whk732:empty,
    label.st-emotion-cache-1whk732:empty,
    label.st-emotion-cache-1whk732:not(:has(input)):not(:has(span:not(:empty))):not(:has(div:not(.stTooltipIcon))) {
        display: none !important;
        visibility: hidden !important;
        position: absolute !important;
        left: -9999px !important;
    }

    /* Sadece tooltip icon'lu boş label'lar - en spesifik */
    label:has(.stTooltipIcon):not(:has(input)):not(:has(span:not(:empty))):not(:has(div:not(.stTooltipIcon))):not(:has(div:not(.stTooltipHoverTarget))) {
        display: none !important;
        visibility: hidden !important;
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    /* Tooltip icon'un kendisini gizle */
    .stTooltipIcon:only-child,
    .stTooltipHoverTarget:only-child {
        display: none !important;
    }

    /* Boş tooltip container'ları */
    label:has(.stTooltipIcon):not(:has(:not(.stTooltipIcon):not(.stTooltipHoverTarget))) {
        display: none !important;
    }

    /* Radio group temizliği */
    .stRadio label:empty,
    .stRadio > div > label:empty,
    .stRadio > div > label:not(:has(div:not(:empty))) {
        display: none !important;
    }

    /* Boş card'ları temizle */
    .card:empty,
    div.card:empty {
        display: none !important;
        height: 0 !important;
    }

    /* Expander */
    .streamlit-expander {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background: #f8fafc;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid #e5e7eb;
        background: #f8fafc;
        color: #6b7280;
        font-size: 0.9rem;
    }

    .footer-heart {
        color: #ef4444;
        animation: heartbeat 2s ease-in-out infinite;
    }

    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    /* Responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }

        .card {
            padding: 1rem;
        }

        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
""", unsafe_allow_html=True)


def get_secure_api_key():
    """Güvenli API key yönetimi"""
    # 1. Environment variable
    env_key = os.getenv('GOOGLE_API_KEY')
    if env_key and env_key.strip():
        return env_key.strip()

    # 2. Streamlit secrets
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            return st.secrets['GOOGLE_API_KEY']
    except:
        pass

    # 3. .env dosyası
    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        return line.split('=', 1)[1].strip().strip('"\'')
        except:
            pass

    return None


def read_file(uploaded_file):
    """CSV/Excel dosyası oku"""
    try:
        file_ext = uploaded_file.name.lower().split('.')[-1]

        if file_ext == 'csv':
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Desteklenmeyen format: {file_ext}")

        # Temizlik
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['TEXT'])
        df = df[df['TEXT'].str.strip() != '']

        return df, file_ext
    except Exception as e:
        raise Exception(f"Dosya okuma hatası: {str(e)}")


def create_excel_output(df):
    """Excel çıktısı oluştur"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Ana sonuçlar
        df.to_excel(writer, sheet_name='Sonuçlar', index=False)

        # Özet istatistikler
        leaders = ['RTE', 'ÖÖ', 'MY', 'EI']
        names = ['R.T. Erdoğan', 'Ö. Özel', 'M. Yavaş', 'E. İmamoğlu']

        summary = []
        for leader, name in zip(leaders, names):
            mentions = len(df[df[f'IS_{leader}'] == 1])
            if mentions > 0:
                sentiments = df[df[f'IS_{leader}'] == 1][f'{leader}_SENTIMENT']
                pos = len(sentiments[sentiments == 1])
                neg = len(sentiments[sentiments == -1])
                neu = len(sentiments[sentiments == 0])

                summary.append({
                    'Lider': name,
                    'Bahsetme': mentions,
                    'Pozitif': pos,
                    'Nötr': neu,
                    'Negatif': neg,
                    'Pozitif %': round(pos / mentions * 100, 1) if mentions > 0 else 0
                })

        if summary:
            pd.DataFrame(summary).to_excel(writer, sheet_name='Özet', index=False)

    return output.getvalue()


def render_leader_card(leader_code, leader_name, result):
    """Lider sonuç kartı"""
    is_relevant = result.get(f'IS_{leader_code}', 0)
    sentiment = result.get(f'{leader_code}_SENTIMENT', 0)

    # Durum belirleme
    if is_relevant == 1:
        if sentiment == 1:
            css_class = "positive"
            icon = "😊"
            status = "Pozitif"
        elif sentiment == -1:
            css_class = "negative"
            icon = "😠"
            status = "Negatif"
        else:
            css_class = "relevant"
            icon = "😐"
            status = "Nötr"
    else:
        css_class = "neutral"
        icon = "➖"
        status = "İlgisiz"

    st.markdown(f"""
    <div class="leader-result {css_class}">
        <div class="leader-icon">{icon}</div>
        <div class="leader-name">{leader_name}</div>
        <div class="leader-status">{status}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Ana uygulama"""

    # Başlık
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🇹🇷 Siyasi Analiz Sistemi</h1>
        <p class="subtitle">AI destekli otomatik lider sınıflandırma ve sentiment analizi</p>
        <p class="developer-credit">Baran Can Ercan tarafından geliştirilmiştir.</p>
    </div>
    """, unsafe_allow_html=True)

    # Güvenli API key yönetimi
    api_key = get_secure_api_key()

    if not api_key:
        st.markdown("""
        <div class="alert alert-error">
            <strong>🔑 API Anahtarı Gerekli</strong><br>
            Lütfen Google Gemini API anahtarınızı .env dosyasına veya environment variables'a ekleyin.
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔧 API Key Nasıl Ayarlanır?"):
            st.code('''
# .env dosyası oluşturun ve şunu ekleyin:
GOOGLE_API_KEY=your_api_key_here

# Veya environment variable olarak:
export GOOGLE_API_KEY="your_api_key_here"
            ''', language='bash')

        # Geçici API key girişi
        temp_key = st.text_input("Geçici API Key:", type="password",
                                 help="Güvenlik için .env dosyası kullanımı önerilir")
        if temp_key:
            api_key = temp_key

    if not api_key:
        st.stop()

    # Lider tanımları
    leaders = {
        'RTE': 'R.T. Erdoğan',
        'ÖÖ': 'Ö. Özel',
        'MY': 'M. Yavaş',
        'EI': 'E. İmamoğlu'
    }

    # İşlem modu seçimi
    st.markdown("### İşlem Türü Seçin:")
    mode = st.radio(
        "",
        ["🧪 Tek İçerik", "📊 Toplu Analiz"],
        horizontal=True,
        help="Tek içerik testi veya CSV/Excel dosyası analizi",
        key="mode_selection"
    )

    st.divider()

    # Tek İçerik Analizi
    if mode == "🧪 Tek İçerik":
        st.markdown('<div class="card">', unsafe_allow_html=True)

        content = st.text_area(
            "İçerik:",
            "Mansur Yavaş'la harika bir proje yaptık! Teşekkürler.",
            height=120,
            help="Analiz edilecek sosyal medya içeriği"
        )

        # Opsiyonel hesap adı
        with st.expander("⚙️ Gelişmiş Ayarlar (Opsiyonel)"):
            account = st.text_input("Hesap Adı:", placeholder="@ornek_hesap",
                                    help="Opsiyonel - varsayılan: @anonymous")

        if st.button("🚀 Analiz Et"):
            if not content.strip():
                st.error("❌ İçerik gerekli!")
            else:
                with st.spinner("Analiz yapılıyor..."):
                    try:
                        analyzer = PoliticalAnalysisSystem(
                            api_key,
                            batch_size=1,
                            max_workers=1,
                            rate_limit_sec=1.5
                        )

                        result = analyzer.process_single_content(
                            account.strip() if account.strip() else "@anonymous",
                            content
                        )

                        if result:
                            st.markdown("""
                            <div class="alert alert-success">
                                ✅ <strong>Analiz tamamlandı!</strong>
                            </div>
                            """, unsafe_allow_html=True)

                            # Sonuçları göster
                            cols = st.columns(4)
                            for i, (code, name) in enumerate(leaders.items()):
                                with cols[i]:
                                    render_leader_card(code, name, result)
                        else:
                            st.error("❌ Analiz başarısız!")

                    except Exception as e:
                        st.error(f"❌ Hata: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Toplu Analiz
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "📁 Dosya Yükle:",
            type=['csv', 'xlsx', 'xls'],
            help="ACCOUNT_NAME ve TEXT sütunları gerekli"
        )

        if uploaded_file:
            try:
                df, file_type = read_file(uploaded_file)

                st.markdown(f"""
                <div class="alert alert-info">
                    📄 <strong>{len(df):,} kayıt yüklendi</strong>
                    <span style="float: right;">Format: {file_type.upper()}</span>
                </div>
                """, unsafe_allow_html=True)

                # Sütun kontrolü
                required = ['ACCOUNT_NAME', 'TEXT']
                missing = [col for col in required if col not in df.columns]

                if missing:
                    st.error(f"❌ Eksik sütunlar: {', '.join(missing)}")
                else:
                    # Önizleme
                    with st.expander("👀 Veri Önizleme"):
                        st.dataframe(df.head(5), use_container_width=True)

                    # Ayarlar
                    col1, col2 = st.columns(2)
                    with col1:
                        batch_size = st.selectbox("Batch Boyutu:", [1, 3, 5], index=1)
                    with col2:
                        rate_limit = st.selectbox("Hız Limiti (s):", [1.0, 1.5, 2.0], index=1)

                    # Analiz butonu
                    if st.button("🚀 Analizi Başlat"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        try:
                            analyzer = PoliticalAnalysisSystem(
                                api_key,
                                batch_size=batch_size,
                                max_workers=2,
                                rate_limit_sec=rate_limit
                            )

                            data_records = df.to_dict('records')
                            results = []
                            total = len(data_records)

                            # Batch işleme
                            for i in range(0, total, batch_size):
                                batch = data_records[i:i + batch_size]
                                current_end = min(i + batch_size, total)

                                status_text.text(f"İşleniyor: {i + 1}-{current_end}/{total}")

                                batch_results = analyzer.process_batch_parallel(batch)
                                results.extend(batch_results)

                                progress_bar.progress(current_end / total)

                            # Sonuçları kaydet
                            st.session_state.results = results
                            st.session_state.results_df = pd.DataFrame(results)

                            status_text.success("✅ Analiz tamamlandı!")
                            time.sleep(1)
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Analiz hatası: {str(e)}")

            except Exception as e:
                st.error(f"❌ Dosya hatası: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Sonuçları göster
        if 'results' in st.session_state and st.session_state.results:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📊 Sonuçlar")

            results = st.session_state.results

            # Özet metrikler
            st.markdown('<div class="metric-grid">', unsafe_allow_html=True)

            for code, name in leaders.items():
                mentions = sum(1 for r in results if r.get(f'IS_{code}') == 1)

                if mentions > 0:
                    sentiments = [r.get(f'{code}_SENTIMENT', 0)
                                  for r in results if r.get(f'IS_{code}') == 1]
                    pos = sum(1 for s in sentiments if s == 1)
                    neg = sum(1 for s in sentiments if s == -1)

                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-number">{mentions}</div>
                        <div class="metric-label">{name}</div>
                        <div class="metric-detail">+{pos} -{neg}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-number">0</div>
                        <div class="metric-label">{name}</div>
                        <div class="metric-detail">Bahsetme yok</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Görsel analiz
            mention_counts = [sum(1 for r in results if r.get(f'IS_{code}') == 1)
                              for code in leaders.keys()]

            if any(count > 0 for count in mention_counts):
                fig = px.bar(
                    x=list(leaders.values()),
                    y=mention_counts,
                    title="Lider Bahsetme Sayıları",
                    color=mention_counts,
                    color_continuous_scale="viridis"
                )
                fig.update_layout(
                    title_font_size=16,
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            # İndirme seçenekleri
            st.subheader("💾 İndir")

            df_results = st.session_state.results_df
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            col1, col2 = st.columns(2)

            with col1:
                csv_data = df_results.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    "📄 CSV İndir",
                    csv_data,
                    f"analiz_{timestamp}.csv",
                    "text/csv",
                    use_container_width=True
                )

            with col2:
                excel_data = create_excel_output(df_results)
                st.download_button(
                    "📊 Excel İndir",
                    excel_data,
                    f"analiz_{timestamp}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

    # Sistem bilgisi
    with st.expander("ℹ️ Sistem Bilgisi"):
        st.markdown("""
        **Liderler:**
        - **RTE**: Recep Tayyip Erdoğan (Cumhurbaşkanı)
        - **ÖÖ**: Özgür Özel (CHP Genel Başkanı)
        - **MY**: Mansur Yavaş (Ankara Büyükşehir Belediye Başkanı)
        - **EI**: Ekrem İmamoğlu (İstanbul Büyükşehir Belediye Başkanı)

        **Değerler:**
        - **Sınıflandırma**: 1 (İlgili), 0 (İlgisiz)
        - **Sentiment**: +1 (Pozitif), 0 (Nötr), -1 (Negatif)
        """)

    # Footer
    st.markdown("""
    <div class="footer">
        <p>
            Baran Can Ercan tarafından 
            <span class="footer-heart">❤️</span> 
            ile yapılmıştır
        </p>
        <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 0.5rem;">
            🇹🇷 Türk Siyasi Lider Analiz Sistemi V2.0 • 🤖 AI Destekli • 🔒 Güvenli
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()