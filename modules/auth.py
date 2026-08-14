import streamlit as st
import random

# नकली SMS OTP भेजने का फ़ंक्शन (यहाँ अपना SMS API / Supabase SMS जोड़ें)
def send_otp_to_mobile(mobile_number):
    otp = str(random.randint(1000, 9999))
    st.session_state['generated_otp'] = otp
    st.session_state['reset_mobile'] = mobile_number
    
    # Fast2SMS / Twilio API कॉल यहाँ होगी
    # example: requests.post("https://api.sms.com/send", data={"to": mobile_number, "otp": otp})
    
    st.success(f"📱 OTP सफलतापूर्वक आपके मोबाइल नंबर {mobile_number} पर भेज दिया गया है!")
    # (टेस्टिंग के लिए स्क्रीन पर दिखा रहे हैं, प्रोडक्शन में इसे हटा दें)
    st.info(f"🔑 Demo OTP: {otp}")

def render_login_page():
    st.title("🏫 Campus ERP Pro - Login")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📲 Forgot / Reset Password"])
    
    # ---------------- TAB 1: LOGIN ----------------
    with tab1:
        with st.form("login_form"):
            email = st.text_input("User ID / Email / Mobile")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                # यहाँ Supabase/Database से रोल, क्लास और सब्जेक्ट फ़ेच करें
                if email == "admin@school.com" and password == "admin123":
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = email
                    st.session_state['user_role'] = 'admin'
                    st.session_state['assigned_class'] = "ALL"
                    st.session_state['assigned_subjects'] = ["ALL"]
                    st.rerun()
                elif email == "teacher@school.com" and password == "teacher123":
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = email
                    st.session_state['user_role'] = 'class_teacher'  # या 'subject_teacher'
                    st.session_state['assigned_class'] = "Class 10-A"
                    st.session_state['assigned_subjects'] = ["Maths", "Science"]
                    st.rerun()
                else:
                    st.error("❌ गलत ID या पासवर्ड!")

    # ---------------- TAB 2: FORGOT PASSWORD (OTP) ----------------
    with tab2:
        st.subheader("🔑 Password Reset via Mobile OTP")
        
        step = st.session_state.get('reset_step', 1)
        
        if step == 1:
            mobile = st.text_input("अपना रजिस्टर मोबाइल नंबर दर्ज करें:")
            if st.button("📲 Send OTP"):
                if len(mobile) >= 10:
                    send_otp_to_mobile(mobile)
                    st.session_state['reset_step'] = 2
                    st.rerun()
                else:
                    st.error("कृपया सही 10 अंकों का मोबाइल नंबर डालें।")
                    
        elif step == 2:
            st.info(f"मोबाइल नंबर: {st.session_state.get('reset_mobile')}")
            user_otp = st.text_input("4-अंकों का OTP दर्ज करें:", max_chars=4)
            
            if st.button("Verify OTP"):
                if user_otp == st.session_state.get('generated_otp'):
                    st.success("✅ OTP सत्यापित हो गया!")
                    st.session_state['reset_step'] = 3
                    st.rerun()
                else:
                    st.error("❌ गलत OTP, पुनः प्रयास करें।")
                    
        elif step == 3:
            new_pass = st.text_input("नया पासवर्ड (New Password):", type="password")
            confirm_pass = st.text_input("पासवर्ड की पुष्टि करें:", type="password")
            
            if st.button("💾 Reset Password"):
                if new_pass and new_pass == confirm_pass:
                    # DB में पासवर्ड अपडेट का कोड यहाँ आएगा
                    st.success("🎉 पासवर्ड सफलतापूर्वक बदल दिया गया है! अब लॉगिन करें।")
                    st.session_state['reset_step'] = 1
                else:
                    st.error("❌ पासवर्ड मैच नहीं हो रहे हैं।")


def logout_user():
    st.session_state['authenticated'] = False
    st.session_state['user_role'] = None
    st.rerun()
