import streamlit as st
import bcrypt
from database.supabase import supabase

def hash_password(password: str) -> str:
    """Plain password को सुरक्षित Bcrypt Hash में बदलेगा"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Plain password और Hash को चेक करेगा"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def render_login_page():
    st.markdown("""
        <style>
            .login-box {
                max-width: 420px;
                margin: 0 auto;
                padding: 30px;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>🏫 Campus ERP Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Secure Login Access</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("📧 Email ID", placeholder="admin@school.com")
            password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("🚀 Sign In", use_container_width=True)

            if submit:
                clean_email = email.strip().lower()
                clean_pass = password.strip()

                if not clean_email or not clean_pass:
                    st.warning("⚠️ कृपया ईमेल और पासवर्ड दोनों दर्ज करें।")
                elif not supabase:
                    st.error("❌ डेटाबेस कनेक्ट नहीं है। कृपया Supabase सेटिंग्स जांचें।")
                else:
                    try:
                        # Supabase से User Fetch करें
                        res = supabase.table("users").select("*").eq("email", clean_email).execute()
                        users = res.data or []

                        if not users:
                            st.error("❌ यह ईमेल आईडी पंजीकृत नहीं है।")
                        else:
                            user = users[0]
                            db_password = user.get("password", "")

                            # Password Matching (Supports both Hash and Plain Old Passwords)
                            is_valid = False
                            if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
                                is_valid = verify_password(clean_pass, db_password)
                            else:
                                # Backward compatibility: अगर डेटाबेस में पुराना Plain Password पड़ा है
                                is_valid = (clean_pass == db_password)
                                if is_valid:
                                    # ऑटोमेटिकली पुराने पासवर्ड को Hashed पासवर्ड में अपडेट करें
                                    new_hash = hash_password(clean_pass)
                                    supabase.table("users").update({"password": new_hash}).eq("id", user["id"]).execute()

                            if is_valid:
                                st.session_state['logged_in'] = True
                                st.session_state['authenticated'] = True
                                st.session_state['user_email'] = user['email']
                                st.session_state['user_name'] = user.get('name', 'User')
                                st.session_state['user_role'] = user.get('role', 'teacher')
                                st.session_state['assigned_class'] = user.get('assigned_class', 'Class 10')
                                st.session_state['assigned_classes'] = user.get('assigned_classes') or [user.get('assigned_class', 'Class 10')]
                                st.session_state['assigned_subjects'] = user.get('assigned_subjects', [])
                                
                                st.success("✅ लॉगिन सफल! रीडायरेक्ट हो रहा है...")
                                st.rerun()
                            else:
                                st.error("❌ गलत पासवर्ड। कृपया पुनः प्रयास करें।")

                    except Exception as err:
                        st.error(f"❌ लॉगिन एरर: {err}")

def logout_user():
    st.session_state.clear()
    st.rerun()
