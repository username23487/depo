import random
import time
import os
from typing import Dict, Tuple, Any

# --- KONSOL RENK AYARLARI ---
class Renk:
    YESIL = '\033[92m'
    KIRMIZI = '\033[91m'
    MAVI = '\033[94m'
    SARI = '\033[93m'
    MOR = '\033[95m'
    KAPAT = '\033[0m'

# --- OYUN AYARLARI ---
GOZLEM_SURESI = 1.5 # Herkes için zorunlu gözlem süresi (Saniye)
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

    return esya_adi, gercek_deger, gorunum

def depo_olustur() -> Tuple[Dict[str, Any], int, str, str]:
    """Rastgele depo içeriği, değeri, büyüklüğü ve durumu oluşturur."""
    depo: Dict[str, Any] = {}
    depo_degeri = 0
    esya_sayisi = random.randint(5, 15)
    
    for _ in range(esya_sayisi):
        esya_adi, gercek_deger, nadirlik_tipi = rastgele_esya_sec()
        depo.setdefault(esya_adi, {"deger": gercek_deger, "sayi": 0, "nadirlik": nadirlik_tipi})
        depo[esya_adi]["sayi"] += 1
        depo_degeri += gercek_deger
    
    depo_buyuklugu = random.choice(DEPO_BUYUKLUKLERI)
    depo_durumu = random.choice(DEPO_DURUMLARI)

    return depo, depo_degeri, depo_buyuklugu, depo_durumu

