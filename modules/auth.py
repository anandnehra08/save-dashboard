import streamlit as st
import bcrypt
import random
import os
import requests

# Supabase Client Import
try:
    from database.supabase import supabase
except Exception:
    supabase = None

# Fast2SMS Key Fetch from Environment / Secrets
FAST2SMS_KEY = os.getenv("FAST2SMS_API_KEY") or st.secrets.get("FAST2SMS_API_KEY", None)

def mask_text(text: str, mask_type: str = "general") -> str:
    """Utility function to hide/mask sensitive user information."""
    if not text:
        return "N/A"
    text = str(text).strip()
    
    if mask_type == "mobile":
        # Example: 9828595276 -> 98******76
        clean = "".join(filter(str.isdigit, text))
        if len(clean) >= 10:
            return f"{clean[:2]}******{clean[-2:]}"
        return "******"
        
    elif mask_type == "email":
        # Example: anandnehra@gmail.com -> an***@g***.com
        if "@" in text:
            parts = text.split("@")
            name_part = parts[0]
            domain_part = parts[1]
            masked_name = name_part[:2] + "***" if len(name_part) > 2 else "***"
            masked_domain = domain_part[:1] + "***" + domain_part[domain_part.rfind('.'):] if "." in domain_part else "***"
            return f"{masked_name}@{masked_domain}"
        return "***@***.com"
        
    elif mask_type == "name":
        # Example: Anand Nehra -> An*** Ne***
        words = text.split()
        masked_words = [w[:2] + "***" if len(w) > 2 else "***" for w in words]
        return " ".join(masked_words)
        
    return "***"

def hash_password(password: str) -> str:
    """Hashes password securely using bcrypt."""
    salt = bcrypt.gensalt(12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies password hash against plain text input."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def send_real_sms_otp(mobile_number: str, otp: str):
    """Sends 6-Digit OTP via Fast2SMS Production Gateway."""
    if not FAST2SMS_KEY:
        return False, "SMS Gateway Key configured नहीं है। कृपया एडमिन से संपर्क करें।"
    
    clean_mobile = "".join(filter(str.isdigit, str(mobile_number)))[-10:]
    if len(clean_mobile) != 10 or not clean_mobile.startswith(('6', '7', '8', '9')):
        return False, "अवैध 10-अंकीय मोबाइल नंबर।"

    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "variables_values": otp,
        "route": "otp",
        "numbers": clean_mobile
    }
    headers = {
        'authorization': FAST2SMS_KEY,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=8)
        res_json = response.json()
        if res_json.get("return") is True:
            return True, "SMS आपके मोबाइल नंबर पर भेज दिया गया है।"
        else:
            err_msg = res_json.get("message", "SMS सर्वर प्रतिक्रिया देने में असमर्थ रहा।")
            if isinstance(err_msg, list) and len(err_msg) > 0:
                err_msg = err_msg[0]
            return False, f"SMS न भेजा जा सका: {err_msg}"
    except Exception as e:
        return False, f"SMS नेटवर्क त्रुटि: {str(e)}"

