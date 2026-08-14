import streamlit as st
from modules.auth import render_login_page, logout_user
from modules.attendance import render_attendance_module
from modules.exams import render_exams_module
from modules.student_dashboard import render_student_dashboard

# Streamlit Page Config
st.set_page_config(page_title="School Portal", layout="wide")

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Router Logic
if not st.session_state['logged_in']:
    render_login_page()
else:
    # Sidebar Profile Info
    st.sidebar.title(f"👤 {st.session_state.get('user_email', 'User')}")
    st.sidebar.caption(f"Role: **{st.session_state.get('user_role', 'Admin')}**")
    
    if st.sidebar.button("🔒 Logout", use_container_width=True):
        logout_user()

    st.sidebar.write("---")
    menu = st.sidebar.radio("Navigation", ["🎓 Student Portal", "📅 Attendance", "📝 Exams & Marks"])
    
    if menu == "🎓 Student Portal":
        render_student_dashboard()
    elif menu == "📅 Attendance":
        render_attendance_module()
    elif menu == "📝 Exams & Marks":
        render_exams_module()
