import tkinter as tk
from tkinter import ttk, messagebox

from gui.theme import (
    COLOR_BG_LIGHT, COLOR_CARD_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_HEADER_BG, COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER, COLOR_STATUS_RED, FONT_TITLE, FONT_SUBTITLE,
    FONT_LABEL, FONT_BODY
)

class RoomsView(tk.Frame):
    """View managing individual room registrations, floor assignments, and occupancy visual matrices."""
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg=COLOR_BG_LIGHT)
        self.db = db_manager
        self.room_types_cache = {}
        
        self.pack_propagate(False)
        self.create_layout()
        self.refresh_room_types_dropdown()
        self.refresh_rooms_list()

    def create_layout(self):
        # Header block
        header = tk.Frame(self, bg=COLOR_BG_LIGHT, pady=15, padx=25)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="Room Unit Allocation & Management", font=FONT_TITLE, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_PRIMARY)
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = tk.Label(header, text="Register physical dorm units, map layout tiers, assign floor capacities, and inspect real-time vacancies", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_subtitle.pack(anchor="w", pady=2)

        # Dual-column Workspace
        workspace = tk.Frame(self, bg=COLOR_BG_LIGHT, padx=25, pady=5)
        workspace.pack(fill="both", expand=True)
        
        # Left Panel - Register Room Form
        left_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT, width=320)
        left_panel.pack(side="left", fill="y", padx=(0, 15), pady=10)
        left_panel.pack_propagate(False)
        
        card_form = tk.Frame(left_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        card_form.pack(fill="both", expand=True)
        
        lbl_form_hdr = tk.Label(card_form, text="Register New Room Unit", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_form_hdr.pack(anchor="w", pady=(0, 15))
        
        # Inputs
        tk.Label(card_form, text="Room Identifier (Number):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.ent_number = ttk.Entry(card_form)
        self.ent_number.pack(fill="x", pady=(0, 10))
        
        tk.Label(card_form, text="Floor Assignment:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.cmb_floor = ttk.Combobox(card_form, values=["Floor 1", "Floor 2", "Floor 3", "Floor 4", "Floor 5"], state="readonly")
        self.cmb_floor.pack(fill="x", pady=(0, 10))
        self.cmb_floor.set("Floor 1")
        
        tk.Label(card_form, text="Layout Tier Class:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.cmb_type = ttk.Combobox(card_form, state="readonly")
        self.cmb_type.pack(fill="x", pady=(0, 10))
        self.cmb_type.bind("<<ComboboxSelected>>", self.on_type_selected)
        
        # Live Pricing Feedback Card (Read-only status area)
        self.price_frame = tk.Frame(card_form, bg=COLOR_BG_LIGHT, highlightbackground=COLOR_BORDER, highlightthickness=1, pady=10, padx=12)
        self.price_frame.pack(fill="x", pady=(5, 12))
        
        self.lbl_tier_price = tk.Label(self.price_frame, text="Semester Rate: $0.00", font=("Segoe UI", 10, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG_LIGHT)
        self.lbl_tier_price.pack(anchor="w")
        
        self.lbl_tier_assets = tk.Label(self.price_frame, text="Assets: No layout selected", font=("Segoe UI", 8, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_BG_LIGHT, wraplength=240, justify="left")
        self.lbl_tier_assets.pack(anchor="w", pady=(5, 0))
        
        tk.Label(card_form, text="Total Bed Capacity:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)
        self.cmb_capacity = ttk.Combobox(card_form, values=["1", "2", "4", "6", "8"], state="readonly")
        self.cmb_capacity.pack(fill="x", pady=(0, 15))
        self.cmb_capacity.set("2")

        btn_save = ttk.Button(card_form, text="Register Room Unit", style="Primary.TButton", command=self.save_room)
        btn_save.pack(fill="x", ipady=5, pady=(5, 0))

        # Right Panel - Configuration Master Table
        right_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT)
        right_panel.pack(side="right", fill="both", expand=True, pady=10)
        
        card_table = tk.Frame(right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        card_table.pack(fill="both", expand=True)
        
        lbl_table_hdr = tk.Label(card_table, text="Room Inventory Directory", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_table_hdr.pack(anchor="w", pady=(0, 15))
        
        # Table Grid (Treeview)
        cols = ("id", "number", "type", "floor", "occupancy", "status", "assets")
        self.tree = ttk.Treeview(card_table, columns=cols, show="headings")
        
        self.tree.heading("id", text="Room ID")
        self.tree.heading("number", text="Room #")
        self.tree.heading("type", text="Layout Class")
        self.tree.heading("floor", text="Floor")
        self.tree.heading("occupancy", text="Beds Occupied")
        self.tree.heading("status", text="Status Flag")
        self.tree.heading("assets", text="Equipped Assets Checklist")
        
        self.tree.column("id", width=60, minwidth=50, anchor="center")
        self.tree.column("number", width=70, minwidth=60, anchor="center")
        self.tree.column("type", width=130, minwidth=100, anchor="w")
        self.tree.column("floor", width=90, minwidth=80, anchor="center")
        self.tree.column("occupancy", width=90, minwidth=80, anchor="center")
        self.tree.column("status", width=110, minwidth=90, anchor="center")
        self.tree.column("assets", width=180, minwidth=140, anchor="w")
        
        # Scrollbars
        vsb = ttk.Scrollbar(card_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(card_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack layouts inside right frame
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        hsb.pack(fill="x")

    def refresh_room_types_dropdown(self):
        """Loads room category options from the database and saves metadata locally."""
        try:
            records = self.db.get_room_types()
            names = []
            self.room_types_cache.clear()
            for r in records:
                names.append(r["type_name"])
                self.room_types_cache[r["type_name"]] = r
                
            self.cmb_type.configure(values=names)
            if names:
                self.cmb_type.set(names[0])
                self.on_type_selected()
        except Exception as e:
            print(f"Error loading dropdown filters: {e}")

    def on_type_selected(self, event=None):
        """Fires automatically on room type selections to lock in semester rates."""
        selected = self.cmb_type.get()
        r_type = self.room_types_cache.get(selected)
        if r_type:
            price = float(r_type.get("semester_base_price", 0))
            assets = r_type.get("inventory_assets", [])
            
            self.lbl_tier_price.configure(text=f"Semester Rate: ${price:,.2f}")
            self.lbl_tier_assets.configure(text=f"Assets: {', '.join(assets) or 'None'}")

    def refresh_rooms_list(self):
        """Fetches physical unit profiles and renders standard table row data."""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            records = self.db.get_rooms()
            for r in records:
                occ_str = f"{r['current_occupancy']} / {r['total_capacity']}"
                assets_str = ", ".join(r.get("inventory_assets", []))
                
                self.tree.insert("", "end", values=(
                    r["room_id"],
                    r["room_number"],
                    r["type_name"],
                    r["floor_assignment"],
                    occ_str,
                    r["room_status"],
                    assets_str or "None"
                ))
        except Exception as e:
            print(f"Error refreshing rooms table: {e}")

    def save_room(self):
        """Validates entry values and updates physical rooms catalog."""
        number = self.ent_number.get().strip()
        floor = self.cmb_floor.get()
        type_name = self.cmb_type.get()
        capacity_raw = self.cmb_capacity.get()
        
        if not number:
            messagebox.showerror("Validation Error", "Room Identifier Number is required.")
            return

        try:
            capacity = int(capacity_raw)
            if capacity <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Total capacity must be a positive integer.")
            return

        r_type = self.room_types_cache.get(type_name)
        if not r_type:
            messagebox.showerror("Validation Error", "Please register a valid layout class tier first.")
            return
            
        type_id = r_type["room_type_id"]

        try:
            self.db.add_room(type_id, number, floor, capacity)
            messagebox.showinfo("Success", f"Dorm Room unit '{number}' successfully created and allocated to {type_name}.")
            
            self.ent_number.delete(0, tk.END)
            self.refresh_rooms_list()
        except Exception as e:
            messagebox.showerror("Database Write Error", f"Failed to register room record. Verify that Room Number is unique!\n\n{e}")
