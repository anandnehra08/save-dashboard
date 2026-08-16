# =========================================================
# CAMPUS ERP PRO
# STAFF & ACCESS CONTROL MANAGEMENT
#
# REAL SUPABASE AUTH
# REAL EMAIL VERIFICATION
# REAL PHONE OTP
# MULTIPLE CLASSES
# MULTIPLE SUBJECTS
# PHASE 1-4 COMPATIBLE
# NO DEMO / FAKE ACCOUNT
# =========================================================

import re
import streamlit as st

from database.supabase import supabase

try:
    from database.supabase_admin import supabase_admin
except Exception:
    supabase_admin = None


# =========================================================
# CONSTANTS
# =========================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]

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
            subjects = [
                row.get("subject_name")
                for row in response.data
                if row.get("subject_name")
            ]

            if subjects:
                return subjects

    except Exception:
        pass

    return DEFAULT_SUBJECTS


# =========================================================
# EMAIL VALIDATION
# =========================================================

def is_valid_email(email):

    if not email:
        return False

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
# MOBILE VALIDATION
# =========================================================

def normalize_phone(phone):

    digits = re.sub(
        r"\D",
        "",
        str(phone or "")
    )

    if len(digits) == 10:

        if digits[0] in "6789":
            return "+91" + digits

    if len(digits) == 12 and digits.startswith("91"):

        number = digits[2:]

        if number and number[0] in "6789":
            return "+" + digits

    if (
        len(digits) == 12
        and digits.startswith("919")
    ):
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
            "Password में कम से कम एक letter होना चाहिए।"
        )

    if not re.search(r"[0-9]", password):
        return (
            False,
            "Password में कम से कम एक number होना चाहिए।"
        )

    return True, ""


# =========================================================
# CHECK DUPLICATE PROFILE
# =========================================================

def email_exists(email):

    if not supabase:
        return False

    try:
        response = (
            supabase
            .table("users")
            .select("id")
            .eq(
                "email",
                email.strip().lower()
            )
            .limit(1)
            .execute()
        )

        return bool(response.data)

    except Exception:
        return False


