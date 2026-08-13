import streamlit as st

# 1. Page Config (यह पूरे ऐप में सबसे ऊपर केवल एक बार रहेगा)
st.set_page_config(
    page_title="Campus ERP Pro", 
    page_icon="🏫", 
    layout="wide"
)

# 2. Imports (आपके सभी पुराने मॉड्यूल्स)
from modules.auth import render_login_page, logout_user
from modules.students import render_students_module
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module
from modules.exams import render_exams_module

# -----------------------------------------------------------
# NEW: MAIN DASHBOARD COMPONENT (आपका डिज़ाइनर डैशबोर्ड)
# -----------------------------------------------------------
def render_main_dashboard():
    # Header & Logo
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("https://via.placeholder.com/150", width=120)
        
    with col_title:
        st.title("🏫 Campus ERP Pro")
        st.caption("📍 Address: Near Bus Stand, Main Road, City Center - 344032")
        st.markdown("**Contact:** +91 98765 43210 | **Email:** support@campuserp.com")

    st.markdown("---")

    # Quick Stats
    st.subheader("📊 School Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="👨‍🎓 Total Students", value="1,250", delta="+12 this month")
    m2.metric(label="👨‍🏫 Teaching Staff", value="48", delta="Active")
    m3.metric(label="💰 Fee Collection", value="₹ 4.2 Lakhs", delta="85% Paid")
    m4.metric(label="📝 Active CBT Exams", value="3 Live Tests")

    st.markdown("---")

    # Quick Actions Grid
    st.subheader("🚀 Quick Actions")
    q1, q2, q3 = st.columns(3)
    
    with q1:
        st.info("🎒 **New Student Admission**\n\nRegister new students and assign classes.")
    with q2:
        st.success("💳 **Collect School Fee**\n\nGenerate fee receipts and manage dues.")
    with q3:
        st.warning("🎯 **Launch CBT Exam**\n\nAssign online test papers and view result.")

    st.write("")
    st.write("")
    st.markdown("---")

    # Developer Footer
    st.markdown("""
        <style>
            .footer {
                background-color: #f1f5f9;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                color: #475569;
                font-size: 14px;
                margin-top: 30px;
                border-top: 2px solid #cbd5e1;
            }
        </style>
        <div class="footer">
            <p>💻 <b>Designed & Developed by:</b> Your Name / Company Name</p>
            <p>📍 <b>Office:</b> IT Park, Tech City, India | 📞 <b>Dev Support:</b> +91 98765 43210</p>
            <p>© 2026 Campus ERP Pro. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)


# 3. Session State Init
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 4. Auth Gatekeeper
if not st.session_state['authenticated']:
    render_login_page()
else:
    # यूज़र डेटा निकालें
    user_role = st.session_state.get('user_role', 'admin')
    user_email = st.session_state.get('user_email', '')

    # Sidebar UI Controls
    with st.sidebar:
        st.title("🏫 Campus ERP Pro")
        st.write(f"👤 **{user_email}** ({user_role.capitalize()})")
        st.markdown("---")

        # रोल अनुसार नेविगेशन ऑप्शंस
        if user_role == "admin":
            menu_options = [
                "📊 Dashboard", 
                "👨‍🎓 Student Directory", 
                "📅 Attendance Register", 
                "💳 Accounting & Fees", 
                "📝 Exam & Marks"
            ]
        else:
            menu_options = [
                "📅 Attendance Register", 
                "📝 Exam & Marks"
            ]

        # SINGLE Radio Widget
        menu = st.radio(
            "Navigation Menu", 
            menu_options, 
            key="campus_erp_nav_menu_unique"
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout_main"):
            logout_user()

    # 5. Page Routing
    if menu == "📊 Dashboard":
        # अब पुराना st.info हटाकर पूरा डिज़ाइनर डैशबोर्ड रेंडर होगा
        render_main_dashboard()

    elif menu == "👨‍🎓 Student Directory":
        render_students_module()

    elif menu == "📅 Attendance Register":
        render_attendance_module()

    elif menu == "💳 Accounting & Fees":
        render_fees_module()

    elif menu == "📝 Exam & Marks":
        render_exams_module()
