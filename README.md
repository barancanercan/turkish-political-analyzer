# 🇹🇷 Python Türk Siyasi Lider Analiz Sistemi

Bu sistem, sosyal medya içeriklerini analiz ederek Türk siyasi liderlerine göre kategorize eden ve sentiment analizi yapan Python tabanlı bir AI sistemidir.

## 📦 Hızlı Kurulum

### 1. Python ve pip kurulumu
```bash
# Python 3.8+ gerekli
python --version  # 3.8+ olmalı
pip --version
```

### 2. Proje dosyalarını indirin
```bash
# Proje klasörü oluşturun
mkdir turkish-political-analyzer
cd turkish-political-analyzer

# Dosyaları kopyalayın (yukarıdaki kodları)
# political_analyzer.py
# web_interface.py
# requirements.txt
```

### 3. Gerekli paketleri yükleyin
```bash
pip install -r requirements.txt
```

## 📋 requirements.txt

```txt
# Temel bağımlılıklar
requests>=2.28.0
pandas>=1.5.0
tqdm>=4.64.0
colorama>=0.4.5

# Web arayüzü için (opsiyonel)
streamlit>=1.25.0
plotly>=5.15.0

# Geliştirme için (opsiyonel)
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
```

## 🚀 Kullanım Seçenekleri

### Seçenek 1: Komut Satırı (Önerilen - Büyük veri setleri)

```bash
# Temel kullanım
python political_analyzer.py input.csv output.csv YOUR_API_KEY

# Örnek
python political_analyzer.py sample.csv results.csv AIzaSyCklJ6T0IDgjuH7N8fbWl6AQtJuCEGbRA8

# Özelleştirilmiş parametreler
python political_analyzer.py data.csv results.csv YOUR_API_KEY \
  --batch-size 10 \
  --workers 3 \
  --rate-limit 2.0 \
  --max-retries 5

# Yardım
python political_analyzer.py --help
```

### Seçenek 2: Web Arayüzü (Test ve küçük dosyalar)

```bash
# Web arayüzünü başlat
streamlit run web_interface.py

# Tarayıcıda açılacak: http://localhost:8501
```

### Seçenek 3: Python Kodunda Kullanım

```python
from political_analyzer import PoliticalAnalysisSystem
import pandas as pd

# Sistem oluştur
analyzer = PoliticalAnalysisSystem(
    api_key="YOUR_API_KEY",
    batch_size=5,
    max_workers=3,
    rate_limit_sec=1.5
)

# Tek içerik analizi
result = analyzer.process_single_content(
    "@test_account", 
    "Mansur Yavaş ile harika bir proje yaptık!"
)
print(result)

# Dosya analizi
analyzer.process_file("input.csv", "output.csv")
```

## 📊 Örnek CSV Formatı

### Girdi (input.csv):
```csv
ACCOUNT_NAME,TEXT
@burcukoksal03,"Ata tohumlarımızı hasat ettik! Mansur Yavaş'la birlikte..."
@user123,"Ekrem İmamoğlu için oy vereceğim"
@siyasi_takip,"Erdoğan'ın son açıklaması çok önemliydi"
@chp_destekci,"Özgür Özel partiye yeni bir soluk getirdi"
```

### Çıktı (output.csv):
```csv
ACCOUNT_NAME,TEXT,IS_RTE,IS_ÖÖ,IS_MY,IS_EI,RTE_SENTIMENT,ÖÖ_SENTİMENT,MY_SENTIMENT,EI_SENTIMENT
@burcukoksal03,"Ata tohumlarımızı hasat ettik! Mansur Yavaş'la birlikte...",-1,-1,1,-1,,,,1
@user123,"Ekrem İmamoğlu için oy vereceğim",-1,-1,-1,1,,,,1
@siyasi_takip,"Erdoğan'ın son açıklaması çok önemliydi",1,-1,-1,-1,0,,,
@chp_destekci,"Özgür Özel partiye yeni bir soluk getirdi",-1,1,-1,-1,,1,,
```

## 🎯 Sistem Özellikleri

