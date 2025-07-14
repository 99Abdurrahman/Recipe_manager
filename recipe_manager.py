import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from datetime import datetime
import os

class RecipeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🏨 ARİN RESORT HOTEL Mutfak Reçete Yönetimi")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Database connection
        self.conn = sqlite3.connect('recipes.db')
        self.c = self.conn.cursor()
        self.create_table()
        
        # Create GUI
        self.create_widgets()
        
    def create_table(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun TEXT,
                ogun TEXT,
                bolum TEXT,
                yemek_adi TEXT,
                malzemeler TEXT,
                küvet INTEGER
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🏨 ARİN RESORT HOTEL Mutfak Reçete Yönetimi", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_add_tab()
        self.create_view_tab()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_add_tab(self):
        # Add Recipe Tab
        add_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(add_frame, text="📥 Reçete Ekle")
        
        # Input fields
        ttk.Label(add_frame, text="Gün:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.gun_var = tk.StringVar()
        gun_combo = ttk.Combobox(add_frame, textvariable=self.gun_var, 
                                values=["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        gun_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(add_frame, text="Öğün:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ogun_var = tk.StringVar()
        ogun_combo = ttk.Combobox(add_frame, textvariable=self.ogun_var, 
                                 values=["Sabah", "Öğle", "Akşam"])
        ogun_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(add_frame, text="Bölüm:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.bolum_var = tk.StringVar()
        bolum_combo = ttk.Combobox(add_frame, textvariable=self.bolum_var, 
                                  values=["Soğuk", "Sıcak", "Pastane"])
        bolum_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(add_frame, text="Yemek Adı:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.yemek_adi_var = tk.StringVar()
        yemek_entry = ttk.Entry(add_frame, textvariable=self.yemek_adi_var)
        yemek_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(add_frame, text="Malzemeler:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.malzemeler_text = tk.Text(add_frame, height=5, width=40)
        self.malzemeler_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(add_frame, text="Küvet Sayısı:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.küvet_var = tk.IntVar(value=1)
        küvet_spin = ttk.Spinbox(add_frame, from_=1, to=100, textvariable=self.küvet_var)
        küvet_spin.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Save button
        save_btn = ttk.Button(add_frame, text="💾 Kaydet", command=self.save_recipe)
        save_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Configure grid weights
        add_frame.columnconfigure(1, weight=1)
        
    def create_view_tab(self):
        # View Recipes Tab
        view_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(view_frame, text="📋 Reçeteleri Görüntüle")
        
        # Buttons frame
        button_frame = ttk.Frame(view_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Yenile", command=self.refresh_data)
        refresh_btn.grid(row=0, column=0, padx=5)
        
        export_btn = ttk.Button(button_frame, text="⬇️ Excel'e Aktar", command=self.export_to_excel)
        export_btn.grid(row=0, column=1, padx=5)
        
        delete_btn = ttk.Button(button_frame, text="🗑️ Seçili Kaydı Sil", command=self.delete_selected)
        delete_btn.grid(row=0, column=2, padx=5)
        
        # Treeview for displaying data
        columns = ("ID", "Gün", "Öğün", "Bölüm", "Yemek Adı", "Malzemeler", "Küvet")
        self.tree = ttk.Treeview(view_frame, columns=columns, show="headings", height=15)
        
        # Define column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(view_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Update/Edit frame
        edit_frame = ttk.LabelFrame(view_frame, text="Seçili Kaydı Düzenle", padding="10")
        edit_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Edit fields
        ttk.Label(edit_frame, text="Gün:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.edit_gun_var = tk.StringVar()
        edit_gun_combo = ttk.Combobox(edit_frame, textvariable=self.edit_gun_var, 
                                     values=["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        edit_gun_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(edit_frame, text="Öğün:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.edit_ogun_var = tk.StringVar()
        edit_ogun_combo = ttk.Combobox(edit_frame, textvariable=self.edit_ogun_var, 
                                      values=["Sabah", "Öğle", "Akşam"])
        edit_ogun_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(edit_frame, text="Bölüm:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.edit_bolum_var = tk.StringVar()
        edit_bolum_combo = ttk.Combobox(edit_frame, textvariable=self.edit_bolum_var, 
                                       values=["Soğuk", "Sıcak", "Pastane"])
        edit_bolum_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(edit_frame, text="Küvet:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.edit_küvet_var = tk.IntVar()
        edit_küvet_spin = ttk.Spinbox(edit_frame, from_=1, to=100, textvariable=self.edit_küvet_var)
        edit_küvet_spin.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(edit_frame, text="Yemek Adı:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.edit_yemek_adi_var = tk.StringVar()
        edit_yemek_entry = ttk.Entry(edit_frame, textvariable=self.edit_yemek_adi_var)
        edit_yemek_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(edit_frame, text="Malzemeler:").grid(row=3, column=0, sticky=tk.NW, pady=2)
        self.edit_malzemeler_text = tk.Text(edit_frame, height=3, width=60)
        self.edit_malzemeler_text.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        # Update button
        update_btn = ttk.Button(edit_frame, text="🔄 Güncelle", command=self.update_recipe)
        update_btn.grid(row=4, column=0, columnspan=4, pady=10)
        
        # Configure grid weights
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(1, weight=1)
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.columnconfigure(3, weight=1)
        
        # Bind treeview selection
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Load initial data
        self.refresh_data()
        
    def save_recipe(self):
        gun = self.gun_var.get()
        ogun = self.ogun_var.get()
        bolum = self.bolum_var.get()
        yemek_adi = self.yemek_adi_var.get()
        malzemeler = self.malzemeler_text.get("1.0", tk.END).strip()
        küvet = self.küvet_var.get()
        
        if not yemek_adi or not malzemeler:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return
        
        try:
            self.c.execute('INSERT INTO recipes (gun, ogun, bolum, yemek_adi, malzemeler, küvet) VALUES (?, ?, ?, ?, ?, ?)',
                          (gun, ogun, bolum, yemek_adi, malzemeler, küvet))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Reçete başarıyla kaydedildi!")
            
            # Clear fields
            self.gun_var.set("")
            self.ogun_var.set("")
            self.bolum_var.set("")
            self.yemek_adi_var.set("")
            self.malzemeler_text.delete("1.0", tk.END)
            self.küvet_var.set(1)
            
            # Refresh data if on view tab
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt sırasında hata: {str(e)}")
    
    def refresh_data(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch and display data
        self.c.execute('SELECT * FROM recipes ORDER BY id DESC')
        rows = self.c.fetchall()
        
        for row in rows:
            self.tree.insert('', 'end', values=row)
    
    def on_item_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # Populate edit fields
            self.edit_gun_var.set(values[1])
            self.edit_ogun_var.set(values[2])
            self.edit_bolum_var.set(values[3])
            self.edit_yemek_adi_var.set(values[4])
            self.edit_malzemeler_text.delete("1.0", tk.END)
            self.edit_malzemeler_text.insert("1.0", values[5])
            self.edit_küvet_var.set(values[6])
    
    def update_recipe(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen güncellemek için bir kayıt seçin!")
            return
        
        item = self.tree.item(selection[0])
        recipe_id = item['values'][0]
        
        gun = self.edit_gun_var.get()
        ogun = self.edit_ogun_var.get()
        bolum = self.edit_bolum_var.get()
        yemek_adi = self.edit_yemek_adi_var.get()
        malzemeler = self.edit_malzemeler_text.get("1.0", tk.END).strip()
        küvet = self.edit_küvet_var.get()
        
        if not yemek_adi or not malzemeler:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return
        
        try:
            self.c.execute('''
                UPDATE recipes 
                SET gun=?, ogun=?, bolum=?, yemek_adi=?, malzemeler=?, küvet=?
                WHERE id=?
            ''', (gun, ogun, bolum, yemek_adi, malzemeler, küvet, recipe_id))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Reçete güncellendi!")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme sırasında hata: {str(e)}")
    
    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin!")
            return
        
        if messagebox.askyesno("Onay", "Seçili kaydı silmek istediğinizden emin misiniz?"):
            item = self.tree.item(selection[0])
            recipe_id = item['values'][0]
            
            try:
                self.c.execute('DELETE FROM recipes WHERE id=?', (recipe_id,))
                self.conn.commit()
                messagebox.showinfo("Başarılı", "Kayıt silindi!")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Hata", f"Silme sırasında hata: {str(e)}")
    
    def export_to_excel(self):
        try:
            self.c.execute('SELECT * FROM recipes')
            data = self.c.fetchall()
            
            if not data:
                messagebox.showwarning("Uyarı", "Aktarılacak veri bulunamadı!")
                return
            
            df = pd.DataFrame(data, columns=["ID", "Gün", "Öğün", "Bölüm", "Yemek Adı", "Malzemeler", "Küvet"])
            
            # File dialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Excel dosyasını kaydet"
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Başarılı", f"Veriler {filename} dosyasına aktarıldı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Excel aktarımı sırasında hata: {str(e)}")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
 
if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeManager(root)
    root.mainloop()