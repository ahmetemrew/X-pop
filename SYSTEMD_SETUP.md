# Systemd ile X-Pop Bot Kurulumu

Bu rehber, X-Pop Bot'u Linux sistemde systemd servisi olarak çalıştırmanız için gerekli adımları içerir.

## Neden Systemd?

- ✅ Otomatik başlatma (sistem açılınca)
- ✅ Otomatik yeniden başlatma (çökerse)
- ✅ Log yönetimi
- ✅ Kolay kontrol (start/stop/restart)

## Kurulum Adımları

### 1. Service Dosyasını Düzenleyin

`xpop-bot.service` dosyasını açın ve düzenleyin:

```bash
nano xpop-bot.service
```

Değiştirmeniz gerekenler:

```ini
User=your-username          # Linux kullanıcı adınız
WorkingDirectory=/path/to/X-pop    # Proje klasörünün tam yolu
ExecStart=/path/to/X-pop/venv/bin/python -m src.main  # Python tam yolu
StandardOutput=append:/path/to/X-pop/logs/bot.log     # Log tam yolu
StandardError=append:/path/to/X-pop/logs/error.log    # Error log tam yolu
```

**Örnek:**

```ini
User=ubuntu
WorkingDirectory=/home/ubuntu/X-pop
ExecStart=/home/ubuntu/X-pop/venv/bin/python -m src.main
StandardOutput=append:/home/ubuntu/X-pop/logs/bot.log
StandardError=append:/home/ubuntu/X-pop/logs/error.log
```

### 2. Virtual Environment Oluşturun

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 3. Service Dosyasını Kopyalayın

```bash
sudo cp xpop-bot.service /etc/systemd/system/
```

### 4. Systemd'yi Reload Edin

```bash
sudo systemctl daemon-reload
```

### 5. Servisi Etkinleştirin

```bash
# Servisi etkinleştir (sistem açılınca otomatik başlasın)
sudo systemctl enable xpop-bot

# Servisi başlat
sudo systemctl start xpop-bot
```

## Kullanım

### Servisi Başlat

```bash
sudo systemctl start xpop-bot
```

### Servisi Durdur

```bash
sudo systemctl stop xpop-bot
```

### Servisi Yeniden Başlat

```bash
sudo systemctl restart xpop-bot
```

### Servis Durumunu Kontrol Et

```bash
sudo systemctl status xpop-bot
```

**Çıktı örneği:**

```
● xpop-bot.service - X-Pop Bot - AI-powered Twitter/X Bot
   Loaded: loaded (/etc/systemd/system/xpop-bot.service; enabled)
   Active: active (running) since Mon 2025-01-15 10:30:00 UTC; 2h 15min ago
 Main PID: 12345 (python)
   Status: "Running..."
```

### Log'ları İzle

```bash
# Bot log'larını canlı izle
tail -f logs/bot.log

# Error log'larını izle
tail -f logs/error.log

# Systemd log'larını izle
sudo journalctl -u xpop-bot -f
```

### Servisi Devre Dışı Bırak

```bash
# Servisi durdur
sudo systemctl stop xpop-bot

# Otomatik başlamayı kapat
sudo systemctl disable xpop-bot
```

## Sorun Giderme

### Servis başlamıyor

```bash
# Detaylı log'ları kontrol edin
sudo journalctl -u xpop-bot -n 50 --no-pager

# Servis durumunu kontrol edin
sudo systemctl status xpop-bot
```

### Yaygın hatalar:

**1. "Permission denied"**

```bash
# Log klasörüne izin verin
chmod 755 logs/
chmod 644 logs/*.log
```

**2. "Python not found"**

- `ExecStart` yolunu kontrol edin
- `which python` komutuyla Python yolunu bulun

**3. ".env not found"**

- `.env` dosyasının proje klasöründe olduğunu kontrol edin
- İzinleri kontrol edin: `chmod 600 .env`

**4. "Import error"**

- Virtual environment'ın doğru kurulu olduğunu kontrol edin
- Bağımlılıkları yeniden yükleyin:
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## Log Rotation (Opsiyonel)

Log dosyalarının çok büyümesini önlemek için:

```bash
sudo nano /etc/logrotate.d/xpop-bot
```

İçerik:

```
/path/to/X-pop/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 your-username your-username
}
```

## Servis Yönetimi İpuçları

### Servis başlatma sırasını kontrol et

```bash
sudo systemctl list-dependencies xpop-bot
```

### Servis çöktüğünde email gönder

`xpop-bot.service` dosyasına ekleyin:

```ini
[Service]
OnFailure=failure-notification@%n.service
```

### Resource limitleri belirle

```ini
[Service]
MemoryLimit=500M
CPUQuota=50%
```

## Güvenlik Önerileri

1. **Ayrı kullanıcı oluşturun:**

```bash
sudo useradd -r -s /bin/false xpop-bot
sudo chown -R xpop-bot:xpop-bot /path/to/X-pop
```

2. **.env dosyasını koruyun:**

```bash
chmod 600 .env
```

3. **SELinux/AppArmor kullanın** (ileri seviye)

---

**Servisiniz artık hazır! 🎉**

Sistem açıldığında otomatik olarak başlayacak ve çökerse kendini yeniden başlatacak.
