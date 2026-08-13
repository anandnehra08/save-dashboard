import streamlit as st
from database.supabase import supabase

def login_user(email, password):
    """Supabase Auth के माध्यम से यूज़र को लॉगिन करता है"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        user_id = response.user.id
        # यूज़र का रोल (Admin/Teacher) प्राप्त करें
        profile_res = supabase.table("profiles").select("role").eq("id", user_id).execute()
        
        role = "teacher"  # Default role
        if profile_res.data:
            role = profile_res.data[0].get("role", "teacher")
            
        st.session_state['authenticated'] = True
        st.session_state['user_email'] = email
        st.session_state['user_role'] = role
        st.success("✅ लॉगिन सफल रहा!")
        st.rerun()
        
    except Exception as e:
        st.error("❌ गलत ईमेल या पासवर्ड। कृपया पुनः प्रयास करें।")

def logout_user():
    """यूज़र को लॉगआउट करता है"""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state['authenticated'] = False
    st.session_state['user_email'] = None
    st.session_state['user_role'] = None
    st.rerun()

def render_login_page():
    st.markdown("<h2 style='text-align: center;'>🏫 Campus ERP Pro - Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("📧 Email Address")
            password = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("Log In", use_container_width=True)
            
            if submit:
                if email and password:
                    login_user(email, password)
                else:
                    st.warning("कृपया ईमेल और पासवर्ड दोनों दर्ज करें।")
