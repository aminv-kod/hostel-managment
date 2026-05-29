import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from gui.theme import (
    COLOR_BG_LIGHT, COLOR_CARD_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_HEADER_BG, COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER, COLOR_STATUS_RED, FONT_TITLE, FONT_SUBTITLE,
    FONT_LABEL, FONT_BODY, FONT_CAPTION
)

class ResidentsView(tk.Frame):
    """View managing resident records, ledger audits, onboarding fields, and dynamic field locks."""
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg=COLOR_BG_LIGHT)
        self.db = db_manager
        self.rooms_cache = {}
        
        self.pack_propagate(False)
        self.create_layout()
        self.refresh_rooms_dropdown()
        self.search_residents()

    def create_layout(self):
        # Header block
        header = tk.Frame(self, bg=COLOR_BG_LIGHT, pady=12, padx=25)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="Resident Onboarding & Directory", font=FONT_TITLE, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_PRIMARY)
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = tk.Label(header, text="Manage student profiles, hostel tuition contracts, and allocate bed-spaces", font=FONT_BODY, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_MUTED)
        lbl_subtitle.pack(anchor="w", pady=2)

        # Dual-column Workspace
        workspace = tk.Frame(self, bg=COLOR_BG_LIGHT, padx=25, pady=5)
        workspace.pack(fill="both", expand=True)
        
        # Left Panel - Register Resident Form (Scrollable for smaller heights)
        left_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT, width=340)
        left_panel.pack(side="left", fill="y", padx=(0, 15), pady=5)
        left_panel.pack_propagate(False)
        
        # Canvas for scrollable form
        form_canvas = tk.Canvas(left_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        form_vsb = ttk.Scrollbar(left_panel, orient="vertical", command=form_canvas.yview)
        
        self.card_form = tk.Frame(form_canvas, bg=COLOR_CARD_BG, padx=15, pady=15)
        self.card_form.bind(
            "<Configure>", 
            lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all"))
        )
        
        form_canvas_window = form_canvas.create_window((0, 0), window=self.card_form, anchor="nw")
        form_canvas.configure(yscrollcommand=form_vsb.set)
        
        # Bind resize to make sure form stays full width of canvas
        form_canvas.bind('<Configure>', lambda e: form_canvas.itemconfig(form_canvas_window, width=e.width))
        
        form_vsb.pack(side="right", fill="y")
        form_canvas.pack(side="left", fill="both", expand=True)
        
        lbl_form_hdr = tk.Label(self.card_form, text="Onboard Student Resident", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_form_hdr.pack(anchor="w", pady=(0, 10))
        
        # Form Fields
        tk.Label(self.card_form, text="Student ID Number:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_student_id = ttk.Entry(self.card_form)
        self.ent_student_id.pack(fill="x", pady=(0, 8))
        
        tk.Label(self.card_form, text="Resident Full Name:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_name = ttk.Entry(self.card_form)
        self.ent_name.pack(fill="x", pady=(0, 8))
        
        tk.Label(self.card_form, text="Academic Major / Program:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_major = ttk.Entry(self.card_form)
        self.ent_major.pack(fill="x", pady=(0, 8))
        
        tk.Label(self.card_form, text="Assign Room Unit:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.cmb_room = ttk.Combobox(self.card_form, state="readonly")
        self.cmb_room.pack(fill="x", pady=(0, 8))
        self.cmb_room.bind("<<ComboboxSelected>>", self.on_room_selected)
        
        # Dates
        tk.Label(self.card_form, text="Check-In Date (YYYY-MM-DD):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_checkin = ttk.Entry(self.card_form)
        self.ent_checkin.pack(fill="x", pady=(0, 8))
        self.ent_checkin.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(self.card_form, text="Check-Out Date (YYYY-MM-DD):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_checkout = ttk.Entry(self.card_form)
        self.ent_checkout.pack(fill="x", pady=(0, 8))
        self.ent_checkout.insert(0, (datetime.now() + timedelta(days=150)).strftime("%Y-%m-%d"))
        
        # Ledger details
        tk.Label(self.card_form, text="Security Deposit Paid ($):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_deposit = ttk.Entry(self.card_form)
        self.ent_deposit.pack(fill="x", pady=(0, 8))
        self.ent_deposit.insert(0, "200.00")
        
        tk.Label(self.card_form, text="Hostel Tuition Fee ($):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_hostel_fee = ttk.Entry(self.card_form)
        self.ent_hostel_fee.pack(fill="x", pady=(0, 8))
        self.ent_hostel_fee.insert(0, "0.00")
        
        tk.Label(self.card_form, text="Academic Tuition Debt ($):", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_debt = ttk.Entry(self.card_form)
        self.ent_debt.pack(fill="x", pady=(0, 8))
        self.ent_debt.insert(0, "0.00")
        
        # Allocation status with probation reason hook
        tk.Label(self.card_form, text="Allocation Ledger Status:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.cmb_status = ttk.Combobox(self.card_form, values=['Fully Registered', 'Probational Allocation', 'Outstanding Arrears'], state="readonly")
        self.cmb_status.pack(fill="x", pady=(0, 8))
        self.cmb_status.set("Fully Registered")
        self.cmb_status.bind("<<ComboboxSelected>>", self.toggle_probation_field)
        
        tk.Label(self.card_form, text="Probation Approval Reason:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(anchor="w", pady=2)
        self.ent_probation = tk.Text(self.card_form, height=3, font=FONT_BODY, wrap="word", highlightbackground=COLOR_BORDER, highlightthickness=1, borderwidth=0)
        self.ent_probation.pack(fill="x", pady=(0, 12))
        
        # Initial lock on probation field
        self.toggle_probation_field()

        btn_save = ttk.Button(self.card_form, text="Onboard Student Resident", style="Primary.TButton", command=self.save_resident)
        btn_save.pack(fill="x", ipady=4)

        # Right Panel - Search Directory & Treeview Grid
        right_panel = tk.Frame(workspace, bg=COLOR_BG_LIGHT)
        right_panel.pack(side="right", fill="both", expand=True, pady=5)
        
        # Search block
        search_card = tk.Frame(right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=15, pady=10)
        search_card.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_card, text="Search Directory:", font=FONT_LABEL, bg=COLOR_CARD_BG).pack(side="left", padx=(0, 10))
        self.ent_search = ttk.Entry(search_card)
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", self.on_search_key)
        
        btn_clear = ttk.Button(search_card, text="Reset", style="Secondary.TButton", command=self.clear_search)
        btn_clear.pack(side="right")

        # Table Grid Card
        card_table = tk.Frame(right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        card_table.pack(fill="both", expand=True)
        
        lbl_table_hdr = tk.Label(card_table, text="Student Directory & Ledger Status", font=FONT_SUBTITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        lbl_table_hdr.pack(anchor="w", pady=(0, 15))
        
        cols = ("student_id", "name", "room", "major", "dates", "deposit", "debt", "status")
        self.tree = ttk.Treeview(card_table, columns=cols, show="headings")
        
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("room", text="Room")
        self.tree.heading("major", text="Academic Major")
        self.tree.heading("dates", text="Allocation Window")
        self.tree.heading("deposit", text="Deposit")
        self.tree.heading("debt", text="Academic Debt")
        self.tree.heading("status", text="Allocation Ledger")
        
        self.tree.column("student_id", width=90, minwidth=80, anchor="center")
        self.tree.column("name", width=120, minwidth=100, anchor="w")
        self.tree.column("room", width=60, minwidth=50, anchor="center")
        self.tree.column("major", width=120, minwidth=100, anchor="w")
        self.tree.column("dates", width=150, minwidth=130, anchor="center")
        self.tree.column("deposit", width=80, minwidth=70, anchor="e")
        self.tree.column("debt", width=95, minwidth=80, anchor="e")
        self.tree.column("status", width=120, minwidth=100, anchor="center")
        
        vsb = ttk.Scrollbar(card_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(card_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        hsb.pack(fill="x")
        
        # Grid Operations Pane (Buttons below grid)
        operations = tk.Frame(right_panel, bg=COLOR_BG_LIGHT)
        operations.pack(fill="x", pady=(10, 0))
        
        btn_checkout = ttk.Button(operations, text="Check-Out / Remove Selected Resident", style="Secondary.TButton", command=self.checkout_resident)
        btn_checkout.pack(side="right")

    def refresh_rooms_dropdown(self):
        """Pulls list of rooms and formats dropdown display options."""
        try:
            records = self.db.get_rooms()
            options = []
            self.rooms_cache.clear()
            for r in records:
                # Include capacity indicator so operator knows vacancy
                label = f"Room {r['room_number']} ({r['type_name']} - {r['current_occupancy']}/{r['total_capacity']} Beds)"
                
                # Cache rooms that are not fully booked
                if r["current_occupancy"] < r["total_capacity"]:
                    options.append(label)
                    self.rooms_cache[label] = r
                else:
                    # Keep record cached but add marker
                    label_full = f"Room {r['room_number']} (FULL)"
                    options.append(label_full)
                    self.rooms_cache[label_full] = r
                    
            self.cmb_room.configure(values=options)
            if options:
                self.cmb_room.set(options[0])
                self.on_room_selected()
        except Exception as e:
            print(f"Error loading rooms dropdown: {e}")

    def on_room_selected(self, event=None):
        """Autoloads room baseline tuition pricing to simplify input entries."""
        selected = self.cmb_room.get()
        room = self.rooms_cache.get(selected)
        if room:
            base_price = float(room.get("semester_base_price", 0))
            self.ent_hostel_fee.delete(0, tk.END)
            self.ent_hostel_fee.insert(0, f"{base_price:.2f}")

    def toggle_probation_field(self, event=None):
        """Enables/Disables probation reason fields depending on status configurations."""
        status = self.cmb_status.get()
        if status == 'Probational Allocation':
            self.ent_probation.configure(state="normal", bg="#ffffff")
        else:
            self.ent_probation.delete("1.0", tk.END)
            self.ent_probation.configure(state="disabled", bg=COLOR_BG_LIGHT)

    def on_search_key(self, event):
        self.search_residents()

    def clear_search(self):
        self.ent_search.delete(0, tk.END)
        self.search_residents()

    def search_residents(self):
        """Queries residents list using active filters."""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        term = self.ent_search.get().strip()
        try:
            records = self.db.search_residents(term)
            for r in records:
                dates_str = f"{r['check_in_date']} to {r['check_out_date']}"
                deposit_str = f"${float(r['deposit_paid']):,.2f}"
                debt_str = f"${float(r['academic_tuition_debt']):,.2f}"
                
                self.tree.insert("", "end", values=(
                    r["student_id"],
                    r["full_name"],
                    r["room_number"],
                    r["academic_major"],
                    dates_str,
                    deposit_str,
                    debt_str,
                    r["allocation_status"]
                ), tags=(r["resident_id"],))
        except Exception as e:
            print(f"Error searching directory: {e}")

    def save_resident(self):
        """Validates all inputs and registers the new student resident stay."""
        student_id = self.ent_student_id.get().strip()
        name = self.ent_name.get().strip()
        major = self.ent_major.get().strip()
        room_sel = self.cmb_room.get()
        checkin = self.ent_checkin.get().strip()
        checkout = self.ent_checkout.get().strip()
        deposit_raw = self.ent_deposit.get().strip()
        fee_raw = self.ent_hostel_fee.get().strip()
        debt_raw = self.ent_debt.get().strip()
        status = self.cmb_status.get()
        probation = self.ent_probation.get("1.0", tk.END).strip()

        # Validations
        if not student_id or not name or not major or not checkin or not checkout:
            messagebox.showerror("Validation Error", "All basic personal details and dates must be completed.")
            return

        room = self.rooms_cache.get(room_sel)
        if not room:
            messagebox.showerror("Validation Error", "Please select a valid room unit allocation.")
            return

        if room["current_occupancy"] >= room["total_capacity"]:
            messagebox.showerror("Validation Error", "Target room is fully booked. Select another unit.")
            return

        try:
            deposit = float(deposit_raw)
            fee = float(fee_raw)
            debt = float(debt_raw)
            if deposit < 0 or fee < 0 or debt < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Financial entries (Deposit, Fees, Debt) must be non-negative values.")
            return

        # Date string formatting check
        try:
            datetime.strptime(checkin, "%Y-%m-%d")
            datetime.strptime(checkout, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Dates must match the format YYYY-MM-DD.")
            return

        if status == 'Probational Allocation' and not probation:
            messagebox.showerror("Validation Error", "Probation Allocation requires a clear Approval Reason.")
            return

        probation_val = probation if status == 'Probational Allocation' else None

        try:
            self.db.add_resident(
                room_id=room["room_id"],
                student_id=student_id,
                full_name=name,
                academic_major=major,
                check_in_date=checkin,
                check_out_date=checkout,
                deposit_paid=deposit,
                hostel_tuition_fee=fee,
                academic_tuition_debt=debt,
                allocation_status=status,
                probation_reason=probation_val
            )
            messagebox.showinfo("Success", f"Resident '{name}' has been successfully registered to room {room['room_number']}.")
            
            # Reset inputs
            self.ent_student_id.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)
            self.ent_major.delete(0, tk.END)
            self.ent_probation.delete("1.0", tk.END)
            
            # Refresh lists
            self.refresh_rooms_dropdown()
            self.search_residents()
        except Exception as e:
            messagebox.showerror("Onboarding Failed", f"Database failed to process registration. Check that Student ID is unique!\n\n{e}")

    def checkout_resident(self):
        """Selects target row and triggers resident stay delete operations."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a resident from the directory directory first.")
            return
            
        tags = self.tree.item(selected[0], "tags")
        if not tags:
            return
            
        resident_id = tags[0]
        student_id = self.tree.item(selected[0], "values")[0]
        student_name = self.tree.item(selected[0], "values")[1]

        confirm = messagebox.askyesno(
            "Confirm Check-Out", 
            f"Are you sure you want to trigger check-out/removal for student resident {student_name} ({student_id})?\n\nThis will remove them from directory, free up their bed, and adjust occupancy."
        )
        if confirm:
            try:
                self.db.delete_resident(resident_id)
                messagebox.showinfo("Checked Out", f"Resident stays cleared for {student_name}.")
                self.refresh_rooms_dropdown()
                self.search_residents()
            except Exception as e:
                messagebox.showerror("Check-Out Failed", f"Database error during deletion:\n{e}")
