import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Campus ERP Pro", 
    page_icon="🏫", 
    layout="wide"
)

# 2. Imports
from modules.auth import render_login_page, logout_user
from modules.students import render_students_module
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module
from modules.exams import render_exams_module

# -----------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "📊 Dashboard"

# Quick Navigation Function (बटन पर क्लिक करने पर यही चलेगा)
def navigate_to(page_name):
    st.session_state["nav_page"] = page_name

# -----------------------------------------------------------
# MAIN DASHBOARD COMPONENT
# -----------------------------------------------------------
def render_main_dashboard():
    # Header
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.markdown("## 🏫")
        
    with col_title:
        st.title("Campus ERP Pro")
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

    # Quick Actions Grid (वर्किंग on_click कॉल बैक के साथ)
    st.subheader("🚀 Quick Actions")
    q1, q2, q3 = st.columns(3)
    
    with q1:
        st.info("🎒 **Student Directory & Admission**\n\nRegister new students and view directory.")
        st.button(
            "Go to Student Directory ➡️", 
            key="qa_btn_student", 
            use_container_width=True,
            on_click=navigate_to, 
            args=("👨‍🎓 Student Directory",)
        )

    with q2:
        st.success("💳 **Collect School Fee**\n\nGenerate fee receipts and manage dues.")
        st.button(
            "Go to Fees & Accounting ➡️", 
            key="qa_btn_fee", 
            use_container_width=True,
            on_click=navigate_to, 
            args=("💳 Accounting & Fees",)
        )

    with q3:
        st.warning("🎯 **Launch CBT Exam**\n\nAssign online test papers and view result.")
        st.button(
            "Go to Exam & Marks ➡️", 
            key="qa_btn_exam", 
            use_container_width=True,
            on_click=navigate_to, 
            args=("📝 Exam & Marks",)
        )

    st.write("")
    st.write("")
    st.markdown("---")

    # Footer
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
            <p>💻 <b>Designed & Developed by:</b> Campus ERP Team</p>
            <p>📍 <b>Office:</b> IT Park, Tech City, India | 📞 <b>Dev Support:</b> +91 98765 43210</p>
            <p>© 2026 Campus ERP Pro. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------
# MAIN AUTH & ROUTING GATEKEEPER
# -----------------------------------------------------------
if not st.session_state.get('logged_in', False) and not st.session_state.get('authenticated', False):
    render_login_page()
else:
    user_role = st.session_state.get('user_role', 'admin')
    user_email = st.session_state.get('user_email', '')

    # Sidebar UI Controls
    with st.sidebar:
        st.title("🏫 Campus ERP Pro")
        st.write(f"👤 **{user_email}** ({user_role.capitalize()})")
        st.markdown("---")

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

        # Sync active index
        current_active = st.session_state.get("nav_page", "📊 Dashboard")
        default_idx = menu_options.index(current_active) if current_active in menu_options else 0

        # Callback function for sidebar radio
        def update_from_radio():
            st.session_state["nav_page"] = st.session_state["sidebar_menu_radio"]

        st.radio(
            "Navigation Menu", 
            menu_options, 
            index=default_idx,
            key="sidebar_menu_radio",
            on_change=update_from_radio
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout_main"):
            logout_user()

    # Routing based on session state
    target_page = st.session_state["nav_page"]

    if target_page == "📊 Dashboard":
        render_main_dashboard()

    elif target_page == "👨‍🎓 Student Directory":
        render_students_module()

    elif target_page == "📅 Attendance Register":
        render_attendance_module()

    elif target_page == "💳 Accounting & Fees":
        render_fees_module()

    elif target_page == "📝 Exam & Marks":
        render_exams_module()
