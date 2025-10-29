import random
from typing import Dict, Tuple, Any

# --- KONSOL RENK AYARLARI (Web'de kullanılmayacak ama sabitler için tutuldu) ---
class Renk:
    YESIL = '\033[92m'
    KIRMIZI = '\033[91m'
    MAVI = '\033[94m'
    SARI = '\033[93m'
    MOR = '\033[95m'
    KAPAT = '\033[0m'

# --- OYUN AYARLARI ---
GOZLEM_SURESI = 1.5 
MIN_TEKLIF_ARTISI = 50
KREDI_LIMITI = 5000
KREDI_FAIZ_ORANI = 0.10 

# Sadeleştirilmiş Nadirlik, Eşya ve Depo Durumu Listeleri
NADIRLIK_AYARLARI = {
    "Önemsiz": (0.1, 0.5, 0.35, f"{Renk.KIRMIZI}Önemsiz{Renk.KAPAT}"),
    "Sıradan": (0.5, 1.5, 0.30, f"{Renk.KAPAT}Sıradan"),
    "Nadir": (1.5, 3.0, 0.20, f"{Renk.MAVI}Nadir{Renk.KAPAT}"),
    "Antika": (3.0, 7.0, 0.15, f"{Renk.SARI}Antika{Renk.KAPAT}")
}
GENIS_ESYA_LISTESI = [(100, "Kutu"), (500, "Elektronik"), (1000, "Mobilya"), (300, "Sanat Eseri")]
DEPO_BUYUKLUKLERI = ["Küçük", "Orta", "Büyük"]
DEPO_DURUMLARI = ["Kötü durumda", "Normal", "İyi durumda"]

# --- YARDIMCI FONKSİYONLAR ---

def rastgele_esya_sec():
    """Rastgele bir eşya ve gerçek değerini seçer."""
    r = random.random()
    olasılık_toplami = 0
    secilen_ayar = list(NADIRLIK_AYARLARI.values())[-1]
    
    for _, ayar in NADIRLIK_AYARLARI.items():
        olasılık_toplami += ayar[2]
        if r <= olasılık_toplami:
            secilen_ayar = ayar
            break
            
    carpan_min, carpan_max, _, gorunum = secilen_ayar
    taban_fiyat, esya_adi_sablon = random.choice(GENIS_ESYA_LISTESI)
    
    carpan = random.uniform(carpan_min, carpan_max)
    gercek_deger = round(taban_fiyat * carpan)
    esya_adi = f"{gorunum} {esya_adi_sablon}"

    return esya_adi, gercek_deger, gorunum, taban_fiyat 

def depo_olustur() -> Tuple[Dict[str, Any], int, str, str]:
    """Rastgele depo içeriği, değeri, büyüklüğü ve durumu oluşturur."""
    depo: Dict[str, Any] = {}
    depo_degeri = 0
    esya_sayisi = random.randint(5, 15)
    
    for _ in range(esya_sayisi):
        esya_adi, gercek_deger, nadirlik_tipi, taban_fiyat = rastgele_esya_sec()
        
        # Web için gerekli tüm verileri içeren bir sözlük yapısı
        depo.setdefault(esya_adi, {
            "birim_deger": gercek_deger, # Gerçek birim fiyat
            "sayi": 0, 
            "nadirlik": nadirlik_tipi,
            "taban_fiyat": taban_fiyat # İpucu için taban fiyat
        })
        depo[esya_adi]["sayi"] += 1
        depo_degeri += gercek_deger
    
    depo_buyuklugu = random.choice(DEPO_BUYUKLUKLERI)
    depo_durumu = random.choice(DEPO_DURUMLARI)

    return depo, depo_degeri, depo_buyuklugu, depo_durumu

def esya_sat(depo_icerigi: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """Kazanılan depodaki eşyaları satar. Satış detayı ve toplam geliri döndürür."""
    toplam_satis_geliri = 0
    satis_detaylari = {}

    for esya_adi, detay in depo_icerigi.items():
        esya_satis_geliri = 0
        tahmini_piyasa_degeri = detay["birim_deger"] 
        
        for _ in range(detay["sayi"]):
            # Satışta %50 ile %120 arasında rastgele bir değer elde etme mantığı korundu.
            rakip_teklifleri = [round(tahmini_piyasa_degeri * random.uniform(0.5, 1.2))]
            son_teklif = max(rakip_teklifleri) if rakip_teklifleri else 10
            esya_satis_geliri += son_teklif
            
        toplam_satis_geliri += esya_satis_geliri
        satis_detaylari[esya_adi] = esya_satis_geliri
        
    return toplam_satis_geliri, satis_detaylari