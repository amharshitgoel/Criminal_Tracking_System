import sqlite3
from auth import hash_password

def initialize_db_core():
    """
    Initializes core database tables without any interactive admin creation.
    Safe to call at app startup.
    """
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    # 🔐 Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role_id INTEGER,
            email TEXT UNIQUE NOT NULL,
            FOREIGN KEY(role_id) REFERENCES roles(id)
        )
    """)

    # 📨 Pending Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            requested_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 🧑‍💼 Roles
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # 📁 Criminals
    cur.execute("""
        CREATE TABLE IF NOT EXISTS criminals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            mobile TEXT,
            address TEXT,
            dob TEXT,
            aadhaar TEXT UNIQUE NOT NULL,
            gender TEXT,
            photo_blob BLOB
        )
    """)

    # 📂 Cases
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            criminal_id INTEGER,
            jurisdiction TEXT,
            section_of_law TEXT,
            status TEXT,
            date_registered TEXT,
            officer_name TEXT,
            FOREIGN KEY(criminal_id) REFERENCES criminals(id)
        )
    """)

    # 🕵️ Audit Logs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ✅ Permissions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            permission TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # 🔁 Seed roles
    for role in ['Admin', 'Investigating Officer', 'Data Entry Staff', 'Senior Official']:
        cur.execute("INSERT OR IGNORE INTO roles (name) VALUES (?)", (role,))

    conn.commit()
    conn.close()

def is_user_table_empty():
    """
    Checks if the users table is empty.
    """
    try:
        conn = sqlite3.connect("Criminal Tracking System.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        conn.close()
        return count == 0
    except:
        return True

def create_first_admin(username, password, email):
    """
    Inserts first admin into users table.
    Should only be called if users table is empty.
    """
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    cur.execute("SELECT id FROM roles WHERE name = 'Admin'")
    role = cur.fetchone()
    if not role:
        conn.close()
        return False, "⚠️ Role 'Admin' not found."

    role_id = role[0]
    password_hash = hash_password(password)

    cur.execute("""
        INSERT INTO users (username, password_hash, role_id, email)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, role_id, email))

    conn.commit()
    conn.close()
    return True, f"✅ Admin '{username}' created successfully."