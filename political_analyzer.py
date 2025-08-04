#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türk Siyasi Lider Analiz Sistemi
Python versiyonu - Ölçeklenebilir ve profesyonel kullanım için

Kurulum:
pip install requests pandas tqdm colorama

Kullanım:
python political_analyzer.py input.csv output.csv YOUR_API_KEY
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
import argparse
from pathlib import Path
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from colorama import init, Fore, Style

# Colorama'yı başlat
init()


class PoliticalAnalysisSystem:
    """
    Türk Siyasi Lider Analiz Sistemi

    Bu sınıf sosyal medya içeriklerini analiz ederek siyasi liderlere göre
    kategorize eder ve sentiment analizi yapar.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Sistem başlatıcı

        Args:
            api_key: Google Gemini API anahtarı
            **kwargs: Konfigürasyon seçenekleri
        """
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

        # Konfigürasyon
        self.config = {
            'rate_limit_sec': kwargs.get('rate_limit_sec', 1.5),
            'max_retries': kwargs.get('max_retries', 3),
            'batch_size': kwargs.get('batch_size', 5),
            'timeout_sec': kwargs.get('timeout_sec', 30),
            'save_progress': kwargs.get('save_progress', True),
            'max_workers': kwargs.get('max_workers', 3),
        }

        # Lider tanımları
        self.leaders = {
            'RTE': 'Recep Tayyip Erdoğan',
            'ÖÖ': 'Özgür Özel',
            'MY': 'Mansur Yavaş',
            'EI': 'Ekrem İmamoğlu'
        }

        # İstatistikler
        self.stats = {
            'processed': 0,
            'errors': 0,
            'start_time': None,
            'total_items': 0
        }

        # Thread-safe için lock
        self.stats_lock = threading.Lock()

        # Logging kurulumu
        self.setup_logging()

    def setup_logging(self):
        """Logging sistemini kur"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('political_analysis.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def print_header(self):
        """Başlık yazdır"""
        print(f"{Fore.CYAN}{'=' * 60}")
        print(f"🇹🇷 TÜRKİYE SİYASİ LİDER ANALİZ SİSTEMİ")
        print(f"{'=' * 60}{Style.RESET_ALL}")

    def load_progress(self, progress_file: str) -> Dict:
        """Progress dosyasından devam et"""
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Progress dosyası okunamadı: {e}")

        return {'processed': [], 'last_index': 0}

    def save_progress(self, progress_file: str, data: Dict):
        """Progress kaydet"""
        if self.config['save_progress']:
            try:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.logger.error(f"Progress kaydedilemedi: {e}")

    def make_api_request(self, prompt: str, retries: int = 0) -> Optional[str]:
        """
        Gemini API'ye istek gönder

        Args:
            prompt: Gönderilecek prompt
            retries: Retry sayısı

        Returns:
            API yanıtı veya None
        """
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json=payload,
                headers=headers,
                timeout=self.config['timeout_sec']
            )

            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']

            elif response.status_code == 429:  # Rate limit
                if retries < self.config['max_retries']:
                    wait_time = (2 ** retries) * 2  # Exponential backoff
                    self.logger.warning(f"Rate limit, {wait_time}s bekleniyor...")
                    time.sleep(wait_time)
                    return self.make_api_request(prompt, retries + 1)

            else:
                self.logger.error(f"API Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            if retries < self.config['max_retries']:
                self.logger.warning(f"Timeout, retry {retries + 1}")
                time.sleep(2)
                return self.make_api_request(prompt, retries + 1)
            else:
                self.logger.error("API timeout")

        except Exception as e:
            self.logger.error(f"API request error: {e}")

        return None

    def classify_by_leader(self, text: str, account_name: str) -> Dict:
        """
        Agent 1: İçeriği liderlere göre sınıflandır

        Args:
            text: Analiz edilecek metin
            account_name: Hesap adı

        Returns:
            Sınıflandırma sonucu
        """
        prompt = f'''
Sen bir Türk siyasi analiz uzmanısın. Aşağıdaki sosyal medya içeriğini analiz ederek, bu içeriğin hangi siyasi lideri ilgilendirdiğini belirle.

Liderler:
- RTE: Recep Tayyip Erdoğan (AK Parti, Cumhurbaşkanı)
- ÖÖ: Özgür Özel (CHP Genel Başkanı)
- MY: Mansur Yavaş (Ankara Büyükşehir Belediye Başkanı, CHP)
- EI: Ekrem İmamoğlu (İstanbul Büyükşehir Belediye Başkanı, CHP)

Kurallar:
1. İçerik bir lideri doğrudan bahsediyorsa, o lidere +1 ver
2. İçerik bir liderin partisini/görevini bahsediyorsa, o lidere +1 ver
3. Diğer tüm liderlere -1 ver
4. Eğer hiçbir lider açık şekilde ilgili değilse, hepsine -1 ver
5. Birden fazla lider ilgiliyse, en çok ilgili olana +1, diğerlerine -1 ver

İçerik: "{text}"
Hesap: "{account_name}"

Sonucu sadece JSON formatında ver:
{{
    "IS_RTE": 1 veya -1,
    "IS_ÖÖ": 1 veya -1,
    "IS_MY": 1 veya -1,
    "IS_EI": 1 veya -1,
    "reasoning": "Kısa açıklama"
}}
'''

        response = self.make_api_request(prompt)

        if response:
            try:
                # JSON'u bul ve parse et
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parse error: {e}")

        # Fallback değerler
        with self.stats_lock:
            self.stats['errors'] += 1

        return {
            "IS_RTE": -1,
            "IS_ÖÖ": -1,
            "IS_MY": -1,
            "IS_EI": -1,
            "reasoning": "API hatası - varsayılan değerler"
        }

    def analyze_sentiment_for_leader(self, text: str, account_name: str, leader_name: str) -> int:
        """
        Agent 2: Belirli bir lider için sentiment analizi

        Args:
            text: Analiz edilecek metin
            account_name: Hesap adı
            leader_name: Lider adı

        Returns:
            Sentiment değeri (-1, 0, 1)
        """
        prompt = f'''
Sen bir sentiment analiz uzmanısın. Aşağıdaki sosyal medya içeriğinin "{leader_name}" hakkındaki duygusal tonunu analiz et.

İçerik: "{text}"
Hesap: "{account_name}"

Sentiment kategorileri:
- 1: Pozitif (övgü, destek, beğeni)
- 0: Nötr (tarafsız bahsetme, objektif)
- -1: Negatif (eleştiri, saldırı, olumsuz)

Sadece sayısal değeri ver (1, 0, veya -1):
'''

        response = self.make_api_request(prompt)

        if response:
            try:
                # Sayısal değeri çıkar
                import re
                number_match = re.search(r'-?[01]', response.strip())
                if number_match:
                    return int(number_match.group())
            except ValueError:
                pass

        with self.stats_lock:
            self.stats['errors'] += 1

        return 0  # Varsayılan nötr

    def process_single_content(self, account_name: str, text: str) -> Optional[Dict]:
        """
        Tek bir içeriği işle

        Args:
            account_name: Hesap adı
            text: İçerik metni

        Returns:
            İşlem sonucu
        """
        if not text or not text.strip():
            return None

        try:
            # Agent 1: Lider sınıflandırması
            classification = self.classify_by_leader(text, account_name)

            # Agent 2: Sentiment analizi (sadece ilgili liderler için)
            sentiment_results = {
                "RTE_SENTIMENT": None,
                "ÖÖ_SENTİMENT": None,
                "MY_SENTIMENT": None,
                "EI_SENTIMENT": None
            }

            for code, full_name in self.leaders.items():
                is_key = f"IS_{code}"
                if classification.get(is_key) == 1:
                    sentiment_key = f"{code}_SENTIMENT"
                    sentiment_results[sentiment_key] = self.analyze_sentiment_for_leader(
                        text, account_name, full_name
                    )

            # İstatistikleri güncelle
            with self.stats_lock:
                self.stats['processed'] += 1

            return {
                'ACCOUNT_NAME': account_name,
                'TEXT': text,
                'IS_RTE': classification.get('IS_RTE', -1),
                'IS_ÖÖ': classification.get('IS_ÖÖ', -1),
                'IS_MY': classification.get('IS_MY', -1),
                'IS_EI': classification.get('IS_EI', -1),
                'RTE_SENTIMENT': sentiment_results['RTE_SENTIMENT'],
                'ÖÖ_SENTİMENT': sentiment_results['ÖÖ_SENTİMENT'],
                'MY_SENTIMENT': sentiment_results['MY_SENTIMENT'],
                'EI_SENTIMENT': sentiment_results['EI_SENTIMENT'],
                'reasoning': classification.get('reasoning', '')
            }

        except Exception as e:
            self.logger.error(f"İçerik işleme hatası: {e}")
            with self.stats_lock:
                self.stats['errors'] += 1
            return None

    def process_batch_parallel(self, data_batch: List[Dict]) -> List[Dict]:
        """
        Batch'i paralel olarak işle

        Args:
            data_batch: İşlenecek veri batch'i

        Returns:
            İşlem sonuçları
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Her içerik için task oluştur
            future_to_item = {
                executor.submit(
                    self.process_single_content,
                    item.get('ACCOUNT_NAME', ''),
                    item.get('TEXT', '')
                ): item for item in data_batch
            }

            # Sonuçları topla
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    if result:
                        results.append(result)

                    # Rate limiting
                    time.sleep(self.config['rate_limit_sec'] / self.config['max_workers'])

                except Exception as e:
                    self.logger.error(f"Batch işleme hatası: {e}")

        return results

    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        CSV dosyasını oku

        Args:
            file_path: CSV dosya yolu

        Returns:
            Pandas DataFrame
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')

            # Sütun isimlerini temizle
            df.columns = df.columns.str.strip()

            # Gerekli sütunları kontrol et
            required_columns = ['ACCOUNT_NAME', 'TEXT']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Eksik sütunlar: {missing_columns}")

            # Boş satırları temizle
            df = df.dropna(subset=['TEXT'])
            df = df[df['TEXT'].str.strip() != '']

            self.logger.info(f"CSV okundu: {len(df)} kayıt")
            return df

        except Exception as e:
            self.logger.error(f"CSV okuma hatası: {e}")
            raise

    def write_csv(self, file_path: str, results: List[Dict]):
        """
        Sonuçları CSV'ye yaz

        Args:
            file_path: Çıktı dosya yolu
            results: Sonuç listesi
        """
        try:
            df = pd.DataFrame(results)

            # Sütun sıralaması
            columns = [
                'ACCOUNT_NAME', 'TEXT', 'IS_RTE', 'IS_ÖÖ', 'IS_MY', 'IS_EI',
                'RTE_SENTIMENT', 'ÖÖ_SENTİMENT', 'MY_SENTIMENT', 'EI_SENTIMENT'
            ]

            # Mevcut sütunları al
            available_columns = [col for col in columns if col in df.columns]
            df = df[available_columns]

            df.to_csv(file_path, index=False, encoding='utf-8')
            self.logger.info(f"Sonuçlar {file_path} dosyasına yazıldı")

        except Exception as e:
            self.logger.error(f"CSV yazma hatası: {e}")
            raise

    def generate_report(self, results: List[Dict]) -> Dict:
        """
        Analiz raporu oluştur

        Args:
            results: Analiz sonuçları

        Returns:
            Rapor dictionary'si
        """
        if not results:
            return {}

        # Temel istatistikler
        total_processed = len(results)
        total_time = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0

        # Lider istatistikleri
        leader_stats = {}
        for leader_code in self.leaders.keys():
            mentions = sum(1 for r in results if r.get(f'IS_{leader_code}') == 1)

            sentiment_key = f'{leader_code}_SENTIMENT'
            sentiments = [r.get(sentiment_key) for r in results if r.get(sentiment_key) is not None]

            positive = sum(1 for s in sentiments if s == 1)
            neutral = sum(1 for s in sentiments if s == 0)
            negative = sum(1 for s in sentiments if s == -1)

            leader_stats[leader_code] = {
                'name': self.leaders[leader_code],
                'mentions': mentions,
                'positive': positive,
                'neutral': neutral,
                'negative': negative,
                'total_sentiment': len(sentiments)
            }

        return {
            'summary': {
                'total_processed': total_processed,
                'total_errors': self.stats['errors'],
                'processing_time_seconds': round(total_time, 2),
                'avg_time_per_item': round(total_time / total_processed, 2) if total_processed > 0 else 0,
                'success_rate': round((total_processed / (total_processed + self.stats['errors'])) * 100, 2) if (
                                                                                                                            total_processed +
                                                                                                                            self.stats[
                                                                                                                                'errors']) > 0 else 0
            },
            'leader_statistics': leader_stats,
            'generated_at': datetime.now().isoformat()
        }

    def print_report(self, report: Dict):
        """
        Raporu güzel formatta yazdır

        Args:
            report: Rapor dictionary'si
        """
        print(f"\n{Fore.GREEN}{'=' * 60}")
        print(f"📊 ANALİZ RAPORU")
        print(f"{'=' * 60}{Style.RESET_ALL}")

        summary = report.get('summary', {})
        print(f"✅ Toplam işlenen: {summary.get('total_processed', 0)}")
        print(f"❌ Hatalar: {summary.get('total_errors', 0)}")
        print(f"⏱️  Toplam süre: {self.format_time(summary.get('processing_time_seconds', 0))}")
        print(f"⚡ Ortalama hız: {summary.get('avg_time_per_item', 0):.2f} saniye/kayıt")
        print(f"📈 Başarı oranı: {summary.get('success_rate', 0):.1f}%")

        leader_stats = report.get('leader_statistics', {})
        print(f"\n{Fore.CYAN}📈 LİDER İSTATİSTİKLERİ:{Style.RESET_ALL}")

        for leader_code, stats in leader_stats.items():
            if stats['mentions'] > 0:
                print(f"\n{Fore.YELLOW}{stats['name']} ({leader_code}):{Style.RESET_ALL}")
                print(f"  Toplam bahsetme: {stats['mentions']}")

                if stats['total_sentiment'] > 0:
                    pos_pct = (stats['positive'] / stats['total_sentiment']) * 100
                    neu_pct = (stats['neutral'] / stats['total_sentiment']) * 100
                    neg_pct = (stats['negative'] / stats['total_sentiment']) * 100

                    print(f"  {Fore.GREEN}Pozitif: {stats['positive']} ({pos_pct:.1f}%){Style.RESET_ALL}")
                    print(f"  {Fore.BLUE}Nötr: {stats['neutral']} ({neu_pct:.1f}%){Style.RESET_ALL}")
                    print(f"  {Fore.RED}Negatif: {stats['negative']} ({neg_pct:.1f}%){Style.RESET_ALL}")
            else:
                print(f"\n{stats['name']} ({leader_code}): Bahsetme yok")

    def format_time(self, seconds: float) -> str:
        """
        Zamanı human-readable formata çevir

        Args:
            seconds: Saniye cinsinden zaman

        Returns:
            Formatlanmış zaman string'i
        """
        if seconds < 60:
            return f"{seconds:.1f} saniye"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{int(minutes)} dakika {secs:.0f} saniye"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{int(hours)} saat {int(minutes)} dakika"

    def process_file(self, input_file: str, output_file: str):
        """
        Ana işlem fonksiyonu - CSV dosyasını işle

        Args:
            input_file: Girdi CSV dosyası
            output_file: Çıktı CSV dosyası
        """
        self.stats['start_time'] = time.time()

        # Header yazdır
        self.print_header()
        print(f"📁 Girdi dosyası: {input_file}")
        print(f"📁 Çıktı dosyası: {output_file}")
        print(f"⚙️  Batch boyutu: {self.config['batch_size']}")
        print(f"⚙️  Max worker: {self.config['max_workers']}")
        print(f"⚙️  Rate limit: {self.config['rate_limit_sec']} saniye")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

        # Progress dosyası
        progress_file = f"{output_file}.progress.json"
        progress = self.load_progress(progress_file)

        try:
            # CSV'yi oku
            df = self.read_csv(input_file)
            self.stats['total_items'] = len(df)

            # Progress'ten devam et
            start_index = progress.get('last_index', 0)
            processed_results = progress.get('processed', [])

            remaining_data = df.iloc[start_index:].to_dict('records')

            print(f"📊 Toplam kayıt: {len(df)}")
            print(f"✅ İşlenmiş: {len(processed_results)}")
            print(f"⏳ Kalan: {len(remaining_data)}")
            print("\n🚀 İşlem başlıyor...\n")

            # Progress bar
            pbar = tqdm(total=len(remaining_data), desc="İşleniyor",
                        unit="kayıt", colour="green")

            all_results = processed_results.copy()

            # Batch'ler halinde işle
            for i in range(0, len(remaining_data), self.config['batch_size']):
                batch = remaining_data[i:i + self.config['batch_size']]
                current_index = start_index + i

                # Batch'i işle
                batch_results = self.process_batch_parallel(batch)
                all_results.extend(batch_results)

                # Progress güncelle
                progress['processed'] = all_results
                progress['last_index'] = current_index + len(batch)
                self.save_progress(progress_file, progress)

                # Progress bar güncelle
                pbar.update(len(batch))

                # Ara rapor
                if (i // self.config['batch_size']) % 5 == 0:
                    elapsed = time.time() - self.stats['start_time']
                    remaining_items = len(remaining_data) - i - len(batch)
                    if i > 0:
                        avg_time_per_batch = elapsed / ((i // self.config['batch_size']) + 1)
                        estimated_remaining = (remaining_items / self.config['batch_size']) * avg_time_per_batch
                        pbar.set_postfix({
                            'Hata': self.stats['errors'],
                            'Kalan': self.format_time(estimated_remaining)
                        })

            pbar.close()

            # Sonuçları kaydet
            self.write_csv(output_file, all_results)

            # Progress dosyasını temizle
            if os.path.exists(progress_file):
                os.remove(progress_file)

            # Rapor oluştur ve yazdır
            report = self.generate_report(all_results)
            self.print_report(report)

            # JSON raporu kaydet
            report_file = output_file.replace('.csv', '_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"\n{Fore.GREEN}🎉 İşlem başarıyla tamamlandı!{Style.RESET_ALL}")
            print(f"📄 Detaylı rapor: {report_file}")

        except Exception as e:
            self.logger.error(f"İşlem hatası: {e}")
            print(f"\n{Fore.RED}💥 Hata oluştu: {e}{Style.RESET_ALL}")
            print(f"📁 Progress {progress_file} dosyasında kaydedildi.")
            raise


def main():
    """Ana fonksiyon - Komut satırı arayüzü"""
    parser = argparse.ArgumentParser(
        description='🇹🇷 Türk Siyasi Lider Analiz Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Örnek kullanım:
  python political_analyzer.py data.csv results.csv AIzaSyCklJ6T0IDgjuH7N8fbWl6AQtJuCEGbRA8

  # Özelleştirilmiş parametrelerle:
  python political_analyzer.py data.csv results.csv YOUR_API_KEY --batch-size 10 --workers 2
        '''
    )

    parser.add_argument('input_file', help='Girdi CSV dosyası')
    parser.add_argument('output_file', help='Çıktı CSV dosyası')
    parser.add_argument('api_key', help='Google Gemini API anahtarı')

    parser.add_argument('--batch-size', type=int, default=5,
                        help='Batch boyutu (default: 5)')
    parser.add_argument('--workers', type=int, default=3,
                        help='Paralel worker sayısı (default: 3)')
    parser.add_argument('--rate-limit', type=float, default=1.5,
                        help='Rate limit saniye (default: 1.5)')
    parser.add_argument('--max-retries', type=int, default=3,
                        help='Maksimum retry sayısı (default: 3)')
    parser.add_argument('--no-progress', action='store_true',
                        help='Progress kaydetme')

    args = parser.parse_args()

    # Dosya kontrolü
    if not os.path.exists(args.input_file):
        print(f"{Fore.RED}❌ Girdi dosyası bulunamadı: {args.input_file}{Style.RESET_ALL}")
        sys.exit(1)

    # Çıktı dizinini oluştur
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Sistem oluştur
    config = {
        'batch_size': args.batch_size,
        'max_workers': args.workers,
        'rate_limit_sec': args.rate_limit,
        'max_retries': args.max_retries,
        'save_progress': not args.no_progress
    }

    analyzer = PoliticalAnalysisSystem(args.api_key, **config)

    try:
        analyzer.process_file(args.input_file, args.output_file)
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  İşlem kullanıcı tarafından durduruldu{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}💥 Fatal hata: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()