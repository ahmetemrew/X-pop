# 🔧 X-Pop Bot - Kapsamlı Fix Rehberi

## Sorun

Bot sürekli crash ediyor. Ana sebepler:
1. **Groq 0.9.0 eski** - Yeni API ile uyumsuz
2. **Config eksiklikleri** - temperature, duplicate_detection gibi
3. **ChromeDriver hataları** - Path ve permission sorunları
4. **Error handling yetersiz** - Hatalar düzgün yakalanmıyor

## ✅ TEK SEFERDE ÇÖZÜM

### 1. Sunucuya Bağlan

```bash
ssh root@sunucun_ip
cd /root/X-pop  # veya bot'un kurulu olduğu dizin
```

### 2. Fix Script'i Çalıştır

```bash
sudo ./fix-all.sh
```

Bu script **TÜM** sorunları otomatik çözecek:
- ✅ Bot'u durduracak
- ✅ Groq'u 0.11.0+ sürümüne güncelleyecek
- ✅ Tüm Python paketlerini güncelleyecek
- ✅ Config'i kontrol edip eksikleri ekleyecek
- ✅ Sistem testlerini yapacak
- ✅ Bot'u başlatacak

### 3. Durumu Kontrol Et

```bash
# Bot durumunu gör
twitter

# Canlı log izle
journalctl -u xpop-bot -f
```

## 🧪 Manuel Test (Opsiyonel)

Eğer önce test etmek istersen:

```bash
./test-bot.sh
```

Bu script:
- Python paketlerini kontrol eder
- Config dosyalarını kontrol eder
- AI Generator'ı test eder
- Database'i test eder

## 📋 Neler Değişti?

### 1. `requirements.txt`
```diff
- groq==0.9.0
+ groq>=0.11.0
```

### 2. `src/ai_generator.py`
- ✅ Groq client initialization düzeltildi
- ✅ Better error handling eklendi
- ✅ Logging iyileştirildi

### 3. `src/bot.py`
- ✅ AI generator init'e validation eklendi
- ✅ Environment variable kontrolleri eklendi
- ✅ Detaylı error logging eklendi

### 4. `src/selenium_twitter_client.py`
- ✅ ChromeDriver path detection iyileştirildi
- ✅ Ek stability options eklendi
- ✅ Better error handling

### 5. `config/config.yaml`
Script otomatik şunları ekler:
- `ai.temperature: 0.7`
- `duplicate_detection` section
- `database.path`
- `selenium` settings
- Eksik olan diğer tüm alanlar

## 🚨 Sık Sorunlar ve Çözümleri

### Bot hala crash ediyorsa

1. **Log'ları kontrol et:**
```bash
journalctl -u xpop-bot -n 100 --no-pager
```

2. **Manuel başlatıp hatayı gör:**
```bash
sudo systemctl stop xpop-bot
cd /root/X-pop
source venv/bin/activate
python -m src.main --test
```

3. **Groq API key'i kontrol et:**
```bash
cat .env | grep GROQ_API_KEY
```

### ChromeDriver hatası

```bash
# ChromeDriver'ı temizle ve yeniden yüklet
rm -rf ~/.wdm/
```

### Twitter login başarısız

1. **Şifreyi kontrol et:**
```bash
nano .env
# TWITTER_USERNAME ve TWITTER_PASSWORD'u kontrol et
```

2. **Cookie'leri temizle:**
```bash
rm -f data/twitter_cookies.json
sudo systemctl restart xpop-bot
```

3. **Headless mode'u kapat (debug için):**
```bash
nano config/config.yaml
# selenium.headless: false yap
```

## 📊 Başarı Göstergeleri

Eğer her şey düzgün çalışıyorsa şunları görmelisin:

```
✅ Bot çalışıyor (systemctl status xpop-bot)
✅ Groq version >= 0.11.0
✅ Twitter login başarılı
✅ Crash yok (20+ saniye çalışıyor)
✅ Log'da "Cycle completed successfully"
```

## 🔄 Rollback (Geri Alma)

Eğer bir şeyler ters giderse:

```bash
# Bot'u durdur
sudo systemctl stop xpop-bot

# Git'ten eski haline dön
git stash

# Veya son commit'e dön
git reset --hard HEAD~1
```

## 💡 İpuçları

1. **Her zaman log'ları takip et:**
   ```bash
   journalctl -u xpop-bot -f
   ```

2. **Periyodik restart (opsiyonel):**
   ```bash
   # Günde bir restart (cache temizliği için)
   crontab -e
   0 4 * * * systemctl restart xpop-bot
   ```

3. **Backup al:**
   ```bash
   tar -czf xpop-backup-$(date +%Y%m%d).tar.gz data/ config/ .env
   ```

## 📞 Yardım

Hala sorun yaşıyorsan:
1. `journalctl -u xpop-bot -n 200 > bot-error.log` çalıştır
2. `bot-error.log` dosyasını paylaş
3. Python versiyonu: `python3 --version`
4. OS versiyonu: `cat /etc/os-release`

---

**Oluşturulma:** 2025-01-07
**Versiyon:** 2.0 - Comprehensive Fix
