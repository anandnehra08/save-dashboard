# =========================================================
# CAMPUS ERP PRO
# STAFF & ACCESS CONTROL MANAGEMENT
#
# REAL SUPABASE AUTH
# REAL EMAIL
# REAL PHONE
# MULTIPLE CLASSES
# MULTIPLE SUBJECTS
# PHASE 1-4 COMPATIBLE
# =========================================================

import re
import streamlit as st

from database.supabase import (
    supabase,
    supabase_admin,
)


# =========================================================
# CONSTANTS
# =========================================================

CLASSES = [
    f"Class {i}"
    for i in range(1, 13)
]

SECTIONS = [
    "A",
    "B",
    "C",
    "D",
]


DEFAULT_SUBJECTS = [
    "Maths",
    "Science",
    "English",
    "Hindi",
    "Physics",
    "Chemistry",
    "Social Studies",
]


# =========================================================
# SUBJECT MASTER
# =========================================================

def get_master_subjects():

    if not supabase:

        return DEFAULT_SUBJECTS

    try:

        response = (
            supabase
            .table("subjects_master")
            .select("subject_name")
            .execute()
        )

        if response.data:

            return [
                x["subject_name"]
                for x in response.data
                if x.get("subject_name")
            ]

    except Exception:
        pass

    return DEFAULT_SUBJECTS


# =========================================================
# EMAIL VALIDATION
# =========================================================

def is_valid_email(email):

    pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}$"
    )

    return bool(
        re.match(
            pattern,
            email.strip()
        )
    )


# =========================================================
# INDIAN MOBILE VALIDATION
# =========================================================

def normalize_phone(phone):

    digits = re.sub(
        r"\D",
        "",
        str(phone)
    )

    # 10 digit Indian number
    if len(digits) == 10:

        if digits[0] in "6789":

            return "+91" + digits

    # +91XXXXXXXXXX
    if len(digits) == 12 and digits.startswith("91"):

        number = digits[2:]

        if number[0] in "6789":

            return "+" + digits

    return None


# =========================================================
# PASSWORD VALIDATION
# =========================================================

def validate_password(password):

    if len(password) < 8:

        return (
            False,
            "Password कम से कम 8 characters का होना चाहिए।"
        )

    if not re.search(r"[A-Za-z]", password):

        return (
            False,
            "Password में letter होना चाहिए।"
        )

    if not re.search(r"[0-9]", password):

        return (
            False,
            "Password में number होना चाहिए।"
        )

    return True, ""


# =========================================================
# CREATE REAL SUPABASE AUTH USER
# =========================================================

def create_teacher_auth_user(
    email,
    password,
    phone
):

    if not supabase_admin:

        return (
            None,
            "❌ SUPABASE_SERVICE_ROLE_KEY configured नहीं है।"
        )

    try:

        response = (
            supabase_admin
            .auth.admin
            .create_user(
                {
                    "email": email,
                    "password": password,

                    # Email verification required
                    "email_confirm": False,

                    # Phone is real but remains unverified
                    "phone": phone,
                    "phone_confirm": False,

                    "user_metadata": {
                        "account_type": "teacher"
                    }
                }
            )
        )

        user = getattr(
            response,
            "user",
            None
        )

        if not user:

            return (
                None,
                "❌ Supabase Auth user create नहीं हुआ।"
            )

        return user, None

    except Exception as e:

        return None, str(e)


# =========================================================
# CREATE TEACHER DATABASE PROFILE
# =========================================================

def create_teacher_profile(
    auth_user_id,
    name,
    email,
    phone,
    role,
    assigned_classes,
    assigned_section,
    assigned_subjects
):

    if not supabase:

        return False, "Supabase database connected नहीं है।"

    payload = {

        # Auth link
        "auth_user_id": str(auth_user_id),

        "name": name,

        "email": email,

        "phone": phone,

        "role": role,

        # Phase 1-4 compatibility
        "assigned_class": (
            assigned_classes[0]
            if assigned_classes
            else None
        ),

        "assigned_classes": assigned_classes,

        "assigned_section": assigned_section,

        "assigned_subjects": assigned_subjects,

        # Verification starts false
        "email_verified": False,

        "phone_verified": False,

        "is_active": True,
    }

    try:

        (
            supabase
            .table("users")
            .insert(payload)
            .execute()
        )

        return True, None

    except Exception as e:

        return False, str(e)


