# 🛡️ X-Pop Bot - Garanti Sistemi

## ✅ İmplementasyon Garantileri

Bu dokümantasyonda sistemde yapılan tüm güvenlik ve stabilite önlemleri listelenmiştir.

### 1. Network İletişimi

**Problem:** API çağrıları zaman aşımına uğrayabilir, ağ kesintileri olabilir.

**Çözüm:**
- ✅ Tüm Groq API çağrılarında otomatik 3 deneme
- ✅ Exponential backoff (2s, 4s, 8s gecikme)
- ✅ 30 saniyelik timeout
- ✅ Boş response kontrolü
- ✅ Detaylı hata loglama

**Dosya:** `src/ai_generator.py` - `generate_tweet()` metodu

```python
@retry_on_exception(max_attempts=3, delay=2.0, backoff=2.0)
def call_groq_api():
    response = self.client.chat.completions.create(
        ...,
        timeout=30.0
    )
```

---

### 2. Selenium & ChromeDriver

**Problem:** Chrome/Selenium crash olabilir, timeout olabilir.

**Çözüm:**
- ✅ Page load timeout: 60 saniye
- ✅ Element wait timeout: 30 saniye
- ✅ Implicit wait: 10 saniye
- ✅ ChromeDriver path detection iyileştirildi
- ✅ Otomatik executable permission ayarlama
- ✅ Login başarısızlığında driver cleanup
- ✅ Ek stability flags eklendi

**Dosya:** `src/selenium_twitter_client.py`

```python
self.wait = WebDriverWait(self.driver, 30)
self.driver.set_page_load_timeout(60)
self.driver.implicitly_wait(10)
```

---

### 3. Config Yönetimi

**Problem:** Eksik config değerleri, geçersiz formatlar.

**Çözüm:**
- ✅ Tüm config değerleri validate edilir
- ✅ Eksik değerler için otomatik defaults
- ✅ Type checking (int/float/string/list)
- ✅ Range validation (temperature 0-2, pozitif sayılar)
- ✅ Geçersiz mod değerleri düzeltilir
- ✅ Boş/null değerler handle edilir

**Dosya:** `src/utils.py` - `validate_config()`

**Test Edilen Alanlar:**
- mode, monitored_accounts, bot.*, ai.*, duplicate_detection, database, selenium, human_behavior, images

---

### 4. Database İşlemleri

**Problem:** SQLite lock, concurrent access, corruption.

**Çözüm:**
- ✅ Context manager ile otomatik connection yönetimi
- ✅ WAL mode (Write-Ahead Logging) aktif
- ✅ 30 saniyelik connection timeout
- ✅ Otomatik rollback on error
- ✅ Connection pooling benzeri yapı
- ✅ Tüm hatalarda detaylı loglama

**Dosya:** `src/database.py`

```python
@contextmanager
def _get_connection(self, timeout: float = 30.0):
    conn = sqlite3.connect(self.db_path, timeout=timeout)
    conn.execute('PRAGMA journal_mode=WAL')
```

---

### 5. Graceful Shutdown

**Problem:** Bot'un ani kapanması, resource leak, zombie processes.

**Çözüm:**
- ✅ SIGTERM ve SIGINT signal handlers
- ✅ Otomatik cleanup on exit (atexit)
- ✅ Selenium driver düzgün kapatılır
- ✅ Database connections kapatılır
- ✅ Temporary files temizlenir
- ✅ Shutdown flag ile çalışma döngüsü durdurulur

**Dosya:** `src/bot.py`

```python
signal.signal(signal.SIGTERM, self._signal_handler)
signal.signal(signal.SIGINT, self._signal_handler)
atexit.register(self.cleanup)
```

---

### 6. Disk Alanı Yönetimi

**Problem:** Log/download klasörü dolabilir.

**Çözüm:**
- ✅ Her başlangıçta disk alanı kontrolü (min 100MB)
- ✅ Otomatik log temizliği (7+ gün önce)
- ✅ Otomatik download temizliği (1+ gün önce)
- ✅ Yetersiz alan uyarısı
- ✅ Periyodik cleanup

