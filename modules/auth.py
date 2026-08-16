# ============================================================
# CAMPUS ERP PRO
# AUTHENTICATION MODULE
# REAL SUPABASE AUTH + EMAIL / PHONE VERIFICATION
# ============================================================

import os
import re
import streamlit as st

try:
    from database.supabase import supabase
except Exception:
    supabase = None

# ============================================================
# OPTIONAL ADMIN CLIENT
# ============================================================

try:
    from database.supabase_admin import supabase_admin
except Exception:
    supabase_admin = None

# ============================================================
# CONSTANTS
# ============================================================

APP_NAME = "Campus ERP Pro"

ROLES = {
    "admin": "Admin",
    "class_teacher": "Class Teacher",
    "subject_teacher": "Subject Teacher",
    "staff": "Staff",
    "teacher": "Teacher",
}

# ============================================================
# VALIDATION HELPERS
# ============================================================

def valid_email(email: str) -> bool:
    if not email:
        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(
            pattern,
            email.strip().lower()
        )
    )


def valid_mobile(mobile: str) -> bool:
    if not mobile:
        return False

    clean = re.sub(
        r"\D",
        "",
        str(mobile)
    )

    return (
        len(clean) == 10
        and clean[0] in "6789"
    )


# ============================================================
# SESSION HELPERS
# ============================================================

def clear_auth_session():

    auth_keys = [
        "logged_in",
        "authenticated",
        "user_email",
        "user_name",
        "user_role",
        "user_id",
        "assigned_class",
        "assigned_classes",
        "assigned_section",
        "assigned_subjects",
        "phone_verified",
        "email_verified",
    ]

    for key in auth_keys:
        st.session_state.pop(
            key,
            None
        )


def set_authenticated_session(
    user,
    profile=None
):

    profile = profile or {}

    user_id = getattr(
        user,
        "id",
        None
    )

    user_email = (
        getattr(
            user,
            "email",
            None
        )
        or profile.get("email")
        or ""
    )

    user_metadata = getattr(
        user,
        "user_metadata",
        {}
    ) or {}

    user_name = (
        profile.get("name")
        or user_metadata.get("name")
        or "User"
    )

    role = (
        profile.get("role")
        or "staff"
    ).lower()

    assigned_classes = (
        profile.get("assigned_classes")
        or []
    )

    assigned_class = (
        profile.get("assigned_class")
        or (
            assigned_classes[0]
            if assigned_classes
            else None
        )
    )

    assigned_subjects = (
        profile.get("assigned_subjects")
        or []
    )

    assigned_section = (
        profile.get("assigned_section")
        or "ALL"
    )

    # --------------------------------------------------------
    # Verification status
    # --------------------------------------------------------

    email_verified = (
        profile.get("email_verified")
        if profile.get("email_verified") is not None
        else bool(
            getattr(
                user,
                "email_confirmed_at",
                None
            )
        )
    )

    phone_verified = bool(
        profile.get("phone_verified", False)
        or getattr(
            user,
            "phone_confirmed_at",
            None
        )
    )

    # --------------------------------------------------------
    # Session
    # --------------------------------------------------------

    st.session_state["logged_in"] = True
    st.session_state["authenticated"] = True

    st.session_state["user_id"] = user_id
    st.session_state["user_email"] = user_email
    st.session_state["user_name"] = user_name
    st.session_state["user_role"] = role

    st.session_state["assigned_class"] = (
        assigned_class
    )

    st.session_state["assigned_classes"] = (
        assigned_classes
    )

    st.session_state["assigned_section"] = (
        assigned_section
    )

    st.session_state["assigned_subjects"] = (
        assigned_subjects
    )

    st.session_state["email_verified"] = (
        email_verified
    )

    st.session_state["phone_verified"] = (
        phone_verified
    )


# ============================================================
# GET USER PROFILE
# ============================================================