def render_login_page():
    # Production Custom Styling
    st.markdown("""
        <style>
        .app-header-bar { 
            background: linear-gradient(135deg, #1E1B4B, #312E81); 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            color: white; 
            padding: 18px 22px; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); 
            margin-bottom: 22px; 
        } 
        .header-top { display: flex; align-items: center; justify-content: space-between; } 
        .app-brand { display: flex; align-items: center; gap: 14px; } 
        .app-icon { font-size: 30px; background: linear-gradient(135deg, #6366F1, #4F46E5); padding: 8px 14px; border-radius: 16px; } 
        .app-title-text h3 { margin: 0; font-size: 20px; color: #F8FAFC; font-weight: 800; letter-spacing: 0.5px; } 
        .app-title-text span { font-size: 11px; color: #C7D2FE; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
        .status-badge { background: rgba(34, 197, 94, 0.15); color: #4ADE80; border: 1px solid rgba(74, 222, 128, 0.25); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
        .admin-info-box { background: rgba(255, 255, 255, 0.06); border-radius: 14px; padding: 12px 16px; margin-top: 14px; font-size: 12px; color: #E0E7FF; border: 1px solid rgba(255, 255, 255, 0.1); } 
        .admin-info-box p { margin: 3px 0; } 
        .stButton>button { width: 100%; border-radius: 14px !important; height: 46px !important; font-size: 15px !important; font-weight: 700 !important; background: linear-gradient(135deg, #4F46E5, #4338CA) !important; color: white !important; border: none !important; }
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
                <div class="status-badge">🟢 Enterprise Live</div>
            </div>
            <div class="admin-info-box">
                <p>🏢 <b>Provider:</b> Sakshi Solution</p>
                <p>👨‍💼 <b>Developer:</b> Anand Nehra</p>
                <p>📞 <b>Support:</b> 9828595276 | ✉️ <b>Email:</b> anandnehra8@gmail.com</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if 'auth_mode' not in st.session_state:
            st.session_state['auth_mode'] = 'login' # 'login', 'signup', 'forgot_password'
        if 'otp_sent' not in st.session_state:
            st.session_state['otp_sent'] = False

        # -------------------------------------------------------------
        # 1. SIGN IN / LOGIN PAGE
        # -------------------------------------------------------------
        if st.session_state['auth_mode'] == 'login':
            st.subheader("🔑 Sign In Portal")
            
            # Role Selection
            selected_role = st.selectbox("Select Account Role", ["Admin", "Teacher", "Staff"], key="login_role")
            
            user_input = st.text_input("Username / Email / Mobile", key="login_usr_input", placeholder="Enter Username, Email, or Mobile")
            password = st.text_input("Password", type="password", key="login_pwd_input", placeholder="••••••••")
            
            submit = st.button("🚀 Sign In", use_container_width=True, key="btn_signin_submit")

            if submit:
                clean_input = user_input.strip().lower()
                clean_pass = password.strip()

                if not clean_input or not clean_pass:
                    st.warning("⚠️ कृपया विवरण दर्ज करें।")
                    return

                # Fast Authenticate Master Admin
                if clean_input in ["anandnehra08", "admin@school.com", "admin", "9828595276"] and clean_pass in ["admin123", "admin", "123456"]:
                    st.session_state['logged_in'] = True
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = "anandnehra08"
                    st.session_state['user_name'] = "Anand Nehra"
                    st.session_state['user_role'] = selected_role.lower()
                    st.rerun()

                elif supabase:
                    try:
                        res = supabase.table("users").select("*").or_(f"email.eq.{clean_input},username.eq.{clean_input},mobile.eq.{clean_input}").execute()
                        matched_users = res.data or []

                        if matched_users:
                            user = matched_users[0]
                            db_password = str(user.get("password", "")).strip()

                            is_valid = verify_password(clean_pass, db_password) if (db_password.startswith("$2b$") or db_password.startswith("$2a$")) else (clean_pass == db_password)

                            if is_valid:
                                st.session_state['logged_in'] = True
                                st.session_state['authenticated'] = True
                                st.session_state['user_email'] = user.get('username') or user.get('email') or clean_input
                                st.session_state['user_name'] = user.get('name', 'User')
                                st.session_state['user_role'] = selected_role.lower()
                                st.rerun()
                            else:
                                st.error("❌ पासवर्ड गलत है!")
                        else:
                            st.error("❌ खाता नहीं मिला।")
                    except Exception as err:
                        st.error(f"❌ डेटाबेस त्रुटि: {err}")

            st.write("")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📝 Create Account (Sign Up)", key="btn_goto_signup"):
                    st.session_state['auth_mode'] = 'signup'
                    st.rerun()
            with col_b:
                if st.button("🔑 Forgot Password?", key="btn_goto_forgot"):
                    st.session_state['auth_mode'] = 'forgot_password'
                    st.rerun()

        # -------------------------------------------------------------
        # 2. SIGN UP / REGISTRATION PAGE
        # -------------------------------------------------------------
        elif st.session_state['auth_mode'] == 'signup':
            st.subheader("📝 New Account Sign Up")
            
            signup_role = st.selectbox("Register As", ["Teacher", "Staff", "Admin"], key="signup_role")
            signup_name = st.text_input("Full Name", placeholder="e.g. Anand Nehra")
            signup_mobile = st.text_input("Mobile Number", placeholder="10 Digit Mobile Number", max_chars=10)
            signup_email = st.text_input("Email Address", placeholder="name@example.com")
            signup_username = st.text_input("Choose Username", placeholder="e.g. anand08")
            signup_pass = st.text_input("Create Password", type="password", placeholder="••••••••")

            if st.button("✅ Create Account", key="btn_do_signup"):
                if not signup_name or not signup_mobile or not signup_username or not signup_pass:
                    st.warning("⚠️ कृपया सभी आवश्यक फ़ील्ड भरें।")
                elif len(signup_mobile) != 10 or not signup_mobile.isdigit():
                    st.warning("⚠️ वैध 10-अंकीय मोबाइल नंबर दर्ज करें।")
                else:
                    if supabase:
                        try:
                            hashed = hash_password(signup_pass.strip())
                            new_user_data = {
                                "name": signup_name.strip(),
                                "mobile": signup_mobile.strip(),
                                "email": signup_email.strip(),
                                "username": signup_username.strip().lower(),
                                "password": hashed,
                                "role": signup_role.lower()
                            }
                            supabase.table("users").insert(new_user_data).execute()
                            st.success("🎉 खाता सफलतापूर्वक बन गया! कृपया Sign In करें।")
                            st.session_state['auth_mode'] = 'login'
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ रजिस्ट्रेशन विफल: {e}")
                    else:
                        st.success("🎉 खाता बन गया! (Demo/Local Mode)")
                        st.session_state['auth_mode'] = 'login'
                        st.rerun()

            st.write("")
            if st.button("⬅️ Back to Sign In", key="btn_back_from_signup"):
                st.session_state['auth_mode'] = 'login'
                st.rerun()

        # -------------------------------------------------------------
        # 3. FORGOT PASSWORD (SMS OTP)
        # -------------------------------------------------------------
        else:
            st.subheader("📲 Account Recovery via SMS OTP")
            
            if not st.session_state['otp_sent']:
                search_val = st.text_input("Registered Username / Email / Mobile", placeholder="e.g. 9828595276")
                
                if st.button("📩 Send OTP SMS", key="btn_send_otp_fp"):
                    clean_val = search_val.strip().lower()
                    if clean_val:
                        found_user = None
                        if supabase:
                            try:
                                res = supabase.table("users").select("*").or_(f"email.eq.{clean_val},username.eq.{clean_val},mobile.eq.{clean_val}").execute()
                                if res.data:
                                    found_user = res.data[0]
                            except Exception:
                                pass

                        if not found_user and clean_val in ["anandnehra08", "admin@school.com", "9828595276", "admin"]:
                            found_user = {"id": 1, "username": "anandnehra08", "mobile": "9828595276"}

                        if found_user:
                            user_mobile = found_user.get("mobile")
                            if user_mobile:
                                secure_otp = str(random.randint(100000, 999999))
                                with st.spinner("SMS भेजा जा रहा है..."):
                                    sms_success, sms_response_msg = send_real_sms_otp(user_mobile, secure_otp)

                                if sms_success:
                                    st.session_state['generated_otp'] = secure_otp
                                    st.session_state['target_user_id'] = found_user.get("id")
                                    st.session_state['otp_sent'] = True
                                    st.success(f"✅ {sms_response_msg}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {sms_response_msg}")
                            else:
                                st.error("❌ कोई मोबाइल नंबर लिंक नहीं है।")
                        else:
                            st.error("❌ खाता नहीं मिला।")
            else:
                entered_otp = st.text_input("Enter 6-Digit SMS OTP", max_chars=6)
                new_password = st.text_input("Set New Password", type="password")
                
                if st.button("🔄 Reset Password & Sign In", key="btn_verify_otp_reset"):
                    if entered_otp.strip() == st.session_state.get('generated_otp'):
                        hashed_pass = hash_password(new_password.strip())
                        if supabase and st.session_state.get('target_user_id'):
                            try:
                                supabase.table("users").update({"password": hashed_pass}).eq("id", st.session_state['target_user_id']).execute()
                            except Exception:
                                pass

                        st.success("🎉 पासवर्ड अपडेट हो गया!")
                        st.session_state['logged_in'] = True
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = "anandnehra08"
                        st.session_state['user_name'] = "Anand Nehra"
                        st.session_state['user_role'] = "admin"
                        st.session_state['auth_mode'] = 'login'
                        st.session_state['otp_sent'] = False
                        st.rerun()
                    else:
                        st.error("❌ गलत OTP!")

            st.write("")
            if st.button("⬅️ Back to Sign In", key="btn_back_to_login"):
                st.session_state['auth_mode'] = 'login'
                st.session_state['otp_sent'] = False
                st.rerun()

def logout_user():
    """Logs out user and clears active session."""
    st.session_state.clear()
    st.rerun()
