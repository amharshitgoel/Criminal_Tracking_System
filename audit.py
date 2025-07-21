import sqlite3
import pandas as pd

# ✅ Log any user action with optional details
def log_action(username, action):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO audit_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

# 📜 View all audit logs (wrapped version)
def view_logs():
    return view_logs_filtered()  # Returns all logs as DataFrame

# 🔍 Filter logs by username and/or date
def view_logs_filtered(username=None, date=None):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    query = "SELECT username, action, timestamp FROM audit_logs WHERE 1=1"
    params = []

    if username:
        query += " AND username = ?"
        params.append(username)

    if date:
        query += " AND DATE(timestamp) = ?"
        params.append(date)

    query += " ORDER BY timestamp DESC"
    cur.execute(query, tuple(params))
    logs = cur.fetchall()
    conn.close()

    return pd.DataFrame(logs, columns=["Username", "Action", "Timestamp"])