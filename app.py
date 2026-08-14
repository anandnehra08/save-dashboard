import streamlit as st
import datetime

# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Campus ERP Pro",
    page_icon="🏫",
    layout="wide"
)


# ============================================================
# 2. SUPABASE CONNECTION
# ============================================================

try:
    from database.supabase import supabase
except Exception:
    supabase = None


# ============================================================
# 3. MODULE IMPORTS
# ============================================================

from modules.auth import render_login_page, logout_user
from modules.students import render_students_module
from modules.attendance import render_attendance_module
from modules.fees import render_fees_module
from modules.exams import render_exams_module
from modules.teacher_management import render_teacher_management_module
from modules.ai_assistant import render_ai_assistant


# ============================================================
# 4. SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "📊 Dashboard"


# ============================================================
# 5. NAVIGATION FUNCTION
# ============================================================

def navigate_to(page_name):
    st.session_state["nav_page"] = page_name


# ============================================================
# 6. DASHBOARD - SAVE TO SUPABASE
# ============================================================

def save_dashboard_to_supabase(username, metrics_data):

    if not supabase:
        return False, "Supabase client not connected!"

    try:

        supabase.table("user_dashboards").upsert(
            {
                "username": username,
                "dashboard_data": metrics_data,
                "updated_at": datetime.datetime.now().isoformat()
            },
            on_conflict="username"
        ).execute()

        return True, "✅ Dashboard state saved to Supabase!"

    except Exception as e:

        return False, f"❌ Save Error: {e}"


# ============================================================
# 7. DASHBOARD - LOAD FROM SUPABASE
# ============================================================

