import streamlit as st
from database.supabase import supabase

def render_login_page():
    st.title("🏫 Campus ERP Pro - Access Portal")
    st.caption("Admin & Staff Login / Registration")

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Admin Sign Up / Create Password"])

    # -------------------------------------------------------------
    # TAB 1: LOGIN WITH EMAIL & PASSWORD
    # -------------------------------------------------------------
    with tab_login:
        st.subheader("Sign In to Your Account")
        email_input = st.text_input("Enter Registered Email", key="login_email", placeholder="admin@school.com")
        password_input = st.text_input("Enter Password", type="password", key="login_pass")

        if st.button("Login", type="primary", use_container_width=True):
            if email_input.strip() and password_input.strip() and supabase:
                try:
                    res = supabase.table("users") \
                        .select("*") \
                        .eq("email", email_input.strip().lower()) \
                        .eq("password", password_input.strip()) \
                        .execute()
                    
                    user_data = res.data

                    if user_data:
                        user = user_data[0]
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = user['email']
                        st.session_state['user_name'] = user['name']
                        st.session_state['user_role'] = user.get('role', 'admin')
                        st.session_state['assigned_class'] = user.get('assigned_class', 'ALL')
                        st.session_state['assigned_section'] = user.get('assigned_section', 'ALL')
                        st.session_state['assigned_subjects'] = user.get('assigned_subjects', ['ALL'])

                        st.success(f"✅ Successful Login! Welcome, {user['name']}.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Email ID or Password. Please try again.")
                except Exception as e:
                    st.error(f"Login error: {e}")
            else:
                st.warning("Please fill in both Email and Password fields.")

    # -------------------------------------------------------------
    # TAB 2: REGISTER NEW ADMIN & SET PASSWORD
    # -------------------------------------------------------------
    with tab_register:
        st.subheader("Create Admin Account")
        st.info("यहाँ से Admin खुद का Name, Email ID, Phone और Password सेट कर सकते हैं।")

        admin_name = st.text_input("Full Name", key="reg_name", placeholder="e.g. Principal Sharma")
        admin_email = st.text_input("Email Address", key="reg_email", placeholder="e.g. admin@school.com")
        admin_phone = st.text_input("Mobile Number", key="reg_phone", placeholder="e.g. 9876543210")
        new_password = st.text_input("Set New Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm New Password", type="password", key="reg_confirm_pass")

        if st.button("Create Admin Account", type="primary", use_container_width=True):
            cleaned_email = admin_email.strip().lower()
            cleaned_phone = admin_phone.strip()

            if not admin_name.strip() or not cleaned_email or not new_password:
                st.warning("All fields are required.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif supabase:
                try:
                    # Check if email already exists
                    existing_user = supabase.table("users").select("email").eq("email", cleaned_email).execute()
                    
                    if existing_user.data:
                        st.error("⚠️ This Email ID is already registered. Please go to the Login tab.")
                    else:
                        # Insert Admin Details
                        payload = {
                            "name": admin_name.strip(),
                            "email": cleaned_email,
                            "phone": cleaned_phone,
                            "password": new_password.strip(),
                            "role": "admin",
                            "assigned_class": "ALL",
                            "assigned_section": "ALL",
                            "assigned_subjects": ["ALL"]
                        }
                        
                        supabase.table("users").insert(payload).execute()
                        st.success("🎉 Admin Account created successfully! You can now login.")
                except Exception as err:
                    st.error(f"❌ Registration Error: {err}")

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state.clear()
    st.rerun()
