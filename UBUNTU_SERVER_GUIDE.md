# 🖥️ Ubuntu Server Kurulum Rehberi

Bu rehber, X-Pop Bot'u Ubuntu sunucusunda kurmanız ve çalıştırmanız için hazırlanmıştır.

## 🚀 Hızlı Başlangıç (5 Dakika)

### 1. Sunucuya Dosyaları Yükleyin

```bash
# Git ile
git clone <repo-url>
cd X-pop

# Veya scp ile
scp -r X-pop/ user@your-server:/home/user/
```

### 2. Bağımlılıkları Yükleyin

```bash
# Python ve pip
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Chrome (Selenium için gerekli)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y

# Python bağımlılıkları
pip3 install -r requirements.txt
```

### 3. İnteraktif Kurulum Çalıştırın

```bash
python3 setup.py
```

Bu script size adım adım şunları soracak:

#### Adım 1: Twitter Hesap Bilgileri
```
❓ Twitter kullanıcı adınız (@ olmadan): kullanici_adi
❓ Twitter şifreniz: ********
❓ Twitter email adresiniz: email@example.com
❓ Tarayıcı görünmez modda çalışsın mı? [E/h]: E
```

#### Adım 2: Takip Edilecek Hesaplar
```
❓ Hesap #1 (@ olmadan): bbcturkce
✅ Eklendi: @bbcturkce
❓ Hesap #2 (@ olmadan): cnnturk
✅ Eklendi: @cnnturk
❓ Hesap #3 (@ olmadan): [Enter ile bitir]
```

#### Adım 3: Yapay Zeka Ayarları
```
1. Groq (Llama 3.1 70B) - ÖNERİLEN
   → Çok hızlı, ücretsiz, mükemmel Türkçe
   → https://console.groq.com/

❓ Groq API Key'iniz: gsk_xxxxxxxxxxxxxxxxxx
```

#### Adım 4: Bot Kişiliği
```
1. Yorumcu - Haberleri yorumlayarak paylaşır
2. Haber Duyurucu - Objektif, düz haber
3. Analist - Derin analiz ve içgörüler
4. Mizahçı - Esprili ama saygılı
5. Sakin Paylaşımcı - Minimal, az kelime

❓ Seçiminiz [1]: 1
✅ Seçildi: Yorumcu
```

#### Adım 5: Zamanlama
```
❓ Kontrol aralığı (dakika) [10]: 10
✅ Kontrol aralığı: Her 10 dakikada bir

❓ Her çalıştırmada kaç tweet atılsın? [1]: 1
✅ Tweet sayısı: Her çalıştırmada 1 tweet
```

### 4. Botu Başlatın

```bash
# Test edin
python3 -m src.main --test

# Dry run (tweet atmadan)
python3 -m src.main --dry-run

# Başlatın
python3 -m src.main
```

**TAM OTOMATİK:**

```bash
# start.sh her şeyi otomatik yapar
./start.sh
```

---

## 📁 Kurulum Sonrası Dosya Yapısı

```
X-pop/
├── .env                    # Otomatik oluşturuldu (hassas bilgiler)
├── config/
│   └── config.yaml        # Otomatik oluşturuldu
├── data/
│   ├── tweets.db          # SQLite database
│   └── twitter_cookies.json  # Login cookies
├── logs/
│   └── bot.log           # Bot logları
└── ...
```

---

## 🔄 Arka Planda Çalıştırma

### Option 1: Screen (Kolay)

```bash
# Screen oluştur
screen -S xpop

# Bot'u başlat
python3 -m src.main

# Detach: Ctrl+A sonra D
# Tekrar bağlan: screen -r xpop
# Kapat: exit
```

### Option 2: Nohup

```bash
# Arka planda başlat
nohup python3 -m src.main > bot.log 2>&1 &

# Process ID'yi kaydet
echo $! > bot.pid

# Durdurmak için
kill $(cat bot.pid)

# Logları izle
tail -f bot.log
```

### Option 3: Systemd (Production - Önerilen)

#### 1. Service Dosyasını Düzenleyin

`xpop-bot.service` dosyasını açın:

```bash
nano xpop-bot.service
```

Şu satırları kendi bilgilerinizle değiştirin:

```ini
User=ubuntu                                    # Kullanıcı adınız
WorkingDirectory=/home/ubuntu/X-pop            # Proje yolu
ExecStart=/home/ubuntu/X-pop/venv/bin/python -m src.main
StandardOutput=append:/home/ubuntu/X-pop/logs/bot.log
StandardError=append:/home/ubuntu/X-pop/logs/error.log
```

#### 2. Service'i Yükleyin

```bash
sudo cp xpop-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xpop-bot
sudo systemctl start xpop-bot
```

#### 3. Kontrol Edin

```bash
# Durum
sudo systemctl status xpop-bot

# Log'lar
sudo journalctl -u xpop-bot -f

# Başlat/Durdur/Restart
sudo systemctl start xpop-bot
sudo systemctl stop xpop-bot
sudo systemctl restart xpop-bot
```

---

## 🔧 Ayarları Değiştirme

### Kişiliği Değiştir

```bash
nano config/config.yaml
```

```yaml
bot:
  personality: "analist"  # Değiştir: yorumcu, haber_duyurucu, analist, mizahci, sakin_paylasimci
```

