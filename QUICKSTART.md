# ⚡ Hızlı Başlangıç Rehberi

Ubuntu sunucunda 5 dakikada X-Pop Bot kurup çalıştırın!

## 🚀 Adım 1: Dosyaları Yükleyin

```bash
# Sunucuya SSH ile bağlanın
ssh kullanici@sunucu-ip

# Projeyi yükleyin (git veya scp ile)
git clone <repo-url> X-pop
cd X-pop
```

## 🔧 Adım 2: Otomatik Kurulum

**Tek komut ile her şey hazır:**

```bash
./install.sh
```

Bu script:
- ✅ Python yoksa kurar
- ✅ Chrome kurar (Selenium için)
- ✅ Tüm bağımlılıkları yükler
- ✅ Klasörleri oluşturur
- ✅ Her şeyi hazırlar

## ⚙️ Adım 3: Bot'u Yapılandırın

```bash
python3 setup.py
```

İnteraktif sorular gelecek:
- Twitter kullanıcı adı/şifre
- Takip edilecek hesaplar
- Groq API key
- Kişilik seçimi
- Zamanlama

## 🎮 Adım 4: Bot'u Başlatın

### Screen ile (Önerilen - SSH kapansa çalışır)

```bash
screen -S xpop
./start.sh

# Ctrl+A+D ile çıkın (bot çalışmaya devam eder)
```

### Direkt Başlatma

```bash
./start.sh
```

---

## 📊 İstatistikleri Görüntüleme

### SSH'a Yeniden Bağlandığınızda

```bash
# Detaylı istatistikler
./stats.sh

# Bot durumu
./status.sh

# Canlı log izleme
./monitor.sh

# Screen'e geri dön (bot ekranı)
screen -r xpop
```

### Stats Çıktı Örneği:

```
╔═══════════════════════════════════════════════════════╗
║              📊  X-POP BOT İSTATİSTİKLER              ║
╚═══════════════════════════════════════════════════════╝

📈 Genel İstatistikler:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📥 Toplanan Tweet: 245
  📤 Paylaşılan Tweet: 42
  ⏳ İşlenmemiş: 15
  📅 Bugün Paylaşılan: 8

⏰ Son Aktiviteler:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Son 5 Paylaşılan Tweet:
Tweet                         Kişilik        Zaman
----------------------------  ------------  -------------------
Ekonomi verileri açıklan...  yorumcu       2025-01-15 14:32:15
Son dakika: Yeni gelişme...  haber_duy...  2025-01-15 14:18:42
...
```

### Status Çıktı Örneği:

```
╔═══════════════════════════════════════════════════════╗
║              🔍  X-POP BOT DURUMU                     ║
╚═══════════════════════════════════════════════════════╝

🤖 Bot Durumu:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Bot çalışıyor (screen session: xpop)
  ✅ Python process aktif (PID: 12345)
  📊 CPU: 2.3%, RAM: 1.8%

⚙️  Konfigürasyon:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ config.yaml mevcut
  🔧 Mod: selenium
  🎭 Kişilik: yorumcu
  ⏰ Kontrol Aralığı: 10 dakika

📝 Log Durumu:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Log dosyası: 2.3M (5847 satır)
  🕐 Son log: 2025-01-15 14:35
```

---

## 🎮 Temel Komutlar

### Bot Yönetimi

```bash
./start.sh          # Bot'u başlat
./status.sh         # Durumu kontrol et
./stats.sh          # İstatistikleri gör
./monitor.sh        # Canlı log izle
```

### Screen Komutları

```bash
screen -S xpop       # Yeni session oluştur
screen -r xpop       # Session'a bağlan
Ctrl+A+D             # Session'dan çık (bot çalışmaya devam eder)
screen -list         # Tüm session'ları listele
```

### Log Komutları

```bash
tail -f logs/bot.log           # Canlı log izle
tail -100 logs/bot.log         # Son 100 satır
grep "ERROR" logs/bot.log      # Hataları bul
```

### Database Sorguları

```bash
# SQLite ile database'e bak
sqlite3 data/tweets.db

# Toplam tweet sayısı
SELECT COUNT(*) FROM posted_tweets;

# Bugünkü tweetler
SELECT content, posted_at FROM posted_tweets
WHERE DATE(posted_at) = DATE('now')
ORDER BY posted_at DESC;

# Çıkış
.quit
```

---

## 🔄 SSH Kapansa Bile Çalışma

### Screen Kullanımı (En Kolay)

```bash
# 1. Screen session oluştur
screen -S xpop

# 2. Bot'u başlat
./start.sh

# 3. Ctrl+A+D ile çık
# Bot arka planda çalışmaya devam eder

# 4. SSH'a tekrar bağlandığında
screen -r xpop     # Geri dön
./status.sh        # veya sadece duruma bak
./stats.sh         # veya istatistiklere bak
```

### Systemd (Production için)

```bash
# Systemd servis olarak kur
sudo cp xpop-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/xpop-bot.service  # Yolları düzenle
sudo systemctl daemon-reload
sudo systemctl enable xpop-bot
sudo systemctl start xpop-bot

# Kontrol
sudo systemctl status xpop-bot
```

---

## 📱 Günlük Rutin

### Her Gün Yapmanız Gerekenler

**1. Sabah Kontrolü:**
```bash
ssh kullanici@sunucu
./status.sh    # Bot çalışıyor mu?
./stats.sh     # Dün kaç tweet attı?
```

**2. Gerekirse Müdahale:**
```bash
screen -r xpop         # Bot ekranını görüntüle
tail -50 logs/bot.log  # Son log'lara bak
```

**3. Ayar Değişikliği:**
```bash
nano config/config.yaml  # Ayarları değiştir
screen -r xpop           # Bot ekranına gir
Ctrl+C                   # Bot'u durdur
./start.sh               # Yeniden başlat
Ctrl+A+D                 # Çık
```

---

## ⚠️ Sorun Giderme

### Bot Çalışmıyor

```bash
./status.sh              # Durum kontrolü
tail -50 logs/bot.log    # Hataları oku
python3 -m src.main --test  # Manuel test
```

### Screen Session Yok

```bash
screen -list             # Session'ları listele
screen -S xpop ./start.sh  # Yeni session başlat
```

### Database Hatası

```bash
# Database'i sıfırla (dikkat: tüm veriler silinir!)
rm data/tweets.db
python3 -m src.main --test
```

### Log Dosyası Çok Büyüdü

```bash
# Log'u temizle
> logs/bot.log

# Veya eski log'u yedekle
mv logs/bot.log logs/bot.log.old
```

---

## 🎯 İpuçları

1. **Screen her zaman kullanın** - SSH kapansa bot çalışır
2. **Günde 1 kez ./status.sh çalıştırın** - Her şey yolunda mı?
3. **./stats.sh ile başarıyı izleyin** - Kaç tweet paylaştı?
4. **Ayarları küçük değişikliklerle test edin** - Interval, kişilik, vs.
5. **Log'ları düzenli okuyun** - Hatayı erken yakalayın

---

## 📋 Özet - Tek Sayfa

```bash
# KURULUM
./install.sh
python3 setup.py

# BAŞLATMA
screen -S xpop
./start.sh
Ctrl+A+D

# İZLEME (SSH'a tekrar bağlandığında)
./status.sh      # Durum
./stats.sh       # İstatistikler
./monitor.sh     # Canlı izle
screen -r xpop   # Bot ekranı

# DURDURMA
screen -r xpop   # Ekrana gir
Ctrl+C           # Durdur
```

**Bu kadar! Hızlı ve kolay. 🚀**