### Agent 1: Lider Sınıflandırma
Her içerik için hangi liderin ilgili olduğunu belirler:
- **+1**: İlgili lider
- **-1**: İlgisiz liderler

### Agent 2: Sentiment Analizi  
İlgili liderler için duygusal ton analizi:
- **+1**: Pozitif (övgü, destek)
- **0**: Nötr (tarafsız)
- **-1**: Negatif (eleştiri)

### Liderler:
- **RTE**: Recep Tayyip Erdoğan
- **ÖÖ**: Özgür Özel
- **MY**: Mansur Yavaş
- **EI**: Ekrem İmamoğlu

## ⚙️ Konfigürasyon Seçenekleri

| Parametre | Açıklama | Varsayılan | Aralık |
|-----------|----------|------------|--------|
| `--batch-size` | Aynı anda işlenecek kayıt sayısı | 5 | 1-20 |
| `--workers` | Paralel işlem sayısı | 3 | 1-10 |
| `--rate-limit` | API çağrıları arası bekleme (saniye) | 1.5 | 0.5-10 |
| `--max-retries` | Maksimum tekrar deneme | 3 | 1-10 |
| `--no-progress` | Progress kaydetmeyi devre dışı bırak | False | - |

## 📈 Performans Optimizasyonu

### Hız vs Maliyet Dengesi

```bash
# Hızlı işlem (daha maliyetli)
python political_analyzer.py data.csv results.csv API_KEY \
  --batch-size 10 --workers 5 --rate-limit 0.8

# Ekonomik işlem (daha yavaş)  
python political_analyzer.py data.csv results.csv API_KEY \
  --batch-size 3 --workers 2 --rate-limit 3.0

# Dengeli işlem (önerilen)
python political_analyzer.py data.csv results.csv API_KEY \
  --batch-size 5 --workers 3 --rate-limit 1.5
```

### Performans Tahminleri

| Kayıt Sayısı | Tahmini Süre | API Çağrısı | Tahmini Maliyet |
|-------------|-------------|-------------|----------------|
| 100         | 3-5 dakika  | ~150        | $0.15         |
| 1,000       | 25-35 dakika| ~1,500      | $1.50         |
| 10,000      | 4-6 saat    | ~15,000     | $15.00        |
| 100,000     | 2-3 gün     | ~150,000    | $150.00       |

## 🛠️ Gelişmiş Kullanım

### 1. Environment Variables ile Konfigürasyon

```bash
# .env dosyası oluşturun
echo "GOOGLE_API_KEY=your_api_key_here" > .env
echo "BATCH_SIZE=5" >> .env
echo "MAX_WORKERS=3" >> .env
echo "RATE_LIMIT=1.5" >> .env

# Python'da kullanım
pip install python-dotenv

# Kod içinde:
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
```

### 2. Büyük Dosyalar için Optimizasyon

```python
# big_file_processor.py
import pandas as pd
from political_analyzer import PoliticalAnalysisSystem

def process_large_file(input_file, output_file, api_key, chunk_size=1000):
    """Büyük CSV dosyalarını parça parça işle"""
    
    analyzer = PoliticalAnalysisSystem(api_key, batch_size=3, max_workers=2)
    
    # Dosyayı chunk'lar halinde oku
    chunk_iter = pd.read_csv(input_file, chunksize=chunk_size)
    
    all_results = []
    
    for i, chunk in enumerate(chunk_iter):
        print(f"Chunk {i+1} işleniyor: {len(chunk)} kayıt")
        
        # Chunk'ı işle
        chunk_data = chunk.to_dict('records')
        chunk_results = []
        
        for record in chunk_data:
            result = analyzer.process_single_content(
                record['ACCOUNT_NAME'], 
                record['TEXT']
            )
            if result:
                chunk_results.append(result)
        
        all_results.extend(chunk_results)
        
        # Ara kayıt
        if i % 10 == 0:
            temp_df = pd.DataFrame(all_results)
            temp_df.to_csv(f"{output_file}.temp", index=False)
    
    # Final kayıt
    final_df = pd.DataFrame(all_results)
    final_df.to_csv(output_file, index=False)
    
    print(f"İşlem tamamlandı: {len(all_results)} kayıt")

# Kullanım
process_large_file("huge_file.csv", "results.csv", "YOUR_API_KEY")
```

