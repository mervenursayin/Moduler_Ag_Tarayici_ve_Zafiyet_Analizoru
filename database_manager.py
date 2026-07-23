import sqlite3
from datetime import datetime

DB_NAME = "security_scanner.db"

def init_db():
    """
    Veritabanını ve gerekli tabloları oluşturur.
    Proje ilk kez çalıştığında bu fonksiyon çağrılmalıdır.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Taramalar Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT NOT NULL,
        scan_date TEXT NOT NULL
    )
    """)
    
    # 2. Tarama Sonuçları Tablosu (Foreign Key bağlantılı)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        port INTEGER,
        status TEXT,
        banner TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("[+] Veritabanı ve tablolar başarıyla hazırlandı.")

def save_scan_results(target, results):
    """
    Tarama sonuçlarını veritabanına kaydeder.
    results parametresi şu formatta olmalıdır: [(port, status, banner), ...]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Önce ana tarama kaydını oluşturuyoruz
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO scans (target, scan_date) VALUES (?, ?)", (target, current_time))
    scan_id = cursor.lastrowid # Oluşan taramanın ID'sini alıyoruz
    
    # Şimdi bu taramaya ait port sonuçlarını topluca ekliyoruz (Bulk Insert)
    for port, status, banner in results:
        cursor.execute("""
        INSERT INTO scan_results (scan_id, port, status, banner)
        VALUES (?, ?, ?, ?)
        """, (scan_id, port, status, banner))
        
    conn.commit()
    conn.close()
    print(f"[+] Tarama verileri (ID: {scan_id}) başarıyla veritabanına kaydedildi.")

def get_all_scans():
    """Web arayüzünde listelemek için geçmiş taramaları çeker."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    # Test etmek için veritabanını ilklendiriyoruz
    init_db()
    
    # Sahte bir tarama sonucu kaydederek test edelim
    sample_target = "scanme.nmap.org"
    sample_results = [
        (80, "OPEN", "Apache/2.4.7 (Ubuntu)"),
        (22, "CLOSED", None),
        (443, "OPEN", "nginx/1.18.0")
    ]
    save_scan_results(sample_target, sample_results)