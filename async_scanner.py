import asyncio
import time

# Aynı anda maksimum kaç paralel bağlantı denemesi yapılacağını sınırlarız.
# Bu sınır (Semaphore), işletim sisteminin kaynaklarını (File Descriptors) tüketmemek için şarttır.
MAX_CONCURRENT_TASKS = 100

async def scan_port(target_host, port, semaphore):
    """
    Belirtilen portu asenkron olarak tarar.
    """
    # Semaphore kullanarak aynı anda sadece izin verilen miktarda görevin 
    # bu bloğa girmesini sağlıyoruz.
    async with semaphore:
        try:
            # asyncio.open_connection hem soket açar hem de 3-way handshake dener.
            # Başarılı olursa okuma ve yazma nesneleri (streams) döner.
            # 1.5 saniyelik zaman aşımı (timeout) uyguluyoruz.
            coro = asyncio.open_connection(target_host, port)
            reader, writer = await asyncio.wait_for(coro, timeout=1.5)
            
            # Bağlantı kurulabildiyse port AÇIKTIR.
            print(f"[+] Port {port} IS OPEN!")
            
            # Açılan bağlantıyı güvenli bir şekilde kapatıyoruz.
            writer.close()
            await writer.wait_closed()
            return port, "OPEN"
            
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            # Port kapalıysa, firewall varsa veya zaman aşımına uğradıysa buraya düşer.
            # Terminali çöpe boğmamak için kapalı portları yazdırmıyoruz.
            return port, "CLOSED"

async def main():
    target = "scanme.nmap.org"
    # Test için en yaygın ve kritik 20 portu ve birkaç kapalı portu içeren bir liste oluşturalım
    ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 8080, 8443, 9000]
    
    print(f"[*] {target} üzerinde asenkron tarama başlıyor...")
    start_time = time.time()
    
    # Eşzamanlılık sınırımızı tanımlıyoruz
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    
    # Tüm portlar için asenkron görevleri (tasks) hazırlıyoruz
    tasks = []
    for port in ports_to_scan:
        tasks.append(scan_port(target, port, semaphore))
        
    # asyncio.gather ile tüm bu görevleri aynı anda (paralel gibi) tetikliyoruz
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    print("\n--- Tarama Sonuçları Raporu ---")
    open_ports = [port for port, status in results if status == "OPEN"]
    
    print(f"[*] Toplam süre: {end_time - start_time:.2f} saniye")
    print(f"[+] Açık Portlar: {open_ports}")

if __name__ == "__main__":
    # Asenkron ana döngüyü (Event Loop) başlatıyoruz
    asyncio.run(main()) 