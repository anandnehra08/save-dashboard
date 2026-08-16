# ============================================================
# CAMPUS ERP PRO
# NORMAL SUPABASE CLIENT
#
# Used for:
# - Login
# - Database read/write
# - Normal application operations
#
# IMPORTANT:
# यहाँ SERVICE ROLE KEY इस्तेमाल नहीं करनी है।
# ============================================================

import os
import streamlit as st
from supabase import create_client, Client


# ============================================================
# GET SECRET
# ============================================================

def get_secret(section, key, default=""):
    """
    Safely read value from Streamlit secrets
    or environment variables.
    """

    # --------------------------------------------------------
    # 1. [supabase] section
    # --------------------------------------------------------

    try:

        if section in st.secrets:

            value = st.secrets[section].get(
                key,
                ""
            )

            if value:
                return str(value).strip()

    except Exception:
        pass


    # --------------------------------------------------------
    # 2. Root-level secret
    # --------------------------------------------------------

    try:

        value = st.secrets.get(
            key,
            ""
        )

        if value:
            return str(value).strip()

    except Exception:
        pass


    # --------------------------------------------------------
    # 3. Environment variable
    # --------------------------------------------------------

    return os.getenv(
        key,
        default
    ).strip()


# ============================================================
# INITIALIZE SUPABASE
# ============================================================

@st.cache_resource
def init_supabase() -> Client | None:

    # --------------------------------------------------------
    # Read URL
    # --------------------------------------------------------

    raw_url = get_secret(
        "supabase",
        "SUPABASE_URL"
    )


    # --------------------------------------------------------
    # Read NORMAL/PUBLISHABLE/ANON key
    # --------------------------------------------------------

    raw_key = get_secret(
        "supabase",
        "SUPABASE_KEY"
    )


    # --------------------------------------------------------
    # Clean URL
    # --------------------------------------------------------

    clean_url = (
        str(raw_url)
        .strip()
        .strip('"')
        .strip("'")
        .rstrip("/")
    )


    # --------------------------------------------------------
    # Clean Key
    # --------------------------------------------------------

    clean_key = (
        str(raw_key)
        .strip()
        .strip('"')
        .strip("'")
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not clean_url:

        st.error(
            "❌ Supabase URL missing है।\n\n"
            "`.streamlit/secrets.toml` में "
            "`SUPABASE_URL` configure करें।"
        )

        return None


    if not clean_key:

        st.error(
            "❌ Supabase API Key missing है।\n\n"
            "`.streamlit/secrets.toml` में "
            "`SUPABASE_KEY` configure करें।"
        )

        return None


    if not clean_url.startswith(
        "https://"
    ):

        st.error(
            "❌ Supabase URL गलत है।\n\n"
            "URL `https://` से शुरू होना चाहिए।"
        )

        return None


    # ========================================================
    # CREATE CLIENT
    # ========================================================

    try:

        client = create_client(
            clean_url,
            clean_key
        )

        return client

    except Exception as e:

        st.error(
            f"❌ Supabase connection failed:\n{e}"
        )

        return None


# ============================================================
# GLOBAL NORMAL CLIENT
# ============================================================

supabase = init_supabase()
