import asyncio
import time
import re # Düzenli ifadelerle versiyon ayıklamak için

MAX_CONCURRENT_TASKS = 100

async def grab_banner(reader, writer, port):
    """
    Açık olan porttan servis versiyon bilgisini (Banner) çekmeye çalışır.
    """
    try:
        if port == 80 or port == 8080:
            # Port 80 bir Web servisidir. Standart bir HTTP isteği göndermemiz gerekir.
            http_request = "HEAD / HTTP/1.1\r\nHost: scanme.nmap.org\r\nUser-Agent: SecurityScanner/1.0\r\n\r\n"
            writer.write(http_request.encode())
            await writer.drain() # Verinin tamamen gönderildiğinden emin oluyoruz
            
            # Gelen yanıtı oku (İlk 1024 bayt yeterlidir)
            data = await asyncio.wait_for(reader.read(1024), timeout=2.0)
            response = data.decode(errors='ignore')
            
            # HTTP yanıtı içindeki "Server:" başlığını regex ile ara
            server_match = re.search(r"[Ss]erver:\s*(.+)", response)
            if server_match:
                return server_match.group(1).strip()
            return "HTTP Service (Banner hidden)"
            
        else:
            # SSH, FTP gibi servisler bağlantı kurulur kurulmaz doğrudan banner döner.
            # Ekstra bir şey göndermeden direkt okumayı deniyoruz.
            data = await asyncio.wait_for(reader.read(512), timeout=2.0)
            banner = data.decode(errors='ignore').strip()
            return banner if banner else "Unknown Service"
            
    except Exception:
        return "Unknown Service (Timeout/No Banner)"

async def scan_port(target_host, port, semaphore):
    """
    Portu tarar, açıksa anında banner grabber'ı tetikler.
    """
    async with semaphore:
        try:
            coro = asyncio.open_connection(target_host, port)
            reader, writer = await asyncio.wait_for(coro, timeout=1.5)
            
            # Port açık! Şimdi arkasında ne çalıştığını öğrenme zamanı.
            print(f"[+] Port {port} IS OPEN! Banner çekiliyor...")
            banner = await grab_banner(reader, writer, port)
            
            writer.close()
            await writer.wait_closed()
            return port, "OPEN", banner
            
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return port, "CLOSED", None

async def main():
    target = "scanme.nmap.org"
    # Test listemize SSH (22) ve HTTP (80) portlarını kesin ekleyelim
    ports_to_scan = [22, 80, 443, 8080]
    
    print(f"[*] {target} üzerinde Banner Grabbing destekli tarama başlıyor...")
    start_time = time.time()
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    tasks = [scan_port(target, port, semaphore) for port in ports_to_scan]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    print("\n--- Detaylı Tarama Raporu ---")
    print(f"[*] Toplam süre: {end_time - start_time:.2f} saniye\n")
    
    for port, status, banner in results:
        if status == "OPEN":
            print(f"[+] Port: {port:<5} | Durum: {status:<4} | Servis/Banner: {banner}")

if __name__ == "__main__":
    asyncio.run(main())