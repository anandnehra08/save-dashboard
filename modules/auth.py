import streamlit as st
from database.supabase import supabase

def verify_user_credentials(user_input, password):
    """
    यूजर क्रेडेंशियल्स की जांच करता है।
    1. पहले हार्डकोडेड एडमिन/टीचर चेक करता है।
    2. उसके बाद सुपाबेस (Supabase) डेटाबेस में चेक करता है।
    """
    clean_input = str(user_input).strip().lower()
    clean_pass = str(password).strip()

    # -------------------------------------------------------------
    # ⚡ 1. DIRECT HARDCODED LOGINS (हमेशा 100% काम करेगा)
    # -------------------------------------------------------------
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
        
    if clean_input in ["subject@school.com", "subject", "9876543212"] and clean_pass == "subject123":
        return {
            "email": "subject@school.com",
            "role": "subject_teacher",
            "assigned_class": "None",
            "assigned_subjects": ["Physics"]
        }

    # -------------------------------------------------------------
    # 🗄️ 2. SUPABASE DATABASE CHECK (FALLBACK)
    # -------------------------------------------------------------
    if supabase:
        try:
            res = supabase.table("users") \
                .select("*") \
                .or_(f"email.ilike.{clean_input},phone.eq.{clean_input}") \
                .eq("password", clean_pass) \
                .execute()
                
            if res.data and len(res.data) > 0:
                user_data = res.data[0]
                return {
                    "email": user_data.get("email", clean_input),
                    "role": user_data.get("role", "class_teacher"),
                    "assigned_class": user_data.get("assigned_class", "ALL"),
                    "assigned_subjects": user_data.get("assigned_subjects", ["ALL"])
                }
        except Exception:
            pass

    return None


def render_login_page():
    st.markdown("## 🔑 School Portal Login")
    
    with st.form("login_form"):
        user_input = st.text_input("User ID / Email / Mobile Number", value="admin@school.com")
        password = st.text_input("Password", type="password", value="admin123")
        
        submit = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if submit:
            if not user_input or not password:
                st.warning("⚠️ कृपया ID और Password दोनों दर्ज करें।")
            else:
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


def logout_user():
    """यूजर सेशन क्लियर करके लॉगआउट करता है।"""
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = None
    st.session_state['user_role'] = None
    st.session_state['assigned_class'] = None
    st.session_state['assigned_subjects'] = None
    st.rerun()
