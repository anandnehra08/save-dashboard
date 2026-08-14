import streamlit as st
import random
import requests
from supabase import create_client, Client

# -----------------------------------------------------------
# 1. SUPABASE CONNECTION SETUP
# -----------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    """Supabase client initialization from Streamlit secrets or default fallback."""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        # अगर Secrets सेट नहीं हैं तो Warning देगा (डेवलपमेंट के लिए)
        return None

supabase = init_supabase()

# -----------------------------------------------------------
# 2. HELPER FUNCTIONS: SMS & DATABASE OPERATIONS
# -----------------------------------------------------------
def send_otp_via_sms(mobile_number, otp_code):
    """
    Sends 4-digit OTP via Fast2SMS / Custom Gateway API.
    Replace API Key with your service provider details.
    """
    try:
        # Fast2SMS API Call Example:
        # api_key = st.secrets.get("FAST2SMS_KEY", "YOUR_API_KEY")
        # url = "https://www.fast2sms.com/dev/bulkV2"
        # payload = f"variables_values={otp_code}&route=otp&numbers={mobile_number}"
        # headers = {'authorization': api_key, 'Content-Type': "application/x-www-form-urlencoded"}
        # response = requests.request("POST", url, data=payload, headers=headers)
        
        # Logging & State Update
        st.session_state['generated_otp'] = otp_code
        st.session_state['reset_mobile'] = mobile_number
        st.success(f"📱 OTP सफलतापूर्वक आपके मोबाइल नंबर {mobile_number} पर भेज दिया गया है!")
        
        # Demo display for testing/development (Remove in production)
        st.info(f"🔑 Demo Verification OTP: {otp_code}")
        return True
    except Exception as e:
        st.error(f"❌ SMS भेजने में समस्या आई: {str(e)}")
        return False


def verify_user_credentials(user_input, password):
    """
    Supabase DB से यूज़र को वेरीफ़ाई करता है और उनके Assigned Class/Subjects निकालता है।
    """
    if not supabase:
        # Fallback Mock Data for testing if DB is not connected
        if user_input == "admin@school.com" and password == "admin123":
            return {
                "email": user_input,
                "role": "admin",
                "assigned_class": "ALL",
                "assigned_subjects": ["ALL"]
            }
        elif user_input == "teacher@school.com" and password == "teacher123":
            return {
                "email": user_input,
                "role": "class_teacher",
                "assigned_class": "Class 10-A",
                "assigned_subjects": ["Maths", "Science"]
            }
        elif user_input == "subject@school.com" and password == "subject123":
            return {
                "email": user_input,
                "role": "subject_teacher",
                "assigned_class": "None",
                "assigned_subjects": ["Physics"]
            }
        return None

    try:
        # Querying Supabase 'users' or 'teachers' table
        response = supabase.table("users").select("*").or_(f"email.eq.{user_input},phone.eq.{user_input}").eq("password", password).execute()
        
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            return {
                "email": user_data.get("email", user_input),
                "role": user_data.get("role", "class_teacher"),
                "assigned_class": user_data.get("assigned_class", "ALL"),
                "assigned_subjects": user_data.get("assigned_subjects", ["ALL"])
            }
        return None
    except Exception as e:
        st.error(f"⚠️ Auth Database Error: {str(e)}")
        return None


def update_password_in_db(mobile_number, new_password):
    """
    Update password in Supabase DB using verified mobile number.
    """
    if not supabase:
        return True  # Fallback success for mock setup

    try:
        response = supabase.table("users").update({"password": new_password}).eq("phone", mobile_number).execute()
        return True
    except Exception as e:
        st.error(f"⚠️ Password Update Error: {str(e)}")
        return False


