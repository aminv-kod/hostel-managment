import tkinter as tk
from tkinter import ttk, messagebox
import json

from gui.theme import (
    COLOR_BG_LIGHT, COLOR_CARD_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_HEADER_BG, FONT_TITLE, FONT_SUBTITLE,
    FONT_LABEL, FONT_BODY
)

class RoomTypesView(tk.Frame):
    """View managing the creation of room categories (e.g. Deluxe Single) and JSON inventory checkbox mapping."""
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg=COLOR_BG_LIGHT)
        self.db = db_manager
        
        self.pack_propagate(False)
        self.create_layout()
        self.refresh_list()

    def create_layout(self):
        # Header block
        header = tk.Frame(self, bg=COLOR_BG_LIGHT, pady=15, padx=25)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="Room Categories & Inventory Setups", font=FONT_TITLE, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_PRIMARY)
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = tk.Label(header, text="Configure accommodation tiers, baseline pricing, and standard physical asset checklist", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_subtitle.pack(anchor="w", pady=2)

        # Dual-column Workspace
        workspace = tk.Frame(self, bg=COLOR_BG_LIGHT, padx=25, pady=5)
        workspace.pack(fill="both", expand=True)
        
        # Left Panel - Registration Form
        left_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT, width=320)
        left_panel.pack(side="left", fill="y", padx=(0, 15), pady=10)
        left_panel.pack_propagate(False)
        
        card_form = tk.Frame(left_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        card_form.pack(fill="both", expand=True)
        
        lbl_form_hdr = tk.Label(card_form, text="Create Layout Tier", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_form_hdr.pack(anchor="w", pady=(0, 15))
        
        # Inputs
        tk.Label(card_form, text="Category Class Name:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.ent_name = ttk.Entry(card_form)
        self.ent_name.pack(fill="x", pady=(0, 10))
        
        tk.Label(card_form, text="Semester Base Rate ($):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.ent_price = ttk.Entry(card_form)
        self.ent_price.pack(fill="x", pady=(0, 15))
        
        # Inventory checklist block
        tk.Label(card_form, text="Assigned Physical Assets:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        
        checklist_frame = tk.Frame(card_form, bg=COLOR_CARD_BG)
        checklist_frame.pack(fill="x", pady=(0, 15))
        
        # List of items to checkbox map
        self.assets_list = ["Air Conditioner", "Mini Fridge", "Study Desk", "Pillows", "Fan", "Shared Lockers", "Personal Safe"]
        self.assets_vars = {}
        
        for item in self.assets_list:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(
                checklist_frame, 
                text=item, 
                variable=var, 
                bg=COLOR_CARD_BG, 
                activebackground=COLOR_CARD_BG,
                font=FONT_BODY,
                anchor="w"
            )
            chk.pack(fill="x", pady=2)
            self.assets_vars[item] = var

        # Optional Custom asset field
        tk.Label(card_form, text="Add Custom Asset:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.ent_custom = ttk.Entry(card_form)
        self.ent_custom.pack(fill="x", pady=(0, 15))

        btn_save = ttk.Button(card_form, text="Save Classification Tier", style="Primary.TButton", command=self.save_category)
        btn_save.pack(fill="x", ipady=5, pady=(5, 0))

        # Right Panel - Configuration Master Table
        right_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT)
        right_panel.pack(side="right", fill="both", expand=True, pady=10)
        
        card_table = tk.Frame(right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        card_table.pack(fill="both", expand=True)
        
        lbl_table_hdr = tk.Label(card_table, text="Registered Configurations", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_table_hdr.pack(anchor="w", pady=(0, 15))
        
        # Table Grid (Treeview)
        cols = ("id", "name", "price", "assets")
        self.tree = ttk.Treeview(card_table, columns=cols, show="headings")
        
        self.tree.heading("id", text="Type ID")
        self.tree.heading("name", text="Layout Tier Class Name")
        self.tree.heading("price", text="Base Rate / Semester")
        self.tree.heading("assets", text="Equipped Assets Inventory Checklist")
        
        self.tree.column("id", width=60, minwidth=50, anchor="center")
        self.tree.column("name", width=180, minwidth=150, anchor="w")
        self.tree.column("price", width=120, minwidth=100, anchor="e")
        self.tree.column("assets", width=250, minwidth=200, anchor="w")
        
        # Scrollbars
        vsb = ttk.Scrollbar(card_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(card_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack layouts inside right frame
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        hsb.pack(fill="x")

    def refresh_list(self):
        """Fetches classification profiles and populates the data table grid."""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            records = self.db.get_room_types()
            for r in records:
                assets_str = ", ".join(r.get("inventory_assets", []))
                price_val = f"${float(r['semester_base_price']):,.2f}"
                
                self.tree.insert("", "end", values=(
                    r["room_type_id"],
                    r["type_name"],
                    price_val,
                    assets_str or "None Selected"
                ))
        except Exception as e:
            print(f"Error loading room categories table: {e}")

    def save_category(self):
        """Reads variables, parses custom inputs, and posts database payload."""
        name = self.ent_name.get().strip()
        price_raw = self.ent_price.get().strip()
        custom_asset = self.ent_custom.get().strip()
        
        if not name or not price_raw:
            messagebox.showerror("Validation Error", "All fields are required. Please input Class Name and Base Price.")
            return
            
        try:
            price = float(price_raw)
            if price <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Semester Base Rate must be a valid positive number.")
            return

        # Aggregate checklist variables
        selected_assets = []
        for asset, var in self.assets_vars.items():
            if var.get():
                selected_assets.append(asset)
                
        if custom_asset:
            selected_assets.append(custom_asset)

        try:
            self.db.add_room_type(name, price, selected_assets)
            messagebox.showinfo("Success", f"Category layout '{name}' saved successfully.")
            
            # Reset Fields
            self.ent_name.delete(0, tk.END)
            self.ent_price.delete(0, tk.END)
            self.ent_custom.delete(0, tk.END)
            for var in self.assets_vars.values():
                var.set(False)
                
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Database Write Error", f"Could not create room category record:\n{e}")
