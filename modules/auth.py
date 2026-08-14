import streamlit as st
from database.supabase import supabase

def verify_user_credentials(user_input, password):
    clean_input = str(user_input).strip().lower()
    clean_pass = str(password).strip()

    # Hardcoded Credentials
    if clean_input in ["admin@school.com", "admin", "9876543210"] and clean_pass == "admin123":
        return {
            "email": "admin@school.com",
            "role": "admin",
            "assigned_class": "ALL",
            "assigned_subjects": ["ALL"]
        }
    
    if clean_input in ["teacher@school.com", "teacher", "9876543211"] and clean_pass == "teacher123":
        return {
            "email": "teacher@school.com",
            "role": "class_teacher",
            "assigned_class": "Class 10-A",
            "assigned_subjects": ["Maths", "Science"]
        }

    return None

def render_login_page():
    st.markdown("## 🔑 School Portal Login")
    
    # Form layout without nested button issues
    user_input = st.text_input("User ID / Email / Mobile Number", value="admin@school.com", key="login_user_input")
    password = st.text_input("Password", type="password", value="admin123", key="login_pass_input")
    
    st.write("")
    if st.button("🚀 Login", use_container_width=True, type="primary"):
        user_data = verify_user_credentials(user_input, password)
        if user_data:
            st.session_state['logged_in'] = True
            st.session_state['user_email'] = user_data['email']
            st.session_state['user_role'] = user_data['role']
            st.session_state['assigned_class'] = user_data['assigned_class']
            st.session_state['assigned_subjects'] = user_data['assigned_subjects']
            st.success("✅ सफलतापूर्वक लॉगिन हो गया!")
            st.rerun()
        else:
            st.error("❌ गलत ID या पासवर्ड! पुनः प्रयास करें।")

    # 🆘 EMERGENCY DIRECT ENTRANCE
    st.write("---")
    if st.button("⚡ Emergency Admin Direct Entrance (डायरेक्ट खोलें)", use_container_width=True):
        st.session_state['logged_in'] = True
        st.session_state['user_email'] = "admin@school.com"
        st.session_state['user_role'] = "admin"
        st.session_state['assigned_class'] = "ALL"
        st.session_state['assigned_subjects'] = ["ALL"]
        st.rerun()

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = None
    st.session_state['user_role'] = None
    st.session_state['assigned_class'] = None
    st.session_state['assigned_subjects'] = None
    st.rerun()
