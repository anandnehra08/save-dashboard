# =========================================================
# CAMPUS ERP PRO
# SUPABASE CONNECTION
# NORMAL CLIENT + ADMIN CLIENT
# =========================================================

import os
import streamlit as st
from supabase import create_client, Client


# =========================================================
# READ SECRET
# =========================================================

def get_secret(name: str, default: str = "") -> str:

    try:
        # [supabase] section
        if "supabase" in st.secrets:
            value = st.secrets["supabase"].get(name, "")

            if value:
                return str(value).strip().strip('"').strip("'")

        # Root-level secret
        value = st.secrets.get(name, "")

        if value:
            return str(value).strip().strip('"').strip("'")

    except Exception:
        pass

    # Environment variable fallback
    return str(
        os.environ.get(name, default)
    ).strip().strip('"').strip("'")


# =========================================================
# SUPABASE URL
# =========================================================

SUPABASE_URL = get_secret("SUPABASE_URL")


# =========================================================
# NORMAL / PUBLIC APPLICATION KEY
# =========================================================

SUPABASE_KEY = get_secret("SUPABASE_KEY")


# =========================================================
# SERVICE ROLE KEY
# IMPORTANT:
# Never expose this in browser/client-side code.
# =========================================================

SUPABASE_SERVICE_ROLE_KEY = get_secret(
    "SUPABASE_SERVICE_ROLE_KEY"
)


# =========================================================
# VALIDATE URL
# =========================================================

def validate_url():

    if not SUPABASE_URL:

        st.error(
            "❌ SUPABASE_URL missing है।"
        )

        return False

    if not SUPABASE_URL.startswith("https://"):

        st.error(
            "❌ Supabase URL गलत है। "
            "URL https:// से शुरू होना चाहिए।"
        )

        return False

    return True


# =========================================================
# NORMAL SUPABASE CLIENT
# =========================================================

@st.cache_resource
def init_supabase() -> Client | None:

    if not validate_url():

        return None

    if not SUPABASE_KEY:

        st.error(
            "❌ SUPABASE_KEY missing है।"
        )

        return None

    try:

        return create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    except Exception as e:

        st.error(
            f"❌ Supabase connection failed: {e}"
        )

        return None


# =========================================================
# ADMIN SUPABASE CLIENT
#
# Used ONLY for trusted server-side operations such as:
# - Creating teacher Auth accounts
# - Disabling Auth users
# - Admin user management
#
# =========================================================

@st.cache_resource
def init_supabase_admin() -> Client | None:

    if not validate_url():

        return None

    if not SUPABASE_SERVICE_ROLE_KEY:

        return None

    try:

        return create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY
        )

    except Exception:

        return None


# =========================================================
# GLOBAL CLIENTS
# =========================================================

supabase = init_supabase()

supabase_admin = init_supabase_admin()


# =========================================================
# STATUS HELPERS
# =========================================================

def is_supabase_connected():

    return supabase is not None


def is_supabase_admin_available():

    return supabase_admin is not None
