from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
# Güvenlik için bir gizli anahtar şarttır (Flask oturumları için)
app.secret_key = 'super_secret_depo_key_123' 

# Sabitler
MIN_INCREMENT = 100
STARTING_BUDGET = 10000

class AI_Buyer:
    """Teklif veren YZ Karakteri Sınıfı."""
    def __init__(self, name, aggressiveness, budget):
        self.name = name
        self.aggressiveness = aggressiveness
        self.budget = budget
        self.max_bid_limit = 0
        self.is_active = True

    def calculate_max_limit(self, estimated_depot_value):
        """Tahmini değere ve hırs seviyesine göre YZ'nin maksimum teklif limitini belirler."""
        # YZ, tahmini değere göre %10 ile %50 arasında bir marjla limit belirler.
        multiplier = 1 + (self.aggressiveness * random.uniform(0.1, 0.5))
        self.max_bid_limit = int(estimated_depot_value * multiplier)
        
    def get_bid(self, highest_bid):
        """Mevcut en yüksek teklife göre YZ'nin bir sonraki teklifini hesaplar."""
        if not self.is_active or self.budget < highest_bid + MIN_INCREMENT:
            return 0 
            
        if highest_bid >= self.max_bid_limit:
            self.is_active = False # Limite ulaştı, pasif kal
            return 0 
            
        # Basit Blöf Mekaniği: Yüksek Hırslı YZ'ler, düşük tekliflerde blöf yapabilir.
        if self.aggressiveness > 0.7 and highest_bid < self.max_bid_limit * 0.5 and random.random() < 0.3:
             bluff_bid = int(self.max_bid_limit * 0.8)
             return min(bluff_bid, self.budget)

        # Normal Artış
        next_bid = highest_bid + MIN_INCREMENT
        
        return next_bid if next_bid <= self.max_bid_limit else 0

def initialize_game():
    """Oyunun başlangıç durumunu ayarlar."""
    session['player_budget'] = STARTING_BUDGET
    session['ai_buyers'] = [
        AI_Buyer("Barry 'The Gambler'", 0.9, STARTING_BUDGET).__dict__,
        AI_Buyer("Dave 'The Calculator'", 0.5, STARTING_BUDGET).__dict__,
        AI_Buyer("Brandi 'The Cautious'", 0.3, STARTING_BUDGET).__dict__,
    ]
    session['depot_count'] = 0
    session['player_inventory'] = []

def start_new_auction():
    """Yeni bir depo ve açık artırma başlatır."""
    session['depot_count'] += 1
    session['current_depot'] = {
        'name': f"Depo #{session['depot_count']}",
        # Gerçek Değer: 5000$ ile 25000$ arası rastgele değer
        'real_value': random.randint(5000, 25000), 
        'initial_bid': random.choice([500, 1000, 1500]),
        'winner': 'Teklif Verilmedi',
        'winning_bid': 0
    }
    session['highest_bid'] = session['current_depot']['initial_bid']
    session['winner'] = None
    session['status_message'] = "Açık artırma başladı! İlk teklif verildi."
    
    # YZ'leri sıfırla ve yeni limitlerini belirle
    ai_buyers_data = session['ai_buyers']
    for ai_data in ai_buyers_data:
        ai_buyer = AI_Buyer(**ai_data) # YZ nesnesini yeniden oluştur
        # YZ'ler, gerçek değere yakın ama farklı bir tahminle limit belirler
        estimated_value = int(session['current_depot']['real_value'] * random.uniform(0.8, 1.2))
        ai_buyer.calculate_max_limit(estimated_value)
        ai_buyer.is_active = True
        ai_data.update(ai_buyer.__dict__) # Oturum verisini güncelle

@app.route('/')
def index():
    """Ana Sayfa ve Oyun Başlangıcı."""
    if 'player_budget' not in session:
        initialize_game()
        start_new_auction()

    return render_template('index.html', 
                           depot=session['current_depot'],
                           highest_bid=session['highest_bid'],
                           player_budget=session['player_budget'],
                           ai_buyers=session['ai_buyers'],
                           status_message=session.get('status_message', 'Hazır.'),
                           min_next_bid=session['highest_bid'] + MIN_INCREMENT)

@app.route('/bid', methods=['POST'])
def bid():
    """Oyuncunun teklif gönderme işlemi."""
    player_bid = int(request.form['player_bid'])
    highest_bid = session['highest_bid']
    
    # Teklif Kontrolleri
    if player_bid <= highest_bid:
        session['status_message'] = "Hata: Teklifiniz mevcut en yüksek tekliften yüksek olmalıdır."
        return redirect(url_for('index'))
    if player_bid > session['player_budget']:
        session['status_message'] = "Hata: Yeterli bütçeniz yok!"
        return redirect(url_for('index'))

    # Oyuncunun Teklifi Kabul Edildi
    session['highest_bid'] = player_bid
    session['winner'] = 'SİZ'
    session['status_message'] = f"TEKLİFİNİZ: {player_bid}$! Sıra YZ'lerde..."
    
    # Hemen YZ'lerin teklif vermesini tetikle
    ai_turn()
    
    return redirect(url_for('index'))

@app.route('/ai-turn')
def ai_turn():
    """YZ'lerin teklif verme döngüsü."""
    highest_bid = session['highest_bid']
    current_winner = session['winner']
    
    # YZ'leri tekrar nesne olarak yükle
    ai_buyers = [AI_Buyer(**data) for data in session['ai_buyers']]
    
    # Bir tur boyunca YZ'ler teklif verir
    for ai_buyer in ai_buyers:
        if ai_buyer.name != current_winner: # Kazanan YZ tekrar teklif vermez
            new_bid = ai_buyer.get_bid(highest_bid)
            
            if new_bid > highest_bid:
                highest_bid = new_bid
                current_winner = ai_buyer.name
                session['status_message'] += f" -> {current_winner} teklifi {highest_bid}$'a yükseltti!"
            
            # YZ'nin güncel durumunu oturuma kaydet
            for i, data in enumerate(session['ai_buyers']):
                if data['name'] == ai_buyer.name:
                    session['ai_buyers'][i] = ai_buyer.__dict__
                    break
    
    session['highest_bid'] = highest_bid
    session['winner'] = current_winner
    
    # Teklif döngüsünün bittiğini kontrol et
    active_buyers = [b for b in ai_buyers if b.is_active and b.budget >= highest_bid + MIN_INCREMENT and b.name != current_winner]
    
    if len(active_buyers) == 0 and current_winner != 'Teklif Verilmedi':
        end_auction(current_winner, highest_bid)

    return redirect(url_for('index'))

def end_auction(winner, winning_bid):
    """Açık artırmayı sonlandırır ve bütçeleri günceller."""
    session['status_message'] = f"*** AÇIK ARTIRMA SONA ERDİ! KAZANAN: {winner} ({winning_bid}$)! ***"
    
    if winner == 'SİZ':
        session['player_budget'] -= winning_bid
        session['player_inventory'].append(session['current_depot']['name'])
    else:
        # Kazanan YZ'nin bütçesini düşür
        for i, data in enumerate(session['ai_buyers']):
            if data['name'] == winner:
                session['ai_buyers'][i]['budget'] -= winning_bid
                break
                
@app.route('/next-depot')
def next_depot():
    """Yeni depoya geçiş."""
    start_new_auction()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Bu kısmı terminalde 'flask run' yerine koddan çalıştırmak için kullanabilirsiniz.
    app.run(debug=True)
