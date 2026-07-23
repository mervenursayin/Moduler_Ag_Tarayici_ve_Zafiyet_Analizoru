import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import time
import re

# Önceki adımlarda yazdığımız fonksiyonları buraya entegre ediyoruz
import sqlite3
from datetime import datetime

DB_NAME = "security_scanner.db"

# --- ASENKRON TARAYICI MOTORU ---
async def scan_port(target_host, port, semaphore):
    async with semaphore:
        try:
            coro = asyncio.open_connection(target_host, port)
            reader, writer = await asyncio.wait_for(coro, timeout=1.5)
            
            # Banner Grabbing
            try:
                if port == 80 or port == 8080:
                    http_request = f"HEAD / HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
                    writer.write(http_request.encode())
                    await writer.drain()
                    data = await asyncio.wait_for(reader.read(512), timeout=1.5)
                    response = data.decode(errors='ignore')
                    server_match = re.search(r"[Ss]erver:\s*(.+)", response)
                    banner = server_match.group(1).strip() if server_match else "HTTP Service"
                else:
                    data = await asyncio.wait_for(reader.read(256), timeout=1.5)
                    banner = data.decode(errors='ignore').strip()
            except:
                banner = "Unknown Service"
                
            writer.close()
            await writer.wait_closed()
            return {"Port": port, "Status": "OPEN", "Banner": banner}
        except:
            return {"Port": port, "Status": "CLOSED", "Banner": "None"}

async def run_scanner(target, ports):
    semaphore = asyncio.Semaphore(50)
    tasks = [scan_port(target, port, semaphore) for port in ports]
    return await asyncio.gather(*tasks)

# --- VERİTABANI İŞLEMLERİ ---
def save_to_db(target, results):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO scans (target, scan_date) VALUES (?, ?)", (target, current_time))
    scan_id = cursor.lastrowid
    
    for r in results:
        cursor.execute("INSERT INTO scan_results (scan_id, port, status, banner) VALUES (?, ?, ?, ?)",
                       (scan_id, r["Port"], r["Status"], r["Banner"]))
    conn.commit()
    conn.close()

# --- STREAMLIT ARAYÜZÜ ---
st.set_page_config(page_title="Advanced Vulnerability Scanner", page_icon="🛡️", layout="wide")

st.title("🛡️ Modüler Ağ Tarayıcı & Zafiyet Analizörü")
st.markdown("3. Sınıf Bilgisayar Mühendisliği Siber Güvenlik Projesi")

# Yan Panel (Sidebar) - Tarama Ayarları
st.sidebar.header("⚙️ Tarama Ayarları")
target_input = st.sidebar.text_input("Hedef IP veya Alan Adı:", value="scanme.nmap.org")
port_mode = st.sidebar.selectbox("Port Seçimi:", ["Yaygın Portlar (Top 20)", "Özelleştirilmiş Aralık"])

if port_mode == "Yaygın Portlar (Top 20)":
    ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 8080, 8443]
else:
    start_p = st.sidebar.number_input("Başlangıç Portu", min_value=1, max_value=65535, value=1)
    end_p = st.sidebar.number_input("Bitiş Portu", min_value=1, max_value=65535, value=100)
    ports_to_scan = list(range(start_p, end_p + 1))

start_scan_btn = st.sidebar.button("🚀 Taramayı Başlat")

# Ana Panel
tab1, tab2 = st.tabs(["📊 Güncel Tarama", "📜 Geçmiş Taramalar"])

with tab1:
    if start_scan_btn:
        st.info(f"🔄 {target_input} üzerinde {len(ports_to_scan)} port taranıyor... Lütfen bekleyin.")
        
        # Asenkron tarayıcıyı Streamlit içinde tetikliyoruz
        start_time = time.time()
        scan_results = asyncio.run(run_scanner(target_input, ports_to_scan))
        end_time = time.time()
        
        # Veritabanına kaydet
        save_to_db(target_input, scan_results)
        
        # Verileri DataFrame'e dönüştür
        df = pd.DataFrame(scan_results)
        df_open = df[df["Status"] == "OPEN"]
        
        st.success(f"✅ Tarama {end_time - start_time:.2f} saniyede tamamlandı!")
        
        # Metrikler
        col1, col2 = st.columns(2)
        col1.metric("Toplam Taranan Port", len(df))
        col2.metric("Açık Port Sayısı", len(df_open))
        
        # Grafik ve Tablo Görselleştirme
        if not df_open.empty:
            st.subheader("🔓 Tespit Edilen Açık Portlar")
            st.dataframe(df_open[["Port", "Banner"]], use_container_width=True)
            
            # Pasta Grafiği
            st.subheader("📈 Port Durum Dağılımı")
            fig = px.pie(df, names="Status", title="Açık / Kapalı Port Oranı", color_discrete_sequence=["#EF553B", "#636EFA"])
            st.plotly_chart(fig)
        else:
            st.warning("Hedef üzerinde hiç açık port bulunamadı.")
    else:
        st.write("Tarama başlatmak için sol paneldeki butona tıklayın.")

with tab2:
    st.subheader("🕒 Sistemde Kayıtlı Geçmiş Taramalar")
    try:
        conn = sqlite3.connect(DB_NAME)
        df_scans = pd.read_sql_query("SELECT * FROM scans ORDER BY id DESC", conn)
        conn.close()
        if not df_scans.empty:
            st.dataframe(df_scans, use_container_width=True)
        else:
            st.write("Henüz geçmiş tarama kaydı bulunmuyor.")
    except:
        st.write("Veritabanı bağlantısı kurulurken bir hata oluştu.")