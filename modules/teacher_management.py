import re
import streamlit as st

from database.supabase import supabase


# ============================================================
# CONSTANTS
# ============================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]

ROLES = {
    "class_teacher": "Class Teacher",
    "subject_teacher": "Subject Teacher",
}


# ============================================================
# VALIDATION
# ============================================================

def validate_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(pattern, email.strip()))


def validate_indian_mobile(phone: str) -> bool:
    phone = phone.strip().replace(" ", "")

    # +91XXXXXXXXXX
    if phone.startswith("+91"):
        phone = phone[3:]

    # 91XXXXXXXXXX
    elif phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]

    return bool(re.fullmatch(r"[6-9]\d{9}", phone))


def normalize_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "")

    if phone.startswith("+91"):
        return phone

    if phone.startswith("91") and len(phone) == 12:
        return "+" + phone

    return "+91" + phone


# ============================================================
# SUBJECT MASTER
# ============================================================

def get_master_subjects():

    default_subjects = [
        "Maths",
        "Science",
        "English",
        "Hindi",
        "Physics",
        "Chemistry",
        "Social Studies",
        "Biology",
        "Computer",
        "Sanskrit",
    ]

    if not supabase:
        return default_subjects

    try:

        response = (
            supabase
            .table("subjects_master")
            .select("subject_name")
            .execute()
        )

        if response.data:
            subjects = [
                row["subject_name"]
                for row in response.data
                if row.get("subject_name")
            ]

            if subjects:
                return subjects

    except Exception:
        pass

    return default_subjects


# ============================================================
# DUPLICATE CHECK
# ============================================================

def teacher_email_exists(email):

    if not supabase:
        return False

    try:

        response = (
            supabase
            .table("users")
            .select("id")
            .eq("email", email)
            .limit(1)
            .execute()
        )

        return bool(response.data)

    except Exception:
        return False


def teacher_phone_exists(phone):

    if not supabase:
        return False

    try:

        response = (
            supabase
            .table("users")
            .select("id")
            .eq("phone", phone)
            .limit(1)
            .execute()
        )

        return bool(response.data)

    except Exception:
        return False


# ============================================================
# CREATE SUPABASE AUTH USER
# ============================================================

def create_auth_teacher(email, password, name, phone):

    """
    Supabase Auth में real teacher account बनाने की कोशिश।

    IMPORTANT:
    supabase.auth.admin.create_user()
    तभी काम करेगा जब database.supabase में
    server-side secret/service-role capable client उपलब्ध हो।
    """

    if not supabase:
        return None, "Supabase connection उपलब्ध नहीं है।"

    try:

        response = supabase.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "name": name,
                    "phone": phone,
                    "account_type": "teacher",
                },
            }
        )

        user = getattr(response, "user", None)

        if user:
            return user, None

        if isinstance(response, dict):
            user = response.get("user")

            if user:
                return user, None

        return None, "Supabase Auth ने user create नहीं किया।"

    except Exception as e:

        error_text = str(e)

        return None, error_text


# ============================================================
# ROLLBACK AUTH USER
# ============================================================

def delete_auth_user(user_id):

    if not supabase or not user_id:
        return

    try:
        supabase.auth.admin.delete_user(user_id)
    except Exception:
        pass


# ============================================================
# CREATE TEACHER DATABASE PROFILE
# ============================================================

def create_teacher_profile(
    auth_user_id,
    name,
    email,
    phone,
    role,
    assigned_classes,
    assigned_section,
    assigned_subjects,
):

    payload = {
        "name": name,
        "email": email,
        "phone": phone,

        # Existing system compatibility
        "role": role,
        "assigned_class": assigned_classes[0],
        "assigned_classes": assigned_classes,
        "assigned_section": assigned_section,
        "assigned_subjects": assigned_subjects,
    }

    # अगर users table में auth_user_id column मौजूद है
    # तो इसे automatically use किया जा सकता है।
    if auth_user_id:
        payload["auth_user_id"] = auth_user_id

    return supabase.table("users").insert(payload).execute()


# ============================================================
# MAIN MODULE
# ============================================================

