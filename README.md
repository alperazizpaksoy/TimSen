# Timur - Virtuoso 🎭

**Eğitim ve Yetiştirme Platform**

Öğrenciler, stajyerler ve tecrübesiz profesyoneller için AI-destekli senaryo tabanlı eğitim sistemi. Gerçek hayat senaryoları üzerinden pratik yapma ve uzman denetimi ile değerlendirme alabilme imkanı.

## 🎯 Özellikler

- **Senaryo Oluşturma**: Özel senaryolar oluştur ve AI ile rolu oynat
- **AI Konuşması**: Google Gemini API ile gerçekçi diyaloglar
- **Duygu Analizi**: Konuşma sırasında kullanıcının duygularını analiz et
- **Değerlendirme Raporu**: Performans analizi ve geri bildirim
- **Multi-Model Desteği**: Farklı LLM modelleri ile çalışabilme

## 🛠️ Teknoloji Stack

- **UI**: PyQt5
- **AI**: Google Gemini API, Transformers
- **NLP**: Sentence Transformers (Duygu Analizi)
- **Backend**: Python 3.9+

## 📦 Kurulum

### 1. Repository'yi klonla
```bash
git clone https://github.com/kullaniciadi/Timur-Virtuoso.git
cd Timur-Virtuoso
```

### 2. Virtual Environment oluştur
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları yükle
```bash
pip install -r requirements.txt
```

### 4. API Key'i ayarla
```bash
# .env dosyası oluştur (proje kök dizininde)
# .env dosyasına ekle:
GEMINI_API_KEY="your-api-key-here"
```

Google AI Studio'dan API key almak için:
1. https://aistudio.google.com/app/apikey adresine git
2. API Key oluştur
3. `.env` dosyasına yapıştır

### 5. Uygulamayı başlat
```bash
python main.py
```

## 📂 Proje Yapısı

```
Timur-Virtuoso/
├── main.py                 # Ana giriş noktası
├── config.py              # Konfigürasyon ayarları
├── requirements.txt       # Bağımlılıklar
├── llm/                   # AI/LLM modülleri
│   ├── gemini_client.py  # Gemini API istemcisi
│   └── emotion_analyzer.py # Duygu analiz motoru
├── ui/                    # Kullanıcı arayüzü
│   ├── chat_window.py    # Sohbet penceresi
│   ├── scenario_creator.py # Senaryo oluşturucu
│   ├── scenario_selector.py # Senaryo seçici
│   └── custom_messagebox.py # Özel mesaj kutuları
├── assets/               # Görüntü ve ikonlar
└── data/                 # Veriler (GitHub'a yüklenmez)
    ├── models/          # LLM modelleri
    ├── scenarios/       # Senaryolar
    └── conversations/   # Konuşma geçmişi
```

## 🚀 Kullanım

1. **Overlay Başlat**: Uygulama başlatıldığında overlay gösterilir
2. **Senaryo Seç veya Oluştur**: Var olan senaryodan seç veya yeni oluştur
3. **AI ile Konuş**: Senaryo rolüne uygun diyalog yap
4. **Rapor Al**: Konuşmanın bitiminde değerlendirme raporunu gör

## 🔐 Güvenlik

- API Key'ler `.env` dosyasında saklanır (`.gitignore`'da dışlanır)
- Sensitif veriler GitHub'a yüklenmez
- Ortam değişkenleri üzerinden yönetilir

## 📝 Ortam Değişkenleri

`GEMINI_API_KEY` - Google Gemini API anahtarı (gerekli)

## 🤝 Katkı

Pull request'ler hoş geldinir! Büyük değişiklikler için lütfen önce bir issue açın.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## 👤 Yazar

Timur - Virtuoso Geliştirme Ekibi

---

**Not**: Bu uygulama Google Gemini API'yi kullanır. Kullanmadan önce API key'inizi `.env` dosyasında ayarladığınızdan emin olun.
