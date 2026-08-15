# ============================================================
# CAMPUS ERP PRO
# SUPABASE SERVER-SIDE ADMIN CLIENT
# ============================================================

import os
import streamlit as st

from supabase import create_client, Client


# ============================================================
# SECRET READER
# ============================================================

def _read_secret(name: str) -> str:
    """
    Streamlit secrets या environment variables से secret पढ़ता है।
    """

    value = ""

    try:
        # [supabase] section
        if "supabase" in st.secrets:

            value = st.secrets["supabase"].get(
                name,
                ""
            )

        # Root-level secret
        if not value:

            value = st.secrets.get(
                name,
                ""
            )

    except Exception:
        value = ""

    # Environment fallback
    if not value:

        value = os.environ.get(
            name,
            ""
        )

    return (
        str(value)
        .strip()
        .strip('"')
        .strip("'")
    )


# ============================================================
# ADMIN CLIENT INITIALIZATION
# ============================================================

@st.cache_resource
def init_supabase_admin() -> Client | None:

    # --------------------------------------------------------
    # IMPORTANT:
    # यह SERVER-SIDE secret है।
    #
    # SUPABASE_SERVICE_ROLE_KEY को कभी भी:
    # - frontend में
    # - browser JavaScript में
    # - public GitHub repository में
    # - normal client code में
    # expose नहीं करना है।
    # --------------------------------------------------------

    supabase_url = _read_secret(
        "SUPABASE_URL"
    )

    service_role_key = _read_secret(
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    if not supabase_url:

        st.error(
            "❌ SUPABASE_URL configured नहीं है।"
        )

        return None

    if not supabase_url.startswith(
        "https://"
    ):

        st.error(
            "❌ SUPABASE_URL गलत है। "
            "यह https:// से शुरू होना चाहिए।"
        )

        return None

    # --------------------------------------------------------
    # Validate Service Role Key
    # --------------------------------------------------------

    if not service_role_key:

        st.error(
            "❌ SUPABASE_SERVICE_ROLE_KEY "
            "configured नहीं है।"
        )

        return None

    # --------------------------------------------------------
    # Create Admin Client
    # --------------------------------------------------------

    try:

        admin_client = create_client(
            supabase_url.rstrip("/"),
            service_role_key
        )

        return admin_client

    except Exception as e:

        st.error(
            f"❌ Supabase Admin connection failed: {e}"
        )

        return None


# ============================================================
# GLOBAL ADMIN CLIENT
# ============================================================

supabase_admin = init_supabase_admin()