### 3. Parallel Processing ile Hızlandırma

```python
# parallel_processor.py
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def process_batch_worker(batch_data):
    """Worker fonksiyonu - ayrı process'te çalışır"""
    from political_analyzer import PoliticalAnalysisSystem
    
    analyzer = PoliticalAnalysisSystem(
        api_key=batch_data['api_key'],
        batch_size=1,
        max_workers=1
    )
    
    results = []
    for item in batch_data['items']:
        result = analyzer.process_single_content(
            item['ACCOUNT_NAME'], 
            item['TEXT']
        )
        if result:
            results.append(result)
    
    return results

def parallel_process_file(input_file, output_file, api_key, num_processes=4):
    """Paralel processing ile dosya işle"""
    
    # CSV'yi oku
    df = pd.read_csv(input_file)
    data = df.to_dict('records')
    
    # Veriyi process'lere böl
    chunk_size = len(data) // num_processes
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Her chunk için worker data hazırla
    worker_data = [
        {'api_key': api_key, 'items': chunk} 
        for chunk in chunks
    ]
    
    # Parallel processing
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = executor.map(process_batch_worker, worker_data)
    
    # Sonuçları birleştir
    all_results = []
    for batch_results in results:
        all_results.extend(batch_results)
    
    # Kaydet
    result_df = pd.DataFrame(all_results)
    result_df.to_csv(output_file, index=False)
    
    print(f"Parallel işlem tamamlandı: {len(all_results)} kayıt")
```

## 🐳 Docker ile Kullanım

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY political_analyzer.py .
COPY web_interface.py .

# Veri ve sonuç dizinleri
RUN mkdir -p /app/data /app/results

EXPOSE 8501

