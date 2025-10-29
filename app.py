# app.py
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import time
import random

# OYUN MANTIK DOSYASINDAN İMPORT
from depo_mantigi import (
    depo_olustur, 
    esya_sat, 
    GOZLEM_SURESI, 
    MIN_TEKLIF_ARTISI
) 

app = Flask(__name__)
# Flask, oturum (session) verilerini şifrelemek için gizli bir anahtara ihtiyaç duyar.
app.config['SECRET_KEY'] = 'sizin_guvenli_gizli_anahtarınız' 
# SocketIO, gerçek zamanlı iletişim için kullanılır (teklifler, zamanlayıcı).
socketio = SocketIO(app)

# --- Global Oyun Durumu ---
# Tüm aktif odaları ve içindeki oyun durumunu tutar
AKTIF_ODALAR = {} 

@app.route('/')
def index():
    """Oyun giriş ve oda seçimi ekranı."""
    # Henüz HTML dosyamız yok, bu yüzden sadece bir yer tutucu döndürelim.
    return "<h1>Depo Savaşları (Çok Oyunculu Prototip)</h1><p>Lütfen kullanıcı adı ve oda kodu girin.</p><form method='POST' action='/oyna'><input type='text' name='username' placeholder='Kullanıcı Adı'><input type='text' name='room_code' placeholder='Oda Kodu'><button type='submit'>Oyna</button></form>"

@app.route('/oyna', methods=['POST'])
def oyna():
    """Oda oluşturma veya odaya katılma."""
    kullanici_adi = request.form.get('username')
    oda_kodu = request.form.get('room_code')
    
    if not kullanici_adi or not oda_kodu:
        return redirect(url_for('index'))
    
    # Yeni oda oluşturma
    if oda_kodu not in AKTIF_ODALAR:
        depo_icerigi, toplam_deger, buyukluk, durum = depo_olustur()
        AKTIF_ODALAR[oda_kodu] = {
            'depo_bilgisi': {'icerik': depo_icerigi, 'deger': toplam_deger, 'buyukluk': buyukluk, 'durum': durum},
            'teklif': 0,
            'kazanan': 'Kimse',
            'oyuncular': {},
            'aktif': True,
            'gozlem_basi_zaman': None
        }
        
    session['username'] = kullanici_adi
    session['room'] = oda_kodu
    return redirect(url_for('oda_bekle'))

@app.route('/oda')
def oda_bekle():
    """Oda bekleme ve gözlem ekranı (Şimdilik yer tutucu)."""
    if 'room' not in session or session['room'] not in AKTIF_ODALAR:
        return redirect(url_for('index'))

    oda = AKTIF_ODALAR[session['room']]
    
    # Gerçek HTML arayüzüne taşınacak kısım:
    return f"<h2>Oda: {session['room']}</h2><p>Hoş geldin, {session['username']}. Diğer oyuncular bekleniyor...</p><p>Aktif Oyuncular: {list(oda['oyuncular'].values())}"

# --- SOCKETIO (GERÇEK ZAMANLI İLETİŞİM) ---

@socketio.on('join')
def on_join(data):
    """Oyuncunun odaya katılması ve durumu güncelleme."""
    oda_kodu = session.get('room')
    kullanici_adi = session.get('username')
    
    if oda_kodu in AKTIF_ODALAR:
        join_room(oda_kodu)
        # Oyuncuyu SocketIO ID'si ile kaydet
        AKTIF_ODALAR[oda_kodu]['oyuncular'][request.sid] = kullanici_adi
        
        # Odaya katılan herkese güncel durumu gönder
        socketio.emit('oda_guncelle', {
            'mesaj': f"{kullanici_adi} odaya katıldı.",
            'oyuncular': list(AKTIF_ODALAR[oda_kodu]['oyuncular'].values())
        }, room=oda_kodu)
        
        # Burada, yeterli oyuncu varsa (örneğin 2) gözlem sayacı başlatılır.

@socketio.on('teklif_gonder')
def handle_teklif(data):
    """Oyuncudan gelen yeni teklifi işler."""
    oda_kodu = session.get('room')
    kullanici_adi = session.get('username')
    yeni_teklif = int(data['teklif']) # Güvenlik kontrolü yapılmalı!
    
    oda = AKTIF_ODALAR.get(oda_kodu)
    # Teklifin minimum artış kuralına uygun olup olmadığını kontrol et
    if oda and yeni_teklif >= oda['teklif'] + MIN_TEKLIF_ARTISI:
        oda['teklif'] = yeni_teklif
        oda['kazanan'] = kullanici_adi
        
        # Tüm odaya yeni teklifi duyur
        socketio.emit('teklif_guncelle', {
            'teklif': yeni_teklif,
            'kazanan': kullanici_adi
        }, room=oda_kodu)

if __name__ == '__main__':
    # Flask-SocketIO sunucusunu başlat
    # Bu komutu çalıştırdığınızda sunucu başlayacaktır.
    socketio.run(app, debug=True)