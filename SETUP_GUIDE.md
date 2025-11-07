# 🚀 X-Pop Bot Kurulum Rehberi

Bu rehber, X-Pop Bot'u sıfırdan kurmanız için adım adım talimatlar içerir.

## 📑 İçindekiler

1. [Python Kurulumu](#1-python-kurulumu)
2. [Twitter API Anahtarları](#2-twitter-api-anahtarları)
3. [Groq API Anahtarı](#3-groq-api-anahtarı)
4. [Bot Kurulumu](#4-bot-kurulumu)
5. [İlk Çalıştırma](#5-ilk-çalıştırma)

---

## 1. Python Kurulumu

### Windows

1. [Python.org](https://www.python.org/downloads/) adresinden Python 3.8+ indirin
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. Komut satırında test edin:

```cmd
python --version
```

### macOS

```bash
# Homebrew ile
brew install python3

# Veya python.org'dan indirin
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## 2. Twitter API Anahtarları

### Adım 1: Developer Account Oluşturun

1. [developer.twitter.com](https://developer.twitter.com/) adresine gidin
2. Twitter hesabınızla giriş yapın
3. **"Sign up for Free Account"** butonuna tıklayın
4. Formu doldurun:
   - **What's your use case?**: Making a bot (veya benzer)
   - **Will you make Twitter content available?**: No
   - **Will you use Twitter data?**: Yes, to create a bot
5. Email adresinizi doğrulayın

### Adım 2: Proje ve App Oluşturun

1. Developer Portal'da **"Create Project"** butonuna tıklayın
2. Proje adı girin (örn: "XPopBot")
3. Use case seçin: **"Making a bot"**
4. App adı girin (örn: "xpop-bot")

### Adım 3: App Ayarları

1. Oluşturduğunuz App'e tıklayın
2. **"Settings"** sekmesine gidin
3. **"App permissions"** kısmında:
   - **"Read and Write"** seçin (çok önemli!)
   - Save edin

### Adım 4: Anahtarları Alın

1. **"Keys and Tokens"** sekmesine gidin

2. **API Key and Secret** bölümünden:
   - `API Key` → `.env`'de `TWITTER_API_KEY`
   - `API Secret` → `.env`'de `TWITTER_API_SECRET`

3. **Access Token and Secret** bölümünden:
   - **"Generate"** butonuna tıklayın
   - `Access Token` → `.env`'de `TWITTER_ACCESS_TOKEN`
   - `Access Token Secret` → `.env`'de `TWITTER_ACCESS_TOKEN_SECRET`

4. **Bearer Token** bölümünden:
   - `Bearer Token` → `.env`'de `TWITTER_BEARER_TOKEN`

⚠️ **ÖNEMLİ**: Bu anahtarları not edin! Tekrar gösterilmezler.

### Free Tier Limitler

Twitter API Free tier'da şunları yapabilirsiniz:
- Ayda 500,000 tweet okuma
- Ayda 1,667 tweet yazma
- Dakikada 5 istek

Bu limitler X-Pop Bot için yeterlidir.

---

## 3. Groq API Anahtarı

### Neden Groq?

- ✅ **Tamamen ücretsiz**
- ✅ **Çok hızlı** (saniyede 500+ token)
- ✅ **Güçlü model** (Llama 3.1 70B)
- ✅ **Mükemmel Türkçe**

### Adım 1: Hesap Oluşturun

1. [console.groq.com](https://console.groq.com/) adresine gidin
2. **"Sign Up"** ile ücretsiz hesap oluşturun
3. Email adresinizi doğrulayın

### Adım 2: API Key Oluşturun

1. Dashboard'da **"API Keys"** sekmesine gidin
2. **"Create API Key"** butonuna tıklayın
3. İsim verin (örn: "xpop-bot")
4. **Create** butonuna tıklayın
5. Oluşan anahtarı kopyalayın → `.env`'de `GROQ_API_KEY`

⚠️ **ÖNEMLİ**: Bu anahtarı kaydedin! Tekrar gösterilmez.

### Free Tier Limitler

Groq'un ücretsiz planında:
- Dakikada 30 istek
- Dakikada 6,000 token
- Sınırsız kullanım

Bu limitler X-Pop Bot için yeterlidir.

---

## 4. Bot Kurulumu

### Adım 1: Projeyi İndirin

```bash
git clone <repo-url>
cd X-pop
```

### Adım 2: Gerekli Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 3: .env Dosyasını Oluşturun

```bash
cp .env.example .env
```

Şimdi `.env` dosyasını düzenleyin:

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

Aldığınız anahtarları buraya yapıştırın.

### Adım 4: Ayarları Özelleştirin

`config/config.yaml` dosyasını açın:

```yaml
# İzlemek istediğiniz hesapları ekleyin
monitored_accounts:
  - "bbcturkce"
  - "cnnturk"
  - "NTV"
  # @ işareti olmadan, sadece kullanıcı adı

# Bot kişiliğini seçin
bot:
  personality: "yorumcu"  # 5 seçenek var, README'de detaylar
  check_interval: 5  # Kaç dakikada bir kontrol edilsin
  tweets_to_post_per_run: 1  # Her seferde kaç tweet atılsın
```

**Kişilik seçenekleri:**
- `yorumcu` - Yorumlu paylaşım
- `haber_duyurucu` - Düz haber
- `analist` - Derin analiz
- `mizahci` - Esprili
- `sakin_paylasimci` - Minimal

---

## 5. İlk Çalıştırma

### Test 1: API Bağlantılarını Test Edin

```bash
python -m src.main --test
```

**Başarılı çıktı:**
```
✅ Twitter API connection successful!
```

**Hata alırsanız:**
- `.env` dosyasındaki anahtarları kontrol edin
- Twitter App'inizde "Read and Write" izninin olduğunu kontrol edin

### Test 2: Dry Run (Tweet Atmadan)

```bash
python -m src.main --dry-run
```

Bu komut:
- Tweet'leri toplar
- AI ile tweet oluşturur
- Ama **gerçekten atmaz**

Çıktıyı kontrol edin, sorun yoksa devam edin.

### Test 3: Tek Seferlik Çalıştırma

```bash
python -m src.main --once
```

Bu komut:
- Tweet'leri toplar
- AI ile tweet oluşturur
- **Gerçekten atar** (dikkat!)
- Bir kez çalışır ve durur

### Sürekli Çalıştırma

```bash
python -m src.main
```

Bu komut bot'u sürekli çalıştırır (her 5 dakikada bir).

Durdurmak için: `Ctrl+C`

---

## 🎉 Tebrikler!

Bot artık çalışıyor! 🚀

### Sonraki Adımlar

1. **Log'ları takip edin**: `tail -f logs/bot.log`
2. **İstatistikleri kontrol edin**: Her çalıştırma sonunda gösterilir
3. **Kişiliği değiştirin**: `config/config.yaml`'da `personality` ayarını değiştirin
4. **Yeni hesaplar ekleyin**: `monitored_accounts` listesine ekleyin

---

## 🆘 Sorun mu Yaşıyorsunuz?

### Yaygın Hatalar

**1. "Module not found" hatası**

```bash
pip install -r requirements.txt
```

**2. "Authentication failed"**

- API anahtarlarını tekrar kontrol edin
- Twitter App'inizde "Read and Write" izninin olduğunu kontrol edin
- Anahtarları yeniden oluşturun

**3. "Rate limit exceeded"**

- Çok fazla istek attınız
- `check_interval`'i artırın (örn: 10 dakika)
- Birkaç saat bekleyin

**4. "No tweets collected"**

- İzlediğiniz hesapların son 24 saatte tweet attığını kontrol edin
- Hesap adlarının doğru olduğunu kontrol edin (@ olmadan)

---

## 📞 Destek

Hala sorun mu yaşıyorsunuz?

1. `logs/bot.log` dosyasını kontrol edin
2. Hatayı Google'da arayın
3. GitHub'da Issue açın

---

**İyi Tweetler! 🐦**