### Interval Değiştir

```yaml
bot:
  check_interval: 15  # 15 dakika
```

### Takip Edilen Hesapları Değiştir

```yaml
monitored_accounts:
  - "bbcturkce"
  - "yeni_hesap"
  - "baska_hesap"
```

Değişiklikten sonra restart edin:

```bash
sudo systemctl restart xpop-bot
```

---

## 📊 İzleme ve Yönetim

### Log'ları İzleme

```bash
# Bot log'ları
tail -f logs/bot.log

# Error log'ları
tail -f logs/error.log

# Systemd log'ları (systemd kullanıyorsanız)
sudo journalctl -u xpop-bot -f
```

### İstatistikler

Bot her çalıştırmada istatistikleri gösterir:

```
📊 Statistics:
   Total collected: 150
   Total posted: 25
   Unprocessed: 10
   Today's posts: 3
```

### Database'i Görüntüleme

```bash
# SQLite CLI ile
sqlite3 data/tweets.db

# Tablolar
.tables

# Son paylaşılan tweetler
SELECT * FROM posted_tweets ORDER BY posted_at DESC LIMIT 10;

# Çıkış
.quit
```

---

## 🛡️ Güvenlik ve İyileştirmeler

### 1. Firewall Ayarları

```bash
# UFW yükle
sudo apt install ufw

# SSH'a izin ver (dikkat!)
sudo ufw allow ssh

# Firewall'u aktif et
sudo ufw enable
```

### 2. Otomatik Güncelleme

```bash
# Unattended-upgrades
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 3. Fail2ban (Opsiyonel)

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Resource Limitleri

`xpop-bot.service` dosyasına ekleyin:

```ini
[Service]
MemoryLimit=512M
CPUQuota=50%
```

### 5. Log Rotation

```bash
sudo nano /etc/logrotate.d/xpop-bot
```

```
/home/ubuntu/X-pop/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ubuntu ubuntu
}
```

---

## 🐛 Sorun Giderme

### Bot Başlamıyor

```bash
# Log'ları kontrol et
tail -n 50 logs/bot.log

# Systemd hataları
sudo journalctl -u xpop-bot -n 50 --no-pager

# Manuel başlat ve hataları gör
python3 -m src.main --test
```

### Chrome/ChromeDriver Sorunu

```bash
# Chrome versiyonunu kontrol et
google-chrome --version

# ChromeDriver'ı yeniden yükle
pip3 install --upgrade webdriver-manager

# Manuel ChromeDriver indir
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

### Login Başarısız

```bash
# Cookies'i sil
rm data/twitter_cookies.json

# Headless=false yaparak tarayıcıyı görün
nano .env
# SELENIUM_HEADLESS=false

# Tekrar dene
python3 -m src.main --test
```

### Memory/CPU Sorunu

```bash
# Resource kullanımı
top
htop

# Bot'a limit koy (systemd)
nano /etc/systemd/system/xpop-bot.service
# MemoryLimit=512M ekle

sudo systemctl daemon-reload
sudo systemctl restart xpop-bot
```

---

## 🔄 Güncelleme

```bash
# Yeni versiyonu çek
git pull origin main

# Bağımlılıkları güncelle
pip3 install --upgrade -r requirements.txt

# Bot'u restart et
sudo systemctl restart xpop-bot
```

---

## 📈 Performans Optimizasyonu

### 1. Headless Mode Kullanın

`.env` dosyasında:

```env
SELENIUM_HEADLESS=true
```

### 2. Interval'i Artırın

Sunucu yükünü azaltmak için:

```yaml
bot:
  check_interval: 15  # 10 yerine 15 dakika
```

### 3. Tweet Sayısını Azaltın

```yaml
bot:
  tweets_to_post_per_run: 1  # Her seferde sadece 1 tweet
```

### 4. Takip Edilen Hesap Sayısını Azaltın

Daha az hesap = daha az kaynak kullanımı

---

## 🆘 Hızlı Komutlar

```bash
# Kurulum
python3 setup.py

# Başlat
./start.sh

# Test
python3 -m src.main --test

# Dry run
python3 -m src.main --dry-run

# Tek seferlik
python3 -m src.main --once

# Sürekli çalıştır
python3 -m src.main

# Log izle
tail -f logs/bot.log

# Systemd status
sudo systemctl status xpop-bot

# Restart
sudo systemctl restart xpop-bot
```

---

## 💡 İpuçları

1. **İlk kurulumda SELENIUM_HEADLESS=false yapın** - Tarayıcıyı görün
2. **Bot hesabı kullanın** - Ana hesabınızı riske atmayın
3. **Küçük başlayın** - Az hesap, uzun interval
4. **Log'ları düzenli kontrol edin**
5. **Sistemd kullanın** - Otomatik restart
6. **Backup alın** - database ve .env dosyalarını
7. **Screen/tmux kullanın** - SSH bağlantısı kopsa bile çalışır

---

## 📞 Destek

Sorun yaşıyorsanız:

1. `logs/bot.log` dosyasını kontrol edin
2. `python3 -m src.main --test` ile test edin
3. GitHub'da issue açın
4. SELENIUM_SETUP.md dosyasına bakın

---

**Sunucunuzda iyi tweetler! 🚀**