**Dosyalar:** `src/utils.py`, `src/bot.py`

```python
check_disk_space(min_mb=100)
cleanup_old_files('logs', days=7, pattern='*.log')
cleanup_old_files('downloads', days=1, pattern='*')
```

---

### 7. Text Sanitization

**Problem:** Özel karakterler, null bytes, aşırı uzun text.

**Çözüm:**
- ✅ Null byte ve control character temizleme
- ✅ Whitespace normalization
- ✅ Otomatik truncate (280 karakter)
- ✅ Min length validation (10 karakter)
- ✅ Empty response kontrolü

**Dosya:** `src/utils.py` - `sanitize_text()`

---

### 8. Error Handling & Logging

**Problem:** Sessiz hatalar, debug zorluğu.

**Çözüm:**
- ✅ Her kritik noktada try-except
- ✅ `exc_info=True` ile full stack trace
- ✅ Log levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Dosya + console logging
- ✅ Timestamp'li log mesajları
- ✅ Her işlem için progress logging

**Tüm dosyalarda:**
```python
except Exception as e:
    self.logger.error(f"Error: {e}", exc_info=True)
```

---

### 9. Health Monitoring

**Problem:** Bot çalışıyor gibi görünüp aslında hatalı durumda olabilir.

**Çözüm:**
- ✅ `is_healthy()` metodu ile sağlık kontrolü
- ✅ Disk alanı kontrolü
- ✅ Database bağlantısı kontrolü
- ✅ AI generator kontrolü
- ✅ Twitter client kontrolü
- ✅ Config yüklenme kontrolü
- ✅ Her cycle başında health check

**Dosya:** `src/bot.py` - `is_healthy()`

---

### 10. File I/O Safety

**Problem:** Dosya kilitleri, permission errors, concurrent access.

**Çözüm:**
- ✅ `safe_file_operation()` wrapper ile 3 deneme
- ✅ Exponential backoff dosya işlemlerinde
- ✅ IOError, OSError, PermissionError yakalama
- ✅ Otomatik directory oluşturma
- ✅ File lock handling

**Dosya:** `src/utils.py` - `safe_file_operation()`

---

### 11. Personalities Fallback

**Problem:** personalities.yaml eksik/bozuk olabilir.

**Çözüm:**
- ✅ Dosya bulunamazsa default personality
- ✅ Geçersiz YAML'da default personality
- ✅ Boş dosyada default personality
- ✅ Dosya okuma hatasında graceful fallback

**Dosya:** `src/ai_generator.py` - `_get_default_personalities()`

---

### 12. Rate Limiting Awareness

**Problem:** Twitter/Groq rate limit'e takılabilir.

**Çözüm:**
- ✅ Human behavior simulation ile natural pacing
- ✅ Random delays between actions
- ✅ Configurable check intervals
- ✅ Random skip chance (%5)
- ✅ Working hours simulation

**Dosya:** `src/human_behavior.py`

---

### 13. Memory Management

**Problem:** Memory leaks, orphan processes.

**Çözüm:**
- ✅ Context managers ile otomatik cleanup
- ✅ Selenium driver her zaman kapatılır
- ✅ Database connections her zaman kapatılır
- ✅ Temporary files silinir
- ✅ Image cleanup after posting
- ✅ Old file periodic cleanup

---

### 14. Concurrent Safety

**Problem:** Multiple bot instance çalışırsa conflict.

**Çözüm:**
- ✅ SQLite WAL mode (concurrent reads OK)
- ✅ Database timeout handling
- ✅ File locking aware operations
- ✅ Systemd service tek instance garantisi

**Not:** Systemd service zaten tek instance garantiler ama database concurrent-safe.

---

### 15. Validation & Type Safety

**Problem:** Runtime'da geçersiz değerler, type errors.

