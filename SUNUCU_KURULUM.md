# 🚀 Sunucuya Kurulum - Komple Rehber

## 📋 Ön Bilgi

- **Sunucu**: Ubuntu (18.04+)
- **Kullanıcı**: Root veya sudo yetkisi olan kullanıcı
- **Gereksinimler**: İnternet bağlantısı

---

## ⚡ Hızlı Kurulum (3 Komut)

### 1. Sunucuya Bağlan ve Repoyu Yükle

```bash
# SSH ile bağlan
ssh root@sunucu-ip

# Veya normal kullanıcıyla
ssh kullanici@sunucu-ip

# Repoyu indir (GitHub/GitLab'dan)
git clone https://github.com/kullanici/X-pop.git
cd X-pop

# VEYA wget ile (zip olarak)
wget https://github.com/kullanici/X-pop/archive/main.zip
unzip main.zip
cd X-pop-main
```

### 2. Otomatik Kurulum

```bash
# Her şeyi kurar (Python, Chrome, vs.)
./install.sh
```

### 3. Bot'u Yapılandır ve Başlat

```bash
# İnteraktif yapılandırma
python3 setup.py

# Systemd service olarak kur (sürekli çalışır)
./service-install.sh

# İşte bu kadar! ✅
```

---

## 📝 Detaylı Adımlar

### Adım 1: Sunucuya Bağlanma

```bash
ssh root@YOUR_SERVER_IP
# Veya
ssh username@YOUR_SERVER_IP
```

**İlk bağlantıda:**
- Şifre soracak, gir
- Veya SSH key kullanıyorsan otomatik girecek

### Adım 2: Repo'yu Yükleme

**Seçenek A: Git ile (Önerilen)**

```bash
# Git yoksa kur
apt install git -y  # Root ise
# veya
sudo apt install git -y  # Normal kullanıcıysa

# Repo'yu kopyala
cd ~
git clone https://github.com/KULLANICI_ADINIZ/X-pop.git
cd X-pop
```

**Seçenek B: Dosyaları Manuel Yükle**

```bash
# Bilgisayarından sunucuya
# Terminalden (bilgisayarında):
scp -r X-pop/ root@sunucu-ip:/root/

# Sonra sunucuda:
cd /root/X-pop
```

**Seçenek C: Wget ile**

```bash
wget https://github.com/KULLANICI/X-pop/archive/refs/heads/main.zip
unzip main.zip
cd X-pop-main
```

### Adım 3: Kurulum

```bash
# Script'i çalıştırılabilir yap
chmod +x *.sh

# Otomatik kurulum (Python + Chrome + her şey)
./install.sh
```

**Bu script:**
- ✅ Python'ı kurar (yoksa)
- ✅ Chrome'u kurar
- ✅ Gerekli paketleri yükler
- ✅ Virtual environment oluşturur
- ✅ Python bağımlılıklarını kurar

**Çıktı:**
```
╔═══════════════════════════════════════════════════════╗
║     🚀  X-POP BOT - UBUNTU KURULUM  🚀               ║
╚═══════════════════════════════════════════════════════╝

[1/6] Sistem güncellemesi yapılıyor...
[2/6] Python kontrol ediliyor...
✅ Python kuruldu!
[3/6] Google Chrome kontrol ediliyor...
✅ Chrome kuruldu!
[4/6] Gerekli sistem paketleri kuruluyor...
[5/6] Python virtual environment oluşturuluyor...
[6/6] Python bağımlılıkları yükleniyor...

✅  KURULUM TAMAMLANDI!
```

### Adım 4: Bot Yapılandırma

```bash
python3 setup.py
```

**Sorular gelecek:**

```
❓ Twitter kullanıcı adınız (@ olmadan): bot_hesabi
❓ Twitter şifreniz: ********
❓ Twitter email adresiniz: bot@email.com
❓ Tarayıcı görünmez modda çalışsın mı? [E/h]: E

❓ Hesap #1 (@ olmadan): bbcturkce
✅ Eklendi: @bbcturkce
❓ Hesap #2 (@ olmadan): cnnturk
✅ Eklendi: @cnnturk
❓ Hesap #3 (@ olmadan): [Enter - bitti]

❓ Groq API Key'iniz: gsk_xxxxxxxxxxxxxx

1. Yorumcu - Haberleri yorumlayarak paylaşır
2. Haber Duyurucu - Objektif, düz haber
3. Analist - Derin analiz
4. Mizahçı - Esprili
5. Sakin Paylaşımcı - Minimal

❓ Seçiminiz [1]: 1

❓ Kontrol aralığı (dakika) [10]: 10
❓ Her çalıştırmada kaç tweet atılsın? [1]: 1

✅ KURULUM TAMAMLANDI!
```

