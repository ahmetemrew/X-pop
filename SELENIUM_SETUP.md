# 🌐 Selenium Mode Kurulum Rehberi

Bu rehber, X-Pop Bot'u **Twitter API anahtarları olmadan** Selenium ile çalıştırmanız için gerekli adımları içerir.

## 🤔 Selenium Mode Nedir?

Selenium mode, Twitter API anahtarlarına ihtiyaç duymadan, web tarayıcısı otomasyonu kullanarak Twitter'ı kontrol eder.

### Avantajlar ✅

- **API anahtarı gerekmez** - Developer account'a gerek yok
- **Ücretsiz** - Hiçbir şey için ödeme yapmanıza gerek yok
- **Kolay kurulum** - Sadece kullanıcı adı ve şifre yeterli

### Dezavantajlar ⚠️

- **Daha yavaş** - Web scraping API'den daha yavaş
- **Daha riskli** - Twitter botu algılayabilir ve hesabınızı kısıtlayabilir
- **Daha az güvenilir** - Twitter arayüzü değişirse kod güncellenmesi gerekir
- **Captcha riski** - Bazen captcha çıkabilir

## 🚀 Kurulum

### 1. Chrome Kurulumu

Selenium, Chrome tarayıcısını kullanır. Sisteminizde Chrome olmalı.

