import streamlit as st

# --- MODULE IMPORTS ---
from modules.students import render_student_module
from modules.search import render_search_module
from modules.fees import render_fees_module
from modules.attendance import render_attendance_module
from modules.staff import render_staff_module
from modules.exams import render_exams_module
from modules.certificates import render_certificates_module
from modules.cbt import render_cbt_module
from modules.accounts import render_accounts_module
from modules.communication import render_communication_module

st.set_page_config(page_title="Campus School ERP Pro V2", page_icon="🎓", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Campus School ERP Pro V2 - Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "Super Admin"
            st.rerun()
        else:
            st.error("Invalid Credentials!")
    st.stop()

# SIDEBAR NAVIGATION
st.sidebar.title("🎓 Campus ERP V2")
st.sidebar.write(f"👤 **Logged as:** `{st.session_state.role}`")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "1. 📖 Student Admission & SR Register",
        "2. 🔍 Live Student Directory & Search",
        "3. 💰 Fee Management & Receipts",
        "4. 📈 Attendance Register & Analytics",
        "5. 👨‍🏫 Staff & Payroll Directory",
        "6. 📝 Exam Marks Entry & Marksheets",
        "7. 📜 Certificate Generator (TC/Study)",
        "8. 💻 NEET / Board CBT Exam Engine",
        "9. 💼 Accounts Cash Book & Ledger",
        "10. 📱 WhatsApp & Broadcast Portal"
    ]
)

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# MODULE ROUTING
if menu == "1. 📖 Student Admission & SR Register":
    render_student_module()
elif menu == "2. 🔍 Live Student Directory & Search":
    render_search_module()
elif menu == "3. 💰 Fee Management & Receipts":
    render_fees_module()
elif menu == "4. 📈 Attendance Register & Analytics":
    render_attendance_module()
elif menu == "5. 👨‍🏫 Staff & Payroll Directory":
    render_staff_module()
elif menu == "6. 📝 Exam Marks Entry & Marksheets":
    render_exams_module()
elif menu == "7. 📜 Certificate Generator (TC/Study)":
    render_certificates_module()
elif menu == "8. 💻 NEET / Board CBT Exam Engine":
    render_cbt_module()
elif menu == "9. 💼 Accounts Cash Book & Ledger":
    render_accounts_module()
elif menu == "10. 📱 WhatsApp & Broadcast Portal":
    render_communication_module()
    import streamlit as st
from modules.students import render_students_module

st.set_page_config(page_title="Campus School ERP Pro", page_icon="🏫", layout="wide")

st.sidebar.title("🏫 Campus ERP Pro")
menu = st.sidebar.radio(
    "Modules Navigation",
    ["Dashboard", "Student Master", "Fee Management", "Attendance", "Examination", "Settings"]
)

if menu == "Dashboard":
    st.title("📊 School Overview Dashboard")
    st.info("Welcome to Campus School ERP Pro V2! Select a module from the sidebar.")
    
elif menu == "Student Master":
    render_students_module()

elif menu == "Fee Management":
    st.title("💰 Fee Collection & Accounts")
    st.write("Fee Module Under Integration...")

elif menu == "Attendance":
    st.title("📅 Daily Attendance Engine")
    st.write("Attendance Module Under Integration...")

elif menu == "Examination":
    st.title("📝 Examination & Marksheets")
    st.write("Exam Engine Under Integration...")
    import streamlit as st
from modules.attendance import render_attendance_module
from modules.students import render_students_module

st.set_page_config(page_title="Campus School ERP Pro", page_icon="🏫", layout="wide")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Student Master", "Attendance", "Fees", "Exams"])

if menu == "Attendance":
    render_attendance_module()
elif menu == "Student Master":
    render_students_module()
    import streamlit as st
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module
from modules.students import render_students_module

st.set_page_config(page_title="Campus School ERP Pro", page_icon="🏫", layout="wide")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Student Master", "Attendance", "Fee Management", "Exams"])

if menu == "Fee Management":
    render_fees_module()
elif menu == "Attendance":
    render_attendance_module()
elif menu == "Student Master":
    render_students_module()
