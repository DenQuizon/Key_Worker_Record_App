import os
import sys
import sqlite3
import hashlib

# Resolve path to DB next to the EXE when frozen, else next to this file
def _app_dir():
    return os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_app_dir(), 'alyson_house.db')


def hash_password(password):
    """Hashes a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_db():
    """Creates the database file and tables if they don't exist, and migrates older schemas safely."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Ensure 'users' table exists first
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'staff',
            first_login INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # Migrate: add missing columns in existing databases
    cur.execute("PRAGMA table_info(users)")
    user_cols = [row[1] for row in cur.fetchall()]
    if 'role' not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'staff'")
    if 'first_login' not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN first_login INTEGER NOT NULL DEFAULT 1")

    # Create default supervisor if missing
    cur.execute("SELECT 1 FROM users WHERE username = 'supervisor' LIMIT 1")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (username, password_hash, role, first_login) VALUES (?, ?, ?, ?)",
            ('supervisor', hash_password('password'), 'supervisor', 0)
        )
        print("Default supervisor account created with username 'supervisor' and password 'password'")

    # --- Service Users Table ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS service_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            date_of_birth TEXT
        )
    ''')

    # --- Main Form Table ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY,
            service_user_id INTEGER NOT NULL,
            form_month_year TEXT NOT NULL,
            key_worker_name TEXT, session_datetime TEXT, weight TEXT, bp TEXT,
            weight_bp_comments TEXT, health_concerns TEXT, health_concerns_comments TEXT,
            nails_check TEXT, nails_date TEXT, nails_comments TEXT, hair_check TEXT,
            hair_date TEXT, hair_comments TEXT, mar_sheets_check TEXT,
            mar_sheets_comments TEXT, finance_cash_box TEXT, finance_top_up TEXT,
            finance_take_out TEXT, finance_diary_datetime TEXT, finance_diary_staff TEXT,
            shop_q1_toiletries TEXT, shop_q1_comments TEXT, shop_q2_clothes TEXT, shop_q2_comments TEXT, 
            shop_q3_personal_items TEXT, shop_q3_comments TEXT,
            caredocs_contacts TEXT, caredocs_careplan TEXT, caredocs_meds TEXT,
            caredocs_bodymap TEXT, caredocs_charts TEXT, health_plan_file TEXT,
            actions_required TEXT, family_comm_made TEXT, family_comm_datetime TEXT,
            family_comm_reason TEXT, family_comm_issues TEXT, current_goal TEXT,
            last_goal_progress TEXT, feeling_response TEXT, happy_response TEXT,
            other_notes TEXT,
            FOREIGN KEY (service_user_id) REFERENCES service_users (id),
            UNIQUE(service_user_id, form_month_year)
        )
    ''')

    # Add new shopping comment columns to existing databases
    try:
        cur.execute("ALTER TABLE forms ADD COLUMN shop_q1_comments TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cur.execute("ALTER TABLE forms ADD COLUMN shop_q2_comments TEXT") 
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cur.execute("ALTER TABLE forms ADD COLUMN shop_q3_comments TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Add new icon selection columns for feelings and care sections
    try:
        cur.execute("ALTER TABLE forms ADD COLUMN feeling_icons_selected TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cur.execute("ALTER TABLE forms ADD COLUMN care_icons_selected TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # --- Appointments Table ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            form_id INTEGER NOT NULL,
            name TEXT, last_seen TEXT, next_due TEXT, booked TEXT,
            FOREIGN KEY (form_id) REFERENCES forms (id)
        )
    ''')

    # --- Activity Log Table ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT
        )
    ''')

    con.commit()
    con.close()


# Initialize the database when the program starts
initialize_db()
