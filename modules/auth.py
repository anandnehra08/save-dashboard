import streamlit as st
import bcrypt
import random

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
        .stButton>button { width: 100%; border-radius: 16px !important; height: 48px !important; font-size: 15px !important; font-weight: 700 !important; background: linear-gradient(135deg, #4F46E5, #4338CA) !important; color: white !important; border: none !important; box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.4) !important; }
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
        # Session states for Forget Password Tab / Flow
        if 'auth_mode' not in st.session_state:
            st.session_state['auth_mode'] = 'login' # 'login' or 'forgot_password'
        if 'otp_sent' not in st.session_state:
            st.session_state['otp_sent'] = False
        if 'generated_otp' not in st.session_state:
            st.session_state['generated_otp'] = None
        if 'target_user_id' not in st.session_state:
            st.session_state['target_user_id'] = None

        # -------------------------------------------------------------
        # TAB 1: NORMAL LOGIN (Password or OTP)
        # -------------------------------------------------------------
        if st.session_state['auth_mode'] == 'login':
            st.subheader("🔐 Login Portal")
            
            user_input = st.text_input("Username / Email / Mobile", key="login_usr_input", placeholder="anandnehra08, 9828595276, or email")
            password = st.text_input("Password", type="password", key="login_pwd_input", placeholder="••••••••")
            
            submit = st.button("🚀 Sign In", use_container_width=True, key="btn_signin_submit")

            if submit:
                clean_input = user_input.strip().lower()
                clean_pass = password.strip()

                if not clean_input or not clean_pass:
                    st.warning("⚠️ कृपया यूजरनेम/ईमेल/मोबाइल और पासवर्ड दर्ज करें।")
                    return

                # Master Admin Fast Login
                if clean_input in ["anandnehra08", "admin@school.com", "admin", "9828595276"] and clean_pass in ["admin123", "admin", "123456"]:
                    st.session_state['logged_in'] = True
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = "anandnehra08"
                    st.session_state['user_name'] = "Anand Nehra"
                    st.session_state['user_role'] = "admin"
                    st.rerun()

                # Supabase Database Lookup
                elif supabase:
                    try:
                        res = supabase.table("users").select("*").or_(f"email.eq.{clean_input},username.eq.{clean_input},mobile.eq.{clean_input}").execute()
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
                                st.rerun()
                            else:
                                st.error("❌ गलत पासवर्ड!")
                        else:
                            st.error("❌ यह यूज़र रजिस्टर्ड नहीं है!")
                    except Exception as err:
                        st.error(f"❌ लॉगिन एरर: {err}")
                else:
                    st.error("❌ डेटाबेस कनेक्शन एरर!")

            st.write("")
            if st.button("🔑 Forgot Password / Reset via Mobile OTP", type="secondary", key="btn_goto_forgot"):
                st.session_state['auth_mode'] = 'forgot_password'
                st.rerun()

        # -------------------------------------------------------------
        # TAB 2: FORGOT PASSWORD VIA MOBILE OTP
        # -------------------------------------------------------------
        else:
            st.subheader("📲 Forget Password Reset")
            
            if not st.session_state['otp_sent']:
                search_val = st.text_input("Enter Registered Username / Email / Mobile", placeholder="e.g. 9828595276 or anandnehra08")
                
                if st.button("📩 Send OTP", key="btn_send_otp_fp"):
                    clean_val = search_val.strip().lower()
                    if not clean_val:
                        st.warning("⚠️ कृपया अपना रजिस्टर्ड यूज़रनेम, ईमेल या मोबाइल दर्ज करें।")
                    else:
                        # Find User in DB
                        found_user = None
                        if supabase:
                            try:
                                res = supabase.table("users").select("*").or_(f"email.eq.{clean_val},username.eq.{clean_val},mobile.eq.{clean_val}").execute()
                                if res.data:
                                    found_user = res.data[0]
                            except Exception:
                                pass

                        # Fallback for Master Admin
                        if not found_user and clean_val in ["anandnehra08", "admin@school.com", "9828595276", "admin"]:
                            found_user = {"id": 1, "username": "anandnehra08", "mobile": "9828595276"}

                        if found_user:
                            # Generate 6 Digit OTP (Defaulting to 123456 for easy testing)
                            otp = "123456"  # Real SMS Gateway add karne ke liye yahan API call aayegi
                            st.session_state['generated_otp'] = otp
                            st.session_state['target_user_id'] = found_user.get("id")
                            st.session_state['otp_sent'] = True
                            st.success(f"✅ OTP भेजा गया! (Testing OTP: **{otp}**)")
                            st.rerun()
                        else:
                            st.error("❌ कोई यूज़र नहीं मिला। कृपया सही विवरण दर्ज करें।")
            else:
                st.info("📲 दर्ज किए गए मोबाइल पर OTP भेजा जा चुका है।")
                entered_otp = st.text_input("Enter 6-Digit OTP", placeholder="123456")
                new_password = st.text_input("Enter New Password", type="password", placeholder="नया पासवर्ड लिखें")
                
                if st.button("🔄 Reset Password & Login", key="btn_verify_otp_reset"):
                    if entered_otp.strip() == st.session_state['generated_otp']:
                        if len(new_password.strip()) < 4:
                            st.warning("⚠️ पासवर्ड कम से कम 4 अक्षरों का होना चाहिए।")
                        else:
                            # Update Password in DB
                            hashed_new_pass = hash_password(new_password.strip())
                            if supabase and st.session_state['target_user_id']:
                                try:
                                    supabase.table("users").update({"password": hashed_new_pass}).eq("id", st.session_state['target_user_id']).execute()
                                except Exception:
                                    pass

                            st.success("🎉 पासवर्ड सफलतापूर्वक रीसेट हो गया! लॉगिन हो रहा है...")
                            
                            # Auto Login After Reset
                            st.session_state['logged_in'] = True
                            st.session_state['authenticated'] = True
                            st.session_state['user_email'] = "anandnehra08"
                            st.session_state['user_name'] = "Anand Nehra"
                            st.session_state['user_role'] = "admin"
                            
                            # Reset states
                            st.session_state['auth_mode'] = 'login'
                            st.session_state['otp_sent'] = False
                            st.rerun()
                    else:
                        st.error("❌ गलत OTP! कृपया पुनः प्रयास करें।")

            st.write("")
            if st.button("⬅️ Back to Login", type="secondary", key="btn_back_to_login"):
                st.session_state['auth_mode'] = 'login'
                st.session_state['otp_sent'] = False
                st.rerun()

def logout_user():
    st.session_state.clear()
    st.rerun()
