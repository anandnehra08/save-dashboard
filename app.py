import streamlit as st

# Page Configuration (यह हमेशा सबसे ऊपर होना चाहिए)
st.set_page_config(
    page_title="Campus School ERP Pro",
    page_icon="🏫",
    layout="wide"
)

# Modules Import (हमेशा टॉप पर रखना बेहतर प्रैक्टिस है)
from modules.students import render_students_module
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module

# Custom Sidebar Header
st.sidebar.title("🏫 Campus ERP Pro")

# Sidebar Navigation (Unique Key के साथ)
menu = st.sidebar.radio(
    label="Modules Menu",
    options=["Dashboard", "Student Master", "Attendance", "Fee Management", "Examination"],
    key="main_erp_menu"
)

# Navigation Logic
if menu == "Dashboard":
    st.title("📊 School Overview Dashboard")
    st.info("Welcome to Campus School ERP Pro V2! Select a module from the sidebar.")

elif menu == "Student Master":
    render_students_module()

elif menu == "Attendance":
    render_attendance_module()

elif menu == "Fee Management":
    render_fees_module()

elif menu == "Examination":
    st.title("📝 Examination & Marksheets")
    st.info("Exam Module coming soon!")
    import streamlit as st
from modules.auth import render_login_page, logout_user
from modules.students import render_students_module
from modules.attendance import render_attendance_module

st.set_page_config(page_title="Campus ERP Pro", layout="wide")

# Session state इन्शियलाइज़ करें
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# अगर लॉगिन नहीं है तो लॉगिन पेज दिखाएं
if not st.session_state['authenticated']:
    render_login_page()
else:
    # Sidebar Navigation
    user_role = st.session_state.get('user_role', 'teacher')
    user_email = st.session_state.get('user_email', '')
    
    st.sidebar.title("🏫 Campus ERP Pro")
    st.sidebar.write(f"👤 **{user_email}** ({user_role.capitalize()})")
    
    # रोल के अनुसार मेनू विकल्प
    if user_role == "admin":
        menu_options = ["Student Directory", "Attendance Register", "Admin Dashboard"]
    else:
        menu_options = ["Attendance Register"]  # Teacher को केवल अटेंडेंस एक्सेस
        
    menu = st.sidebar.radio("Navigation", menu_options)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout_user()
        
    # Selected Page Render करें
    if menu == "Student Directory":
        render_students_module()
    elif menu == "Attendance Register":
        render_attendance_module()
    elif menu == "Admin Dashboard":
        st.title("⚙️ Admin Control Panel")
        st.info("यहाँ आप सिस्टम सेटिंग्स और यूज़र मैनेजमेंट संभाल सकते हैं।")
