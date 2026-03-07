import customtkinter as ctk
import sqlite3

# 1. VERİTABANI - HATA VERMEYEN YENİLENMİŞ SÜRÜM
def db_kur():
    conn = sqlite3.connect('meg_giyim.db')
    c = conn.cursor()
    
    # Eski tabloyu tamamen silip en güncel halini kuralım (Hata almamak için)
    c.execute("DROP TABLE IF EXISTS urunler")
    
    c.execute('''CREATE TABLE urunler 
                 (id INTEGER PRIMARY KEY, ad TEXT, fiyat TEXT, etiket TEXT, kategori TEXT)''')
    
    urunler = [
        ('Siyah Oversize Tişört', '450 TL', 'yazlık spor tişört', 'Üst Giyim'),
        ('Beyaz Keten Gömlek', '650 TL', 'yazlık şık gömlek', 'Üst Giyim'),
        ('Siyah Deri Ceket', '2400 TL', 'kışlık havalı deri', 'Dış Giyim'),
        ('Kaşe Uzun Palto', '3500 TL', 'kışlık şık kaban', 'Dış Giyim'),
        ('Mavi Slim Jean', '850 TL', 'günlük rahat pantolon', 'Alt Giyim'),
        ('Kumaş Pantolon', '950 TL', 'resmi iş klasik', 'Alt Giyim'),
        ('Lacivert Takım Elbise', '4200 TL', 'düğün şık damatlık', 'Özel Koleksiyon'),
        ('Saten Gece Elbisesi', '2800 TL', 'düğün parti abiye', 'Özel Koleksiyon')
    ]
    
    c.executemany("INSERT INTO urunler (ad, fiyat, etiket, kategori) VALUES (?,?,?,?)", urunler)
    conn.commit()
    conn.close()

# 2. ANA UYGULAMA
class MegGiyimApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        db_kur() 

        self.sepet_sayisi = 0
        self.toplam_fiyat = 0

        self.title("MEG Giyim - AI Destekli Katalog")
        self.geometry("1000x800")
        self.configure(fg_color="#000000") 

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color="#1A1A1A", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(self.sidebar, text="MEG GIYIM", font=("Impact", 30), text_color="#3B82F6").pack(pady=40)
        
        self.label_sepet = ctk.CTkLabel(self.sidebar, text="Sepet: 0 Ürün", font=("Arial", 14))
        self.label_sepet.pack(side="bottom", pady=20)

        # --- ARAMA ---
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(side="top", fill="x", padx=30, pady=20)
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Stil ara: düğün, yazlık...", width=500, height=45)
        self.entry_search.pack(side="left", padx=10)
        self.btn_sor = ctk.CTkButton(self.search_frame, text="ARA ✨", command=self.ai_ara, width=120)
        self.btn_sor.pack(side="left")

        # --- VİTRİN ---
        self.view = ctk.CTkScrollableFrame(self, fg_color="#000000", label_text="MEG KOLEKSİYONLARI")
        self.view.pack(expand=True, fill="both", padx=30, pady=10)

        self.listele()

    def listele(self, filtre=""):
        for widget in self.view.winfo_children(): widget.destroy()
        conn = sqlite3.connect('meg_giyim.db')
        c = conn.cursor()
        
        kategoriler = ["Üst Giyim", "Alt Giyim", "Dış Giyim", "Özel Koleksiyon"]
        
        for kat in kategoriler:
            if filtre:
                c.execute("SELECT ad, fiyat FROM urunler WHERE kategori=? AND etiket LIKE ?", (kat, f'%{filtre}%'))
            else:
                c.execute("SELECT ad, fiyat FROM urunler WHERE kategori=?", (kat,))
            
            urunler = c.fetchall()
            if urunler:
                ctk.CTkLabel(self.view, text=f"📂 {kat.upper()}", font=("Arial", 18, "bold"), text_color="#3B82F6").pack(anchor="w", pady=(20, 5), padx=10)
                for ad, fiyat in urunler:
                    card = ctk.CTkFrame(self.view, fg_color="#1A1A1A", height=70, corner_radius=12, border_width=1, border_color="#333333")
                    card.pack(fill="x", pady=5)
                    ctk.CTkLabel(card, text=ad, font=("Arial", 15, "bold"), text_color="white").pack(side="left", padx=25)
                    ctk.CTkLabel(card, text=fiyat, font=("Arial", 16, "bold"), text_color="#2ECC71").pack(side="right", padx=30)
                    btn = ctk.CTkButton(card, text="EKLE", width=80, command=self.sepete_ekle)
                    btn.pack(side="right", padx=10)
        conn.close()

    def sepete_ekle(self):
        self.sepet_sayisi += 1
        self.label_sepet.configure(text=f"Sepet: {self.sepet_sayisi} Ürün")

    def ai_ara(self):
        self.listele(self.entry_search.get().lower())

if __name__ == "__main__":
    app = MegGiyimApp()
    app.mainloop()