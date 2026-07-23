import socket
import sys 

def check_single_port(target_host, port):
    """
    Belirtilen hedefteki tek bir portun durumunu kontrol eder.
    """
    # 1. Soket Nesnesi Oluşturma: AF_INET (IPv4), SOCK_STREAM (TCP) anlamına gelir.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # CRITICAL: Eğer hedef port kapalıysa veya bir firewall varsa script'in sonsuza kadar 
    # beklemesini engellemek için maksimum 1.5 saniyelik bir zaman aşımı (timeout) koyuyoruz.
    s.settimeout(1.5)
    
    try:
        # 2. Bağlantıyı Dene (3-Way Handshake başlatılır)
        # connect() fonksiyonu hedefi ve portu bir 'tuple' (demet) olarak alır.
        result = s.connect_ex((target_host, port))
        
        # connect_ex() fonksiyonu hata fırlatmak yerine bir hata kodu döner.
        # Eğer kod 0 ise bağlantı BAŞARILIDIR, yani port AÇIKTIR.
        if result == 0:
            print(self_pwn_message := f"[+] Port {port} IS OPEN!")
            return "OPEN"
        else:
            # Dönen kod 0 değilse port kapalıdır veya erişilemez durumdadır.
            return "CLOSED"
            
    except socket.error as e:
        print(f"[-] Bağlantı hatası oluştu: {e}")
        return "ERROR"
        
    finally:
        # 3. Soketi Kapatma: İşletim sistemi kaynaklarını tüketmemek için 
        # açılan her soket bağlantısı mutlaka kapatılmalıdır.
        s.close()

if __name__ == "__main__":
    # Test etmek için güvenli bir hedef seçiyoruz. 
    # localhost (127.0.0.1) kendi bilgisayarındır.
    # Alternatif olarak siber güvenlik öğrencilerinin test etmesi için yasal olarak sunulan 
    # "scanme.nmap.org" adresini de kullanabilirsin.
    TARGET = "scanme.nmap.org" 
    PORT_TO_TEST = 80 # HTTP portu genellikle açıktır.
    
    print(f"[*] {TARGET} üzerinde {PORT_TO_TEST} portu test ediliyor...")
    status = check_single_port(TARGET, PORT_TO_TEST)
    print(f"[*] Tarama sonucu: {status}")