# 🛡️ Modüler Ağ Tarayıcı & Zafiyet Analizörü

Bu proje, **3. Sınıf Bilgisayar Mühendisliği** müfredatında yer alan ağ protokolleri, soket programlama, asenkron süreç yönetimi ve veri tabanı mimarisi kavramlarını uygulamalı olarak hayata geçirmek amacıyla geliştirilmiş, yüksek hızlı bir ağ tarama ve zafiyet analiz aracıdır.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Asyncio](https://img.shields.io/badge/Asyncio-Concurrency-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 📸 Ekran Görüntüsü & Arayüz

### 1. Tarama ve Tespit Edilen Açık Portlar
<img width="1306" height="600" alt="s" src="https://github.com/user-attachments/assets/62aa14c4-1612-4fba-9225-fa28ac8893e9" />


### 2. Port Durum Dağılımı ve Grafik
<img width="1307" height="597" alt="s2" src="https://github.com/user-attachments/assets/179ae008-2af7-46e8-ade0-e831c52d701f" />

---

## 🚀 Öne Çıkan Mühendislik Yaklaşımları & Özellikler

* **⚡ Asenkron Tarama Motoru (`asyncio`):** Taramalardaki I/O (Giriş/Çıkış) bekleme sürelerini ortadan kaldırmak için asenkron mimari kurulmuştur. Sistem kaynaklarını ve ağ trafiğini korumak amacıyla `Semaphore(50)` sınırlandırması uygulanmıştır. Bu sayede port taramaları **1.5 saniye** gibi rekor sürelerde tamamlanır.
  
* **🔍 Banner Grabbing (Servis Tespiti):** Tespit edilen açık portlara TCP/HTTP seviyesinde soket bağlantıları kurularak servislerin versiyon bilgileri (Örn: `Apache/2.4.7 (Ubuntu)`) regex yapılarıyla ayrıştırılır.
  
* **🗄️ İlişkisel Veri Yönetimi (`SQLite`):** Taranan IP adresleri, bulunan açık portlar, servis versiyonları ve zaman damgaları `scans` ve `scan_results` tabloları arasında `Foreign Key` ilişkisi kurularak saklanır.
  
* **📊 İnteraktif Görsel Dashboard:** `Streamlit` ve `Plotly` kullanılarak tarama sonuçlarının anlık takip edilebildiği, durum oranlarının (% Açık/Kapalı) pasta grafiklerle görselleştirildiği ve geçmiş taramaların sorgulanabildiği bir panelle sunulmuştur.

---

## 🏗️ Sistem Mimari Şeması

```text
  ┌────────────────────────┐
  │  Streamlit Web Panel   │
  └───────────┬────────────┘
              │ (Kullanıcı Girdisi)
              ▼
  ┌────────────────────────┐
  │ Async Scanner Engine   │ ◄───► [ TCP 3-Way Handshake ]
  └───────────┬────────────┘
              │ (Açık Portlar)
              ▼
  ┌────────────────────────┐
  │  Banner Grabber Engine │ ◄───► [ HTTP/TCP Header Extraction ]
  └───────────┬────────────┘
              │ (Servis & Versiyon)
              ▼
  ┌────────────────────────┐
  │    SQLite Database     │ ◄───► [ Relational Data Storage ]
  └────────────────────────┘