def phone_exists(phone):

    if not supabase:
        return False

    clean_phone = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if clean_phone.startswith("91") and len(clean_phone) == 12:
        clean_phone = clean_phone[2:]

    try:
        response = (
            supabase
            .table("users")
            .select("id")
            .eq(
                "phone",
                "+91" + clean_phone
            )
            .limit(1)
            .execute()
        )

        if response.data:
            return True

        # Backward compatibility:
        # कुछ पुराने records में 10 digit mobile हो सकता है।

        response = (
            supabase
            .table("users")
            .select("id")
            .eq(
                "phone",
                clean_phone
            )
            .limit(1)
            .execute()
        )

        return bool(response.data)

    except Exception:
        return False


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

                    # Real email verification required
                    "email_confirm": False,

                    # Real phone verification required
                    "phone": phone,
                    "phone_confirm": False,

                    "user_metadata": {
                        "account_type": "teacher",
                        "name": ""
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
# CREATE DATABASE PROFILE
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

        return (
            False,
            "❌ Supabase database connected नहीं है।"
        )

    payload = {
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

        # Verification starts FALSE
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
# ROLLBACK AUTH USER
# =========================================================

def rollback_auth_user(auth_user_id):

    if not supabase_admin:
        return

    if not auth_user_id:
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

        return (
            False,
            "Database unavailable."
        )

    try:

        (
            supabase
            .table("users")
            .update(
                {
                    "is_active": False
                }
            )
            .eq(
                "id",
                teacher_id
            )
            .execute()
        )

        # Disable Supabase Auth account
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
# RESEND EMAIL VERIFICATION
# =========================================================

def resend_teacher_email(email):

    if not supabase:

        return (
            False,
            "Supabase connection unavailable."
        )

    try:

        supabase.auth.resend(
            {
                "type": "signup",
                "email": email
            }
        )

        return (
            True,
            "📧 Verification email भेज दिया गया है।"
        )

    except Exception as e:

        return False, str(e)


# =========================================================
# RENDER MODULE
# =========================================================

def render_teacher_management_module():

    # =====================================================
    # ADMIN ONLY
    # =====================================================

    if st.session_state.get(
        "user_role"
    ) != "admin":

        st.error(
            "⛔ Access Denied: "
            "केवल Principal/Admin teachers को manage कर सकते हैं।"
        )

        return


    # =====================================================
    # HEADER
    # =====================================================

    st.title(
        "👑 Staff & Access Control Management"
    )

    st.caption(
        "Principal Control Panel: "
        "शिक्षकों को multiple classes और subjects "
        "का सुरक्षित access दें।"
    )


    # =====================================================
    # ADMIN CLIENT CHECK
    # =====================================================

    if not supabase_admin:

        st.error(
            "❌ Real Teacher Authentication उपलब्ध नहीं है।"
        )

        st.info(
            "database/supabase_admin.py में "
            "SUPABASE_SERVICE_ROLE_KEY configure करें।"
        )

        return


    master_subjects = get_master_subjects()


    # =====================================================
    # TABS
    # =====================================================

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
                key="tm_teacher_name"
            )

            t_email = st.text_input(
                "Real Teacher Email ID *",
                placeholder="e.g. ramesh@gmail.com",
                key="tm_teacher_email"
            )

            t_phone = st.text_input(
                "Real Mobile Number *",
                placeholder="e.g. 9876543211",
                max_chars=13,
                key="tm_teacher_phone"
            )

            t_pass = st.text_input(
                "Initial Password *",
                type="password",
                placeholder="Minimum 8 characters",
                key="tm_teacher_password"
            )


        # -------------------------------------------------
        # ACCESS
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
                        "(Incharge of 1 Class)"
                        if x == "class_teacher"
                        else
                        "Subject Teacher "
                        "(Multiple Classes & Subjects)"
                    ),
                key="tm_teacher_role"
            )


            if t_role == "class_teacher":

                assigned_classes = [
                    st.selectbox(
                        "Assigned Incharge Class",
                        CLASSES,
                        key="tm_teacher_class"
                    )
                ]

                assigned_sec = st.selectbox(
                    "Assigned Section",
                    SECTIONS,
                    key="tm_teacher_section"
                )

                assigned_subs = ["ALL"]

                st.info(
                    "💡 Class Teacher अपनी assigned "
                    "class की सभी activities manage कर सकता है।"
                )

            else:

                assigned_classes = st.multiselect(
                    "Select Classes (Multiple)",
                    CLASSES,
                    key="tm_teacher_classes"
                )

                assigned_sec = "ALL"

                assigned_subs = st.multiselect(
                    "Assigned Subjects (Multiple)",
                    master_subjects,
                    key="tm_teacher_subjects"
                )


        st.markdown("---")


        # =================================================
        # REAL ACCOUNT NOTICE
        # =================================================

        st.warning(
            "🔐 यह REAL teacher account होगा। "
            "Fake/demo email, mobile या OTP का उपयोग नहीं होगा।"
        )

        st.info(
            "📧 Email verification + 📱 Mobile verification "
            "पूरा होने तक teacher को ERP access नहीं मिलेगा।"
        )


        # =================================================
        # CREATE
        # =================================================

        if st.button(
            "➕ Create Real Teacher Account",
            type="primary",
            use_container_width=True,
            key="tm_create_teacher"
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
                validate_password(
                    t_pass
                )
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
            # DUPLICATE EMAIL
            # ---------------------------------------------

            if email_exists(email):

                st.error(
                    "❌ यह email पहले से ERP में registered है।"
                )

                return


            # ---------------------------------------------
            # DUPLICATE PHONE
            # ---------------------------------------------

            if phone_exists(phone):

                st.error(
                    "❌ यह mobile number पहले से ERP में registered है।"
                )

                return


            # =================================================
            # CREATE REAL AUTH USER
            # =================================================

            with st.spinner(
                "🔐 Real Supabase Auth account बनाया जा रहा है..."
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
                    "❌ Auth account create नहीं हुआ:"
                )

                st.code(
                    auth_error
                )

                return


            # =================================================
            # CREATE ERP PROFILE
            # =================================================

            with st.spinner(
                "👤 ERP teacher profile बनाया जा रहा है..."
            ):

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


            # =================================================
            # ROLLBACK IF PROFILE FAILS
            # =================================================

            if not profile_ok:

                rollback_auth_user(
                    auth_user.id
                )

                st.error(
                    "❌ ERP profile create नहीं हुआ।"
                )

                st.error(
                    "Auth account rollback कर दिया गया है।"
                )

                st.code(
                    str(profile_error)
                )

                return


            # =================================================
            # SUCCESS
            # =================================================

            st.success(
                f"✅ {name} का REAL teacher account create हो गया।"
            )

            st.info(
                "📧 Verification email भेजा गया है। "
                "Teacher को email verify करना होगा।"
            )

            st.info(
                "📱 Mobile OTP verification भी पूरा करना होगा।"
            )

            st.success(
                "🏫 Classes: "
                + ", ".join(
                    assigned_classes
                )
            )

            st.success(
                "📚 Subjects: "
                + ", ".join(
                    assigned_subs
                )
            )

            st.warning(
                "🔒 दोनों verification पूरे होने तक "
                "ERP access restricted रहेगा।"
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
                "❌ Supabase database connected नहीं है।"
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


        # =================================================
        # TEACHER LIST
        # =================================================

        for teacher in teachers:

            role = (
                teacher.get("role")
                or "staff"
            )

            is_active = teacher.get(
                "is_active",
                True
            )

            email_verified = teacher.get(
                "email_verified",
                False
            )

            phone_verified = teacher.get(
                "phone_verified",
                False
            )


            if (
                is_active
                and email_verified
                and phone_verified
            ):

                status = "🟢 ACTIVE"

            elif not is_active:

                status = "🔴 REVOKED"

            else:

                status = "🟡 VERIFICATION PENDING"


            with st.expander(
                f"👤 {teacher.get('name', 'Unknown')} "
                f"| {role.upper()} | {status}"
            ):

                c1, c2, c3 = st.columns(3)


                # -----------------------------------------
                # EMAIL
                # -----------------------------------------

                with c1:

                    st.write(
                        f"**Email:** "
                        f"{teacher.get('email', '')}"
                    )

                    if email_verified:

                        st.success(
                            "📧 Email Verified"
                        )

                    else:

                        st.warning(
                            "📧 Email Not Verified"
                        )


                # -----------------------------------------
                # PHONE
                # -----------------------------------------

                with c2:

                    st.write(
                        f"**Mobile:** "
                        f"{teacher.get('phone', '')}"
                    )

                    if phone_verified:

                        st.success(
                            "📱 Mobile Verified"
                        )

                    else:

                        st.warning(
                            "📱 Mobile Not Verified"
                        )


                # -----------------------------------------
                # ROLE
                # -----------------------------------------

                with c3:

                    st.write(
                        f"**Role:** {role}"
                    )

                    st.write(
                        f"**Section:** "
                        f"{teacher.get('assigned_section', 'ALL')}"
                    )


                st.markdown("---")


                # -----------------------------------------
                # CLASSES
                # -----------------------------------------

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


                # -----------------------------------------
                # SUBJECTS
                # -----------------------------------------

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


                # =================================================
                # ACCESS STATUS
                # =================================================

                if not is_active:

                    st.error(
                        "🔴 Teacher Access Revoked"
                    )

                elif (
                    email_verified
                    and phone_verified
                ):

                    st.success(
                        "🟢 Teacher Fully Verified & Active"
                    )

                else:

                    st.warning(
                        "🟡 Verification Pending — "
                        "Teacher Access Restricted"
                    )


                # =================================================
                # RESEND EMAIL
                # =================================================

                if (
                    is_active
                    and not email_verified
                    and teacher.get("email")
                ):

                    if st.button(
                        "📧 Resend Verification Email",
                        key=f"resend_email_{teacher['id']}",
                        use_container_width=True
                    ):

                        ok, message = (
                            resend_teacher_email(
                                teacher["email"]
                            )
                        )

                        if ok:

                            st.success(
                                message
                            )

                        else:

                            st.error(
                                message
                            )


                # =================================================
                # REVOKE
                # =================================================

                if (
                    is_active
                    and role != "admin"
                ):

                    if st.button(
                        "🗑️ Revoke Teacher Access",
                        key=f"revoke_teacher_{teacher['id']}",
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
