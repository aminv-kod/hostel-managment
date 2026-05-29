import tkinter as tk
from tkinter import ttk

# --- Slate/Navy Theme Color Palette ---
COLOR_BG_LIGHT = "#f8fafc"       # Slate 50 (General background)
COLOR_BG_DARK = "#0f172a"        # Slate 900 (Sidebar background)
COLOR_HEADER_BG = "#1e293b"      # Slate 800 (Header backgrounds)
COLOR_CARD_BG = "#ffffff"        # Pure White (Card background)
COLOR_BORDER = "#e2e8f0"         # Slate 200 (Card/Field borders)

# Text Colors
COLOR_TEXT_PRIMARY = "#0f172a"   # Slate 900 (Primary text)
COLOR_TEXT_MUTED = "#64748b"     # Slate 500 (Subtitles, captions)
COLOR_TEXT_WHITE = "#ffffff"     # White text for dark headers/buttons

# Status Indicators
COLOR_STATUS_GREEN = "#10b981"   # Emerald 500 (Vacant Space / Success)
COLOR_STATUS_AMBER = "#f59e0b"   # Amber 500 (Partially Booked / Notice)
COLOR_STATUS_RED = "#ef4444"     # Rose 500 (Fully Booked / Danger)

# Theme Brand Accent
COLOR_ACCENT = "#3b82f6"         # Blue 500 (Primary buttons, selections)
COLOR_ACCENT_HOVER = "#2563eb"   # Blue 600

# Fonts
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_CAPTION = ("Segoe UI", 9, "italic")
FONT_KPI = ("Segoe UI", 24, "bold")

def setup_theme(root):
    """Configures the ttk.Style mappings to establish a modern Slate/Navy layout."""
    style = ttk.Style()
    
    # Use 'clam' as a baseline theme for better cross-platform styling support
    if "clam" in style.theme_names():
        style.theme_use("clam")

    # Clear backgrounds
    root.configure(bg=COLOR_BG_LIGHT)

    # Base frame configurations
    style.configure("TFrame", background=COLOR_BG_LIGHT)
    style.configure("Card.TFrame", background=COLOR_CARD_BG, borderwidth=1, relief="solid")
    style.configure("Sidebar.TFrame", background=COLOR_BG_DARK)
    
    # Label Configurations
    style.configure("TLabel", background=COLOR_BG_LIGHT, foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Header.TLabel", background=COLOR_BG_LIGHT, foreground=COLOR_BG_DARK, font=FONT_TITLE)
    style.configure("CardHeader.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_PRIMARY, font=FONT_SUBTITLE)
    style.configure("CardBody.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MUTED, font=FONT_BODY)
    style.configure("Sidebar.TLabel", background=COLOR_BG_DARK, foreground=COLOR_TEXT_WHITE, font=FONT_BODY)

    # Button Configurations
    style.configure("TButton", background=COLOR_BG_LIGHT, foreground=COLOR_TEXT_PRIMARY, borderwidth=1, font=FONT_LABEL)
    style.configure("Primary.TButton", background=COLOR_ACCENT, foreground=COLOR_TEXT_WHITE, borderwidth=0, font=FONT_LABEL)
    style.map("Primary.TButton", background=[("active", COLOR_ACCENT_HOVER)])
    
    style.configure("Secondary.TButton", background=COLOR_BORDER, foreground=COLOR_TEXT_PRIMARY, borderwidth=1, font=FONT_LABEL)
    
    style.configure("Sidebar.TButton", background=COLOR_BG_DARK, foreground=COLOR_TEXT_WHITE, borderwidth=0, font=FONT_BODY, anchor="w", padding=(15, 10))
    style.map("Sidebar.TButton", 
              background=[("active", COLOR_HEADER_BG), ("selected", COLOR_ACCENT)],
              foreground=[("active", COLOR_TEXT_WHITE)])

    # Entry (Inputs) Configurations
    style.configure("TEntry", fieldbackground=COLOR_CARD_BG, borderwidth=1, relief="solid", font=FONT_BODY)
    style.configure("TCombobox", fieldbackground=COLOR_CARD_BG, background=COLOR_BG_LIGHT, borderwidth=1, font=FONT_BODY)

    # Treeview Styles (Grids)
    style.configure("Treeview", 
                    background=COLOR_CARD_BG, 
                    foreground=COLOR_TEXT_PRIMARY, 
                    rowheight=30, 
                    fieldbackground=COLOR_CARD_BG,
                    font=FONT_BODY,
                    borderwidth=1,
                    relief="solid")
    
    style.configure("Treeview.Heading", 
                    background=COLOR_HEADER_BG, 
                    foreground=COLOR_TEXT_WHITE, 
                    font=FONT_LABEL, 
                    borderwidth=0)
    
    style.map("Treeview", 
              background=[("selected", COLOR_ACCENT)],
              foreground=[("selected", COLOR_TEXT_WHITE)])

    # Scrollbar
    style.configure("Vertical.TScrollbar", background=COLOR_BG_LIGHT, borderwidth=0, arrowsize=12)

    return style
