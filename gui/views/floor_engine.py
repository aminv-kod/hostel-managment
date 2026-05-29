import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from gui.theme import (
    COLOR_BG_LIGHT, COLOR_CARD_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_HEADER_BG, COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER, COLOR_STATUS_RED, COLOR_TEXT_WHITE, FONT_TITLE, FONT_SUBTITLE,
    FONT_LABEL, FONT_BODY, FONT_KPI
)

class FloorEngineView(tk.Frame):
    """View rendering color-coded physical grids, executing cron checkout runs, and extending resident stay times."""
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg=COLOR_BG_LIGHT)
        self.db = db_manager
        self.selected_room = None
        self.room_buttons = {}
        
        self.pack_propagate(False)
        self.create_layout()
        self.load_floor_map()

    def create_layout(self):
        # Header block
        header = tk.Frame(self, bg=COLOR_BG_LIGHT, pady=12, padx=25)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="Reactive Floor Engine Map & Stay Auditing", font=FONT_TITLE, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_PRIMARY)
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = tk.Label(header, text="Interactive room grids, batch stay audits, automated check-outs, and booking extensions", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_subtitle.pack(anchor="w", pady=2)

        # Operational Panel (Top Automation Actions)
        action_bar = tk.Frame(self, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=12)
        action_bar.pack(fill="x", padx=25, pady=(5, 10))
        
        lbl_desc = tk.Label(action_bar, text="★ Automated Cron Hook: Scan stay contracts and clear expired occupancy allocations instantly.", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_desc.pack(side="left")
        
        btn_audit = ttk.Button(action_bar, text="Execute Batch Stay Audit", style="Primary.TButton", command=self.run_stay_audit)
        btn_audit.pack(side="right")

        # Two-Section Workspace
        workspace = tk.Frame(self, bg=COLOR_BG_LIGHT, padx=25, pady=5)
        workspace.pack(fill="both", expand=True)
        
        # Left Workspace: Floor Map Grid
        left_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        card_grid = tk.Frame(left_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        card_grid.pack(fill="both", expand=True)
        
        lbl_grid_hdr = tk.Label(card_grid, text="Physical Room Allocations", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_grid_hdr.pack(anchor="w", pady=(0, 10))
        
        # Color Code Legend
        legend = tk.Frame(card_grid, bg=COLOR_CARD_BG)
        legend.pack(fill="x", pady=(0, 15))
        self.create_legend_item(legend, "Vacant Space", COLOR_STATUS_GREEN).pack(side="left", padx=(0, 15))
        self.create_legend_item(legend, "Partially Booked", COLOR_STATUS_AMBER).pack(side="left", padx=(0, 15))
        self.create_legend_item(legend, "Fully Booked", COLOR_STATUS_RED).pack(side="left")

        # Container for the dynamic grid elements
        self.grid_scroll = tk.Canvas(card_grid, bg=COLOR_CARD_BG, borderwidth=0, highlightthickness=0)
        self.grid_vsb = ttk.Scrollbar(card_grid, orient="vertical", command=self.grid_scroll.yview)
        
        self.grid_container = tk.Frame(self.grid_scroll, bg=COLOR_CARD_BG)
        self.grid_container.bind(
            "<Configure>", 
            lambda e: self.grid_scroll.configure(scrollregion=self.grid_scroll.bbox("all"))
        )
        
        grid_window = self.grid_scroll.create_window((0, 0), window=self.grid_container, anchor="nw")
        self.grid_scroll.configure(yscrollcommand=self.grid_vsb.set)
        
        # Keep width scaled
        self.grid_scroll.bind('<Configure>', lambda e: self.grid_scroll.itemconfig(grid_window, width=e.width))
        
        self.grid_vsb.pack(side="right", fill="y")
        self.grid_scroll.pack(fill="both", expand=True)

        # Right Workspace: Room Details & Extend stays Tool
        self.right_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT, width=350)
        self.right_panel.pack(side="right", fill="y", pady=0)
        self.right_panel.pack_propagate(False)
        
        self.card_details = tk.Frame(self.right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        self.card_details.pack(fill="both", expand=True)
        
        self.lbl_details_hdr = tk.Label(self.card_details, text="Inspection Details", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        self.lbl_details_hdr.pack(anchor="w", pady=(0, 15))
        
        # Detail fields
        self.detail_body = tk.Frame(self.card_details, bg=COLOR_CARD_BG)
        self.detail_body.pack(fill="both", expand=True)
        
        self.lbl_empty_state = tk.Label(self.detail_body, text="Select a room card in the physical map to inspect allocations, review residents, or extend contract stay limits.", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG, wraplength=290, justify="left")
        self.lbl_empty_state.pack(pady=40)

    def create_legend_item(self, parent, text, color):
        item = tk.Frame(parent, bg=COLOR_CARD_BG)
        box = tk.Frame(item, bg=color, width=15, height=15)
        box.pack(side="left", padx=(0, 5))
        lbl = tk.Label(item, text=text, font=("Segoe UI", 9), bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED)
        lbl.pack(side="left")
        return item

    def load_floor_map(self):
        """Loads rooms grouped by floor and builds interactive grid tiles."""
        for child in self.grid_container.winfo_children():
            child.destroy()
        self.room_buttons.clear()
        
        try:
            rooms = self.db.get_rooms()
            
            # Group rooms by floor
            floors = {}
            for r in rooms:
                fl = r.get("floor_assignment", "Unknown Floor")
                if fl not in floors:
                    floors[fl] = []
                floors[fl].append(r)
                
            # Render floor-by-floor rows
            for floor_name in sorted(floors.keys()):
                floor_frame = tk.Frame(self.grid_container, bg=COLOR_CARD_BG, pady=10)
                floor_frame.pack(fill="x", anchor="w")
                
                lbl_fl = tk.Label(floor_frame, text=floor_name.upper(), font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
                lbl_fl.pack(anchor="w", padx=5, pady=(0, 8))
                
                grid_tiles = tk.Frame(floor_frame, bg=COLOR_CARD_BG)
                grid_tiles.pack(fill="x", anchor="w")
                
                # Render grid tiles side-by-side
                for r in floors[floor_name]:
                    status = r["room_status"]
                    
                    # Select corresponding status color
                    if status == "Vacant":
                        tile_color = COLOR_STATUS_GREEN
                    elif status == "Partially Booked":
                        tile_color = COLOR_STATUS_AMBER
                    else:
                        tile_color = COLOR_STATUS_RED
                        
                    # Create custom room card
                    tile = tk.Frame(grid_tiles, bg=tile_color, width=100, height=85, cursor="hand2", highlightbackground=COLOR_BORDER, highlightthickness=1)
                    tile.pack(side="left", padx=8, pady=5)
                    tile.pack_propagate(False)
                    
                    # Internal visual details
                    lbl_num = tk.Label(tile, text=f"Room {r['room_number']}", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_WHITE, bg=tile_color)
                    lbl_num.pack(pady=(12, 2))
                    
                    occ_str = f"{r['current_occupancy']} / {r['total_capacity']} Beds"
                    lbl_occ = tk.Label(tile, text=occ_str, font=("Segoe UI", 9), fg=COLOR_TEXT_WHITE, bg=tile_color)
                    lbl_occ.pack()
                    
                    # Bind clicks (on frame and labels) to launch inspector
                    for widget in (tile, lbl_num, lbl_occ):
                        widget.bind("<Button-1>", lambda e, room=r: self.inspect_room(room))
                        
                    self.room_buttons[r["room_id"]] = tile
        except Exception as e:
            print(f"Error drawing floor map: {e}")

    def inspect_room(self, room):
        """Loads active resident allocations and displays them inside the detail panel."""
        self.selected_room = room
        
        # Reset detail canvas
        for child in self.detail_body.winfo_children():
            child.destroy()
            
        self.lbl_details_hdr.configure(text=f"Inspection: Room {room['room_number']}")
        
        # Show specifications
        spec_box = tk.Frame(self.detail_body, bg=COLOR_BG_LIGHT, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=12, pady=10)
        spec_box.pack(fill="x", pady=(0, 15))
        
        tk.Label(spec_box, text=f"Layout Class: {room['type_name']}", font=FONT_LABEL, bg=COLOR_BG_LIGHT).pack(anchor="w")
        tk.Label(spec_box, text=f"Floor Level: {room['floor_assignment']}", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED).pack(anchor="w", pady=2)
        
        price_val = f"${float(room.get('semester_base_price', 0)):,.2f}"
        tk.Label(spec_box, text=f"Semester Rate: {price_val}", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED).pack(anchor="w")

        # Load residents inside this specific room
        tk.Label(self.detail_body, text="ACTIVE BED OCCUPANTS:", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        
        try:
            residents = self.db.fetch_all("SELECT * FROM Residents WHERE room_id = %s", (room["room_id"],))
            if not residents:
                tk.Label(self.detail_body, text="No student residents currently allocated to this room unit.", font=FONT_BODY, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED, wraplength=280, justify="left").pack(pady=15)
            else:
                for idx, res in enumerate(residents):
                    res_card = tk.Frame(self.detail_body, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=10, pady=10)
                    res_card.pack(fill="x", pady=5)
                    
                    # Highlight expired ones
                    is_expired = datetime.strptime(res["check_out_date"], "%Y-%m-%d").date() <= datetime.now().date()
                    date_fg = COLOR_STATUS_RED if is_expired else COLOR_TEXT_MUTED
                    
                    tk.Label(res_card, text=res["full_name"], font=("Segoe UI", 10, "bold"), bg=COLOR_CARD_BG).pack(anchor="w")
                    tk.Label(res_card, text=f"ID: {res['student_id']} | Major: {res['academic_major']}", font=FONT_CAPTION, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED).pack(anchor="w")
                    
                    lbl_dates = tk.Label(res_card, text=f"Checked: {res['check_in_date']} to {res['check_out_date']}", font=FONT_CAPTION, bg=COLOR_CARD_BG, fg=date_fg)
                    lbl_dates.pack(anchor="w", pady=(3, 5))
                    
                    # Button to prolong stay
                    btn_prolong = ttk.Button(
                        res_card, 
                        text="Prolong Booking Time", 
                        style="Secondary.TButton",
                        command=lambda r_id=res["resident_id"], name=res["full_name"], check_out=res["check_out_date"]: self.show_prolong_dialog(r_id, name, check_out)
                    )
                    btn_prolong.pack(fill="x")
        except Exception as e:
            print(f"Error loading occupants detail: {e}")

    def show_prolong_dialog(self, resident_id, name, current_checkout):
        """Displays stay prolong extensions date adjustment window."""
        dialog = tk.Toplevel(self)
        dialog.title("Extend Stay Duration")
        dialog.geometry("380x240")
        dialog.resizable(False, False)
        dialog.configure(bg=COLOR_BG_LIGHT)
        dialog.transient(self)
        dialog.grab_set()

        # Header Frame
        hdr = tk.Frame(dialog, bg=COLOR_HEADER_BG, height=60)
        hdr.pack(fill="x", side="top")
        tk.Label(hdr, text=f"Extend Stay: {name}", fg=COLOR_TEXT_WHITE, bg=COLOR_HEADER_BG, font=FONT_SUBTITLE).pack(pady=15, padx=20, anchor="w")

        # Form content
        body = tk.Frame(dialog, bg=COLOR_BG_LIGHT, padx=25, pady=15)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=f"Current stay End-Date: {current_checkout}", font=FONT_BODY, bg=COLOR_BG_LIGHT).pack(anchor="w", pady=(0, 10))
        tk.Label(body, text="Enter New Check-Out Date (YYYY-MM-DD):", font=FONT_LABEL, bg=COLOR_BG_LIGHT).pack(anchor="w")

        # Prepopulate default date to +6 months from current
        curr_dt = datetime.strptime(current_checkout, "%Y-%m-%d")
        default_future = (curr_dt + timedelta(days=150)).strftime("%Y-%m-%d")
        
        ent_date = ttk.Entry(body)
        ent_date.pack(fill="x", pady=(5, 15))
        ent_date.insert(0, default_future)

        def save_extension():
            new_date = ent_date.get().strip()
            try:
                # Format validations
                new_dt = datetime.strptime(new_date, "%Y-%m-%d").date()
                if new_dt <= curr_dt.date():
                    messagebox.showerror("Validation Error", "The new stay end-date must fall after the current checked-out date limits.", parent=dialog)
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Invalid date format. Please format as YYYY-MM-DD.", parent=dialog)
                return

            try:
                # Update stay End-Date
                self.db.update_booking_time(resident_id, new_date)
                messagebox.showinfo("Success", f"Stay extended successfully to {new_date}.", parent=dialog)
                
                dialog.grab_release()
                dialog.destroy()
                
                # Refresh map and detail panes
                self.load_floor_map()
                if self.selected_room:
                    # Fetch fresh room parameters
                    room_id = self.selected_room["room_id"]
                    refreshed_rooms = self.db.get_rooms()
                    for r in refreshed_rooms:
                        if r["room_id"] == room_id:
                            self.inspect_room(r)
                            break
            except Exception as e:
                messagebox.showerror("Database Write Error", f"Failed to prolong stay limit:\n{e}", parent=dialog)

        btn_save = ttk.Button(body, text="Confirm Extension & Update", style="Primary.TButton", command=save_extension)
        btn_save.pack(fill="x", ipady=4)

    def run_stay_audit(self):
        """Triggers reactive backend automatic stay check-outs and reports output details."""
        try:
            checked_out, rooms_affected = self.db.run_automated_checkout()
            if checked_out > 0:
                msg = f"Auditing Complete!\n\n★ Reactive Hook Fired:\n- {checked_out} students automatically checked out.\n- {rooms_affected} physical room statuses updated back to vacant/partially booked limits."
                messagebox.showinfo("Automation Audit Complete", msg)
                self.load_floor_map()
                if self.selected_room:
                    self.inspect_room(self.selected_room)
            else:
                messagebox.showinfo("Automation Audit Complete", "Auditing Complete!\n\nNo student resident booking allocations have reached expired check-out date targets today.")
        except Exception as e:
            messagebox.showerror("Automation Failure", f"Failed to execute stay audit:\n{e}")
