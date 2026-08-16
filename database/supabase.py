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
# SECRET READER
# ============================================================

def read_secret(key: str, default: str = "") -> str:
    """
    Supabase credentials को safely पढ़ता है।

    Supported:
    1. [supabase] section
    2. Root-level secrets
    3. Environment variables
    """

    value = ""

    # --------------------------------------------------------
    # 1. [supabase] section
    # --------------------------------------------------------

    try:

        supabase_section = st.secrets.get(
            "supabase",
            {}
        )

        if supabase_section:

            value = supabase_section.get(
                key,
                ""
            )

    except Exception:
        value = ""


    # --------------------------------------------------------
    # 2. Root-level secret
    # --------------------------------------------------------

    if not value:

        try:

            value = st.secrets.get(
                key,
                ""
            )

        except Exception:
            value = ""


    # --------------------------------------------------------
    # 3. Environment variable
    # --------------------------------------------------------

    if not value:

        value = os.getenv(
            key,
            default
        )


    # --------------------------------------------------------
    # Clean value
    # --------------------------------------------------------

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .strip('"')
        .strip("'")
    )


# ============================================================
# SUPABASE URL
# ============================================================

def get_supabase_url():

    return read_secret(
        "SUPABASE_URL"
    )


# ============================================================
# SUPABASE NORMAL KEY
# ============================================================

def get_supabase_key():

    # Primary name
    key = read_secret(
        "SUPABASE_KEY"
    )

    # --------------------------------------------------------
    # Compatibility:
    # अगर आपने key को SUPABASE_ANON_KEY नाम दिया है
    # तो उसे भी पढ़ लेगा।
    # --------------------------------------------------------

    if not key:

        key = read_secret(
            "SUPABASE_ANON_KEY"
        )

    # --------------------------------------------------------
    # New Supabase naming compatibility
    # --------------------------------------------------------

    if not key:

        key = read_secret(
            "SUPABASE_PUBLISHABLE_KEY"
        )

    return key


# ============================================================
# INITIALIZE SUPABASE
# ============================================================

@st.cache_resource
def init_supabase() -> Client | None:

    # --------------------------------------------------------
    # Read credentials
    # --------------------------------------------------------

    raw_url = get_supabase_url()

    raw_key = get_supabase_key()


    # --------------------------------------------------------
    # Final cleaning
    # --------------------------------------------------------

    clean_url = (
        str(raw_url)
        .strip()
        .strip('"')
        .strip("'")
        .rstrip("/")
    )

    clean_key = (
        str(raw_key)
        .strip()
        .strip('"')
        .strip("'")
    )


    # ========================================================
    # URL VALIDATION
    # ========================================================

    if not clean_url:

        st.error(
            "❌ Supabase URL missing है।\n\n"
            "`.streamlit/secrets.toml` में "
            "`SUPABASE_URL` configure करें।"
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
    # API KEY VALIDATION
    # ========================================================

    if not clean_key:

        st.error(
            "❌ Supabase API Key missing है।\n\n"
            "`.streamlit/secrets.toml` में इनमें से "
            "किसी एक को configure करें:\n\n"
            "`SUPABASE_KEY`\n"
            "`SUPABASE_ANON_KEY`\n"
            "`SUPABASE_PUBLISHABLE_KEY`"
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
# GLOBAL SUPABASE CLIENT
# ============================================================

supabase = init_supabase()
