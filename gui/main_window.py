import tkinter as tk
from tkinter import ttk, messagebox
import os
import json

from database import DatabaseManager, DatabaseConnectionError, MYSQL_AVAILABLE
from gui.theme import (
    setup_theme, COLOR_BG_DARK, COLOR_BG_LIGHT, COLOR_TEXT_WHITE,
    COLOR_ACCENT, COLOR_BORDER, COLOR_HEADER_BG, FONT_TITLE, FONT_SUBTITLE, FONT_LABEL
)

class DatabaseConfigDialog(tk.Toplevel):
    """A premium configuration dialog to handle MySQL or SQLite connection settings dynamically."""
    def __init__(self, parent, db_manager, on_success_callback):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.on_success = on_success_callback
        
        self.title("HMS - Database Configuration")
        self.geometry("450x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG_LIGHT)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.load_current_values()

    def create_widgets(self):
        # Header block
        header = tk.Frame(self, bg=COLOR_HEADER_BG, height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        lbl_title = tk.Label(header, text="Database Setup Center", fg=COLOR_TEXT_WHITE, bg=COLOR_HEADER_BG, font=FONT_TITLE)
        lbl_title.pack(pady=15, cx=20, anchor="w", padx=20)
        
        # Form frame
        form = tk.Frame(self, bg=COLOR_BG_LIGHT, padx=30, pady=20)
        form.pack(fill="both", expand=True)
        
        # Engine Choice
        tk.Label(form, text="Connection Engine:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=0, column=0, sticky="w", pady=5)
        self.var_engine = tk.StringVar(value="sqlite")
        self.cmb_engine = ttk.Combobox(form, textvariable=self.var_engine, values=["sqlite", "mysql"], state="readonly")
        self.cmb_engine.grid(row=0, column=1, sticky="ew", pady=5)
        self.cmb_engine.bind("<<ComboboxSelected>>", self.toggle_fields)
        
        # MySQL Fields
        tk.Label(form, text="MySQL Host Name:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_host = ttk.Entry(form)
        self.ent_host.grid(row=1, column=1, sticky="ew", pady=5)
        
        tk.Label(form, text="MySQL Port:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=2, column=0, sticky="w", pady=5)
        self.ent_port = ttk.Entry(form)
        self.ent_port.grid(row=2, column=1, sticky="ew", pady=5)
        
        tk.Label(form, text="Username:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=3, column=0, sticky="w", pady=5)
        self.ent_user = ttk.Entry(form)
        self.ent_user.grid(row=3, column=1, sticky="ew", pady=5)
        
        tk.Label(form, text="Password:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=4, column=0, sticky="w", pady=5)
        self.ent_pass = ttk.Entry(form, show="*")
        self.ent_pass.grid(row=4, column=1, sticky="ew", pady=5)
        
        tk.Label(form, text="Database Name:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=5, column=0, sticky="w", pady=5)
        self.ent_db = ttk.Entry(form)
        self.ent_db.grid(row=5, column=1, sticky="ew", pady=5)
        
        # SQLite Field
        tk.Label(form, text="SQLite File Path:", font=FONT_LABEL, bg=COLOR_BG_LIGHT).grid(row=6, column=0, sticky="w", pady=5)
        self.ent_sqlite = ttk.Entry(form)
        self.ent_sqlite.grid(row=6, column=1, sticky="ew", pady=5)
        
        # Grid weights
        form.columnconfigure(1, weight=1)
        
        # Info Box / Warning
        self.lbl_warning = tk.Label(
            form, 
            text="Warning: pymysql is required for MySQL connectivity.", 
            fg="red", 
            bg=COLOR_BG_LIGHT, 
            font=("Segoe UI", 9), 
            wraplength=380, 
            justify="left"
        )
        self.lbl_warning.grid(row=7, column=0, columnspan=2, pady=15)
        
        # Action Buttons frame
        actions = tk.Frame(form, bg=COLOR_BG_LIGHT)
        actions.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
        
        btn_test = ttk.Button(actions, text="Test Connection", style="Secondary.TButton", command=self.test_connection)
        btn_test.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_save = ttk.Button(actions, text="Save & Connect", style="Primary.TButton", command=self.save_and_connect)
        btn_save.pack(side="right", fill="x", expand=True, padx=5)

    def load_current_values(self):
        cfg = self.db_manager.config
        self.var_engine.set(cfg.get("db_type", "sqlite"))
        
        self.ent_host.insert(0, cfg.get("host", "localhost"))
        self.ent_port.insert(0, str(cfg.get("port", 3306)))
        self.ent_user.insert(0, cfg.get("user", "root"))
        self.ent_pass.insert(0, cfg.get("password", ""))
        self.ent_db.insert(0, cfg.get("database", "hostel_management"))
        self.ent_sqlite.insert(0, cfg.get("sqlite_path", "hostel_sandbox.db"))
        
        self.toggle_fields()

    def toggle_fields(self, event=None):
        engine = self.var_engine.get()
        if engine == "mysql":
            self.ent_host.configure(state="normal")
            self.ent_port.configure(state="normal")
            self.ent_user.configure(state="normal")
            self.ent_pass.configure(state="normal")
            self.ent_db.configure(state="normal")
            self.ent_sqlite.configure(state="disabled")
            
            if not MYSQL_AVAILABLE:
                self.lbl_warning.configure(text="MySQL Library Status: Missing! Please install 'pymysql' or click SQLite Sandbox to run instantly.", fg="red")
            else:
                self.lbl_warning.configure(text="MySQL Engine is ready to test.", fg="green")
        else:
            self.ent_host.configure(state="disabled")
            self.ent_port.configure(state="disabled")
            self.ent_user.configure(state="disabled")
            self.ent_pass.configure(state="disabled")
            self.ent_db.configure(state="disabled")
            self.ent_sqlite.configure(state="normal")
            self.lbl_warning.configure(text="SQLite Sandbox active. Zero configuration, local database file.", fg="blue")

    def test_connection(self):
        temp_config = self.get_fields_as_config()
        test_mgr = DatabaseManager()
        test_mgr.config.update(temp_config)
        test_mgr.db_type = temp_config["db_type"]
        
        try:
            test_mgr.connect()
            # If successful, test initializing schema safely
            test_mgr.initialize_schema()
            messagebox.showinfo("Success", f"Successfully connected to the {temp_config['db_type'].upper()} database!", parent=self)
            return True
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Unable to establish database connection:\n\n{e}", parent=self)
            return False

    def get_fields_as_config(self):
        return {
            "db_type": self.var_engine.get(),
            "host": self.ent_host.get().strip(),
            "port": int(self.ent_port.get().strip() or 3306),
            "user": self.ent_user.get().strip(),
            "password": self.ent_pass.get(),
            "database": self.ent_db.get().strip(),
            "sqlite_path": self.ent_sqlite.get().strip()
        }

    def save_and_connect(self):
        if self.test_connection():
            config = self.get_fields_as_config()
            self.db_manager.save_config(config)
            self.db_manager.connect()
            self.db_manager.initialize_schema()
            self.db_manager.insert_seed_data_if_empty()
            
            self.grab_release()
            self.destroy()
            self.on_success()


class MainWindow(tk.Tk):
    """The central application window managing side navigation and view mounts."""
    def __init__(self):
        super().__init__()
        self.title("Hostel Management System (HMS) - Enterprise Dashboard")
        self.geometry("1100x700")
        self.min_width = 980
        self.min_height = 600
        self.minsize(self.min_width, self.min_height)
        
        # Apply modern aesthetics theme configuration
        setup_theme(self)
        
        # Initialise database manager
        self.db = DatabaseManager()
        
        # Setup structural components layout
        self.sidebar_frame = None
        self.content_frame = None
        self.active_button = None
        self.active_view = None
        self.nav_buttons = {}

        self.check_database_and_start()

    def check_database_and_start(self):
        """Attempts connection on startup; spawns DB dialog if fails."""
        try:
            self.db.connect()
            self.db.initialize_schema()
            self.db.insert_seed_data_if_empty()
            self.build_layout()
        except DatabaseConnectionError:
            # Hide main window temporarily
            self.withdraw()
            # Launch setup dialog
            DatabaseConfigDialog(self, self.db, self.on_database_ready)

    def on_database_ready(self):
        """Re-draws and reveals the window once connection is verified."""
        self.deiconify()
        self.build_layout()

    def build_layout(self):
        # Establish base frames
        self.sidebar_frame = tk.Frame(self, bg=COLOR_BG_DARK, width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.content_frame = tk.Frame(self, bg=COLOR_BG_LIGHT)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Build Sidebar Navigation
        self.build_sidebar()
        
        # Show Dashboard View by default on start
        self.switch_view("dashboard")

    def build_sidebar(self):
        # App logo header
        logo_container = tk.Frame(self.sidebar_frame, bg=COLOR_BG_DARK, height=80)
        logo_container.pack(fill="x", side="top")
        logo_container.pack_propagate(False)
        
        lbl_logo = tk.Label(
            logo_container, 
            text="★ HMS Enterprise", 
            fg=COLOR_TEXT_WHITE, 
            bg=COLOR_BG_DARK, 
            font=FONT_SUBTITLE
        )
        lbl_logo.pack(pady=25, padx=20, anchor="w")
        
        # Navigation Buttons list
        menu_items = [
            ("dashboard", "Dashboard View"),
            ("room_types", "Room Categories"),
            ("rooms", "Room Management"),
            ("residents", "Resident Onboarding"),
            ("floor_engine", "Floor Engine Map")
        ]
        
        # Render navbar flat-buttons
        btn_container = tk.Frame(self.sidebar_frame, bg=COLOR_BG_DARK)
        btn_container.pack(fill="both", expand=True)
        
        for view_key, label in menu_items:
            # Create a custom styled sidebar button
            btn = ttk.Button(
                btn_container, 
                text=label, 
                style="Sidebar.TButton",
                command=lambda vk=view_key: self.switch_view(vk)
            )
            btn.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[view_key] = btn

        # Status badge frame at bottom of sidebar
        status_container = tk.Frame(self.sidebar_frame, bg=COLOR_BG_DARK, height=70)
        status_container.pack(fill="x", side="bottom")
        status_container.pack_propagate(False)
        
        db_type = self.db.db_type.upper()
        lbl_status = tk.Label(
            status_container, 
            text=f"DB: {db_type} Mode", 
            fg=COLOR_ACCENT if db_type == "MYSQL" else "#cbd5e1",
            bg=COLOR_HEADER_BG, 
            font=("Segoe UI", 9, "bold"),
            padx=10, 
            pady=5
        )
        lbl_status.pack(pady=10, padx=15, fill="x")

        # Dynamic binding to update status click to open connection config
        lbl_status.bind("<Button-1>", lambda e: DatabaseConfigDialog(self, self.db, self.on_reconfigured))

    def on_reconfigured(self):
        """Called when database configuration is updated via bottom badge click."""
        # Refresh current view
        for child in self.content_frame.winfo_children():
            child.destroy()
        self.build_sidebar()
        self.switch_view("dashboard")

    def switch_view(self, view_key):
        """Destroys previous frame and maps target viewport dynamically."""
        # Visual navbar status toggles
        if self.active_button:
            self.active_button.state(["!selected"])
        
        btn = self.nav_buttons.get(view_key)
        if btn:
            btn.state(["selected"])
            self.active_button = btn

        # Clean viewport
        if self.active_view:
            self.active_view.destroy()

        # Mount target UI frame
        try:
            if view_key == "dashboard":
                from gui.views.dashboard import DashboardView
                self.active_view = DashboardView(self.content_frame, self.db)
            elif view_key == "room_types":
                from gui.views.room_types import RoomTypesView
                self.active_view = RoomTypesView(self.content_frame, self.db)
            elif view_key == "rooms":
                from gui.views.rooms import RoomsView
                self.active_view = RoomsView(self.content_frame, self.db)
            elif view_key == "residents":
                from gui.views.residents import ResidentsView
                self.active_view = ResidentsView(self.content_frame, self.db)
            elif view_key == "floor_engine":
                from gui.views.floor_engine import FloorEngineView
                self.active_view = FloorEngineView(self.content_frame, self.db)
            
            self.active_view.pack(fill="both", expand=True)
        except Exception as e:
            # Fallback error container inside the viewport
            err_frame = tk.Frame(self.content_frame, bg=COLOR_BG_LIGHT)
            err_frame.pack(fill="both", expand=True)
            tk.Label(err_frame, text="View Loading Error", font=FONT_TITLE, fg="red", bg=COLOR_BG_LIGHT).pack(pady=40)
            tk.Label(err_frame, text=f"Unable to load view '{view_key}':\n{e}", font=FONT_LABEL, bg=COLOR_BG_LIGHT, justify="center").pack(pady=10)
            print(f"Viewport Swapping Exception: {e}")