def terminali_temizle():
    """Konsolu temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def hizli_gozlem(depo_icerigi: Dict[str, Any]):
    """1.5 saniyelik zorunlu, ücretsiz detaylı gözlem sağlar. TOPLAM DEĞERİ GİZLER."""
    
    terminali_temizle()
    
    print(f"{Renk.MAVI}👀 ULTRA HIZLI GÖZLEM BAŞLADI (Süre: {GOZLEM_SURESI} Saniye){Renk.KAPAT}")
    print(f"{Renk.MAVI}***************************************************{Renk.KAPAT}")
    print(f"{Renk.SARI}📢 DEĞER BİLİNMİYOR! (Hesaplama Size Ait){Renk.KAPAT}\n")
    
    # Detaylı Gözlem Ekranı: Birim fiyatları ve adetler gösterilir (oyuncu toplamı hesaplamalı)
    for esya_adi, detay in depo_icerigi.items():
        # Sadece birim fiyatı gösteriyoruz, toplam değeri gizliyoruz.
        deger_mesaj = f"{Renk.MOR}[Birim Fiyat: {detay['deger']}]"
        print(f"   - {detay['sayi']}x {esya_adi}: {deger_mesaj}{Renk.KAPAT}")
        
    print(f"{Renk.MAVI}***************************************************{Renk.KAPAT}")
    
    # 1.5 saniye bekletme
    print(f"{Renk.SARI}Gözlem için bekleniyor... {GOZLEM_SURESI} saniye sonra teklif başlayacak.{Renk.KAPAT}")
    try:
        time.sleep(GOZLEM_SURESI)
    except KeyboardInterrupt:
        print(f"{Renk.KIRMIZI}Gözlem erken sonlandırıldı.{Renk.KAPAT}")

    terminali_temizle()

def esya_acik_artirma_ile_sat(depo_icerigi: Dict[str, Any]) -> int:
    """Kazanılan depodaki eşyaları rastgele tekliflerle satar (Satış Aşaması)."""
    toplam_satis_geliri = 0
    print(Renk.MAVI + "\n--- EŞYALAR SATILIYOR ---" + Renk.KAPAT)
    for esya_adi, detay in depo_icerigi.items():
        esya_satis_geliri = 0
        tahmini_piyasa_degeri = detay["deger"] 
        for i in range(detay["sayi"]):
            rakip_teklifleri = [round(tahmini_piyasa_degeri * random.uniform(0.5, 1.2))]
            son_teklif = max(rakip_teklifleri) if rakip_teklifleri else 10
            esya_satis_geliri += son_teklif
        toplam_satis_geliri += esya_satis_geliri
        print(f"   - {detay['sayi']}x {esya_adi} satıldı. Gelir: {esya_satis_geliri}")
        
    return toplam_satis_geliri

def ihale_baslat(toplam_deger: int, oyuncu_parasi: int) -> Tuple[int, bool]:
    """Dinamik açık artırma/atışma mekaniği."""
    
    # DİNAMİK İNATÇILIK: Rakiplerin Hırs Limiti 0.3 ile 1.0 (tam değere kadar) arasında rastgele belirlenir.
    rakip1_hirs = random.uniform(0.3, 1.0)
    rakip2_hirs = random.uniform(0.3, 1.0)
    rakip_limitleri = [round(toplam_deger * rakip1_hirs), round(toplam_deger * rakip2_hirs)]
    
    rakipler = {"Rakip 1 (Dave)": rakip_limitleri[0], "Rakip 2 (Brandi)": rakip_limitleri[1]}
    
    mevcut_teklif = 0
    kazanan_isim = "Kimse"
    
    print(f"\n{Renk.SARI}🔥🔥 AÇIK ARTIRMA BAŞLIYOR! 🔥🔥{Renk.KAPAT}")
    
    while True:
        # Bitiş Kontrolü
        if kazanan_isim == "Oyuncu" and all(limit == -1 for limit in rakipler.values()):
            print(f"{Renk.YESIL}🎉 Depo sizin! Son Teklif: {mevcut_teklif}{Renk.KAPAT}")
            break
            
        rakiplerin_aktif_teklifi_oldu = False
        
        # Rakiplerin Turu
        for rakip_isim in list(rakipler.keys()):
            limit = rakipler[rakip_isim]
            if limit == -1: continue

            # Şüphecilik (İnatçılık değişkendir, Limit ne kadar yüksekse o kadar az pes ederler)
            if limit > toplam_deger * 0.8:
                 cekilme_sansı = 0.10 # Daha inatçı
            else:
                 cekilme_sansı = 0.30 # Daha az inatçı

            if limit <= mevcut_teklif or random.random() < cekilme_sansı:
                print(f"{Renk.KIRMIZI}>> {rakip_isim}: Pas!{Renk.KAPAT}")
                rakipler[rakip_isim] = -1 
            
            elif limit > mevcut_teklif + MIN_TEKLIF_ARTISI:
                mevcut_teklif += MIN_TEKLIF_ARTISI
                kazanan_isim = rakip_isim
                print(f"{Renk.KIRMIZI}>> {rakip_isim}: {mevcut_teklif}!{Renk.KAPAT}")
                rakiplerin_aktif_teklifi_oldu = True
            
            else:
                print(f"{Renk.KIRMIZI}>> {rakip_isim}: Pas!{Renk.KAPAT}")
                rakipler[rakip_isim] = -1 

        # Oyuncunun Turu
        if not all(limit == -1 for limit in rakipler.values()) or not rakiplerin_aktif_teklifi_oldu:
            gecerli_teklif_gerekli = mevcut_teklif + MIN_TEKLIF_ARTISI
            while True:
                try:
                    print(f"\n{Renk.SARI}📢 Mevcut Teklif: {mevcut_teklif} ({kazanan_isim} lider){Renk.KAPAT}")
                    oyuncu_secim = input(f"{Renk.YESIL}Teklif (Min. {gecerli_teklif_gerekli}) / [Enter] Otomatik / [P]as: {Renk.KAPAT}").strip().upper()

                    # Otomatik Teklif (Enter)
                    if not oyuncu_secim: 
                        yeni_teklif = gecerli_teklif_gerekli
                        print(f"{Renk.YESIL}>> Otomatik Teklif: {yeni_teklif}!{Renk.KAPAT}")

                    elif oyuncu_secim == 'P':
                        print(f"{Renk.KIRMIZI}❌ Pas geçtiniz. İhale, {kazanan_isim}'e gidiyor!{Renk.KAPAT}")
                        return mevcut_teklif, kazanan_isim != "Oyuncu"
                    
                    else:
                        yeni_teklif = int(oyuncu_secim)

                    if yeni_teklif < gecerli_teklif_gerekli or yeni_teklif > oyuncu_parasi or yeni_teklif == mevcut_teklif:
                        print(f"{Renk.KIRMIZI}❌ Geçersiz teklif. (Kasa/Minimum Kuralı){Renk.KAPAT}")
                    else:
                        mevcut_teklif = yeni_teklif
                        kazanan_isim = "Oyuncu"
                        if oyuncu_secim: 
                            print(f"{Renk.YESIL}>> Oyuncu: {mevcut_teklif}!{Renk.KAPAT}")
                        break

                except ValueError:
                    print(f"{Renk.KIRMIZI}❌ Lütfen geçerli bir sayı, Enter veya 'P' girin.{Renk.KAPAT}")
        
    return mevcut_teklif, kazanan_isim != "Oyuncu"

# --- ANA OYUN FONKSİYONU ---

def depo_savaslari_simulasyonu(oyuncu_parasi: int) -> int:
    
    depo_icerigi, toplam_deger, buyukluk, durum = depo_olustur()
    
    print(Renk.SARI + "\n="*50 + Renk.KAPAT)
    print(f"{Renk.SARI}--- YENİ İHALE BAŞLIYOR ---{Renk.KAPAT}")
    print(f"{Renk.MAVI}🏢 Depo Bilgisi: Büyüklük: {buyukluk} | Durum: {durum}{Renk.KAPAT}")
    
    # 1. Aşama: Herkes için Ücretsiz Hızlı Gözlem (Toplam Değer Artık Gizli)
    input(f"{Renk.SARI}Devam etmek için [Enter] tuşuna basın. ({GOZLEM_SURESI} saniyelik gözlem başlayacak){Renk.KAPAT}")
    hizli_gozlem(depo_icerigi)
    
    # 2. Aşama: Dinamik Açık Artırma
    son_teklif, kaybetti = ihale_baslat(toplam_deger, oyuncu_parasi)
    
    # 3. Aşama: Sonuçlandırma
    if not kaybetti:
        odenen_ucret = son_teklif 
        yeni_para = oyuncu_parasi - odenen_ucret
        
        gelir = esya_acik_artirma_ile_sat(depo_icerigi)
        kar_zarar = gelir - odenen_ucret
        yeni_para += gelir

        print(Renk.MAVI + "\n--- KAR/ZARAR ANALİZİ ---" + Renk.KAPAT)
        print(f"Gerçek Depo Değeri (Gizliydi): {toplam_deger}") # Bilgi amaçlı gösterim
        print(f"Ödenen Teklif: {odenen_ucret}")
        print(f"Toplam Satış Geliri: {gelir}")
        
        if kar_zarar > 0:
            print(f"{Renk.YESIL}✅ NET KÂR: {kar_zarar}.{Renk.KAPAT}")
        elif kar_zarar < 0:
            print(f"{Renk.KIRMIZI}🛑 NET ZARAR: {abs(kar_zarar)}.{Renk.KAPAT}")
        else:
            print("🤝 Ne kâr ne zarar.")
            
        return yeni_para
            
    else:
        print(f"{Renk.KIRMIZI}\n😔 Depoyu kaçırdın. Son teklif: {son_teklif}.{Renk.KAPAT}")
        return oyuncu_parasi

# --- OYUN BAŞLANGICI VE KREDİ YÖNETİMİ ---
if __name__ == "__main__":
    
    oyuncu_parasi = 5000 
    kredi_miktari = 0
    tur_sayisi = 0

    terminali_temizle()
    print(Renk.SARI + "="*50)
    print("👋 DEPO SAVAŞLARI SİMÜLATÖRÜ")
    print("====================================" + Renk.KAPAT)

    while True:
        tur_sayisi += 1
        print(Renk.MAVI + f"\n+++ TUR {tur_sayisi} BAŞLIYOR +++" + Renk.KAPAT)

        # Kredi Yönetimi ve Faiz
        if kredi_miktari > 0:
            faiz_miktari = round(kredi_miktari * KREDI_FAIZ_ORANI)
            print(f"{Renk.KIRMIZI}🏦 Borç: {kredi_miktari} | Faiz: {faiz_miktari}{Renk.KAPAT}")
            
            odeme = input(f"{Renk.MAVI}Borç ödeme (E/H)?: {Renk.KAPAT}").lower()
            if odeme == 'e':
                try:
                    miktar = int(input(f"{Renk.MAVI}Ödeme miktarı: {Renk.KAPAT}"))
                    miktar = min(miktar, oyuncu_parasi, kredi_miktari)
                    oyuncu_parasi -= miktar
                    kredi_miktari -= miktar
                    print(f"{Renk.YESIL}✅ {miktar} ödendi. Kalan Borç: {kredi_miktari}{Renk.KAPAT}")
                except ValueError: pass
            
            oyuncu_parasi -= faiz_miktari
            kredi_miktari += faiz_miktari 
            if faiz_miktari > 0: print(f"{Renk.KIRMIZI}🏦 Faiz uygulandı. Yeni Borç: {kredi_miktari}{Renk.KAPAT}")
        
        # Kredi Teklifi
        if oyuncu_parasi < 1000 and kredi_miktari < KREDI_LIMITI * 3:
            if input(f"{Renk.KIRMIZI}🚨 Kredi Al ({KREDI_LIMITI}) (E/H)?: {Renk.KAPAT}").lower() == 'e':
                kredi_miktari += KREDI_LIMITI
                oyuncu_parasi += KREDI_LIMITI
                print(f"{Renk.YESIL}🎉 {KREDI_LIMITI} eklendi.{Renk.KAPAT}")
        
        # Oyun Sonu Kontrolü
        if oyuncu_parasi <= 0:
            print(f"{Renk.KIRMIZI}🚨 Paran kalmadı/İflas ettin! Oyun bitti. 😔{Renk.KAPAT}")
            break

        print(f"{Renk.YESIL}💰 KASA: {oyuncu_parasi} | BORÇ: {kredi_miktari}{Renk.KAPAT}")
        oyuncu_parasi = depo_savaslari_simulasyonu(oyuncu_parasi)
        
        if oyuncu_parasi > 0 and input("\nYeni ihaleye gir (E/H)?: ").lower() == 'h':
            print(f"Oyun Bitti. Kasa: {oyuncu_parasi}, Borç: {kredi_miktari}.")
            break