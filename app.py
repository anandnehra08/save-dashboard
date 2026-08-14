import streamlit as st
import datetime
from supabase import create_client

# 1. Page Config
st.set_page_config(
    page_title="Campus ERP Pro", 
    page_icon="🏫", 
    layout="wide"
)

# -----------------------------------------------------------
# SUPABASE CONNECTION (डेटाबेस सेविंग के लिए)
# -----------------------------------------------------------
try:
    SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"⚠️ Supabase Secrets Not Configured: {e}")
    supabase = None

# 2. Imports (आपके ओरिजिनल मॉड्यूल्स)
from modules.auth import render_login_page, logout_user
from modules.students import render_students_module
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module
from modules.exams import render_exams_module
from modules.teacher_management import render_teacher_management_module  # Import Teacher Management

# -----------------------------------------------------------
# DASHBOARD SUPABASE HELPER FUNCTIONS (Save / Load)
# -----------------------------------------------------------
def save_dashboard_to_supabase(username, metrics_data):
    """डैशबोर्ड के लाइव स्टेट को Supabase में सुरक्षित सेव करता है"""
    if not supabase:
        return False, "Supabase client connected nahi hai!"
    try:
        supabase.table("user_dashboards").upsert({
            "username": username,
            "dashboard_data": metrics_data,
            "updated_at": datetime.datetime.now().isoformat()
        }, on_conflict="username").execute()
        return True, "✅ Dashboard data saved to Supabase!"
    except Exception as e:
        return False, f"❌ Save Error: {e}"

def load_dashboard_from_supabase(username):
    """Supabase से सेव डेटा लोड करता है"""
    if not supabase:
        return None
    try:
        response = supabase.table("user_dashboards").select("dashboard_data").eq("username", username).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["dashboard_data"]
        return None
    except Exception as e:
        return None

# -----------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "📊 Dashboard"

# Quick Navigation Function
def navigate_to(page_name):
    st.session_state["nav_page"] = page_name

# -----------------------------------------------------------
# MAIN DASHBOARD COMPONENT
# -----------------------------------------------------------
def render_main_dashboard():
    current_user = st.session_state.get('user_email', 'anandnehra08')

    # Header
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.markdown("## 🏫")
        
    with col_title:
        st.title("Campus ERP Pro")
        st.caption("📍 Powered by Sakshi Solution | Dream Shiksha ERP")
        st.markdown("**Contact:** +91 98285 95276 | **Email:** anandnehra8@gmail.com")

    st.markdown("---")

    # Supabase से डेटा लोड करें (अगर सेव्ड डेटा है तो वही दिखेगा)
    saved_data = load_dashboard_from_supabase(current_user)
    
    if saved_data:
        metrics = saved_data
    else:
        metrics = {
            "total_students": "1,250",
            "teaching_staff": "48",
            "fee_collection": "₹ 4.2 Lakhs",
            "active_exams": "3 Live Tests"
        }

    # Quick Stats
    st.subheader("📊 School Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="👨‍🎓 Total Students", value=metrics.get("total_students", "1,250"), delta="+12 this month")
    m2.metric(label="👨‍🏫 Teaching Staff", value=metrics.get("teaching_staff", "48"), delta="Active")
    m3.metric(label="💰 Fee Collection", value=metrics.get("fee_collection", "₹ 4.2 Lakhs"), delta="85% Paid")
    m4.metric(label="📝 Active CBT Exams", value=metrics.get("active_exams", "3 Live Tests"))

    # Save Button Section
    col_btn, _ = st.columns([2, 3])
    with col_btn:
        if st.button("💾 Save Dashboard State to Supabase", use_container_width=True, type="primary", key="btn_save_dashboard"):
            success, msg = save_dashboard_to_supabase(current_user, metrics)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown("---")

    # Quick Actions Grid
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
                background-color: #1e1b4b;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                color: #f8fafc;
                font-size: 14px;
                margin-top: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .footer p { margin: 2px 0; }
            .footer a { color: #818cf8; text-decoration: none; font-weight: bold; }
        </style>
        <div class="footer">
            <p>💻 <b>Designed & Developed by:</b> Anand Nehra (Sakshi Solution)</p>
            <p>📍 <b>Office:</b> IT Park, City Center | 📞 <b>Dev Support:</b> +91 98285 95276</p>
            <p>© 2026 Campus ERP Pro / Dream Shiksha. All rights reserved.</p>
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

        # Admin vs Teacher Navigation Menu
        if user_role == "admin":
            menu_options = [
                "📊 Dashboard", 
                "👨‍🎓 Student Directory", 
                "📅 Attendance Register", 
                "💳 Accounting & Fees", 
                "📝 Exam & Marks",
                "👑 Staff & Access Control"  # Principal Special Option
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

    elif target_page == "👑 Staff & Access Control":
        render_teacher_management_module()