def render_teacher_management_module():

    # --------------------------------------------------------
    # ADMIN ONLY
    # --------------------------------------------------------

    if st.session_state.get("user_role") != "admin":

        st.error(
            "⛔ **Access Denied:** "
            "केवल Principal/Admin ही शिक्षकों के access को manage कर सकते हैं।"
        )

        return

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("👑 Staff & Access Control Management")

    st.caption(
        "Principal Control Panel: "
        "शिक्षकों को multiple classes और subjects का सुरक्षित access दें।"
    )

    master_subjects = get_master_subjects()

    tab_add, tab_view = st.tabs(
        [
            "➕ Add / Assign Teacher",
            "📋 Manage Active Teachers",
        ]
    )

    # ========================================================
    # TAB 1
    # ========================================================

    with tab_add:

        st.subheader("👨‍🏫 Assign Access to Teacher")

        st.info(
            "🔐 Teacher account real Supabase authentication "
            "के लिए बनाया जाएगा। Demo account नहीं बनाया जाएगा।"
        )

        col1, col2 = st.columns(2)

        # ----------------------------------------------------
        # BASIC DETAILS
        # ----------------------------------------------------

        with col1:

            t_name = st.text_input(
                "Teacher Name *",
                placeholder="Ramesh Kumar",
                key="teacher_name_new",
            )

            t_email = st.text_input(
                "Teacher Email ID *",
                placeholder="teacher@school.com",
                key="teacher_email_new",
            )

            t_phone = st.text_input(
                "Phone Number *",
                placeholder="9876543210",
                key="teacher_phone_new",
                max_chars=13,
            )

            t_pass = st.text_input(
                "Assign Password *",
                type="password",
                placeholder="Minimum 8 characters",
                key="teacher_password_new",
            )

            st.caption(
                "📌 Password कम से कम 8 characters का होना चाहिए।"
            )

        # ----------------------------------------------------
        # ACCESS DETAILS
        # ----------------------------------------------------

        with col2:

            t_role = st.selectbox(
                "Assign Role *",
                list(ROLES.keys()),
                format_func=lambda x: ROLES[x],
                key="teacher_role_new",
            )

            # ------------------------------------------------
            # CLASS TEACHER
            # ------------------------------------------------

            if t_role == "class_teacher":

                assigned_classes = [
                    st.selectbox(
                        "Assigned Incharge Class *",
                        CLASSES,
                        key="class_teacher_class_new",
                    )
                ]

                assigned_sec = st.selectbox(
                    "Assigned Section *",
                    SECTIONS,
                    key="class_teacher_section_new",
                )

                assigned_subs = ["ALL"]

                st.success(
                    "💡 Class Teacher को assigned class की "
                    "सभी applicable academic activities का access मिलेगा।"
                )

            # ------------------------------------------------
            # SUBJECT TEACHER
            # ------------------------------------------------

            else:

                assigned_classes = st.multiselect(
                    "Select Classes *",
                    CLASSES,
                    key="subject_teacher_classes_new",
                    help="एक से अधिक classes चुन सकते हैं।",
                )

                assigned_sec = "ALL"

                assigned_subs = st.multiselect(
                    "Assigned Subjects *",
                    master_subjects,
                    key="subject_teacher_subjects_new",
                    help="एक से अधिक subjects चुन सकते हैं।",
                )

                st.info(
                    "🎯 Subject Teacher को केवल चुनी गई "
                    "classes और subjects का access मिलेगा।"
                )

        st.markdown("---")

        # ====================================================
        # CREATE BUTTON
        # ====================================================

        if st.button(
            "➕ Create Real Teacher Account & Grant Access",
            type="primary",
            use_container_width=True,
            key="create_real_teacher",
        ):

            # ------------------------------------------------
            # BASIC VALIDATION
            # ------------------------------------------------

            name = t_name.strip()
            email = t_email.strip().lower()
            phone = t_phone.strip()
            password = t_pass.strip()

            if not name:

                st.error("❌ Teacher name required है।")
                st.stop()

            if not email:

                st.error("❌ Real teacher email required है।")
                st.stop()

            if not validate_email(email):

                st.error(
                    "❌ Valid email address डालें। "
                    "उदाहरण: teacher@school.com"
                )

                st.stop()

            if not phone:

                st.error("❌ Real mobile number required है।")
                st.stop()

            if not validate_indian_mobile(phone):

                st.error(
                    "❌ Valid Indian mobile number डालें। "
                    "10 digit number जो 6-9 से शुरू हो।"
                )

                st.stop()

            if len(password) < 8:

                st.error(
                    "❌ Password कम से कम 8 characters का होना चाहिए।"
                )

                st.stop()

            if not assigned_classes:

                st.error(
                    "❌ कम से कम एक class assign करें।"
                )

                st.stop()

            if (
                t_role == "subject_teacher"
                and not assigned_subs
            ):

                st.error(
                    "❌ Subject Teacher के लिए कम से कम एक subject चुनें।"
                )

                st.stop()

            if not supabase:

                st.error(
                    "❌ Supabase connection उपलब्ध नहीं है।"
                )

                st.stop()

            normalized_phone = normalize_phone(phone)

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            if teacher_email_exists(email):

                st.error(
                    "❌ यह email पहले से registered है। "
                    "दूसरा teacher बनाने के लिए अलग email इस्तेमाल करें।"
                )

                st.stop()

            if teacher_phone_exists(normalized_phone):

                st.error(
                    "❌ यह mobile number पहले से registered है।"
                )

                st.stop()

            # ------------------------------------------------
            # CREATE AUTH ACCOUNT
            # ------------------------------------------------

            with st.spinner(
                "🔐 Real Supabase teacher account बनाया जा रहा है..."
            ):

                auth_user, auth_error = create_auth_teacher(
                    email=email,
                    password=password,
                    name=name,
                    phone=normalized_phone,
                )

            if auth_error:

                error_lower = auth_error.lower()

                if (
                    "already" in error_lower
                    or "duplicate" in error_lower
                    or "unique" in error_lower
                ):

                    st.error(
                        "❌ यह email/phone Supabase Auth में पहले से registered है।"
                    )

                else:

                    st.error(
                        f"❌ Supabase Auth Account Create Error:\n\n"
                        f"{auth_error}"
                    )

                st.stop()

            # ------------------------------------------------
            # GET AUTH ID
            # ------------------------------------------------

            auth_id = None

            if auth_user:

                if hasattr(auth_user, "id"):
                    auth_id = auth_user.id

                elif isinstance(auth_user, dict):
                    auth_id = auth_user.get("id")

            # ------------------------------------------------
            # SAVE PROFILE
            # ------------------------------------------------

            try:

                create_teacher_profile(
                    auth_user_id=auth_id,
                    name=name,
                    email=email,
                    phone=normalized_phone,
                    role=t_role,
                    assigned_classes=assigned_classes,
                    assigned_section=assigned_sec,
                    assigned_subjects=assigned_subs,
                )

                st.success(
                    f"✅ **{name}** का real teacher account successfully बनाया गया।"
                )

                st.success(
                    f"📧 Login Email: **{email}**"
                )

                st.success(
                    f"📱 Mobile: **{normalized_phone}**"
                )

                st.success(
                    f"👑 Role: **{ROLES[t_role]}**"
                )

                st.success(
                    f"🏫 Classes: **{', '.join(assigned_classes)}**"
                )

                if assigned_subs != ["ALL"]:

                    st.success(
                        f"📚 Subjects: **{', '.join(assigned_subs)}**"
                    )

                st.info(
                    "🔐 Password security के लिए password database की "
                    "`users` table में plain text में store नहीं किया गया है।"
                )

                st.balloons()

                st.rerun()

            except Exception as profile_error:

                # --------------------------------------------
                # IMPORTANT ROLLBACK
                # --------------------------------------------

                if auth_id:
                    delete_auth_user(auth_id)

                st.error(
                    "❌ Teacher profile save नहीं हो सका। "
                    "Auth account को rollback कर दिया गया है।"
                )

                st.error(
                    f"Database Error: {profile_error}"
                )

    # ========================================================
    # TAB 2
    # ========================================================

    with tab_view:

        st.subheader("📋 All Registered Staff & Permissions")

        if not supabase:

            st.error("Supabase connection उपलब्ध नहीं है।")
            return

        try:

            response = (
                supabase
                .table("users")
                .select(
                    "id, auth_user_id, name, email, phone, "
                    "role, assigned_class, assigned_classes, "
                    "assigned_section, assigned_subjects"
                )
                .neq("role", "admin")
                .order("name")
                .execute()
            )

            teachers = response.data or []

            if not teachers:

                st.info(
                    "👨‍🏫 अभी कोई teacher registered नहीं है।"
                )

            else:

                st.write(
                    f"**Total Active Teachers: {len(teachers)}**"
                )

                for teacher in teachers:

                    role_name = ROLES.get(
                        teacher.get("role"),
                        teacher.get("role", "Teacher")
                    )

                    with st.expander(
                        f"👤 {teacher.get('name', 'Unknown')} "
                        f"— {role_name}"
                    ):

                        c1, c2 = st.columns(2)

                        with c1:

                            st.write(
                                f"📧 **Email:** "
                                f"{teacher.get('email', '-')}"
                            )

                            st.write(
                                f"📱 **Phone:** "
                                f"{teacher.get('phone', '-')}"
                            )

                            st.write(
                                f"👑 **Role:** {role_name}"
                            )

                        with c2:

                            classes_list = (
                                teacher.get("assigned_classes")
                                or []
                            )

                            if not classes_list:

                                old_class = teacher.get(
                                    "assigned_class"
                                )

                                if old_class:
                                    classes_list = [old_class]

                            subjects_list = (
                                teacher.get("assigned_subjects")
                                or []
                            )

                            st.write(
                                f"🏫 **Classes:** "
                                f"{', '.join(classes_list) if classes_list else '-'}"
                            )

                            st.write(
                                f"📚 **Subjects:** "
                                f"{', '.join(subjects_list) if subjects_list else '-'}"
                            )

                            st.write(
                                f"🔹 **Section:** "
                                f"{teacher.get('assigned_section', '-')}"
                            )

                        st.markdown("---")

                        # ------------------------------------
                        # REVOKE ACCESS
                        # ------------------------------------

                        if st.button(
                            "🗑️ Revoke Teacher Access",
                            key=f"revoke_teacher_{teacher['id']}",
                            type="secondary",
                        ):

                            auth_id = teacher.get(
                                "auth_user_id"
                            )

                            # Delete Auth account first
                            if auth_id:

                                try:

                                    delete_auth_user(auth_id)

                                except Exception as e:

                                    st.error(
                                        f"Auth account delete error: {e}"
                                    )

                                    st.stop()

                            # Delete application profile
                            try:

                                (
                                    supabase
                                    .table("users")
                                    .delete()
                                    .eq("id", teacher["id"])
                                    .execute()
                                )

                                st.success(
                                    f"✅ {teacher.get('name')} "
                                    f"का access revoke कर दिया गया।"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"❌ Profile delete error: {e}"
                                )

        except Exception as e:

            st.error(
                f"❌ Teacher data fetch error: {e}"
            )
