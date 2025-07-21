import sqlite3
import hashlib
import streamlit as st
from email_utils import send_otp_email

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🔐 Login Credentials Only
def authentication(username, password):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute('''
        SELECT users.id, users.username, users.password_hash, roles.name, users.email
        FROM users JOIN roles ON users.role_id = roles.id
        WHERE users.username = ?
    ''', (username,))
    user = cur.fetchone()
    conn.close()

    if not user or hash_password(password) != user[2]:
        return None, "❌ Invalid username or password."

    # Store email for login OTP validation
    st.session_state.login_email = user[4]

    return {
        'id': user[0],
        'username': user[1],
        'role': user[3],
        'email': user[4]
    }, "✅ Credentials verified. Please enter OTP."

# 📩 Send Login OTP
def send_login_otp(email):
    otp = send_otp_email(email)
    if otp:
        st.session_state.login_otp = otp
        return True, f"📩 OTP sent to {email}"
    return False, "⚠️ Failed to send OTP."

# ✅ Verify Login OTP
def verify_login_otp(entered_otp):
    expected = st.session_state.get("login_otp")
    return entered_otp == expected

# 📝 New account request using stored OTP
def request_account(username, password, role_name, email, entered_otp):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
    if cur.fetchone():
        conn.close()
        return False, "⚠️ Username or email already registered."

    cur.execute("SELECT 1 FROM pending_users WHERE username = ? OR email = ?", (username, email))
    if cur.fetchone():
        conn.close()
        return False, "⚠️ A pending request already exists."

    expected_otp = st.session_state.get("register_otp")
    if entered_otp != expected_otp:
        conn.close()
        return False, "⛔ Incorrect OTP. Request cancelled."

    password_hash = hash_password(password)
    cur.execute('''
        INSERT INTO pending_users (username, password_hash, role_name, email)
        VALUES (?, ?, ?, ?)
    ''', (username, password_hash, role_name, email))
    conn.commit()
    conn.close()
    return True, f"✅ Account request for '{username}' submitted."

# 🔁 Initiate password reset (OTP sent here)
def initiate_password_reset(email):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()

    if not user:
        return False, "❌ No account associated with this email."

    otp = send_otp_email(email)
    if otp:
        st.session_state.reset_email = email
        st.session_state.reset_otp = otp
        return True, f"📩 OTP sent to {email}"
    return False, "⚠️ Failed to send OTP."

# 🔐 Final password reset with verification
def reset_password(entered_otp, new_password):
    expected_otp = st.session_state.get("reset_otp")
    email = st.session_state.get("reset_email")

    if not expected_otp or not email:
        return False, "⚠️ No reset session found."

    if entered_otp != expected_otp:
        return False, "⛔ Incorrect OTP."

    hashed = hash_password(new_password)
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed, email))
    conn.commit()
    conn.close()
    return True, "✅ Password updated successfully."