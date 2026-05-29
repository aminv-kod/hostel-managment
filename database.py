import json
import os
import sqlite3
from datetime import datetime
from decimal import Decimal

# Try to import pymysql for MySQL connectivity
try:
    import pymysql
    import pymysql.cursors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

CONFIG_FILE = "config.json"

class DatabaseConnectionError(Exception):
    """Raised when unable to connect to the database."""
    pass

class DatabaseManager:
    def __init__(self):
        self.db_type = "sqlite"  # Default fallback
        self.config = {
            "db_type": "sqlite",
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "hostel_management",
            "sqlite_path": "hostel_sandbox.db"
        }
        self.load_config()
        self.conn = None

    def load_config(self):
        """Loads configuration from config.json if it exists."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                    self.db_type = self.config.get("db_type", "sqlite")
            except Exception:
                pass

    def save_config(self, new_config):
        """Saves new configuration to config.json."""
        self.config.update(new_config)
        self.db_type = self.config.get("db_type", "sqlite")
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def connect(self):
        """Attempts to connect to the database. Raises DatabaseConnectionError on failure."""
        try:
            if self.db_type == "mysql":
                if not MYSQL_AVAILABLE:
                    raise DatabaseConnectionError("pymysql library is not installed. Please install it to use MySQL.")
                self.conn = pymysql.connect(
                    host=self.config["host"],
                    port=int(self.config["port"]),
                    user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["database"],
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
            else:
                # SQLite mode
                self.conn = sqlite3.connect(self.config["sqlite_path"])
                self.conn.row_factory = sqlite3.Row
                # Enable foreign key support in SQLite
                self.conn.execute("PRAGMA foreign_keys = ON;")
        except Exception as e:
            raise DatabaseConnectionError(str(e))

    def execute_query(self, query, params=None):
        """Executes a non-selecting query (INSERT, UPDATE, DELETE)."""
        if not self.conn:
            self.connect()
        
        # SQLite uses '?' placeholder instead of '%s'
        if self.db_type == "sqlite":
            query = query.replace("%s", "?")

        try:
            if self.db_type == "mysql":
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    return cursor.lastrowid
            else:
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(query, params or ())
                    return cursor.lastrowid
        except Exception as e:
            print(f"Query Execution Error: {e}\nQuery: {query}")
            raise e

    def fetch_all(self, query, params=None):
        """Fetches all results for a SELECT query."""
        if not self.conn:
            self.connect()

        if self.db_type == "sqlite":
            query = query.replace("%s", "?")

        try:
            if self.db_type == "mysql":
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    return cursor.fetchall()
            else:
                cursor = self.conn.cursor()
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Fetch All Error: {e}\nQuery: {query}")
            raise e

    def fetch_one(self, query, params=None):
        """Fetches a single row result for a SELECT query."""
        if not self.conn:
            self.connect()

        if self.db_type == "sqlite":
            query = query.replace("%s", "?")

        try:
            if self.db_type == "mysql":
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    return cursor.fetchone()
            else:
                cursor = self.conn.cursor()
                cursor.execute(query, params or ())
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Fetch One Error: {e}\nQuery: {query}")
            raise e

    def initialize_schema(self):
        """Creates tables using schema DDL. Emulates schema for SQLite if running in sandbox."""
        if self.db_type == "mysql":
            # For MySQL, we run the raw schema commands
            schema_sql = """
            CREATE TABLE IF NOT EXISTS Room_Types (
                room_type_id INT AUTO_INCREMENT PRIMARY KEY,
                type_name VARCHAR(255) NOT NULL,
                semester_base_price DECIMAL(10,2) NOT NULL,
                inventory_assets JSON NOT NULL
            ) ENGINE=InnoDB;
            """
            self.execute_query(schema_sql)
            
            schema_sql2 = """
            CREATE TABLE IF NOT EXISTS Rooms (
                room_id INT AUTO_INCREMENT PRIMARY KEY,
                room_type_id INT NOT NULL,
                room_number VARCHAR(50) NOT NULL UNIQUE,
                floor_assignment VARCHAR(50) NOT NULL,
                total_capacity INT NOT NULL,
                current_occupancy INT NOT NULL DEFAULT 0,
                room_status VARCHAR(50) NOT NULL DEFAULT 'Vacant',
                FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB;
            """
            self.execute_query(schema_sql2)

            schema_sql3 = """
            CREATE TABLE IF NOT EXISTS Residents (
                resident_id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                student_id VARCHAR(100) NOT NULL UNIQUE,
                full_name VARCHAR(255) NOT NULL,
                academic_major VARCHAR(255) NOT NULL,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                deposit_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                hostel_tuition_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                academic_tuition_debt DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                allocation_status VARCHAR(100) NOT NULL DEFAULT 'Fully Registered',
                probation_reason TEXT NULL,
                FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB;
            """
            self.execute_query(schema_sql3)
        else:
            # SQLite emulation schema
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS Room_Types (
                room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL,
                semester_base_price REAL NOT NULL,
                inventory_assets TEXT NOT NULL
            );
            """)
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS Rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type_id INTEGER NOT NULL,
                room_number TEXT NOT NULL UNIQUE,
                floor_assignment TEXT NOT NULL,
                total_capacity INTEGER NOT NULL,
                current_occupancy INTEGER NOT NULL DEFAULT 0,
                room_status TEXT NOT NULL DEFAULT 'Vacant',
                FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """)
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS Residents (
                resident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                student_id TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                academic_major TEXT NOT NULL,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                deposit_paid REAL NOT NULL DEFAULT 0.00,
                hostel_tuition_fee REAL NOT NULL DEFAULT 0.00,
                academic_tuition_debt REAL NOT NULL DEFAULT 0.00,
                allocation_status TEXT NOT NULL DEFAULT 'Fully Registered',
                probation_reason TEXT NULL,
                FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """)

    def insert_seed_data_if_empty(self):
        """Seeds the database with high-quality sample data if no Room_Types exist."""
        types = self.fetch_all("SELECT COUNT(*) as count FROM Room_Types")
        if types and types[0]["count"] > 0:
            return

        # Seed Room Types
        rt1 = self.add_room_type("Single Premium Suite", 2400.00, ["Air Conditioner", "Mini Fridge", "Study Desk", "Pillows", "Personal Safe"])
        rt2 = self.add_room_type("Double Deluxe Room", 1600.00, ["Air Conditioner", "Study Desk", "Pillows", "Fan"])
        rt3 = self.add_room_type("Standard Quad Dorm", 950.00, ["Fan", "Study Desk", "Pillows", "Shared Lockers"])

        # Seed Rooms
        r1_id = self.add_room(rt1, "101", "Floor 1", 1)
        r2_id = self.add_room(rt2, "201", "Floor 2", 2)
        r3_id = self.add_room(rt2, "202", "Floor 2", 2)
        r4_id = self.add_room(rt3, "301", "Floor 3", 4)
        r5_id = self.add_room(rt3, "302", "Floor 3", 4)

        # Seed Residents (STU-001 in 101, STU-002 and STU-003 in 201)
        self.add_resident(
            room_id=r1_id,
            student_id="STU202601",
            full_name="Sarah Jenkins",
            academic_major="Computer Science",
            check_in_date="2026-01-15",
            check_out_date="2026-06-15",
            deposit_paid=500.00,
            hostel_tuition_fee=2400.00,
            academic_tuition_debt=0.00,
            allocation_status="Fully Registered"
        )

        self.add_resident(
            room_id=r2_id,
            student_id="STU202602",
            full_name="Marcus Vance",
            academic_major="Mechanical Engineering",
            check_in_date="2026-01-18",
            check_out_date="2026-06-15",
            deposit_paid=300.00,
            hostel_tuition_fee=1600.00,
            academic_tuition_debt=1250.00,
            allocation_status="Outstanding Arrears"
        )

        self.add_resident(
            room_id=r2_id,
            student_id="STU202603",
            full_name="Emily Zhao",
            academic_major="Biomedical Science",
            check_in_date="2026-01-20",
            check_out_date="2026-05-15", # Checked-out soon or expired
            deposit_paid=300.00,
            hostel_tuition_fee=1600.00,
            academic_tuition_debt=0.00,
            allocation_status="Probational Allocation",
            probation_reason="Temporary academic exchange placement pending official records."
        )

    # --- CRUD operations for Room_Types ---
    def add_room_type(self, name, price, assets):
        """Adds a new Room Type classification with inventory assets JSON."""
        assets_json = json.dumps(assets)
        query = "INSERT INTO Room_Types (type_name, semester_base_price, inventory_assets) VALUES (%s, %s, %s)"
        return self.execute_query(query, (name, float(price), assets_json))

    def get_room_types(self):
        """Returns all registered Room Types."""
        rows = self.fetch_all("SELECT * FROM Room_Types ORDER BY room_type_id DESC")
        # Parse JSON
        for row in rows:
            if isinstance(row.get("inventory_assets"), str):
                try:
                    row["inventory_assets"] = json.loads(row["inventory_assets"])
                except Exception:
                    row["inventory_assets"] = []
        return rows

    # --- CRUD operations for Rooms ---
    def add_room(self, type_id, number, floor, capacity):
        """Adds a new physical room unit."""
        query = "INSERT INTO Rooms (room_type_id, room_number, floor_assignment, total_capacity, current_occupancy, room_status) VALUES (%s, %s, %s, %s, 0, 'Vacant')"
        return self.execute_query(query, (type_id, number, floor, capacity))

    def get_rooms(self):
        """Returns physical room metrics joined with class inventory."""
        query = """
            SELECT r.*, t.type_name, t.semester_base_price, t.inventory_assets
            FROM Rooms r
            JOIN Room_Types t ON r.room_type_id = t.room_type_id
            ORDER BY r.room_number ASC
        """
        rows = self.fetch_all(query)
        for row in rows:
            if isinstance(row.get("inventory_assets"), str):
                try:
                    row["inventory_assets"] = json.loads(row["inventory_assets"])
                except Exception:
                    row["inventory_assets"] = []
        return rows

    def get_rooms_grid(self):
        """Returns list of rooms simplified for Floor Engine view mapping."""
        return self.get_rooms()

    # --- CRUD operations for Residents ---
    def add_resident(self, room_id, student_id, full_name, academic_major, check_in_date, check_out_date,
                     deposit_paid, hostel_tuition_fee, academic_tuition_debt, allocation_status, probation_reason=None):
        """Registers a new student allocation and updates target room metrics."""
        # Check current capacity
        room = self.fetch_one("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        if not room:
            raise ValueError("Target room does not exist.")
        if room["current_occupancy"] >= room["total_capacity"]:
            raise ValueError("Target room is at maximum occupancy.")

        # Create resident record
        query = """
            INSERT INTO Residents (
                room_id, student_id, full_name, academic_major, check_in_date, check_out_date,
                deposit_paid, hostel_tuition_fee, academic_tuition_debt, allocation_status, probation_reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        resident_id = self.execute_query(query, (
            room_id, student_id, full_name, academic_major, check_in_date, check_out_date,
            float(deposit_paid), float(hostel_tuition_fee), float(academic_tuition_debt), allocation_status, probation_reason
        ))

        # Recalculate room occupancy and status
        self.recalculate_room_state(room_id)
        return resident_id

    def search_residents(self, search_term=""):
        """Filters residents catalog using elastic string matches on ID, major, name, or room."""
        if search_term:
            query = """
                SELECT res.*, r.room_number, t.type_name
                FROM Residents res
                JOIN Rooms r ON res.room_id = r.room_id
                JOIN Room_Types t ON r.room_type_id = t.room_type_id
                WHERE res.student_id LIKE %s OR res.full_name LIKE %s OR r.room_number LIKE %s OR res.academic_major LIKE %s
                ORDER BY res.resident_id DESC
            """
            wildcard = f"%{search_term}%"
            return self.fetch_all(query, (wildcard, wildcard, wildcard, wildcard))
        else:
            query = """
                SELECT res.*, r.room_number, t.type_name
                FROM Residents res
                JOIN Rooms r ON res.room_id = r.room_id
                JOIN Room_Types t ON r.room_type_id = t.room_type_id
                ORDER BY res.resident_id DESC
            """
            return self.fetch_all(query)

    def delete_resident(self, resident_id):
        """Removes/Checks-out a resident and triggers room occupancy adjustment."""
        resident = self.fetch_one("SELECT room_id FROM Residents WHERE resident_id = %s", (resident_id,))
        if not resident:
            return False
        
        room_id = resident["room_id"]
        self.execute_query("DELETE FROM Residents WHERE resident_id = %s", (resident_id,))
        self.recalculate_room_state(room_id)
        return True

    def update_booking_time(self, resident_id, new_checkout_date):
        """Updates check-out date for the resident stay extension."""
        self.execute_query("UPDATE Residents SET check_out_date = %s WHERE resident_id = %s", (new_checkout_date, resident_id))

    def recalculate_room_state(self, room_id):
        """Recalculates occupancy and status string for a target room."""
        # Query count of residents in room
        res = self.fetch_one("SELECT COUNT(*) as cnt FROM Residents WHERE room_id = %s", (room_id,))
        occupancy = res["cnt"] if res else 0

        # Query room metadata
        room = self.fetch_one("SELECT total_capacity FROM Rooms WHERE room_id = %s", (room_id,))
        if not room:
            return

        capacity = room["total_capacity"]

        # Determine status flag
        if occupancy == 0:
            status = "Vacant"
        elif occupancy >= capacity:
            status = "Fully Booked"
        else:
            status = "Partially Booked"

        # Update Rooms record
        self.execute_query(
            "UPDATE Rooms SET current_occupancy = %s, room_status = %s WHERE room_id = %s",
            (occupancy, status, room_id)
        )

    # --- High-level KPI aggregates for dashboard ---
    def get_kpi_metrics(self):
        """Returns system metrics: active rooms, occupied beds, open beds, registered residents."""
        res_rooms = self.fetch_one("SELECT COUNT(*) as total FROM Rooms")
        total_rooms = res_rooms["total"] if res_rooms else 0

        res_beds = self.fetch_one("SELECT SUM(total_capacity) as cap, SUM(current_occupancy) as occ FROM Rooms")
        total_beds = res_beds["cap"] if res_beds and res_beds["cap"] is not None else 0
        occupied_beds = res_beds["occ"] if res_beds and res_beds["occ"] is not None else 0
        open_beds = max(0, total_beds - occupied_beds)

        res_residents = self.fetch_one("SELECT COUNT(*) as total FROM Residents")
        active_residents = res_residents["total"] if res_residents else 0

        return {
            "total_rooms": total_rooms,
            "occupied_beds": occupied_beds,
            "open_beds": open_beds,
            "active_residents": active_residents
        }

    def get_financial_summary(self):
        """Returns sum of deposits, hostel fees collected, and active academic debt."""
        query = """
            SELECT 
                SUM(deposit_paid) as deposits, 
                SUM(hostel_tuition_fee) as fees, 
                SUM(academic_tuition_debt) as debt 
            FROM Residents
        """
        row = self.fetch_one(query)
        
        def to_float(val):
            if val is None:
                return 0.0
            if isinstance(val, (Decimal, float, int)):
                return float(val)
            return 0.0

        return {
            "deposits": to_float(row.get("deposits")),
            "fees": to_float(row.get("fees")),
            "debt": to_float(row.get("debt"))
        }

    def get_inventory_summary(self):
        """Aggregates all JSON physical assets mapped to actively operating rooms."""
        rooms = self.get_rooms()
        counts = {}
        for r in rooms:
            assets = r.get("inventory_assets", [])
            # Only count assets for rooms that are active/running (i.e. occupied or vacant, basically in service)
            # We scale the asset count by the room's current capacity or 1 (representing a single layout copy per room)
            for asset in assets:
                counts[asset] = counts.get(asset, 0) + 1
        return counts

    def run_automated_checkout(self):
        """Finds all residents whose stay has lapsed.

        Removes allocations, updates room statuses, and returns count of checked out residents.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        # Select residents whose checkout date matches or precedes today
        expired = self.fetch_all("SELECT resident_id, room_id, full_name FROM Residents WHERE check_out_date <= %s", (today,))
        
        checked_out_count = 0
        affected_rooms = set()
        
        for record in expired:
            self.execute_query("DELETE FROM Residents WHERE resident_id = %s", (record["resident_id"],))
            affected_rooms.add(record["room_id"])
            checked_out_count += 1
            
        for room_id in affected_rooms:
            self.recalculate_room_state(room_id)
            
        return checked_out_count, len(affected_rooms)