# Varsayılan komut - web arayüzü
CMD ["streamlit", "run", "web_interface.py", "--server.address", "0.0.0.0"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  political-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./results:/app/results
    restart: unless-stopped

  # CLI versiyonu için
  analyzer-cli:
    build: .
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./results:/app/results
    command: python political_analyzer.py /app/data/input.csv /app/results/output.csv ${GOOGLE_API_KEY}
    profiles: ["cli"]
```

### Docker kullanımı:
```bash
# Image build et
docker build -t turkish-political-analyzer .

# Web arayüzü çalıştır
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  turkish-political-analyzer

# CLI versiyonu
docker run --rm \
  -e GOOGLE_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  turkish-political-analyzer \
  python political_analyzer.py /app/data/input.csv /app/results/output.csv your_key

# Docker compose ile
echo "GOOGLE_API_KEY=your_key" > .env
docker-compose up  # Web arayüzü
docker-compose --profile cli up  # CLI versiyonu
```

## 🔧 Troubleshooting (Sorun Giderme)

### Yaygın Hatalar ve Çözümleri

#### 1. **ModuleNotFoundError: No module named 'requests'**
```bash
# Çözüm: Bağımlılıkları yükleyin
pip install -r requirements.txt
```

#### 2. **API Error: 403 Forbidden**
```bash
# Çözüm: API anahtarını kontrol edin
# Google Cloud Console'dan yeni anahtar alın
# Gemini API'nin etkin olduğundan emin olun
```

#### 3. **Rate Limit Error: 429**
```bash
# Çözüm: Rate limit'i artırın
python political_analyzer.py input.csv output.csv API_KEY --rate-limit 3.0
```

#### 4. **Memory Error (Büyük dosyalar)**
```python
# Çözüm: Chunk processing kullanın
# Yukarıdaki big_file_processor.py kodunu kullanın
```

#### 5. **CSV Encoding Hatası**
```python
# Çözüm: Encoding belirtin
df = pd.read_csv('input.csv', encoding='utf-8-sig')  # Excel'den gelen dosyalar için
df = pd.read_csv('input.csv', encoding='latin-1')   # Eski Windows dosyaları için
```

### Debug Modu

```bash
# Detaylı log için
python -u political_analyzer.py input.csv output.csv API_KEY 2>&1 | tee debug.log

# Specific line'da hata varsa
python -c "
import pandas as pd
df = pd.read_csv('input.csv')
print('Problematic rows:')
print(df[df['TEXT'].isnull()])
"
```

## 📊 Monitoring ve Analytics

### 1. Log Analizi
```python
# log_analyzer.py
import re
from collections import Counter

def analyze_logs(log_file):
    """Log dosyasını analiz et"""
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = f.read()
    
    # Error sayısı
    errors = re.findall(r'ERROR', logs)
    warnings = re.findall(r'WARNING', logs)
    
    # API hatalarını analiz et
    api_errors = re.findall(r'API Error: (\d+)', logs)
    error_codes = Counter(api_errors)
    
    print(f"Toplam error: {len(errors)}")
    print(f"Toplam warning: {len(warnings)}")
    print(f"API error kodları: {dict(error_codes)}")

# Kullanım
analyze_logs('political_analysis.log')
```

### 2. Progress Tracking
```python
# progress_tracker.py
import json
import time
from datetime import datetime

class ProgressTracker:
    def __init__(self, total_items):
        self.total_items = total_items
        self.processed = 0
        self.errors = 0
        self.start_time = time.time()
    
    def update(self, processed_count, error_count=0):
        self.processed += processed_count
        self.errors += error_count
        
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0
        remaining = (self.total_items - self.processed) / rate if rate > 0 else 0
        
        print(f"Progress: {self.processed}/{self.total_items} "
              f"({(self.processed/self.total_items)*100:.1f}%) "
              f"Rate: {rate:.2f}/sec "
              f"ETA: {remaining/60:.1f}min")
    
    def save_checkpoint(self, filename):
        checkpoint = {
            'processed': self.processed,
            'errors': self.errors,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(checkpoint, f)
```

## 🚀 Production Deployment

### 1. Systemd Service (Linux)
```ini
# /etc/systemd/system/political-analyzer.service
[Unit]
Description=Turkish Political Analyzer
After=network.target

[Service]
Type=simple
User=analyzer
WorkingDirectory=/opt/political-analyzer
Environment=GOOGLE_API_KEY=your_key_here
ExecStart=/usr/bin/python3 political_analyzer.py /data/input.csv /data/output.csv
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service'i etkinleştir
sudo systemctl daemon-reload
sudo systemctl enable political-analyzer
sudo systemctl start political-analyzer
sudo systemctl status political-analyzer
```

### 2. Cron Job ile Otomatik Çalışma
```bash
# Crontab'a ekle
crontab -e

# Her gün saat 02:00'da çalıştır
0 2 * * * cd /opt/political-analyzer && python3 political_analyzer.py /data/daily_input.csv /data/daily_output_$(date +\%Y\%m\%d).csv $GOOGLE_API_KEY >> /var/log/political-analyzer.log 2>&1
```

### 3. API Server (Flask/FastAPI)
```python
# api_server.py
from flask import Flask, request, jsonify
from political_analyzer import PoliticalAnalysisSystem
import os

app = Flask(__name__)
analyzer = PoliticalAnalysisSystem(os.getenv('GOOGLE_API_KEY'))

@app.route('/analyze', methods=['POST'])
def analyze_content():
    data = request.json
    
    result = analyzer.process_single_content(
        data.get('account_name', ''),
        data.get('text', '')
    )
    
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 📞 Destek ve İletişim

### Dokumentasyon
- **GitHub**: Repository link'i buraya gelecek
- **API Docs**: Google Gemini API dokumentasyonu
- **Issues**: Bug report ve feature request için

### Performans Sorunları
1. **API Rate Limits**: `--rate-limit` parametresini artırın
2. **Memory Issues**: Chunk processing kullanın
3. **Slow Processing**: `--workers` ve `--batch-size` parametrelerini ayarlayın

### Katkıda Bulunma
```bash
# Development kurulumu
git clone <repository>
cd turkish-political-analyzer
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Test çalıştır
pytest tests/

# Kod formatla
black political_analyzer.py
flake8 political_analyzer.py
```

---

**🎉 Sistem hazır! Türk siyasi ortamındaki sosyal medya analizleri için kapsamlı bir Python çözümü.**