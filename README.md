# 🤖 X-Pop Bot

Twitter/X için yapay zeka destekli, kişiselleştirilebilir bot sistemi. Belirlediğiniz hesapları takip eder, tweetleri analiz eder ve kendi tarzında yeni tweetler oluşturur.

## ✨ Özellikler

- 🔄 **Otomatik Tweet Toplama**: Belirlediğiniz hesapları her 5 dakikada bir (ayarlanabilir) kontrol eder
- 🤖 **AI Destekli Tweet Oluşturma**: Groq API (ücretsiz) ile güçlü Llama 3.1 70B modeli
- 🎭 **5 Farklı Kişilik**: Yorumcu, Haber Duyurucu, Analist, Mizahçı, Sakin Paylaşımcı
- 🚫 **Akıllı Duplicate Kontrolü**: Aynı içeriği tekrar paylaşmaz
- 💾 **SQLite Database**: Tüm veriler yerel olarak saklanır
- 📊 **İstatistikler**: Toplanan ve paylaşılan tweet istatistikleri
- ⏰ **Zamanlanmış Çalıştırma**: APScheduler ile otomatik çalışma

## 🎭 Kişilikler

Bot 5 farklı kişilik profiliyle çalışabilir:

1. **Yorumcu** 📊
   - Haberleri yorumlayarak paylaşır
   - Objektif ama ilgi çekici
   - Emoji ve hashtag kullanır

2. **Haber Duyurucu** 📰
   - Düz, objektif duyurular
   - Sadece olgular
   - Resmi haber dili

3. **Analist** 🔍
   - Derin analiz ve içgörüler
   - Neden-sonuç ilişkileri
   - Trend ve pattern yakalama

4. **Mizahçı** 😄
   - Esprili ama saygılı
   - İroni ve abartma
   - Güncel internet kültürü

5. **Sakin Paylaşımcı** 🌙
   - Minimal ifadeler
   - Az kelime, maksimum etki
   - Düşündürücü ton

## 📋 Gereksinimler

- Python 3.8+
- Twitter API Anahtarları (Ücretsiz Developer Account)
- Groq API Anahtarı (Ücretsiz)

## 🚀 Kurulum

### 1. Projeyi İndirin

```bash
git clone <repo-url>
cd X-pop
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 3. API Anahtarlarını Alın

#### Twitter API Anahtarları

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)'a gidin
2. "Create Project" butonuna tıklayın
3. Proje ve App oluşturun
4. "Keys and Tokens" sekmesinden anahtarları alın:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token

**Önemli**: Free tier yeterlidir!

#### Groq API Anahtarı

1. [Groq Console](https://console.groq.com/)'a gidin
2. Ücretsiz hesap oluşturun
3. API Key oluşturun

**Tamamen ücretsiz** ve çok hızlı!

### 4. Yapılandırma

```bash
# .env dosyası oluşturun
cp .env.example .env

# .env dosyasını düzenleyin ve API anahtarlarını ekleyin
nano .env
```

**.env dosyası:**

```env
# Twitter API Keys
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Groq AI API
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Ayarları Özelleştirin

`config/config.yaml` dosyasını düzenleyin:

```yaml
# İzlenecek hesapları ekleyin
monitored_accounts:
  - "bbcturkce"
  - "cnnturk"
  - "NTV"
  # Buraya istediğiniz hesapları ekleyin

# Bot kişiliğini seçin
bot:
  personality: "yorumcu"  # yorumcu, haber_duyurucu, analist, mizahci, sakin_paylasimci
  check_interval: 5  # Dakika
  tweets_to_post_per_run: 1  # Her çalıştırmada kaç tweet
```

## 🎮 Kullanım

### Test Modu (API Bağlantılarını Test Et)

```bash
python -m src.main --test
```

### Dry Run (Tweet Atmadan Dene)

```bash
python -m src.main --dry-run
```

### Tek Seferlik Çalıştır

```bash
python -m src.main --once
```

### Sürekli Çalıştır (Önerilen)

```bash
# Varsayılan (5 dakikada bir)
python -m src.main

# Özel interval (örnek: 10 dakika)
python -m src.main --interval 10
```

### Arka Planda Çalıştır

```bash
# nohup ile
nohup python -m src.main > bot.log 2>&1 &

# screen ile
screen -S xpop
python -m src.main
# Ctrl+A+D ile detach
```

## 📁 Proje Yapısı

