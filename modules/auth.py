import streamlit as st
from database.supabase import supabase

def render_login_page():
    st.title("🏫 Campus ERP Pro - Access Portal")
    st.caption("School Management System Login")

    tab_login, tab_admin_setup = st.tabs(["🔐 Sign In", "👑 Principal / Admin Registration"])

    # -------------------------------------------------------------
    # TAB 1: USER LOGIN (Admin / Teachers)
    # -------------------------------------------------------------
    with tab_login:
        st.subheader("Login to your account")
        email_input = st.text_input("Enter Email Address", key="login_email", placeholder="principal@school.com or teacher@school.com")
        password_input = st.text_input("Enter Password", type="password", key="login_pass")

        if st.button("Login", type="primary", use_container_width=True):
            clean_email = email_input.strip().lower()
            clean_pass = password_input.strip()

            if clean_email and clean_pass and supabase:
                try:
                    res = supabase.table("users") \
                        .select("*") \
                        .eq("email", clean_email) \
                        .eq("password", clean_pass) \
                        .execute()
                    
                    user_data = res.data

                    if user_data:
                        user = user_data[0]
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = user['email']
                        st.session_state['user_name'] = user['name']
                        st.session_state['user_role'] = user.get('role', 'subject_teacher')
                        st.session_state['assigned_class'] = user.get('assigned_class', 'ALL')
                        st.session_state['assigned_section'] = user.get('assigned_section', 'ALL')
                        st.session_state['assigned_subjects'] = user.get('assigned_subjects', ['ALL'])

                        st.success(f"✅ Login Successful! Welcome, {user['name']} ({user['role'].upper()})")
                        st.rerun()
                    else:
                        st.error("❌ गलत Email ID या Password! कृपया पुनः प्रयास करें।")
                except Exception as e:
                    st.error(f"Login error: {e}")
            else:
                st.warning("कृपया Email और Password दोनों भरें।")

    # -------------------------------------------------------------
    # TAB 2: FIRST-TIME PRINCIPAL REGISTRATION
    # -------------------------------------------------------------
    with tab_admin_setup:
        st.subheader("Principal / Admin Account Setup")
        st.info("यह सेक्शन केवल Principal/Main Admin का नया खाता बनाने के लिए है।")

        admin_name = st.text_input("Principal Name", key="p_name", placeholder="Dr. R. K. Sharma")
        admin_email = st.text_input("Email ID", key="p_email", placeholder="principal@school.com")
        admin_phone = st.text_input("Phone Number", key="p_phone", placeholder="9876543210")
        new_password = st.text_input("Set Password", type="password", key="p_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="p_conf_pass")

        if st.button("Create Principal Account", type="primary", use_container_width=True):
            cleaned_email = admin_email.strip().lower()

            if not admin_name.strip() or not cleaned_email or not new_password:
                st.warning("सभी फ़ील्ड भरना आवश्यक है।")
            elif new_password != confirm_password:
                st.error("❌ पासवर्ड मैच नहीं हो रहे हैं।")
            elif supabase:
                try:
                    payload = {
                        "name": admin_name.strip(),
                        "email": cleaned_email,
                        "phone": admin_phone.strip(),
                        "password": new_password.strip(),
                        "role": "admin",
                        "assigned_class": "ALL",
                        "assigned_section": "ALL",
                        "assigned_subjects": ["ALL"]
                    }
                    supabase.table("users").insert(payload).execute()
                    st.success("🎉 Principal Account सफलतापूर्वक बन गया है! अब Sign In टैब से लॉगिन करें।")
                except Exception as err:
                    st.error(f"❌ Error: {err}")

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state.clear()
    st.rerun()