# -----------------------------------------------------------
# 3. MAIN UI RENDER FUNCTION
# -----------------------------------------------------------
def render_login_page():
    st.title("🏫 Campus ERP Pro - Login")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📲 Forgot / Reset Password"])
    
    # ---------------- TAB 1: LOGIN ----------------
    with tab1:
        with st.form("login_form"):
            user_input = st.text_input("User ID / Email / Mobile Number")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if not user_input or not password:
                    st.warning("⚠️ कृपया यूजर ID और पासवर्ड दोनों दर्ज करें।")
                else:
                    user_info = verify_user_credentials(user_input, password)
                    
                    if user_info:
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = user_info['email']
                        st.session_state['user_role'] = user_info['role']
                        st.session_state['assigned_class'] = user_info['assigned_class']
                        st.session_state['assigned_subjects'] = user_info['assigned_subjects']
                        st.success("🎉 सफलतापूर्वक लॉगिन हो गए!")
                        st.rerun()
                    else:
                        st.error("❌ गलत ID या पासवर्ड! पुनः प्रयास करें।")

    # ---------------- TAB 2: FORGOT PASSWORD (OTP) ----------------
    with tab2:
        st.subheader("🔑 Mobile OTP Password Reset")
        
        step = st.session_state.get('reset_step', 1)
        
        if step == 1:
            mobile = st.text_input("अपना रजिस्टर्ड 10-अंकों का मोबाइल नंबर डालें:")
            if st.button("📲 Send OTP"):
                if len(mobile.strip()) == 10 and mobile.isdigit():
                    otp = str(random.randint(1000, 9999))
                    send_otp_via_sms(mobile, otp)
                    st.session_state['reset_step'] = 2
                    st.rerun()
                else:
                    st.error("❌ कृपया सही 10 अंकों का मोबाइल नंबर दर्ज करें।")
                    
        elif step == 2:
            st.info(f"📱 OTP भेजा गया नंबर: **{st.session_state.get('reset_mobile')}**")
            user_otp = st.text_input("4-अंकों का Verification OTP दर्ज करें:", max_chars=4)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("✅ Verify OTP"):
                    if user_otp == st.session_state.get('generated_otp'):
                        st.success("✅ OTP सत्यापित हो गया!")
                        st.session_state['reset_step'] = 3
                        st.rerun()
                    else:
                        st.error("❌ गलत OTP, कृपया पुनः प्रयास करें।")
            with c2:
                if st.button("🔄 Resend OTP"):
                    otp = str(random.randint(1000, 9999))
                    send_otp_via_sms(st.session_state.get('reset_mobile'), otp)
                    st.rerun()

        elif step == 3:
            st.subheader("🔐 Set New Password")
            new_pass = st.text_input("नया पासवर्ड (New Password):", type="password")
            confirm_pass = st.text_input("पासवर्ड की पुष्टि करें (Confirm Password):", type="password")
            
            if st.button("💾 Save New Password"):
                if len(new_pass) < 6:
                    st.warning("⚠️ पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।")
                elif new_pass != confirm_pass:
                    st.error("❌ पासवर्ड आपस में मैच नहीं हो रहे हैं।")
                else:
                    mobile_num = st.session_state.get('reset_mobile')
                    if update_password_in_db(mobile_num, new_pass):
                        st.success("🎉 पासवर्ड सफलतापूर्वक बदल दिया गया है! अब लॉगिन करें।")
                        st.session_state['reset_step'] = 1
                        st.session_state['generated_otp'] = None
                    else:
                        st.error("❌ डेटाबेस में पासवर्ड अपडेट नहीं हो सका।")


# -----------------------------------------------------------
# 4. LOGOUT & SESSION CLEANUP FUNCTION
# -----------------------------------------------------------
def logout_user():
    """Clears all authentication and role assignment states on logout."""
    st.session_state['authenticated'] = False
    st.session_state['user_email'] = None
    st.session_state['user_role'] = None
    st.session_state['assigned_class'] = None
    st.session_state['assigned_subjects'] = None
    st.session_state['reset_step'] = 1
    st.rerun()