```
X-pop/
├── src/
│   ├── main.py              # Ana giriş noktası
│   ├── bot.py               # Bot orchestrator
│   ├── twitter_client.py    # Twitter API client
│   ├── ai_generator.py      # Groq AI entegrasyonu
│   ├── database.py          # SQLite veritabanı
│   ├── duplicate_detector.py # Duplicate kontrolü
│   └── scheduler.py         # Zamanlayıcı
├── config/
│   ├── config.yaml          # Ana ayarlar
│   └── personalities.yaml   # Kişilik profilleri
├── data/
│   └── tweets.db           # SQLite veritabanı
├── logs/
│   └── bot.log             # Log dosyası
├── requirements.txt        # Python bağımlılıkları
├── .env                    # API anahtarları (oluşturulacak)
└── README.md              # Bu dosya
```

## 🎨 Kişilik Özelleştirme

Kendi kişiliğinizi oluşturmak için `config/personalities.yaml` dosyasını düzenleyin:

```yaml
ozel_kisiliginiz:
  name: "Özel Kişilik"
  description: "Açıklama"
  system_prompt: |
    Sen bir sosyal medya botusun...

    Kurallar:
    - Maksimum 280 karakter
    - ...

  example_tweets:
    - "Örnek tweet 1"
    - "Örnek tweet 2"
```

Sonra `config/config.yaml`'da kullanın:

```yaml
bot:
  personality: "ozel_kisiliginiz"
```

## 🔍 Özellikler ve Ayarlar

### Duplicate Detection

Sistem iki seviyeli duplicate kontrolü yapar:

1. **Batch içi kontrol**: Aynı çalıştırmada toplanan tweetler arasında
2. **Veritabanı kontrolü**: Geçmişte toplanan/paylaşılan tweetlere karşı

Ayarlar (`config/config.yaml`):

```yaml
duplicate_detection:
  enabled: true
  similarity_threshold: 0.85  # %85 benzerlik = duplicate
  check_last_days: 7  # Son 7 günü kontrol et
```

### Tweet Filtreleme

- **Dil filtresi**: Sadece Türkçe tweetler
- **Uzunluk filtresi**: Minimum kelime sayısı
- **Tip filtresi**: Sadece orijinal tweetler (retweet ve reply yok)

### AI Ayarları

```yaml
ai:
  model: "llama-3.1-70b-versatile"  # Groq model
  temperature: 0.7  # 0-1 (0: tutarlı, 1: yaratıcı)
  max_tokens: 280  # Tweet limiti
```

## 📊 İstatistikler

Her çalıştırma sonunda istatistikler gösterilir:

```
📊 Statistics:
   Total collected: 150
   Total posted: 25
   Unprocessed: 10
   Today's posts: 3
```

## 🐛 Sorun Giderme

### "Authentication failed"

- `.env` dosyasındaki API anahtarlarını kontrol edin
- Twitter Developer Portal'da uygulama izinlerini kontrol edin (Read and Write gerekli)

### "Rate limit exceeded"

- Twitter API free tier limitleri:
  - Tweet okuma: 500,000/ay
  - Tweet yazma: 1,667/ay
- Interval süresini artırın

### "Groq API error"

- API anahtarını kontrol edin
- [Groq Console](https://console.groq.com/) üzerinden kota durumunu kontrol edin

### "No tweets collected"

- İzlenen hesapların son 24 saatte tweet atıp atmadığını kontrol edin
- `monitored_accounts` listesinde @ olmadan kullanıcı adı olmalı

## 🔒 Güvenlik

- `.env` dosyası `.gitignore`'da (asla commit edilmez)
- API anahtarları asla kod içinde değil
- Veritabanı sadece yerel
- Log dosyaları hassas bilgi içermez

## 📝 Notlar

- Bot, Twitter API'nin free tier limitlerine uygundur
- Groq API tamamen ücretsiz ve hızlıdır
- SQLite veritabanı hafif ve yönetimi kolaydır
- Log dosyaları düzenli olarak temizlenmelidir

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Branch'i push edin
5. Pull Request oluşturun

## 📜 Lisans

MIT License

## ⚠️ Yasal Uyarı

Bu bot'u kullanırken:
- Twitter'ın Otomasy Kurallarına uyun
- Spam yapmayın
- Yanıltıcı bilgi yaymayın
- Bot hesabınızı açıkça belirtin

## 📞 Destek

Sorunlar için:
1. Önce bu README'yi okuyun
2. Log dosyalarını kontrol edin
3. Issue açın

---

**Oluşturulma Tarihi**: 2025
**Versiyon**: 1.0.0