# =========================================================
# DELETE AUTH USER IF DATABASE PROFILE CREATION FAILS
# =========================================================

def rollback_auth_user(auth_user_id):

    if not supabase_admin:
        return

    try:

        (
            supabase_admin
            .auth.admin
            .delete_user(
                str(auth_user_id)
            )
        )

    except Exception:
        pass


# =========================================================
# REVOKE TEACHER
# =========================================================

def revoke_teacher(
    teacher_id,
    auth_user_id
):

    if not supabase:

        return False, "Database unavailable."

    try:

        (
            supabase
            .table("users")
            .update(
                {
                    "is_active": False
                }
            )
            .eq("id", teacher_id)
            .execute()
        )

        # Disable Auth account if admin client exists
        if supabase_admin and auth_user_id:

            try:

                (
                    supabase_admin
                    .auth.admin
                    .update_user_by_id(
                        str(auth_user_id),
                        {
                            "ban_duration": "876000h"
                        }
                    )
                )

            except Exception:
                pass

        return True, None

    except Exception as e:

        return False, str(e)


# =========================================================
# RENDER MODULE
# =========================================================

def render_teacher_management_module():

    # -----------------------------------------------------
    # ADMIN ONLY
    # -----------------------------------------------------

    if st.session_state.get("user_role") != "admin":

        st.error(
            "⛔ Access Denied: "
            "केवल Principal/Admin teachers को manage कर सकते हैं।"
        )

        return


    st.title(
        "👑 Staff & Access Control Management"
    )

    st.caption(
        "Principal Control Panel: "
        "शिक्षकों को multiple classes और subjects "
        "का सुरक्षित access दें।"
    )


    # -----------------------------------------------------
    # ADMIN CLIENT CHECK
    # -----------------------------------------------------

    if not supabase_admin:

        st.warning(
            "⚠️ Real Teacher Auth अभी available नहीं है।"
        )

        st.info(
            "`.streamlit/secrets.toml` में "
            "`SUPABASE_SERVICE_ROLE_KEY` configure करें।"
        )

        return


    master_subjects = get_master_subjects()


    tab_add, tab_view = st.tabs(
        [
            "➕ Add / Assign Teacher",
            "📋 Manage Active Teachers",
        ]
    )


    # =====================================================
    # ADD TEACHER
    # =====================================================

    with tab_add:

        st.subheader(
            "➕ Add / Assign New Teacher"
        )

        col1, col2 = st.columns(2)


        # -------------------------------------------------
        # BASIC DETAILS
        # -------------------------------------------------

        with col1:

            t_name = st.text_input(
                "Teacher Name *",
                placeholder="e.g. Ramesh Kumar",
                key="teacher_name"
            )

            t_email = st.text_input(
                "Real Teacher Email ID *",
                placeholder="e.g. ramesh@gmail.com",
                key="teacher_email"
            )

            t_phone = st.text_input(
                "Real Mobile Number *",
                placeholder="e.g. 9876543211",
                key="teacher_phone"
            )

            t_pass = st.text_input(
                "Initial Password *",
                type="password",
                placeholder="Minimum 8 characters",
                key="teacher_password"
            )


        # -------------------------------------------------
        # ACCESS DETAILS
        # -------------------------------------------------

        with col2:

            t_role = st.selectbox(
                "Assign Role",
                [
                    "class_teacher",
                    "subject_teacher"
                ],
                format_func=lambda x:
                    (
                        "Class Teacher "
                        "(Incharge of Class)"
                        if x == "class_teacher"
                        else
                        "Subject Teacher "
                        "(Multiple Classes & Subjects)"
                    ),
                key="teacher_role"
            )


            if t_role == "class_teacher":

                assigned_classes = [
                    st.selectbox(
                        "Assigned Incharge Class",
                        CLASSES,
                        key="teacher_class"
                    )
                ]

                assigned_sec = st.selectbox(
                    "Assigned Section",
                    SECTIONS,
                    key="teacher_section"
                )

                assigned_subs = ["ALL"]

                st.info(
                    "💡 Class Teacher को "
                    "अपनी assigned class की "
                    "सभी subjects की access मिलेगी।"
                )


            else:

                assigned_classes = st.multiselect(
                    "Select Classes",
                    CLASSES,
                    key="teacher_classes"
                )

                assigned_sec = "ALL"

                assigned_subs = st.multiselect(
                    "Assigned Subjects",
                    master_subjects,
                    key="teacher_subjects"
                )


        st.markdown("---")


        # -------------------------------------------------
        # REAL ACCOUNT WARNING
        # -------------------------------------------------

        st.info(
            "🔐 यह Demo Account नहीं होगा। "
            "Teacher का real Supabase Auth account बनेगा। "
            "Email और mobile verification के बाद ही "
            "teacher को active access मिलेगा।"
        )


        # -------------------------------------------------
        # CREATE BUTTON
        # -------------------------------------------------

        if st.button(
            "➕ Create Real Teacher Account",
            type="primary",
            use_container_width=True,
            key="create_teacher_account"
        ):

            name = t_name.strip()

            email = t_email.strip().lower()

            phone = normalize_phone(
                t_phone
            )


            # ---------------------------------------------
            # VALIDATION
            # ---------------------------------------------

            if not name:

                st.error(
                    "❌ Teacher name डालें।"
                )

                return


            if not is_valid_email(email):

                st.error(
                    "❌ Valid real email address डालें।"
                )

                return


            if not phone:

                st.error(
                    "❌ Valid Indian mobile number डालें।"
                )

                return


            if not t_pass:

                st.error(
                    "❌ Password डालें।"
                )

                return


            password_ok, password_error = (
                validate_password(t_pass)
            )

            if not password_ok:

                st.error(
                    f"❌ {password_error}"
                )

                return


            if not assigned_classes:

                st.error(
                    "❌ कम से कम एक class चुनें।"
                )

                return


            if (
                t_role == "subject_teacher"
                and not assigned_subs
            ):

                st.error(
                    "❌ Subject Teacher के लिए "
                    "कम से कम एक subject चुनें।"
                )

                return


            # ---------------------------------------------
            # CHECK EXISTING EMAIL
            # ---------------------------------------------

            try:

                existing = (
                    supabase
                    .table("users")
                    .select(
                        "id,email"
                    )
                    .eq("email", email)
                    .limit(1)
                    .execute()
                )

                if existing.data:

                    st.error(
                        "❌ यह email पहले से registered है।"
                    )

                    return

            except Exception:
                pass


            # ---------------------------------------------
            # CREATE AUTH ACCOUNT
            # ---------------------------------------------

            with st.spinner(
                "Real Supabase Auth account बनाया जा रहा है..."
            ):

                auth_user, auth_error = (
                    create_teacher_auth_user(
                        email=email,
                        password=t_pass,
                        phone=phone
                    )
                )


            if auth_error:

                st.error(
                    f"❌ Auth account create नहीं हुआ: "
                    f"{auth_error}"
                )

                return


            # ---------------------------------------------
            # CREATE DATABASE PROFILE
            # ---------------------------------------------

            profile_ok, profile_error = (
                create_teacher_profile(
                    auth_user_id=auth_user.id,
                    name=name,
                    email=email,
                    phone=phone,
                    role=t_role,
                    assigned_classes=assigned_classes,
                    assigned_section=assigned_sec,
                    assigned_subjects=assigned_subs
                )
            )


            if not profile_ok:

                rollback_auth_user(
                    auth_user.id
                )

                st.error(
                    "❌ Teacher profile create नहीं हुआ। "
                    "Auth account rollback कर दिया गया।"
                )

                st.error(
                    profile_error
                )

                return


            # ---------------------------------------------
            # SUCCESS
            # ---------------------------------------------

            st.success(
                f"✅ {name} का REAL teacher account "
                f"successfully create हो गया।"
            )

            st.info(
                "📧 Email verification और 📱 mobile "
                "verification complete होने के बाद "
                "teacher को active access मिलेगा।"
            )

            st.success(
                "🔐 Assigned Classes: "
                + ", ".join(assigned_classes)
            )

            st.success(
                "📚 Assigned Subjects: "
                + ", ".join(assigned_subs)
            )

            st.rerun()


    # =====================================================
    # MANAGE TEACHERS
    # =====================================================

    with tab_view:

        st.subheader(
            "📋 All Registered Staff & Permissions"
        )


        if not supabase:

            st.error(
                "Supabase database connected नहीं है।"
            )

            return


        try:

            response = (
                supabase
                .table("users")
                .select(
                    """
                    id,
                    auth_user_id,
                    name,
                    email,
                    phone,
                    role,
                    assigned_class,
                    assigned_classes,
                    assigned_section,
                    assigned_subjects,
                    email_verified,
                    phone_verified,
                    is_active
                    """
                )
                .order(
                    "name"
                )
                .execute()
            )

            teachers = response.data or []


        except Exception as e:

            st.error(
                f"❌ Teacher data fetch error: {e}"
            )

            return


        if not teachers:

            st.info(
                "अभी कोई teacher registered नहीं है।"
            )

            return


        # -------------------------------------------------
        # TEACHER CARDS
        # -------------------------------------------------

        for teacher in teachers:

            role = (
                teacher.get("role")
                or "staff"
            )

            is_active = (
                teacher.get(
                    "is_active",
                    True
                )
            )

            email_verified = (
                teacher.get(
                    "email_verified",
                    False
                )
            )

            phone_verified = (
                teacher.get(
                    "phone_verified",
                    False
                )
            )


            status = (
                "🟢 ACTIVE"
                if is_active
                else
                "🔴 REVOKED"
            )


            with st.expander(
                f"👤 {teacher.get('name','Unknown')} "
                f"| {role.upper()} | {status}"
            ):

                c1, c2, c3 = st.columns(3)


                with c1:

                    st.write(
                        f"**Email:** "
                        f"{teacher.get('email','')}"
                    )

                    if email_verified:

                        st.success(
                            "📧 Email Verified"
                        )

                    else:

                        st.warning(
                            "📧 Email Not Verified"
                        )


                with c2:

                    st.write(
                        f"**Mobile:** "
                        f"{teacher.get('phone','')}"
                    )

                    if phone_verified:

                        st.success(
                            "📱 Mobile Verified"
                        )

                    else:

                        st.warning(
                            "📱 Mobile Not Verified"
                        )


                with c3:

                    st.write(
                        f"**Role:** {role}"
                    )

                    st.write(
                        f"**Section:** "
                        f"{teacher.get('assigned_section','ALL')}"
                    )


                st.markdown("---")


                classes_list = (
                    teacher.get(
                        "assigned_classes"
                    )
                    or []
                )


                if not classes_list:

                    old_class = teacher.get(
                        "assigned_class"
                    )

                    if old_class:

                        classes_list = [
                            old_class
                        ]


                subjects_list = (
                    teacher.get(
                        "assigned_subjects"
                    )
                    or []
                )


                c1, c2 = st.columns(2)


                with c1:

                    st.write(
                        "**🏫 Classes Allowed**"
                    )

                    st.write(
                        ", ".join(
                            map(
                                str,
                                classes_list
                            )
                        )
                        if classes_list
                        else "None"
                    )


                with c2:

                    st.write(
                        "**📚 Subjects Allowed**"
                    )

                    st.write(
                        ", ".join(
                            map(
                                str,
                                subjects_list
                            )
                        )
                        if subjects_list
                        else "None"
                    )


                st.markdown("---")


                # -------------------------------------------------
                # VERIFICATION STATUS
                # -------------------------------------------------

                if (
                    email_verified
                    and phone_verified
                    and is_active
                ):

                    st.success(
                        "🟢 Teacher Fully Verified & Active"
                    )

                elif not is_active:

                    st.error(
                        "🔴 Teacher Access Revoked"
                    )

                else:

                    st.warning(
                        "🟡 Verification Pending — "
                        "Teacher Access Restricted"
                    )


                # -------------------------------------------------
                # REVOKE
                # -------------------------------------------------

                if (
                    is_active
                    and role != "admin"
                ):

                    if st.button(
                        "🗑️ Revoke Teacher Access",
                        key=f"revoke_{teacher['id']}",
                        use_container_width=True
                    ):

                        ok, error = revoke_teacher(
                            teacher["id"],
                            teacher.get(
                                "auth_user_id"
                            )
                        )


                        if ok:

                            st.success(
                                "✅ Teacher access revoked."
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"❌ Revoke failed: {error}"
                            )
