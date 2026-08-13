import streamlit as st

# 1. Page Config (यह पूरे ऐप में सबसे ऊपर केवल एक बार रहेगा)
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

        # SINGLE Radio Widget (Duplicate Key Error रोकने के लिए)
        menu = st.radio(
            "Navigation Menu", 
            menu_options, 
            key="campus_erp_nav_menu_unique"
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout_main"):
            logout_user()

    # Page Routing
    if menu == "📊 Dashboard":
        st.title("📊 School Overview Dashboard")
        st.info("Welcome to Campus ERP Pro! Select a module from the sidebar.")

    elif menu == "👨‍🎓 Student Directory":
        render_students_module()

    elif menu == "📅 Attendance Register":
        render_attendance_module()

    elif menu == "💳 Accounting & Fees":
        render_fees_module()

    elif menu == "📝 Exam & Marks":
        render_exams_module()
