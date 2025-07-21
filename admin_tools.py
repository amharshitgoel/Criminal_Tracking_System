import sqlite3
from audit import log_action

def get_pending_requests():
    """Returns a list of pending users with request info."""
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM pending_users")
    requests = cur.fetchall()
    conn.close()
    return requests

def approve_user_by_id(request_id):
    """Approve a single pending user by ID."""
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM pending_users WHERE id = ?", (request_id,))
    req = cur.fetchone()
    if not req:
        conn.close()
        return False, "⚠️ Request not found."

    username, password_hash, role_name, email = req[1], req[2], req[3], req[4]
    cur.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    role = cur.fetchone()
    if not role:
        conn.close()
        return False, f"⚠️ Invalid role '{role_name}'."

    cur.execute("""
        INSERT INTO users (username, password_hash, role_id, email)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, role[0], email))
    cur.execute("DELETE FROM pending_users WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    log_action("Admin", f"Approved user '{username}' as {role_name}")
    return True, f"✅ Approved {username} as {role_name}"

def approve_pending_users():
    """Approve all pending users in one go."""
    pending = get_pending_requests()
    approved = 0
    for req in pending:
        success, _ = approve_user_by_id(req[0])
        if success:
            approved += 1
    return f"✅ {approved} pending user(s) approved."

def delete_user_by_username(username):
    """Delete an approved user by username."""
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return False, f"❌ User '{username}' not found."

    cur.execute("DELETE FROM users WHERE id = ?", (user[0],))
    conn.commit()
    conn.close()
    log_action("Admin", f"Deleted user '{username}'")
    return True, f"✅ User '{username}' has been deleted."