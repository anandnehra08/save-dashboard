# ============================================================
# CAMPUS ERP PRO
# SUPABASE CONNECTION
# ============================================================

import os
import streamlit as st
from supabase import create_client, Client


# ============================================================
# SUPABASE CLIENT INITIALIZATION
# ============================================================

@st.cache_resource(show_spinner=False)
def init_supabase() -> Client | None:

    supabase_url = ""
    supabase_key = ""

    # --------------------------------------------------------
    # 1. Read credentials from Streamlit Secrets
    # --------------------------------------------------------

    try:

        # Preferred format:
        #
        # [supabase]
        # SUPABASE_URL = "https://xxxxx.supabase.co"
        # SUPABASE_KEY = "xxxxx"

        if "supabase" in st.secrets:

            supabase_config = st.secrets["supabase"]

            supabase_url = supabase_config.get(
                "SUPABASE_URL",
                ""
            )

            supabase_key = supabase_config.get(
                "SUPABASE_KEY",
                ""
            )

        # ----------------------------------------------------
        # 2. Fallback: root level secrets
        # ----------------------------------------------------

        else:

            supabase_url = st.secrets.get(
                "SUPABASE_URL",
                ""
            )

            supabase_key = st.secrets.get(
                "SUPABASE_KEY",
                ""
            )

    except Exception:
        pass


    # --------------------------------------------------------
    # 3. Environment Variable Fallback
    # --------------------------------------------------------

    if not supabase_url:

        supabase_url = os.environ.get(
            "SUPABASE_URL",
            ""
        )

    if not supabase_key:

        supabase_key = os.environ.get(
            "SUPABASE_KEY",
            ""
        )


    # --------------------------------------------------------
    # 4. Clean Credentials
    # --------------------------------------------------------

    clean_url = (
        str(supabase_url)
        .strip()
        .strip('"')
        .strip("'")
        .rstrip("/")
    )

    clean_key = (
        str(supabase_key)
        .strip()
        .strip('"')
        .strip("'")
    )


    # --------------------------------------------------------
    # 5. Validate URL
    # --------------------------------------------------------

    if not clean_url:

        st.error(
            "❌ Supabase URL missing है।"
        )

        return None


    if not clean_url.startswith("https://"):

        st.error(
            "❌ Supabase URL गलत है। "
            "URL https:// से शुरू होना चाहिए।"
        )

        return None


    if "supabase.co" not in clean_url:

        st.warning(
            "⚠️ Supabase URL verify करें।"
        )


    # --------------------------------------------------------
    # 6. Validate API Key
    # --------------------------------------------------------

    if not clean_key:

        st.error(
            "❌ Supabase API Key missing है।"
        )

        return None


    # --------------------------------------------------------
    # 7. Create Client
    # --------------------------------------------------------

    try:

        client = create_client(
            clean_url,
            clean_key
        )

        return client

    except Exception as e:

        st.error(
            f"❌ Supabase connection failed: {e}"
        )

        return None


# ============================================================
# GLOBAL SUPABASE CLIENT
# ============================================================

supabase = init_supabase()


# ============================================================
# CONNECTION STATUS HELPER
# ============================================================

def is_supabase_connected() -> bool:

    return supabase is not None


# ============================================================
# SAFE DATABASE TEST
# ============================================================

def test_supabase_connection():

    if supabase is None:

        return False, "Supabase client available नहीं है।"

    try:

        # Lightweight request.
        # Existing users table is used because Campus ERP
        # already depends on this table.

        response = (
            supabase
            .table("users")
            .select("id")
            .limit(1)
            .execute()
        )

        return True, "Supabase connected successfully."

    except Exception as e:

        return False, str(e)
