import os
import sqlite3
import subprocess
import sys
import webbrowser
import urllib.parse
from tkinter import messagebox
from difflib import get_close_matches 

# 1. KÜTÜPHANE KONTROLÜ
try:
    import customtkinter as ctk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# 2. VERİTABANI AYARLARI
dizin = os.path.dirname(os.path.abspath(__file__))
db_yolu = os.path.join(dizin, 'meg_giyim_ai_v20.db')

def db_kur():
    conn = sqlite3.connect(db_yolu)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS urunler (id INTEGER PRIMARY KEY, ad TEXT, fiyat INTEGER, kategori TEXT, stok INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY, k_adi TEXT, sifre TEXT, adres TEXT)")
    
    c.execute("SELECT count(*) FROM urunler")
    if c.fetchone()[0] == 0:
        urunler = [
            ('Oversize Siyah Tişört', 450, 'Üst Giyim', 50), ('Beyaz Basic Gömlek', 750, 'Üst Giyim', 30),
            ('Kapüşonlu Sweat', 950, 'Üst Giyim', 25), ('V Yaka Kazak', 850, 'Üst Giyim', 20),
            ('Mavi Slim Jean', 1200, 'Alt Giyim', 35), ('Siyah Kargo Pantolon', 1100, 'Alt Giyim', 15),
            ('Gri Eşofman Altı', 650, 'Alt Giyim', 50), ('Keten Şort', 550, 'Alt Giyim', 30),
            ('Siyah Deri Ceket', 3500, 'Dış Giyim', 10), ('Kaşe Palto', 4200, 'Dış Giyim', 8),
            ('Şişme Mont', 2100, 'Dış Giyim', 15), ('Kot Ceket', 1500, 'Dış Giyim', 20),
            ('Beyaz Sneaker', 1850, 'Aksesuar', 15), ('Deri Kemer', 350, 'Aksesuar', 100),
            ('Güneş Gözlüğü', 1200, 'Aksesuar', 12), ('Sırt Çantası', 950, 'Aksesuar', 18)
        ]
        c.executemany("INSERT INTO urunler (ad, fiyat, kategori, stok) VALUES (?,?,?,?)", urunler)
    conn.commit()
    conn.close()

class MegGiyimApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        db_kur()
        self.title("MEG Giyim AI v20.0")
        self.geometry("1200x850")
        
        self.current_user = None
        self.sepet = [] 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="MEG GIYIM", font=("Impact", 35), text_color="#3498DB").pack(pady=30)
        
        # AI Arama
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Ürün/Kategori Ara...", width=180)
        self.search_entry.pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="AKILLI ARA", command=self.ai_arama, fg_color="#34495E").pack(pady=5, padx=20)

        ctk.CTkButton(self.sidebar, text="TÜM VİTRİN", command=self.vitrin_ciz).pack(pady=10, padx=20)
        self.btn_cart_sidebar = ctk.CTkButton(self.sidebar, text="SEPETİM (0)", fg_color="#E67E22", command=self.sepeti_goster)
        self.btn_cart_sidebar.pack(pady=10, padx=20)

        self.user_info = ctk.CTkLabel(self.sidebar, text="Giriş Yapılmadı", font=("Arial", 12))
        self.user_info.pack(side="bottom", pady=10)
        self.btn_login = ctk.CTkButton(self.sidebar, text="GİRİŞ / KAYIT", fg_color="#27AE60", command=self.giris_ekrani)
        self.btn_login.pack(side="bottom", pady=20, padx=20)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.vitrin_ciz()

    def temizle(self):
        for w in self.scroll.winfo_children(): w.destroy()

    def ai_arama(self):
        sorgu = self.search_entry.get().lower()
        if not sorgu: return
        self.temizle()

        conn = sqlite3.connect(db_yolu); c = conn.cursor()
        c.execute("SELECT ad FROM urunler")
        tum_adlar = [r[0] for r in c.fetchall()]
        
        eslesmeler = get_close_matches(sorgu, tum_adlar, n=5, cutoff=0.3)
        
        ctk.CTkLabel(self.scroll, text=f"Arama Sonuçları: {sorgu}", font=("Arial", 25, "bold")).pack(pady=20)
        if not eslesmeler:
            ctk.CTkLabel(self.scroll, text="Eşleşen ürün bulunamadı.").pack(pady=20)
        else:
            for ad in eslesmeler:
                c.execute("SELECT * FROM urunler WHERE ad=?", (ad,))
                self.urun_karti_olustur(c.fetchone())
        conn.close()

    def vitrin_ciz(self):
        self.temizle()
        
        # 1. AI Önerileri (Eğer sepet doluysa)
        if self.sepet:
            ctk.CTkLabel(self.scroll, text="✨ Sizin İçin AI Önerileri", font=("Arial", 20, "bold"), text_color="#F1C40F").pack(pady=10)
            son_kat = self.sepet[-1]['kategori']
            conn = sqlite3.connect(db_yolu); c = conn.cursor()
            c.execute("SELECT * FROM urunler WHERE kategori != ? ORDER BY RANDOM() LIMIT 2", (son_kat,))
            for r in c.fetchall(): self.urun_karti_olustur(r, is_special=True)
            ctk.CTkLabel(self.scroll, text="______________________________________________________", text_color="gray").pack(pady=10)
            conn.close()

        # 2. Kategorilere Göre Vitrin
        ctk.CTkLabel(self.scroll, text="Mağaza Koleksiyonu", font=("Arial", 28, "bold")).pack(pady=20)
        
        conn = sqlite3.connect(db_yolu); c = conn.cursor()
        c.execute("SELECT DISTINCT kategori FROM urunler")
        kategoriler = [r[0] for r in c.fetchall()]

        for kat in kategoriler:
            ctk.CTkLabel(self.scroll, text=f"--- {kat} ---", font=("Arial", 18, "italic"), text_color="#3498DB").pack(pady=(15, 5))
            c.execute("SELECT * FROM urunler WHERE kategori=?", (kat,))
            for row in c.fetchall():
                self.urun_karti_olustur(row)
        conn.close()

    def urun_karti_olustur(self, row, is_special=False):
        _, ad, fiyat, kat, _ = row
        color = "#2C3E50" if is_special else "transparent"
        f = ctk.CTkFrame(self.scroll, fg_color=color, border_width=(1 if is_special else 0))
        f.pack(fill="x", pady=5, padx=20)
        
        ctk.CTkLabel(f, text=ad, font=("Arial", 15, "bold"), width=200, anchor="w").pack(side="left", padx=20, pady=12)
        
        # Beden ve Renk Seçimi
        b_var = ctk.StringVar(value="M"); ctk.CTkOptionMenu(f, values=["S","M","L","XL"], variable=b_var, width=70).pack(side="left", padx=5)
        r_var = ctk.StringVar(value="Siyah"); ctk.CTkOptionMenu(f, values=["Siyah","Beyaz","Mavi"], variable=r_var, width=90).pack(side="left", padx=5)

        ctk.CTkButton(f, text=f"{fiyat} TL", width=100, fg_color="#E67E22",
                       command=lambda: self.sepete_ekle(ad, fiyat, b_var.get(), r_var.get(), kat)).pack(side="right", padx=10)

    def sepete_ekle(self, ad, fiyat, beden, renk, kat):
        self.sepet.append({"ad": ad, "fiyat": fiyat, "beden": beden, "renk": renk, "kategori": kat})
        self.btn_cart_sidebar.configure(text=f"SEPETİM ({len(self.sepet)})")
        messagebox.showinfo("AI Bildirimi", f"{ad} eklendi. AI yeni öneriler hazırlıyor!")
        self.vitrin_ciz()

    def sepeti_goster(self):
        self.temizle()
        ctk.CTkLabel(self.scroll, text="Sepetim", font=("Arial", 28, "bold")).pack(pady=20)
        toplam = sum(u['fiyat'] for u in self.sepet)
        for u in self.sepet:
            f = ctk.CTkFrame(self.scroll)
            f.pack(fill="x", pady=2, padx=20)
            ctk.CTkLabel(f, text=f"{u['ad']} ({u['beden']}/{u['renk']})").pack(side="left", padx=20)
            ctk.CTkLabel(f, text=f"{u['fiyat']} TL").pack(side="right", padx=20)
        
        ctk.CTkLabel(self.scroll, text=f"Toplam: {toplam} TL", font=("Arial", 22, "bold"), text_color="#27AE60").pack(pady=20)
        ctk.CTkButton(self.scroll, text="ADRES BİLGİLERİNE GEÇ", height=50, command=self.adres_ekrani).pack(pady=10)

    def adres_ekrani(self):
        if not self.current_user: self.giris_ekrani(); return
        self.temizle()
        
        conn = sqlite3.connect(db_yolu); c = conn.cursor()
        c.execute("SELECT adres FROM kullanicilar WHERE k_adi=?", (self.current_user,))
        eski_adr = c.fetchone()[0] or ""
        conn.close()

        ctk.CTkLabel(self.scroll, text="Teslimat Adresi", font=("Arial", 25)).pack(pady=20)
        t = ctk.CTkTextbox(self.scroll, width=500, height=150)
        t.pack(pady=10); t.insert("0.0", eski_adr)

        def siparis():
            msg = f"*AI DESTEKLİ SİPARİŞ*\n\n" + "\n".join([f"- {u['ad']} ({u['beden']}-{u['renk']})" for u in self.sepet])
            webbrowser.open(f"https://wa.me/905001234567?text={urllib.parse.quote(msg)}")
            self.sepet = []; self.btn_cart_sidebar.configure(text="SEPETİM (0)"); self.vitrin_ciz()

        ctk.CTkButton(self.scroll, text="WHATSAPP İLE GÖNDER", fg_color="#25D366", command=siparis).pack(pady=20)

    def giris_ekrani(self):
        self.temizle()
        f = ctk.CTkFrame(self.scroll, width=400); f.pack(pady=80)
        u_e = ctk.CTkEntry(f, placeholder_text="Kullanıcı Adı"); u_e.pack(pady=10)
        p_e = ctk.CTkEntry(f, placeholder_text="Şifre", show="*"); p_e.pack(pady=10)
        
        def giris():
            conn = sqlite3.connect(db_yolu); c = conn.cursor()
            c.execute("SELECT * FROM kullanicilar WHERE k_adi=? AND sifre=?", (u_e.get(), p_e.get()))
            if c.fetchone():
                self.current_user = u_e.get()
                self.user_info.configure(text=f"Hoş geldin, {self.current_user}")
                self.btn_login.configure(text="ÇIKIŞ", fg_color="#C0392B", command=self.cikis_yap)
                self.vitrin_ciz()
            conn.close()

        def kayit():
            conn = sqlite3.connect(db_yolu); c = conn.cursor()
            try:
                c.execute("INSERT INTO kullanicilar (k_adi, sifre, adres) VALUES (?,?,'')", (u_e.get(), p_e.get()))
                conn.commit(); messagebox.showinfo("OK", "Kayıt Başarılı!")
            except: pass
            conn.close()

        ctk.CTkButton(f, text="GİRİŞ", fg_color="#27AE60", command=giris).pack(pady=5)
        ctk.CTkButton(f, text="KAYIT OL", fg_color="#3498DB", command=kayit).pack(pady=5)

    def cikis_yap(self):
        self.current_user = None; self.user_info.configure(text="Giriş Yapılmadı")
        self.btn_login.configure(text="GİRİŞ / KAYIT", fg_color="#27AE60", command=self.giris_ekrani); self.vitrin_ciz()

if __name__ == "__main__":
    MegGiyimApp().mainloop()