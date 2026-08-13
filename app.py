import streamlit as st

# 1. Page Configuration (पूरे ऐप में केवल एक बार सबसे ऊपर होना चाहिए)
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

# 3. Session State Initialization
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 4. Auth & Navigation Logic
if not st.session_state['authenticated']:
    # अगर यूजर लॉगिन नहीं है तो केवल लॉगिन पेज दिखाएं
    render_login_page()
else:
    # यूज़र की डिटेल्स और रोल निकालें
    user_role = st.session_state.get('user_role', 'teacher')
    user_email = st.session_state.get('user_email', '')

    # Sidebar Header
    st.sidebar.title("🏫 Campus ERP Pro")
    st.sidebar.write(f"👤 **{user_email}** ({user_role.capitalize()})")
    st.sidebar.markdown("---")

    # रोल के अनुसार साइडबार मेनू के विकल्प
    if user_role == "admin":
        menu_options = [
            "📊 Dashboard", 
            "👨‍🎓 Student Directory", 
            "📅 Attendance Register", 
            "💳 Fee Management", 
            "📝 Exam & Marks",
            "⚙️ Admin Control Panel"
        ]
    else:
        # Teacher Role को केवल जरूरी एक्सेस
        menu_options = [
            "📅 Attendance Register", 
            "📝 Exam & Marks"
        ]

    # Single Sidebar Radio Menu (एक ही जगह)
    menu = st.sidebar.radio("Navigation Menu", menu_options, key="main_erp_navigation")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout_user()

    # Page Rendering Logic
    if menu == "📊 Dashboard":
        st.title("📊 School Overview Dashboard")
        st.info("Welcome to Campus ERP Pro! Select a module from the sidebar.")

    elif menu == "👨‍🎓 Student Directory":
        render_students_module()

    elif menu == "📅 Attendance Register":
        render_attendance_module()

    elif menu == "💳 Fee Management":
        render_fees_module()

    elif menu == "📝 Exam & Marks":
        render_exams_module()

    elif menu == "⚙️ Admin Control Panel":
        st.title("⚙️ Admin Control Panel")
        st.info("System settings and user management controls go here.")
        import streamlit as st

st.set_page_config(page_title="Campus ERP Pro", page_icon="🏫", layout="wide")

from modules.auth import render_login_page, logout_user
from modules.students import render_students_module
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module
from modules.exams import render_exams_module

# Session state Check
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    render_login_page()
else:
    user_role = st.session_state.get('user_role', 'admin')
    user_email = st.session_state.get('user_email', '')

    st.sidebar.title("🏫 Campus ERP Pro")
    st.sidebar.write(f"👤 **{user_email}** ({user_role.capitalize()})")
    st.sidebar.markdown("---")

    menu_options = [
        "📊 Dashboard", 
        "👨‍🎓 Student Directory", 
        "📅 Attendance Register", 
        "💳 Accounting & Fees", 
        "📝 Exam & Marks"
    ]

    menu = st.sidebar.radio("Navigation Menu", menu_options, key="main_erp_navigation")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout_user()

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