#### Windows
[Chrome'u indirin](https://www.google.com/chrome/)

#### Linux (Ubuntu/Debian)
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

#### macOS
```bash
brew install --cask google-chrome
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

Bu komut otomatik olarak şunları yükler:
- selenium
- webdriver-manager (ChromeDriver'ı otomatik indirir)

### 3. .env Dosyasını Yapılandırın

`.env.example` dosyasını `.env` olarak kopyalayın:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin ve **Selenium Mode** bölümünü doldurun:

```env
# ============================================
# Selenium Mode (mode: "selenium" in config.yaml)
# ============================================
TWITTER_USERNAME=sizin_kullanici_adiniz
TWITTER_PASSWORD=sizin_sifreniz
TWITTER_EMAIL=sizin_email@example.com  # Opsiyonel ama önerilir

# Selenium Settings
SELENIUM_HEADLESS=true  # false yaparsanız tarayıcıyı görebilirsiniz
```

**ÖNEMLI**:
- `TWITTER_USERNAME`: @ işareti **olmadan** kullanıcı adınız
- `TWITTER_PASSWORD`: Twitter şifreniz
- `TWITTER_EMAIL`: Email doğrulaması gerekirse kullanılır (önerilen)
- `SELENIUM_HEADLESS=false`: Tarayıcıyı görmek isterseniz (debug için)

**Groq API** de gerekli:

```env
# AI Settings
GROQ_API_KEY=your_groq_api_key_here
```

[Groq Console](https://console.groq.com/) adresinden ücretsiz alabilirsiniz.

### 4. Config'i Selenium Mode'a Ayarlayın

`config/config.yaml` dosyasını açın ve mode'u değiştirin:

```yaml
# Çalışma Modu
mode: "selenium"  # "api" yerine "selenium" yazın
```

### 5. İlk Test

```bash
# Bağlantıyı test edin
python -m src.main --test
```

**İlk çalıştırmada:**
- Chrome tarayıcı açılacak (headless=false ise görünür)
- Twitter'a giriş yapılacak
- Cookies kaydedilecek (bir dahaki sefere daha hızlı)
- Login başarılı olursa ✅ mesajı alacaksınız

**Sorun çıkarsa:**
- `SELENIUM_HEADLESS=false` yapın ve tarayıcıyı izleyin
- `logs/bot.log` dosyasını kontrol edin

### 6. Dry Run

```bash
python -m src.main --dry-run
```

Bu komut:
- Belirlediğiniz hesaplardan tweet toplar
- AI ile tweet oluşturur
- Ama **gerçekten atmaz**

Çıktıyı kontrol edin, sorun yoksa devam edin.

### 7. Çalıştırın

```bash
# Tek seferlik
python -m src.main --once

# Sürekli çalıştır (5 dakikada bir)
python -m src.main
```

## 🔧 Ayarlar

### Headless Mode

**Headless Mode (Görünmez Tarayıcı)**

`.env` dosyasında:

```env
SELENIUM_HEADLESS=true  # Tarayıcı görünmez
```

**장avantajları:**
- Daha az kaynak kullanır
- Arka planda sessizce çalışır

**Debug Mode (Görünür Tarayıcı)**

```env
SELENIUM_HEADLESS=false  # Tarayıcı görünür
```

**Ne zaman kullanılır:**
- İlk kurulumda
- Sorun giderirken
- Login sorunları yaşandığında

### Rate Limiting

Selenium mode'da rate limiting'e dikkat edin. `config/config.yaml`:

```yaml
bot:
  check_interval: 10  # Selenium için 10+ dakika öneririz (API'de 5 dakika)
  tweets_to_post_per_run: 1  # Her seferde 1 tweet
```

## 🐛 Sorun Giderme

### 1. "Login failed" Hatası

**Sebep:** Yanlış kullanıcı adı/şifre veya Twitter güvenlik kontrolü

**Çözüm:**
1. `.env` dosyasındaki kullanıcı adı ve şifreyi kontrol edin
2. Twitter hesabınıza elle giriş yapın ve güvenli olduğunu onaylayın
3. 2FA (iki faktörlü doğrulama) kapalı olduğundan emin olun (Selenium 2FA'yı desteklemiyor)

### 2. "Email verification required"

**Sebep:** Twitter email doğrulaması istiyor

**Çözüm:**
```env
TWITTER_EMAIL=sizin_email@example.com
```

Email'inizi `.env` dosyasına ekleyin.

### 3. Captcha Çıkması

**Sebep:** Twitter botu algılamış olabilir

**Çözüm:**
1. Birkaç saat bekleyin
2. Manuel olarak Twitter'a giriş yapın ve captcha'yı çözün
3. `check_interval`'i artırın (örn: 15 dakika)
4. VPN kullanmayı düşünün

### 4. "ChromeDriver not found"

**Sebep:** ChromeDriver yüklenemedi

**Çözüm:**
```bash
pip install --upgrade webdriver-manager
```

### 5. "Session expired" / "Cookies invalid"

**Sebep:** Kaydedilen cookies geçersiz olmuş

**Çözüm:**
```bash
# Cookies'i sil
rm data/twitter_cookies.json

# Tekrar çalıştır (yeniden login olacak)
python -m src.main --test
```

### 6. Bot Çok Yavaş

**Sebep:** Selenium web scraping yavaştır

**İyileştirmeler:**
- Headless mode kullanın (`SELENIUM_HEADLESS=true`)
- `max_tweets_per_run` sayısını azaltın
- Daha az hesap izleyin
- Veya API mode'a geçin

### 7. Twitter Hesabım Kısıtlandı

**Sebep:** Twitter otomasyonu algılamış

**Önlemler:**
- Çok sık istek atmayın (`check_interval: 10+` dakika)
- Günde çok fazla tweet atmayın
- İnsan gibi davranın (rastgele gecikmeler)
- Bot hesabı kullanın (ana hesabınızı riske atmayın)

**Çözüm:**
- Twitter destek'e başvurun
- API mode'a geçmeyi düşünün (daha güvenli)

## 🔒 Güvenlik

### Şifre Güvenliği

`.env` dosyası Git'e push edilmez (`.gitignore`'da). Ama yine de:

1. **Ayrı bir bot hesabı kullanın** - Ana hesabınızı riske atmayın
2. **Güçlü şifre** - Benzersiz ve karmaşık bir şifre
3. **2FA kapalı** - Selenium 2FA'yı desteklemiyor
4. **Düzenli kontrol** - Hesabınızı düzenli kontrol edin

### Cookies

Cookies `data/twitter_cookies.json` dosyasında saklanır.

**Güvenlik:**
```bash
chmod 600 data/twitter_cookies.json  # Sadece sizin erişiminiz
```

**Cookies'i temizleme:**
```bash
rm data/twitter_cookies.json
```

## 🆚 API Mode vs Selenium Mode

| Özellik | API Mode | Selenium Mode |
|---------|----------|---------------|
| **Kurulum** | Zor (API key gerekli) | Kolay (sadece login) |
| **Hız** | Çok hızlı | Yavaş |
| **Güvenilirlik** | Çok güvenilir | Orta |
| **Rate Limit** | Yüksek (500k/ay) | Düşük (manuel gibi) |
| **Ban Riski** | Çok düşük | Orta |
| **Maliyet** | Ücretsiz (limitli) | Ücretsiz |
| **2FA Desteği** | Evet | Hayır |

### Ne zaman Selenium kullanmalı?

- Twitter API key'iniz yoksa
- Developer account alamıyorsanız
- API limitleri yetmiyorsa
- Sadece test etmek istiyorsanız

### Ne zaman API kullanmalı?

- Production kullanım için
- Güvenilir çalışma istiyorsanız
- Yüksek hacimli işlemler için
- Bot olduğunuzu gizlemenize gerek yoksa

## 💡 İpuçları

1. **İlk kullanımda `SELENIUM_HEADLESS=false` yapın** - Tarayıcıyı izleyin
2. **Bot hesabı kullanın** - Ana hesabınızı riske atmayın
3. **Cookies'i saklayın** - Her seferinde login olmasın
4. **Rate limiting'e uyun** - Twitter'ın kurallarına saygı gösterin
5. **Log'ları kontrol edin** - `logs/bot.log` sorunları gösterir
6. **Sakin olun** - Twitter sizi algılarsa hesabınız kısıtlanabilir

## 🔄 API Mode'a Geçiş

Selenium'dan API mode'a geçmek isterseniz:

1. [Twitter Developer Account oluşturun](https://developer.twitter.com/)
2. API anahtarlarını alın (SETUP_GUIDE.md'de detaylar)
3. `.env` dosyasına API anahtarlarını ekleyin
4. `config/config.yaml`'da mode'u değiştirin:
   ```yaml
   mode: "api"
   ```

---

**Başarılar! 🚀**

Selenium mode ile Twitter API anahtarı olmadan bot çalıştırabilirsiniz. Ama unutmayın: API mode daha güvenilir ve hızlıdır.
