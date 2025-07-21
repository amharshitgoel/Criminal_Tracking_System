import sqlite3

# ✅ Grant permission to user by email (Streamlit feedback style)
def grant_permission(email, permission_name):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    # Get user ID
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return False, "❌ No user found with that email."

    user_id = user[0]

    # Check if permission already exists
    cur.execute("SELECT 1 FROM user_permissions WHERE user_id = ? AND permission = ?", (user_id, permission_name))
    if cur.fetchone():
        conn.close()
        return False, f"⚠️ Permission '{permission_name}' is already granted."

    # Grant permission
    cur.execute("INSERT INTO user_permissions (user_id, permission) VALUES (?, ?)", (user_id, permission_name))
    conn.commit()
    conn.close()
    return True, f"✅ Permission '{permission_name}' granted to {email}."

# 🔍 Check permission by user ID (used in UI conditional logic)
def has_permission(user_id, permission_name):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM user_permissions WHERE user_id = ? AND permission = ?", (user_id, permission_name))
    result = cur.fetchone()
    conn.close()
    return bool(result)