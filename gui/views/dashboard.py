import tkinter as tk
from tkinter import ttk

from gui.theme import (
    COLOR_BG_LIGHT, COLOR_CARD_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_HEADER_BG, COLOR_STATUS_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_LABEL, FONT_BODY, FONT_KPI
)

class DashboardView(tk.Frame):
    """View component rendering the central management stats, financial summaries, and inventory audits."""
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg=COLOR_BG_LIGHT)
        self.db = db_manager
        
        self.pack_propagate(False)
        self.create_layout()
        self.refresh_data()

    def create_layout(self):
        # Header block
        header = tk.Frame(self, bg=COLOR_BG_LIGHT, pady=15, padx=25)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="System Analytics & Ledger Summary", font=FONT_TITLE, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_PRIMARY)
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = tk.Label(header, text="Live operational performance and physical assets summary", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_subtitle.pack(anchor="w", pady=2)
        
        # Scrollable container for the dashboard contents
        self.canvas = tk.Canvas(self, bg=COLOR_BG_LIGHT, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scroll_content = tk.Frame(self.canvas, bg=COLOR_BG_LIGHT, padx=25)
        self.scroll_content.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind resize event to ensure responsive layout scaling
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 1. Operational KPIs Block
        lbl_ops_hdr = tk.Label(self.scroll_content, text="OPERATIONAL BED-SPACE STATS", font=FONT_LABEL, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_ops_hdr.pack(anchor="w", pady=(10, 5))
        
        self.kpi_frame = tk.Frame(self.scroll_content, bg=COLOR_BG_LIGHT)
        self.kpi_frame.pack(fill="x", pady=5)
        
        # Define placeholders for KPI text values
        self.lbl_kpi_rooms = self.create_kpi_card(self.kpi_frame, "Total Active Rooms", "0", 0)
        self.lbl_kpi_occupied = self.create_kpi_card(self.kpi_frame, "Total Beds Occupied", "0", 1)
        self.lbl_kpi_open = self.create_kpi_card(self.kpi_frame, "Open Beds Available", "0", 2)
        self.lbl_kpi_residents = self.create_kpi_card(self.kpi_frame, "Active Registrés", "0", 3)
        
        # 2. Financial Ledger Section
        lbl_fin_hdr = tk.Label(self.scroll_content, text="FINANCIAL OVERVIEW (HOSTEL VS ACADEMIC)", font=FONT_LABEL, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_fin_hdr.pack(anchor="w", pady=(20, 5))
        
        self.fin_frame = tk.Frame(self.scroll_content, bg=COLOR_BG_LIGHT)
        self.fin_frame.pack(fill="x", pady=5)
        
        self.lbl_fin_deposits = self.create_financial_card(self.fin_frame, "Security Deposits Held", "$0.00", 0, COLOR_ACCENT)
        self.lbl_fin_fees = self.create_financial_card(self.fin_frame, "Hostel Fees Collected", "$0.00", 1, "#10b981")
        self.lbl_fin_debt = self.create_financial_card(self.fin_frame, "Academic Tuition Arrears", "$0.00", 2, COLOR_STATUS_RED)

        # 3. Floor Equipment/Asset Inventory Section
        lbl_inv_hdr = tk.Label(self.scroll_content, text="FACILITY EQUIPMENT DIRECTORY (PARSED ROOM LAYOUT ASSETS)", font=FONT_LABEL, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_inv_hdr.pack(anchor="w", pady=(25, 5))
        
        self.inv_card = tk.Frame(self.scroll_content, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.inv_card.pack(fill="x", pady=(5, 30))
        
        self.inv_container = tk.Frame(self.inv_card, bg=COLOR_CARD_BG, padx=20, pady=20)
        self.inv_container.pack(fill="both", expand=True)

    def _on_canvas_configure(self, event):
        # Scale the scrollable width to fit window width
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def create_kpi_card(self, parent, title, val, col_idx):
        card = tk.Frame(parent, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=15, pady=15)
        card.grid(row=0, column=col_idx, padx=5, pady=5, sticky="nsew")
        parent.columnconfigure(col_idx, weight=1)
        
        lbl_title = tk.Label(card, text=title.upper(), font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG)
        lbl_title.pack(anchor="w")
        
        lbl_val = tk.Label(card, text=val, font=FONT_KPI, fg=COLOR_TEXT_PRIMARY, bg=COLOR_CARD_BG)
        lbl_val.pack(anchor="w", pady=(5, 0))
        
        return lbl_val

    def create_financial_card(self, parent, title, val, col_idx, value_color):
        card = tk.Frame(parent, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=18, pady=18)
        card.grid(row=0, column=col_idx, padx=6, pady=5, sticky="nsew")
        parent.columnconfigure(col_idx, weight=1)
        
        lbl_title = tk.Label(card, text=title.upper(), font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG)
        lbl_title.pack(anchor="w")
        
        lbl_val = tk.Label(card, text=val, font=("Segoe UI", 20, "bold"), fg=value_color, bg=COLOR_CARD_BG)
        lbl_val.pack(anchor="w", pady=(6, 0))
        
        return lbl_val

    def refresh_data(self):
        """Fetches operational metrics and redraws the cards and asset directories."""
        try:
            # 1. Update KPIs
            kpis = self.db.get_kpi_metrics()
            self.lbl_kpi_rooms.configure(text=str(kpis["total_rooms"]))
            self.lbl_kpi_occupied.configure(text=str(kpis["occupied_beds"]))
            self.lbl_kpi_open.configure(text=str(kpis["open_beds"]))
            self.lbl_kpi_residents.configure(text=str(kpis["active_residents"]))
            
            # 2. Update Financials
            fin = self.db.get_financial_summary()
            self.lbl_fin_deposits.configure(text=f"${fin['deposits']:,.2f}")
            self.lbl_fin_fees.configure(text=f"${fin['fees']:,.2f}")
            self.lbl_fin_debt.configure(text=f"${fin['debt']:,.2f}")
            
            # 3. Rebuild assets breakdown grid
            for child in self.inv_container.winfo_children():
                child.destroy()
                
            assets = self.db.get_inventory_summary()
            if not assets:
                lbl_empty = tk.Label(self.inv_container, text="No active facility equipment registered. Set up layouts to view asset metrics.", font=FONT_BODY, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED)
                lbl_empty.pack(pady=10)
            else:
                # Build an organized multi-column grid list of assets
                r, c = 0, 0
                max_cols = 3
                for idx, (asset_name, count) in enumerate(assets.items()):
                    item_frame = tk.Frame(self.inv_container, bg=COLOR_BG_LIGHT, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=12, pady=10)
                    item_frame.grid(row=r, column=c, padx=10, pady=8, sticky="ew")
                    self.inv_container.columnconfigure(c, weight=1)
                    
                    lbl_name = tk.Label(item_frame, text=asset_name, font=FONT_BODY, fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_LIGHT)
                    lbl_name.pack(side="left")
                    
                    lbl_count = tk.Label(
                        item_frame, 
                        text=f"{count} Units Active", 
                        font=("Segoe UI", 9, "bold"), 
                        fg=COLOR_TEXT_WHITE, 
                        bg=COLOR_HEADER_BG, 
                        padx=8, 
                        pady=3
                    )
                    lbl_count.pack(side="right")
                    
                    c += 1
                    if c >= max_cols:
                        c = 0
                        r += 1
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
