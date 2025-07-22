import streamlit as st
from utils import is_valid_mobile, is_valid_aadhaar
from auth import authentication, request_account
from add_criminal_case import add_criminal_and_case
from add_new_case import add_case
from search_criminal import search_criminal_with_cases
from permission_tools import has_permission
from admin_dashboard import admin_dashboard_ui
from email_utils import send_otp_email
from database import initialize_db_core, is_user_table_empty, create_first_admin
from face_match_utils import search_by_uploaded_photo  # DeepFace-based match

st.set_page_config(page_title="Criminal Tracking System", layout="wide")
initialize_db_core()

# Session setup
for key in ["user", "login_otp", "register_otp", "register_email"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.title("Criminal Tracking System")

# First Admin Setup
if is_user_table_empty():
    st.warning("No users found. Let's create the first Admin account.")
    with st.form("FirstAdminForm"):
        admin_name = st.text_input("Admin Username")
        admin_password = st.text_input("Admin Password", type="password")
        admin_email = st.text_input("Admin Email")
        if st.form_submit_button("Create Admin"):
            success, msg = create_first_admin(admin_name, admin_password, admin_email)
            st.success(msg) if success else st.error(msg)

# Login / Registration
elif not st.session_state.user:
    st.subheader("Login")
    with st.form("SendLoginOTP"):
        login_email = st.text_input("Registered Email")
        if st.form_submit_button("Send OTP"):
            otp = send_otp_email(login_email)
            if otp:
                st.session_state.login_otp = otp
                st.success(f"OTP sent to {login_email}")
            else:
                st.error("Failed to send OTP.")

    with st.form("LoginForm"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        entered_otp = st.text_input("Enter OTP")
        if st.form_submit_button("Login"):
            user_data, msg = authentication(username, password)
            if user_data:
                if entered_otp == st.session_state.login_otp:
                    st.session_state.user = {
                        "id": user_data["id"],
                        "username": user_data["username"],
                        "role": user_data["role"],
                        "email": user_data["email"]
                    }
                    st.success("Logged in successfully.")
                    st.toast("Loading dashboard...")
                    st.rerun()
                else:
                    st.error("Incorrect OTP.")
            else:
                st.error(msg)

    st.divider()
    st.subheader("Request New Account")
    with st.form("SendRegisterOTP"):
        r_email = st.text_input("Email for OTP")
        if st.form_submit_button("Send OTP"):
            otp = send_otp_email(r_email)
            if otp:
                st.session_state.register_otp = otp
                st.session_state.register_email = r_email
                st.success(f"OTP sent to {r_email}")
            else:
                st.error("Could not send OTP.")

    with st.form("RegisterAccount"):
        r_username = st.text_input("New Username")
        r_password = st.text_input("Password", type="password")
        r_role = st.selectbox("Role", ["Admin", "Investigating Officer", "Senior Official", "Data Entry Staff"])
        entered_reg_otp = st.text_input("Enter Received OTP")
        if st.form_submit_button("Submit Request"):
            if entered_reg_otp == st.session_state.register_otp:
                success, msg = request_account(
                    r_username, r_password, r_role,
                    st.session_state.register_email, entered_reg_otp
                )
                st.success(msg) if success else st.error(msg)
            else:
                st.error("Incorrect OTP. Request denied.")

# Sidebar Navigation
else:
    user = st.session_state.user
    st.sidebar.title("Navigation")
    page_options = ["Add Criminal", "Search Criminal", "Add Case"]
    if user["role"].lower() == "admin":
        page_options.append("Admin Dashboard")

    selected_page = st.sidebar.radio("Go to:", page_options)
    st.sidebar.markdown("---")
    st.sidebar.write(f"Username: {user['username']}")
    st.sidebar.write(f"Role: {user['role']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # Page Routing
    if selected_page == "Add Criminal":
        st.subheader("Add Criminal Record")
        with st.form("AddCriminalForm"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=0)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.text_input("Date of Birth (YYYY-MM-DD)")
            mobile = st.text_input("Mobile")
            address = st.text_input("Address")
            aadhaar = st.text_input("Aadhaar")
            photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png"])
            jurisdiction = st.text_input("Jurisdiction")
            section = st.text_input("Section of Law")
            status = st.selectbox("Status", ["Under Investigation", "Closed", "Charges Filed"])
            date_registered = st.text_input("Date Registered")
            officer_name = st.text_input("Officer Name")
            if st.form_submit_button("Add Criminal & Case"):
                if not is_valid_mobile(mobile) or not is_valid_aadhaar(aadhaar):
                    st.error("Invalid mobile or Aadhaar.")
                else:
                    photo_blob = photo.read() if photo else None
                    success, msg = add_criminal_and_case(
                        name, age, dob, mobile, address, aadhaar, gender,
                        photo_blob, jurisdiction, section, status,
                        date_registered, officer_name
                    )
                    st.success(msg) if success else st.error(msg)

    elif selected_page == "Search Criminal":
        st.subheader("Search Criminals")
        tab1, tab2 = st.tabs(["Search by Name/Aadhaar", "Search by Photo"])

        with tab1:
            with st.expander("Advanced Filters"):
                age_range = st.slider("Age Range", 18, 80, (18, 40))
                gender_filter = st.selectbox("Gender", ["", "Male", "Female", "Other"])
                section_filter = st.text_input("Section of Law")
                jurisdiction_filter = st.text_input("Jurisdiction")

            query = st.text_input("Search by Name or Aadhaar")
            if query or gender_filter or section_filter or jurisdiction_filter:
                results = search_criminal_with_cases(
                    query=query if query else None,
                    section_of_law=section_filter if section_filter else None,
                    jurisdiction=jurisdiction_filter if jurisdiction_filter else None,
                    gender=gender_filter if gender_filter else None,
                    age_range=age_range
                )
                if results:
                    for crim in results:
                        st.markdown(f"### {crim['name']} ({crim['gender']})")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"Mobile: {crim['mobile']}")
                            st.write(f"Address: {crim['address']}")
                            st.write(f"Aadhaar: {crim['aadhaar']}")
                            st.write(f"DOB: {crim['dob']}")
                            st.write(f"Age: {crim['age']}")
                        with col2:
                            st.image(crim["photo_blob"], width=200) if crim["photo_blob"] else st.info("No photo available.")
                        st.write("Cases:")
                        for case in crim["cases"]:
                            st.write(f"— Jurisdiction: {case[0]}, Section: {case[1]}, Status: {case[2]}")
                            st.write(f"  Registered: {case[3]}, Officer: {case[4]}")
                else:
                    st.warning("No criminal found.")

        with tab2:
            uploaded = st.file_uploader("Upload Criminal Image", type=["jpg", "jpeg", "png"])
            if uploaded:
                st.info("Matching face against database...")
                matches, msg = search_by_uploaded_photo(uploaded.read())
                st.write(msg)
                if matches:
                    for m in matches:
                        st.markdown(f"### {m['name']} ({m['gender']})")
                        st.write(f"Address: {m['address']}")
                        st.write(f"Mobile: {m['mobile']}")
                    if m.get("cases"):
                        st.write("cases:")
                        for case in m["cases"]:
                             st.write(f"— Jurisdiction: {case[0]}, Section: {case[1]}, Status: {case[2]}")
                             st.write(f"  Registered: {case[3]}, Officer: {case[4]}")
                    else:
                        st.info("No cases linked")

                else:
                    st.warning("No match found.")

    elif selected_page == "Add Case":
        st.subheader("Add Case to Existing Criminal")
        with st.form("AddCaseForm"):
            cid = st.number_input("Criminal ID", min_value=1)
            juri = st.text_input("Jurisdiction")
            sec = st.text_input("Section of Law")
            stat = st.selectbox("Status", ["Under Investigation", "Closed", "Charges Filed"])
            date = st.text_input("Date Registered")
            officer = st.text_input("Officer Name")
            if st.form_submit_button("Add Case"):
                success, msg = add_case(cid, juri, sec, stat, date, officer)
                st.success(msg) if success else st.error(msg)

    elif selected_page == "Admin Dashboard":
        st.subheader("Admin Dashboard")
        admin_dashboard_ui()
