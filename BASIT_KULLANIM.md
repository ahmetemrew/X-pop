# 🚀 Basit Kullanım - 3 Adım

**En kolay yöntem! Bot her zaman çalışır, sen sadece kontrol edersin.**

---

## ⚡ Adım 1: Kurulum

```bash
# Sunucuya bağlan
ssh kullanici@sunucu-ip
cd X-pop

# Her şeyi kur (Python yoksa kurar)
./install.sh

# Bot'u yapılandır
python3 setup.py

# Servisi kur (arka planda sürekli çalışır)
sudo ./service-install.sh
```

**Bu kadar! Bot artık çalışıyor. ✅**

---

## 🎮 Adım 2: Kontrol Et

Her SSH bağlantısında sadece şunu yaz:

```bash
twitter
```

**Menü gelecek:**

```
╔═══════════════════════════════════════════════════════╗
║              🤖  X-POP BOT KONTROL  🤖               ║
╚═══════════════════════════════════════════════════════╝

🟢 Bot Durumu: ÇALIŞIYOR
📊 CPU: 2.3%, RAM: 1.8%

📊 Hızlı İstatistikler:
  📤 Toplam Paylaşılan: 42
  📅 Bugün Paylaşılan: 8

🎮 Seçenekler:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1) 📊 Detaylı İstatistikler
  2) 📺 Canlı Log İzle
  3) 🔄 Bot'u Yeniden Başlat
  4) ⏸️  Bot'u Durdur
  5) ▶️  Bot'u Başlat
  6) ⚙️  Konfigürasyon Göster
  7) 📝 Son Log Satırları
  0) 🚪 Çıkış

Seçiminiz [0-7]:
```

**Seçeneğe basarsın, işini yapar, geri dönersin. Bot hiç durma z!**

---

## 📊 Adım 3: İzle (Opsiyonel)

### Hızlı Komutlar:

```bash
twitter              # Ana kontrol menüsü
./stats.sh           # Sadece istatistikler
./status.sh          # Sadece durum
./monitor.sh         # Canlı log izle
```

### Systemd Komutları (ileri seviye):

```bash
sudo systemctl status xpop-bot      # Durum
sudo systemctl restart xpop-bot     # Yeniden başlat
sudo journalctl -u xpop-bot -f      # Canlı log
```

---

## ✨ Özellikler

### ✅ Sürekli Çalışır

- SSH'ı kapat → **Bot çalışır**
- Bilgisayarını kapat → **Bot çalışır**
- Sunucu yeniden başla → **Bot otomatik başlar**

### ✅ Kolay Kontrol

- `twitter` yaz → Menü gelir
- Seçim yap → İşini yapar
- Çık → Bot çalışmaya devam eder

### ✅ Güvenli

- Bot arka planda
- Senin müdahalen yok
- Her şey otomatik

---

## 🔧 Ayar Değişikliği

```bash
# Config'i değiştir
nano config/config.yaml

# Bot'u yeniden başlat
twitter
# Menüden "3" seç (Yeniden Başlat)
```

---

## 🆘 Sorun Giderme

### Bot çalışmıyor?

```bash
twitter
# Menüden "5" seç (Başlat)
```

### Hata var mı?

```bash
twitter
# Menüden "7" seç (Son Loglar)
```

### Servis kurulmamış mı?

```bash
sudo ./service-install.sh
```

---

## 📱 Günlük Kullanım

### Sabah:

```bash
ssh kullanici@sunucu
twitter
# "1" bas → İstatistikleri gör
# "0" bas → Çık
exit
```

### Akşam:

```bash
ssh kullanici@sunucu
twitter
# "1" bas → Günün sonuçlarını gör
# "0" bas → Çık
exit
```

**Bu kadar basit! 🎉**

---

## 🎯 Özet

```bash
# KURULUM (Bir kez)
./install.sh
python3 setup.py
sudo ./service-install.sh

# KONTROL (Her zaman)
twitter

# BOT DURUR MU?
Hayır! Sürekli çalışır.

# SSH KAPANINCA?
Bot çalışmaya devam eder.

# İSTATİSTİK?
twitter → 1

# LOG?
twitter → 2 veya 7
```

---

**Daha basit olamaz! 🚀**
