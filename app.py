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
