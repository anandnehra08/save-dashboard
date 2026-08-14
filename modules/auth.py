import streamlit as st
import bcrypt

# Supabase Client Import
try:
    from database.supabase import supabase
except Exception:
    supabase = None

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def render_login_page():
    st.markdown("""
        <style>
        .app-header-bar { 
            background: linear-gradient(135deg, #1E1B4B, #312E81); 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            color: white; 
            padding: 16px 18px; 
            border-radius: 24px; 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); 
            margin-bottom: 18px; 
        } 
        .header-top { display: flex; align-items: center; justify-content: space-between; } 
        .app-brand { display: flex; align-items: center; gap: 12px; } 
        .app-icon { font-size: 28px; background: linear-gradient(135deg, #6366F1, #4F46E5); padding: 8px 12px; border-radius: 16px; } 
        .app-title-text h3 { margin: 0; font-size: 18px; color: #F8FAFC; font-weight: 800; } 
        .app-title-text span { font-size: 11px; color: #C7D2FE; font-weight: 600; }
        .status-badge { background: rgba(34, 197, 94, 0.15); color: #4ADE80; border: 1px solid rgba(74, 222, 128, 0.2); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
        .admin-info-box { background: rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 10px 14px; margin-top: 12px; font-size: 12px; color: #E0E7FF; border: 1px solid rgba(255, 255, 255, 0.12); } 
        .admin-info-box p { margin: 2px 0; } 
        .admin-info-box a { color: #818CF8; text-decoration: none; font-weight: 700; }
        .stButton>button { width: 100%; border-radius: 16px !important; height: 50px !important; font-size: 15px !important; font-weight: 700 !important; background: linear-gradient(135deg, #4F46E5, #4338CA) !important; color: white !important; border: none !important; box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.4) !important; }
        </style>

        <div class="app-header-bar">
            <div class="header-top">
                <div class="app-brand">
                    <div class="app-icon">🎓</div>
                    <div class="app-title-text">
                        <h3>Dream Shiksha ERP</h3>
                        <span>POWERED BY SAKSHI SOLUTION</span>
                    </div>
                </div>
                <div class="status-badge">🟢 Live System</div>
            </div>
            <div class="admin-info-box">
                <p>🏢 <b>Provider:</b> Sakshi Solution</p>
                <p>👨‍💼 <b>Developer:</b> Anand Nehra</p>
                <p>📞 <b>Contact:</b> 9828595276 | ✉️ <b>Email:</b> anandnehra8@gmail.com</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login Portal")
        st.radio("Select Portal Mode", ["Admin / Teacher", "Student Portal"], horizontal=True, key="portal_mode_sel")

        # Form ke bajaye direct inputs use kar rahe hain taaki state freeze na ho
        user_input = st.text_input("Admin Username / Email", key="login_usr_input", placeholder="anandnehra08 or admin@school.com")
        password = st.text_input("Admin Password", type="password", key="login_pwd_input", placeholder="••••••••")
        
        submit = st.button("🚀 Sign In", use_container_width=True, key="btn_signin_submit")

        if submit:
            clean_input = user_input.strip().lower()
            clean_pass = password.strip()

            if not clean_input or not clean_pass:
                st.warning("⚠️ कृपया यूजरनेम/ईमेल और पासवर्ड दर्ज करें।")
                return

            # 1. HARDCODED MASTER LOGIN CHECK (Emergency Override)
            if clean_input in ["anandnehra08", "admin@school.com", "admin", "test"] and clean_pass in ["admin123", "admin", "123456"]:
                st.session_state['logged_in'] = True
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = "anandnehra08"
                st.session_state['user_name'] = "Anand Nehra"
                st.session_state['user_role'] = "admin"
                st.session_state['login_error'] = None
                st.rerun()

            # 2. SUPABASE DB CHECK
            elif supabase:
                try:
                    res = supabase.table("users").select("*").or_(f"email.eq.{clean_input},username.eq.{clean_input}").execute()
                    matched_users = res.data or []

                    if matched_users:
                        user = matched_users[0]
                        db_password = str(user.get("password", "")).strip()

                        is_valid = False
                        if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
                            is_valid = verify_password(clean_pass, db_password)
                        else:
                            is_valid = (clean_pass == db_password)

                        if is_valid:
                            st.session_state['logged_in'] = True
                            st.session_state['authenticated'] = True
                            st.session_state['user_email'] = user.get('username') or user.get('email') or clean_input
                            st.session_state['user_name'] = user.get('name', 'Admin')
                            st.session_state['user_role'] = user.get('role', 'admin')
                            st.session_state['login_error'] = None
                            st.rerun()
                        else:
                            st.error("Invalid Admin Credentials!")
                    else:
                        st.error("Invalid Admin Credentials!")
                except Exception as err:
                    # Database error me bhi Master Fallback active rahega
                    st.error("Invalid Admin Credentials!")
            else:
                st.error("Invalid Admin Credentials!")

def logout_user():
    st.session_state.clear()
    st.rerun()