def load_dashboard_from_supabase(username):

    if not supabase:
        return None

    try:

        response = (
            supabase
            .table("user_dashboards")
            .select("dashboard_data")
            .eq("username", username)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return response.data[0]["dashboard_data"]

        return None

    except Exception:
        return None


# ============================================================
# 8. MAIN DASHBOARD
# ============================================================

def render_main_dashboard():

    current_user = st.session_state.get(
        "user_email",
        "anandnehra08"
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    col_logo, col_title = st.columns([1, 4])

    with col_logo:
        st.markdown("## 🏫")

    with col_title:

        st.title("Campus ERP Pro")

        st.caption(
            "📍 Powered by Sakshi Solution | Dream Shiksha ERP"
        )

        st.markdown(
            "**Contact:** +91 98285 95276 | "
            "**Email:** anandnehra8@gmail.com"
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Load Dashboard Data
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # School Overview
    # --------------------------------------------------------

    st.subheader("📊 School Overview")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        label="👨‍🎓 Total Students",
        value=metrics.get(
            "total_students",
            "1,250"
        ),
        delta="+12 this month"
    )

    m2.metric(
        label="👨‍🏫 Teaching Staff",
        value=metrics.get(
            "teaching_staff",
            "48"
        ),
        delta="Active"
    )

    m3.metric(
        label="💰 Fee Collection",
        value=metrics.get(
            "fee_collection",
            "₹ 4.2 Lakhs"
        ),
        delta="85% Paid"
    )

    m4.metric(
        label="📝 Active CBT Exams",
        value=metrics.get(
            "active_exams",
            "3 Live Tests"
        )
    )

    # --------------------------------------------------------
    # Save Dashboard
    # --------------------------------------------------------

    col_btn, _ = st.columns([2, 3])

    with col_btn:

        if st.button(
            "💾 Save Dashboard State to Supabase",
            use_container_width=True,
            type="primary",
            key="btn_save_dash"
        ):

            success, msg = save_dashboard_to_supabase(
                current_user,
                metrics
            )

            if success:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown("---")

    # --------------------------------------------------------
    # Quick Actions
    # --------------------------------------------------------

    st.subheader("🚀 Quick Actions")

    q1, q2, q3 = st.columns(3)

    # Student
    with q1:

        st.info(
            "🎒 **Student Directory & Admission**\n\n"
            "Register new students and view directory."
        )

        st.button(
            "Go to Student Directory ➡️",
            key="qa_btn_student",
            use_container_width=True,
            on_click=navigate_to,
            args=("👨‍🎓 Student Directory",)
        )

    # Fees
    with q2:

        st.success(
            "💳 **Collect School Fee**\n\n"
            "Generate fee receipts and manage dues."
        )

        st.button(
            "Go to Fees & Accounting ➡️",
            key="qa_btn_fee",
            use_container_width=True,
            on_click=navigate_to,
            args=("💳 Accounting & Fees",)
        )

    # Exams
    with q3:

        st.warning(
            "🎯 **Launch CBT Exam**\n\n"
            "Assign online test papers and view result."
        )

        st.button(
            "Go to Exam & Marks ➡️",
            key="qa_btn_exam",
            use_container_width=True,
            on_click=navigate_to,
            args=("📝 Exam & Marks",)
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        .footer {
            background-color: #1e1b4b;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            color: #f8fafc;
            font-size: 14px;
            margin-top: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .footer p {
            margin: 2px 0;
        }

        .footer a {
            color: #818cf8;
            text-decoration: none;
            font-weight: bold;
        }

        </style>

        <div class="footer">

            <p>
                💻 <b>Designed & Developed by:</b>
                Anand Nehra (Sakshi Solution)
            </p>

            <p>
                📍 <b>Office:</b> IT Park, City Center
                |
                📞 <b>Dev Support:</b> +91 98285 95276
            </p>

            <p>
                © 2026 Campus ERP Pro / Dream Shiksha.
                All rights reserved.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 9. LOGIN / AUTHENTICATION
# ============================================================

is_user_logged_in = (
    st.session_state.get("logged_in", False)
    or st.session_state.get("authenticated", False)
)


# ============================================================
# 10. LOGIN SCREEN
# ============================================================

if not is_user_logged_in:

    render_login_page()


# ============================================================
# 11. LOGGED-IN APPLICATION
# ============================================================

else:

    user_role = st.session_state.get(
        "user_role",
        "admin"
    )

    user_email = st.session_state.get(
        "user_email",
        ""
    )

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.title("🏫 Campus ERP Pro")

        st.write(
            f"👤 **{user_email}** "
            f"({user_role.capitalize()})"
        )

        st.markdown("---")

        # ----------------------------------------------------
        # ADMIN MENU
        # ----------------------------------------------------

        if user_role == "admin":

            menu_options = [
                "📊 Dashboard",
                "👨‍🎓 Student Directory",
                "📅 Attendance Register",
                "💳 Accounting & Fees",
                "📝 Exam & Marks",
                "👑 Staff & Access Control",
                "🤖 ERP AI Assistant"
            ]

        # ----------------------------------------------------
        # TEACHER / STAFF MENU
        # ----------------------------------------------------

        else:

            menu_options = [
                "📅 Attendance Register",
                "📝 Exam & Marks"
            ]

        # ----------------------------------------------------
        # Current Page
        # ----------------------------------------------------

        current_active = st.session_state.get(
            "nav_page",
            "📊 Dashboard"
        )

        if current_active in menu_options:

            default_idx = menu_options.index(
                current_active
            )

        else:

            default_idx = 0

            st.session_state["nav_page"] = menu_options[0]

        # ----------------------------------------------------
        # Sidebar Navigation
        # ----------------------------------------------------

        def update_from_radio():

            st.session_state["nav_page"] = (
                st.session_state["sidebar_menu_radio"]
            )

        st.radio(
            "Navigation Menu",
            menu_options,
            index=default_idx,
            key="sidebar_menu_radio",
            on_change=update_from_radio
        )

        st.markdown("---")

        # ----------------------------------------------------
        # Logout
        # ----------------------------------------------------

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="btn_logout_main"
        ):

            logout_user()


    # ========================================================
    # 12. PAGE ROUTING
    # ========================================================

    target_page = st.session_state["nav_page"]


    # Dashboard
    if target_page == "📊 Dashboard":

        render_main_dashboard()


    # Student Directory
    elif target_page == "👨‍🎓 Student Directory":

        render_students_module()


    # Attendance
    elif target_page == "📅 Attendance Register":

        render_attendance_module()


    # Fees
    elif target_page == "💳 Accounting & Fees":

        render_fees_module()


    # Exams
    elif target_page == "📝 Exam & Marks":

        render_exams_module()


    # Staff Management
    elif target_page == "👑 Staff & Access Control":

        render_teacher_management_module()


    # AI Assistant
    elif target_page == "🤖 ERP AI Assistant":

        render_ai_assistant()
