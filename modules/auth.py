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
    # Custom CSS Header and UI Styling
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
        
        portal_mode = st.radio("Select Portal Mode", ["Admin / Teacher", "Student Portal"], horizontal=True)

        with st.form("login_form"):
            user_input = st.text_input("Admin Username / Email", placeholder="anandnehra08 or admin@school.com")
            password = st.text_input("Admin Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("🚀 Sign In", use_container_width=True)

            if submit:
                clean_input = user_input.strip().lower()
                clean_pass = password.strip()

                if not clean_input or not clean_pass:
                    st.warning("⚠️ कृपया यूजरनेम/ईमेल और पासवर्ड दर्ज करें।")
                elif not supabase:
                    st.error("❌ Supabase डेटाबेस से संपर्क नहीं हो पा रहा है।")
                else:
                    try:
                        # 1. First check in 'users' table (Search by email OR username)
                        res = supabase.table("users").select("*").or_(f"email.eq.{clean_input},username.eq.{clean_input}").execute()
                        matched_users = res.data or []

                        # 2. Fallback: Check in 'admins' table
                        if not matched_users:
                            res_admin = supabase.table("admins").select("*").or_(f"username.eq.{clean_input},email.eq.{clean_input}").execute()
                            matched_users = res_admin.data or []

                        if not matched_users:
                            st.error("Invalid Admin Credentials!")
                        else:
                            user = matched_users[0]
                            db_password = str(user.get("password", "")).strip()

                            # Password Match Check (Hash vs Plain Text)
                            is_valid = False
                            if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
                                is_valid = verify_password(clean_pass, db_password)
                            else:
                                is_valid = (clean_pass == db_password)
                                if is_valid:
                                    # Auto-encrypt plain password to hash in DB for security
                                    try:
                                        new_hash = hash_password(clean_pass)
                                        target_table = "users" if "email" in user else "admins"
                                        supabase.table(target_table).update({"password": new_hash}).eq("id", user["id"]).execute()
                                    except Exception:
                                        pass

                            if is_valid:
                                st.session_state['logged_in'] = True
                                st.session_state['authenticated'] = True
                                st.session_state['user_email'] = user.get('email') or user.get('username') or clean_input
                                st.session_state['user_name'] = user.get('name', user.get('username', 'Admin'))
                                st.session_state['user_role'] = user.get('role', 'admin')
                                
                                st.success("✅ लॉगिन सफल!")
                                st.rerun()
                            else:
                                st.error("Invalid Admin Credentials!")

                    except Exception as err:
                        st.error(f"❌ लॉगिन एरर: {err}")

def logout_user():
    st.session_state.clear()
    st.rerun()