def get_user_profile(
    user_id=None,
    email=None
):

    if not supabase:
        return None

    try:

        query = (
            supabase
            .table("users")
            .select(
                """
                id,
                name,
                email,
                mobile,
                username,
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
        )

        if user_id:

            response = (
                query
                .eq(
                    "auth_user_id",
                    user_id
                )
                .limit(1)
                .execute()
            )

        elif email:

            response = (
                query
                .eq(
                    "email",
                    email.strip().lower()
                )
                .limit(1)
                .execute()
            )

        else:
            return None

        if response.data:
            return response.data[0]

    except Exception:

        # ----------------------------------------------------
        # Backward compatibility
        # If auth_user_id column is not present,
        # fallback to email.
        # ----------------------------------------------------

        if email:

            try:

                response = (
                    supabase
                    .table("users")
                    .select("*")
                    .eq(
                        "email",
                        email.strip().lower()
                    )
                    .limit(1)
                    .execute()
                )

                if response.data:
                    return response.data[0]

            except Exception:
                pass

    return None


# ============================================================
# CHECK ACTIVE / VERIFIED USER
# ============================================================

def check_profile_access(profile):

    if not profile:

        return (
            False,
            "❌ आपका ERP profile नहीं मिला। "
            "Principal/Admin से संपर्क करें।"
        )

    # --------------------------------------------------------
    # Active status
    # --------------------------------------------------------

    if profile.get("is_active") is False:

        return (
            False,
            "⛔ आपका ERP access inactive है। "
            "Principal/Admin से संपर्क करें।"
        )

    # --------------------------------------------------------
    # Email verification
    # --------------------------------------------------------

    role = (
        profile.get("role")
        or "staff"
    ).lower()

    email_verified = profile.get(
        "email_verified",
        False
    )

    if not email_verified:

        return (
            False,
            "📧 आपका email अभी verified नहीं है। "
            "पहले email verification पूरा करें।"
        )

    # --------------------------------------------------------
    # Teacher / Staff phone verification
    # --------------------------------------------------------

    if role in [
        "teacher",
        "class_teacher",
        "subject_teacher",
        "staff",
    ]:

        if not profile.get(
            "phone_verified",
            False
        ):

            return (
                False,
                "📱 आपका mobile number अभी verified नहीं है। "
                "OTP verification पूरा करें।"
            )

    return True, ""


# ============================================================
# SEND EMAIL VERIFICATION
# ============================================================

def resend_email_verification(email):

    if not supabase:

        return (
            False,
            "Supabase connection उपलब्ध नहीं है।"
        )

    try:

        supabase.auth.resend(
            {
                "type": "signup",
                "email": email.strip().lower(),
            }
        )

        return (
            True,
            "📧 Verification email दोबारा भेज दिया गया है।"
        )

    except Exception as e:

        return (
            False,
            f"❌ Verification email नहीं भेजा जा सका: {e}"
        )


# ============================================================
# PHONE OTP
# ============================================================

def send_phone_otp(phone):

    if not supabase:

        return (
            False,
            "Supabase connection उपलब्ध नहीं है।"
        )

    clean_phone = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if len(clean_phone) == 10:

        clean_phone = (
            "+91" + clean_phone
        )

    if not clean_phone.startswith("+"):

        return (
            False,
            "❌ Mobile number format गलत है।"
        )

    try:

        supabase.auth.sign_in_with_otp(
            {
                "phone": clean_phone
            }
        )

        return (
            True,
            "📱 Real OTP आपके registered mobile number "
            "पर भेजा गया है।"
        )

    except Exception as e:

        return (
            False,
            f"❌ OTP भेजने में समस्या: {e}"
        )


# ============================================================
# VERIFY PHONE OTP
# ============================================================

def verify_phone_otp(
    phone,
    otp
):

    if not supabase:

        return (
            False,
            None,
            "Supabase connection उपलब्ध नहीं है।"
        )

    clean_phone = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if len(clean_phone) == 10:

        clean_phone = (
            "+91" + clean_phone
        )

    try:

        response = (
            supabase
            .auth
            .verify_otp(
                {
                    "phone": clean_phone,
                    "token": otp.strip(),
                    "type": "sms",
                }
            )
        )

        user = response.user

        if not user:

            return (
                False,
                None,
                "❌ OTP verification failed."
            )

        return (
            True,
            user,
            "✅ Mobile number verified successfully."
        )

    except Exception as e:

        return (
            False,
            None,
            f"❌ गलत या expired OTP: {e}"
        )


# ============================================================
# UPDATE PHONE VERIFICATION IN PROFILE
# ============================================================

def mark_phone_verified(user_id):

    if not supabase or not user_id:
        return

    try:

        (
            supabase
            .table("users")
            .update(
                {
                    "phone_verified": True
                }
            )
            .eq(
                "auth_user_id",
                user_id
            )
            .execute()
        )

    except Exception:
        pass


# ============================================================
# LOGIN WITH EMAIL + PASSWORD
# ============================================================

def login_with_email(
    email,
    password
):

    if not supabase:

        return (
            False,
            "❌ Supabase connection उपलब्ध नहीं है।"
        )

    try:

        response = (
            supabase
            .auth
            .sign_in_with_password(
                {
                    "email": email.strip().lower(),
                    "password": password,
                }
            )
        )

        user = response.user

        if not user:

            return (
                False,
                "❌ Login failed."
            )

        # ----------------------------------------------------
        # Get ERP profile
        # ----------------------------------------------------

        profile = get_user_profile(
            user_id=user.id,
            email=user.email
        )

        if not profile:

            return (
                False,
                "❌ आपका Supabase account मौजूद है, "
                "लेकिन ERP profile नहीं मिला।"
            )

        # ----------------------------------------------------
        # Update email verification status
        # ----------------------------------------------------

        if getattr(
            user,
            "email_confirmed_at",
            None
        ):

            if profile.get(
                "email_verified"
            ) is not True:

                try:

                    (
                        supabase
                        .table("users")
                        .update(
                            {
                                "email_verified": True
                            }
                        )
                        .eq(
                            "id",
                            profile["id"]
                        )
                        .execute()
                    )

                    profile["email_verified"] = True

                except Exception:
                    pass

        # ----------------------------------------------------
        # Access check
        # ----------------------------------------------------

        allowed, message = (
            check_profile_access(
                profile
            )
        )

        if not allowed:

            try:
                supabase.auth.sign_out()
            except Exception:
                pass

            return (
                False,
                message
            )

        # ----------------------------------------------------
        # Create application session
        # ----------------------------------------------------

        set_authenticated_session(
            user,
            profile
        )

        return (
            True,
            "✅ Login successful."
        )

    except Exception as e:

        return (
            False,
            f"❌ Login failed: {e}"
        )


# ============================================================
# PHONE LOGIN
# ============================================================

def find_user_by_mobile(mobile):

    if not supabase:
        return None

    clean_mobile = re.sub(
        r"\D",
        "",
        str(mobile)
    )

    try:

        response = (
            supabase
            .table("users")
            .select("*")
            .eq(
                "mobile",
                clean_mobile
            )
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception:
        pass

    return None


# ============================================================
# FORGOT PASSWORD
# ============================================================

def send_password_reset_email(email):

    if not supabase:

        return (
            False,
            "❌ Supabase connection उपलब्ध नहीं है।"
        )

    try:

        supabase.auth.reset_password_for_email(
            email.strip().lower()
        )

        return (
            True,
            "📧 Password reset link आपके registered "
            "email पर भेज दिया गया है।"
        )

    except Exception as e:

        return (
            False,
            f"❌ Reset email नहीं भेजा जा सका: {e}"
        )


# ============================================================
# SIGN OUT
# ============================================================

def logout_user():

    try:

        if supabase:
            supabase.auth.sign_out()

    except Exception:
        pass

    clear_auth_session()

    st.session_state["auth_mode"] = "login"
    st.session_state["phone_otp_sent"] = False

    st.rerun()


# ============================================================
# HEADER WITH LOGO
# ============================================================

def render_auth_header():

    import os
    import base64

    logo_path = "assets/save_learning_logo.jpg"

    logo_html = ""

    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(
                    image_file.read()
                ).decode()

            logo_html = f"""
                <img
                    src="data:image/jpeg;base64,{encoded_logo}"
                    style="
                        width:110px;
                        height:110px;
                        object-fit:contain;
                        border-radius:16px;
                        background:white;
                        padding:8px;
                        box-shadow:0 5px 15px rgba(0,0,0,.20);
                    "
                >
            """

        except Exception:
            logo_html = "<div style='font-size:70px;'>🏫</div>"

    else:
        logo_html = "<div style='font-size:70px;'>🏫</div>"

    st.markdown(
        f"""
        <style>

        .erp-auth-header {{
            background: linear-gradient(
                135deg,
                #1e1b4b,
                #312e81
            );

            color:white;
            padding:25px;
            border-radius:20px;
            margin-bottom:25px;

            box-shadow:
                0 8px 25px rgba(0,0,0,.20);

            text-align:center;
        }}

        .erp-auth-logo {{
            margin-bottom:12px;
        }}

        .erp-auth-header h2 {{
            margin:8px 0;
            color:white;
            font-size:30px;
        }}

        .erp-auth-header p {{
            margin:5px 0;
            color:#e0e7ff;
            font-size:15px;
        }}

        </style>

        <div class="erp-auth-header">

            <div class="erp-auth-logo">
                {logo_html}
            </div>

            <h2>
                Campus ERP Pro
            </h2>

            <p>
                Secure School Management System
            </p>

            <p>
                🔐 Real Supabase Authentication
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )
# ============================================================
# LOGIN PAGE
# ============================================================

def render_login_page():

    render_auth_header()

    if "auth_mode" not in st.session_state:

        st.session_state["auth_mode"] = "login"

    if "phone_otp_sent" not in st.session_state:

        st.session_state["phone_otp_sent"] = False

    if "phone_login_mobile" not in st.session_state:

        st.session_state["phone_login_mobile"] = ""

    # ========================================================
    # LOGIN
    # ========================================================

    if st.session_state["auth_mode"] == "login":

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            st.subheader(
                "🔐 Secure Sign In"
            )

            login_method = st.radio(
                "Login Method",
                [
                    "📧 Email + Password",
                    "📱 Mobile OTP",
                ],
                horizontal=True,
                key="login_method"
            )

            # ------------------------------------------------
            # EMAIL LOGIN
            # ------------------------------------------------

            if login_method == (
                "📧 Email + Password"
            ):

                email = st.text_input(
                    "Registered Email",
                    placeholder="teacher@school.com",
                    key="auth_login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="auth_login_password"
                )

                if st.button(
                    "🚀 Sign In",
                    type="primary",
                    use_container_width=True,
                    key="real_email_login"
                ):

                    if not valid_email(email):

                        st.warning(
                            "⚠️ Valid registered email डालें।"
                        )

                    elif not password:

                        st.warning(
                            "⚠️ Password डालें।"
                        )

                    else:

                        with st.spinner(
                            "🔐 Authenticating..."
                        ):

                            success, message = (
                                login_with_email(
                                    email,
                                    password
                                )
                            )

                        if success:

                            st.success(message)

                            st.rerun()

                        else:

                            st.error(message)

                st.markdown("---")

                if st.button(
                    "📧 Resend Email Verification",
                    use_container_width=True,
                    key="resend_email_verify"
                ):

                    if not valid_email(email):

                        st.warning(
                            "पहले registered email डालें।"
                        )

                    else:

                        success, message = (
                            resend_email_verification(
                                email
                            )
                        )

                        if success:

                            st.success(message)

                        else:

                            st.error(message)

            # ------------------------------------------------
            # PHONE OTP LOGIN
            # ------------------------------------------------

            else:

                if not st.session_state[
                    "phone_otp_sent"
                ]:

                    mobile = st.text_input(
                        "Registered Mobile Number",
                        placeholder="10 digit mobile number",
                        max_chars=10,
                        key="phone_login_input"
                    )

                    if st.button(
                        "📩 Send Real OTP",
                        type="primary",
                        use_container_width=True,
                        key="send_real_phone_otp"
                    ):

                        if not valid_mobile(mobile):

                            st.warning(
                                "⚠️ Valid Indian mobile number डालें।"
                            )

                        else:

                            profile = (
                                find_user_by_mobile(
                                    mobile
                                )
                            )

                            if not profile:

                                st.error(
                                    "❌ यह mobile number "
                                    "ERP में registered नहीं है।"
                                )

                            elif profile.get(
                                "is_active"
                            ) is False:

                                st.error(
                                    "⛔ यह account inactive है।"
                                )

                            else:

                                with st.spinner(
                                    "📱 Real OTP भेजा जा रहा है..."
                                ):

                                    success, message = (
                                        send_phone_otp(
                                            mobile
                                        )
                                    )

                                if success:

                                    st.session_state[
                                        "phone_otp_sent"
                                    ] = True

                                    st.session_state[
                                        "phone_login_mobile"
                                    ] = mobile

                                    st.success(message)

                                    st.rerun()

                                else:

                                    st.error(message)

                else:

                    mobile = st.session_state[
                        "phone_login_mobile"
                    ]

                    st.info(
                        f"📱 OTP भेजा गया: "
                        f"{mobile[:2]}******{mobile[-2:]}"
                    )

                    otp = st.text_input(
                        "Enter 6-Digit OTP",
                        max_chars=6,
                        key="phone_login_otp"
                    )

                    if st.button(
                        "✅ Verify OTP & Login",
                        type="primary",
                        use_container_width=True,
                        key="verify_phone_login"
                    ):

                        if (
                            not otp
                            or not otp.isdigit()
                            or len(otp) != 6
                        ):

                            st.warning(
                                "⚠️ 6 digit OTP डालें।"
                            )

                        else:

                            with st.spinner(
                                "🔐 OTP verify हो रहा है..."
                            ):

                                success, user, message = (
                                    verify_phone_otp(
                                        mobile,
                                        otp
                                    )
                                )

                            if success:

                                profile = (
                                    find_user_by_mobile(
                                        mobile
                                    )
                                )

                                if not profile:

                                    st.error(
                                        "❌ ERP profile नहीं मिला।"
                                    )

                                else:

                                    # Phone verified
                                    profile[
                                        "phone_verified"
                                    ] = True

                                    mark_phone_verified(
                                        profile.get(
                                            "auth_user_id"
                                        )
                                    )

                                    # Email must still be verified
                                    allowed, access_message = (
                                        check_profile_access(
                                            profile
                                        )
                                    )

                                    if allowed:

                                        set_authenticated_session(
                                            user,
                                            profile
                                        )

                                        st.success(
                                            "✅ Mobile verified. "
                                            "Login successful."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            access_message
                                        )

                            else:

                                st.error(message)

                    if st.button(
                        "🔄 Send OTP Again",
                        use_container_width=True,
                        key="resend_phone_otp"
                    ):

                        st.session_state[
                            "phone_otp_sent"
                        ] = False

                        st.rerun()

            st.markdown("---")

            # ------------------------------------------------
            # PASSWORD RESET
            # ------------------------------------------------

            if st.button(
                "🔑 Forgot Password?",
                use_container_width=True,
                key="goto_password_reset"
            ):

                st.session_state[
                    "auth_mode"
                ] = "forgot_password"

                st.rerun()

    # ========================================================
    # FORGOT PASSWORD
    # ========================================================

    elif (
        st.session_state["auth_mode"]
        == "forgot_password"
    ):

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            st.subheader(
                "🔑 Password Recovery"
            )

            st.info(
                "Password reset के लिए registered "
                "email पर secure Supabase link भेजा जाएगा।"
            )

            email = st.text_input(
                "Registered Email",
                placeholder="teacher@school.com",
                key="reset_email"
            )

            if st.button(
                "📧 Send Reset Link",
                type="primary",
                use_container_width=True,
                key="send_reset_link"
            ):

                if not valid_email(email):

                    st.warning(
                        "⚠️ Valid email डालें।"
                    )

                else:

                    success, message = (
                        send_password_reset_email(
                            email
                        )
                    )

                    if success:

                        st.success(message)

                    else:

                        st.error(message)

            st.markdown("---")

            if st.button(
                "⬅️ Back to Sign In",
                use_container_width=True,
                key="back_login"
            ):

                st.session_state[
                    "auth_mode"
                ] = "login"

                st.rerun()
