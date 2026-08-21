# ============================================================
# CAMPUS ERP PRO
# SUPABASE ADMIN CLIENT
#
# Used ONLY for trusted server-side operations:
#
# - Create real Auth users
# - Delete Auth users
# - Disable / manage Auth users
# - Principal/Admin operations
#
# IMPORTANT:
# SERVICE ROLE KEY कभी frontend/browser में expose नहीं करनी।
# ============================================================

import os
import streamlit as st
from supabase import create_client, Client


# ============================================================
# GET SERVICE ROLE KEY
# ============================================================

def get_service_role_key():

    # --------------------------------------------------------
    # 1. [supabase] section
    # --------------------------------------------------------

    try:

        if "supabase" in st.secrets:

            value = st.secrets["supabase"].get(
                "SUPABASE_SERVICE_ROLE_KEY",
                ""
            )

            if value:

                return (
                    str(value)
                    .strip()
                    .strip('"')
                    .strip("'")
                )

    except Exception:
        pass


    # --------------------------------------------------------
    # 2. Root-level secret
    # --------------------------------------------------------

    try:

        value = st.secrets.get(
            "SUPABASE_SERVICE_ROLE_KEY",
            ""
        )

        if value:

            return (
                str(value)
                .strip()
                .strip('"')
                .strip("'")
            )

    except Exception:
        pass


    # --------------------------------------------------------
    # 3. Environment variable
    # --------------------------------------------------------

    return (
        os.getenv(
            "SUPABASE_SERVICE_ROLE_KEY",
            ""
        )
        .strip()
        .strip('"')
        .strip("'")
    )


# ============================================================
# GET SUPABASE URL
# ============================================================

def get_supabase_url():

    # --------------------------------------------------------
    # [supabase] section
    # --------------------------------------------------------

    try:

        if "supabase" in st.secrets:

            value = st.secrets["supabase"].get(
                "SUPABASE_URL",
                ""
            )

            if value:

                return (
                    str(value)
                    .strip()
                    .strip('"')
                    .strip("'")
                    .rstrip("/")
                )

    except Exception:
        pass


    # --------------------------------------------------------
    # Root-level
    # --------------------------------------------------------

    try:

        value = st.secrets.get(
            "SUPABASE_URL",
            ""
        )

        if value:

            return (
                str(value)
                .strip()
                .strip('"')
                .strip("'")
                .rstrip("/")
            )

    except Exception:
        pass


    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    return (
        os.getenv(
            "SUPABASE_URL",
            ""
        )
        .strip()
        .strip('"')
        .strip("'")
        .rstrip("/")
    )


# ============================================================
# INITIALIZE ADMIN CLIENT
# ============================================================

@st.cache_resource
def init_supabase_admin() -> Client | None:

    supabase_url = get_supabase_url()

    service_role_key = get_service_role_key()


    # ========================================================
    # URL CHECK
    # ========================================================

    if not supabase_url:

        st.error(
            "❌ Supabase URL missing है।\n\n"
            "`.streamlit/secrets.toml` में "
            "`SUPABASE_URL` configure करें।"
        )

        return None


    # ========================================================
    # SERVICE ROLE CHECK
    # ========================================================

    if not service_role_key:

        st.error(
            "❌ SUPABASE_SERVICE_ROLE_KEY missing है।\n\n"
            "Supabase Dashboard → "
            "Project Settings → API में "
            "service_role key configure करें।"
        )

        return None


    # ========================================================
    # URL VALIDATION
    # ========================================================

    if not supabase_url.startswith(
        "https://"
    ):

        st.error(
            "❌ Supabase URL गलत है।\n\n"
            "URL `https://` से शुरू होना चाहिए।"
        )

        return None


    # ========================================================
    # CREATE ADMIN CLIENT
    # ========================================================

    try:

        client = create_client(
            supabase_url,
            service_role_key
        )

        return client

    except Exception as e:

        st.error(
            f"❌ Supabase Admin connection failed:\n{e}"
        )

        return None


# ============================================================
# GLOBAL ADMIN CLIENT
# ============================================================

supabase_admin = init_supabase_admin()
if supabase_admin:
    st.success("✅ Supabase Admin Connected")
else:
    st.error("❌ Supabase Admin Not Connected")
