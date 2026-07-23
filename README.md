# 🛡️ Modüler Ağ Tarayıcı & Zafiyet Analizörü

Bu proje, **3. Sınıf Bilgisayar Mühendisliği** müfredatında yer alan ağ protokolleri, soket programlama, asenkron süreç yönetimi ve veri tabanı mimarisi kavramlarını uygulamalı olarak hayata geçirmek amacıyla geliştirilmiş, yüksek hızlı bir ağ tarama ve zafiyet analiz aracıdır.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Asyncio](https://img.shields.io/badge/Asyncio-Concurrency-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 📸 Ekran Görüntüsü & Arayüz

![Dashboard Ekran Görüntüsü] src="https://raw.githubusercontent.com/mervenursayin/Moduler_Ag_Tarayici_ve_Zafiyet_Analizoru/main/s.png"
*(Arayüz ekran görüntünüzü repoya `preview.png` ismiyle eklediğinizde otomatik belirecektir)*

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