### Adım 5: Systemd Service Kurulumu

```bash
# Root ise:
./service-install.sh

# Normal kullanıcıysa:
sudo ./service-install.sh
```

**Bu script:**
- ✅ Systemd service oluşturur
- ✅ Otomatik başlatma ayarlar
- ✅ Bot'u başlatır
- ✅ `twitter` komutunu sistem geneline ekler

**Çıktı:**
```
[1/5] Service dosyası oluşturuluyor...
✅ Service dosyası oluşturuldu
[2/5] Systemd reload ediliyor...
✅ Systemd reload edildi
[3/5] Servis aktif ediliyor...
✅ Servis aktif edildi
[4/5] Servis başlatılıyor...
✅ Servis başlatıldı
[5/5] Servis durumu kontrol ediliyor...
✅ Servis başarıyla çalışıyor!

✅  KURULUM TAMAMLANDI!
```

---

## 🎮 Kullanım

### Bot'u Kontrol Et

```bash
twitter
```

**Menü gelir:**
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

### Diğer Komutlar

```bash
./stats.sh              # Sadece istatistikler
./status.sh             # Sadece durum
./monitor.sh            # Canlı log izle

# Systemd komutları (ileri seviye)
systemctl status xpop-bot       # Durum
systemctl restart xpop-bot      # Yeniden başlat
journalctl -u xpop-bot -f       # Canlı log
```

---

## 🔧 Root ile mi Normal Kullanıcı ile mi?

### Root ile Kurulum

```bash
ssh root@sunucu-ip
cd ~
git clone <repo-url> X-pop
cd X-pop
./install.sh
python3 setup.py
./service-install.sh
```

**Avantajlar:**
- ✅ Sudo gerekmez
- ✅ Daha basit
- ✅ İzin sorunları olmaz

**Dezavantajlar:**
- ⚠️ Güvenlik riski (root her şeye erişir)

### Normal Kullanıcı ile Kurulum

```bash
ssh kullanici@sunucu-ip
cd ~
git clone <repo-url> X-pop
cd X-pop
./install.sh
python3 setup.py
sudo ./service-install.sh
```

**Avantajlar:**
- ✅ Daha güvenli
- ✅ Best practice

**Dezavantajlar:**
- ⚠️ Sudo gerekli

**Önerim:** Normal kullanıcı ile çalış, sadece `service-install.sh` için sudo kullan.

---

## 🆘 Sorun Giderme

### 1. Git Bulunamadı

```bash
apt install git -y          # Root ise
sudo apt install git -y     # Normal kullanıcıysa
```

### 2. Python Bulunamadı

```bash
# install.sh otomatik kurar ama manuel:
apt install python3 python3-pip python3-venv -y
```

### 3. Chrome Kurulamadı

```bash
# Manuel kurulum:
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install ./google-chrome-stable_current_amd64.deb -y
```

### 4. Service Başlamıyor

```bash
# Log'lara bak
journalctl -u xpop-bot -n 50

# Manuel başlat
cd X-pop
python3 -m src.main --test
```

### 5. Port 443 Hatası (SSL)

```bash
# Zaman senkronizasyonu
apt install ntpdate -y
ntpdate pool.ntp.org
```

---

## 📊 Özet - Copy Paste Komutlar

### Tam Kurulum (Root):

```bash
ssh root@sunucu-ip
cd ~
git clone https://github.com/KULLANICI/X-pop.git
cd X-pop
chmod +x *.sh
./install.sh
python3 setup.py
./service-install.sh
twitter
```

### Sonraki Girişlerde:

```bash
ssh root@sunucu-ip
twitter
```

---

## 🎉 Tebrikler!

Bot artık:
- ✅ Sürekli çalışıyor
- ✅ SSH kapansa çalışıyor
- ✅ Sunucu reboot olsa otomatik başlıyor
- ✅ `twitter` komutuyla kontrol ediyorsun
- ✅ Hiç durmuyor!

**Başka bir şey ister misin?** 🚀