**Çözüm:**
- ✅ Type hints tüm fonksiyonlarda
- ✅ Config validation with defaults
- ✅ None checks before use
- ✅ Empty list/dict checks
- ✅ Numeric range validation
- ✅ String length validation

---

## 🧪 Test Stratejisi

### Otomatik Testler

`test-bot.sh` aşağıdakileri kontrol eder:
1. Python packages yüklü mü?
2. Config dosyaları mevcut mu?
3. Environment variables set mi?
4. AI generator initialize olabiliyor mu?
5. Database bağlantısı çalışıyor mu?

### Manuel Test Checklist

- [ ] Bot başlatılıyor mu?
- [ ] Twitter login çalışıyor mu?
- [ ] AI tweet üretiyor mu?
- [ ] Tweet posting çalışıyor mu?
- [ ] Graceful shutdown çalışıyor mu?
- [ ] Health check pass ediyor mu?
- [ ] Log rotation çalışıyor mu?

---

## 📊 İzleme (Monitoring)

### Log Dosyaları

```bash
# Canlı log takibi
journalctl -u xpop-bot -f

# Son 100 satır
journalctl -u xpop-bot -n 100

# Hata logları
journalctl -u xpop-bot | grep ERROR

# Belirli zaman aralığı
journalctl -u xpop-bot --since "1 hour ago"
```

### Health Check

```bash
# Bot sağlıklı mı?
systemctl status xpop-bot

# Test mode
cd /root/X-pop
source venv/bin/activate
python -m src.main --test
```

### Disk Kullanımı

```bash
# Disk durumu
df -h

# Log boyutu
du -sh /root/X-pop/logs

# Database boyutu
du -sh /root/X-pop/data
```

---

## 🚨 Acil Durum Prosedürleri

### Bot Crash Olursa

1. Log'ları incele:
   ```bash
   journalctl -u xpop-bot -n 200 > /tmp/crash-log.txt
   ```

2. Database check:
   ```bash
   sqlite3 data/tweets.db "PRAGMA integrity_check;"
   ```

3. Disk alanı:
   ```bash
   df -h
   du -sh logs/ data/ downloads/
   ```

4. Restart:
   ```bash
   systemctl restart xpop-bot
   ```

### Rate Limit Olursa

1. Config'de interval'i artır:
   ```yaml
   bot:
     check_interval: 10  # 5'ten 10'a çıkar
   ```

2. Random timing'i aktifleştir:
   ```yaml
   human_behavior:
     random_timing:
       enabled: true
       min_extra_minutes: 10
       max_extra_minutes: 30
   ```

### Memory Problemi Olursa

1. Chrome memory kullanımını sınırla:
   ```python
   # selenium_twitter_client.py'de:
   chrome_options.add_argument("--disable-dev-shm-usage")
   chrome_options.add_argument("--disable-gpu")
   ```

2. Periyodik restart:
   ```bash
   # Crontab'a ekle
   0 */6 * * * systemctl restart xpop-bot
   ```

---

## ✅ Garanti Özeti

| Kategori | Durum | Detay |
|----------|-------|-------|
| Network Retry | ✅ | 3 deneme, exponential backoff |
| Timeouts | ✅ | Tüm işlemlerde timeout var |
| Config Validation | ✅ | Tam validation + defaults |
| Database Safety | ✅ | Context managers + WAL mode |
| Graceful Shutdown | ✅ | Signal handlers + cleanup |
| Disk Management | ✅ | Otomatik temizlik + kontrol |
| Error Handling | ✅ | Her yerde try-except + logging |
| Health Monitoring | ✅ | is_healthy() metodu |
| File I/O Safety | ✅ | Retry logic + error handling |
| Memory Management | ✅ | Context managers + cleanup |
| Type Safety | ✅ | Type hints + validation |
| Concurrent Safety | ✅ | WAL mode + timeouts |

---

**Son Güncelleme:** 2025-01-07
**Versiyon:** 2.1 - Production Ready
**Status:** ✅ GARANTİ SİSTEMİ AKTİF
