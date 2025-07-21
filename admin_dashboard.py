import streamlit as st
import pandas as pd
import sqlite3

# 🔧 Admin feature utilities
from admin_tools import (
    approve_pending_users,
    approve_user_by_id,
    get_pending_requests,
    delete_user_by_username
)

# 📜 Audit log tools
from audit import view_logs_filtered, view_logs

# 🔐 Permission management
from permission_tools import grant_permission


# 🔍 Dashboard Data Summary
def admin_dashboard():
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM criminals")
    total_criminals = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM cases")
    total_cases = cur.fetchone()[0]

    cur.execute("""
        SELECT roles.name, COUNT(users.id)
        FROM users JOIN roles ON users.role_id = roles.id
        GROUP BY roles.name
    """)
    roles_data = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM pending_users")
    pending_requests = cur.fetchone()[0]

    conn.close()
    return {
        "criminals": total_criminals,
        "cases": total_cases,
        "roles": roles_data,
        "pending": pending_requests
    }


# 🔝 Most Active Users
def get_top_users(limit=5):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT username, COUNT(*) as actions
        FROM audit_logs
        GROUP BY username
        ORDER BY actions DESC
        LIMIT ?
    """, (limit,))
    result = cur.fetchall()
    conn.close()
    return pd.DataFrame(result, columns=["Username", "Actions"])


# 👥 All Approved Users
def get_all_users():
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT users.username, roles.name
        FROM users
        JOIN roles ON users.role_id = roles.id
        ORDER BY roles.name, users.username
    """)
    data = cur.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["Username", "Role"])


# 📊 Main Admin Dashboard UI
def admin_dashboard_ui():
    st.header("🧑‍💼 Admin Dashboard")

    # 🧮 Summary Metrics
    summary = admin_dashboard()
    col1, col2, col3 = st.columns(3)
    col1.metric("🧾 Total Criminals", summary["criminals"])
    col2.metric("📂 Total Cases", summary["cases"])
    col3.metric("🕒 Pending Requests", summary["pending"])

    st.divider()

    # 👥 Approved Users
    st.subheader("👥 Approved Users")
    st.dataframe(get_all_users(), use_container_width=True)

    st.divider()

    # 📊 Users by Role
    st.subheader("🔢 Users by Role Summary")
    st.table(pd.DataFrame(summary["roles"], columns=["Role", "Count"]))

    # 🔝 Active Users
    st.subheader("🔥 Top Active Users")
    st.dataframe(get_top_users(), use_container_width=True)

    st.divider()

    # ✅ Manage Pending Account Requests
    st.subheader("✅ Manage Pending Account Requests")
    pending = get_pending_requests()
    if not pending:
        st.info("📭 No pending requests.")
    else:
        for req in pending:
            uid, uname, role_name, email, requested_at = req[:5]
            with st.expander(f"{uname} → {role_name}"):
                st.write(f"📧 Email: {email}")
                st.write(f"⏱ Requested At: {requested_at}")

                colA, colB = st.columns(2)
                with colA:
                    if st.button(f"✅ Approve '{uname}'", key=f"approve_{uid}"):
                        success, msg = approve_user_by_id(uid)
                        st.success(msg) if success else st.error(msg)
                with colB:
                    if st.button(f"🗑️ Delete '{uname}'", key=f"delete_{uid}"):
                        success, msg = delete_user_by_username(uname)
                        st.warning(msg) if success else st.error(msg)

        if st.button("✅ Approve All Pending"):
            msg = approve_pending_users()
            st.success(msg)

    st.divider()

    # 📜 All Audit Logs
    st.subheader("📜 All Audit Logs")
    all_logs = view_logs()
    if all_logs is not None and not all_logs.empty:
        st.dataframe(all_logs, use_container_width=True)
    else:
        st.warning("📭 No audit logs found.")

    st.divider()

    # 🔍 Filter Audit Logs
    st.subheader("🔍 Filter Audit Logs")
    with st.form("AuditLogFilter"):
        uname = st.text_input("Filter by Username")
        date = st.text_input("Filter by Date (YYYY-MM-DD)")
        if st.form_submit_button("Search"):
            filtered = view_logs_filtered(uname or None, date or None)
            if filtered is not None and not filtered.empty:
                st.success("✅ Matching Audit Logs")
                st.dataframe(filtered, use_container_width=True)
            else:
                st.warning("🔍 No matching logs found.")

    st.divider()

    # 🔐 Grant Permissions
    st.subheader("🔐 Grant Permission to User")
    with st.form("PermissionForm"):
        email = st.text_input("User Email")
        permission = st.text_input("Permission to Grant")
        if st.form_submit_button("Grant"):
            success, msg = grant_permission(email, permission)
            st.success(msg) if success else st.error(msg)

    st.divider()

    # 🗑️ Delete Approved User
    st.subheader("🗑️ Delete Approved User")
    with st.form("DeleteUserForm"):
        username = st.text_input("Username to Delete")
        confirm = st.checkbox(f"Yes, delete '{username}' permanently")
        if st.form_submit_button("Delete User"):
            if confirm:
                success, msg = delete_user_by_username(username)
                st.success(msg) if success else st.error(msg)
            else:
                st.warning("⚠️ You must confirm before deleting.")