# ============================================================
# CAMPUS ERP PRO
# DATABASE / SUPABASE CLIENT
#
# NORMAL SUPABASE CLIENT
# ------------------------------------------------------------
# IMPORTANT:
# SUPABASE_KEY में केवल normal application key रखें।
# Service Role Key यहाँ इस्तेमाल नहीं करनी है।
# ============================================================

import os
import streamlit as st
from supabase import create_client, Client


# ============================================================
# SUPABASE INITIALIZATION
# ============================================================

@st.cache_resource
def init_supabase() -> Client | None:

    raw_url = ""
    raw_key = ""

    # ========================================================
    # 1. READ FROM STREAMLIT SECRETS
    # ========================================================

    try:

        # Format:
        #
        # [supabase]
        # SUPABASE_URL = "https://xxxxx.supabase.co"
        # SUPABASE_KEY = "your-normal-key"

        if "supabase" in st.secrets:

            raw_url = st.secrets["supabase"].get(
                "SUPABASE_URL",
                ""
            )

            raw_key = st.secrets["supabase"].get(
                "SUPABASE_KEY",
                ""
            )

        else:

            # =================================================
            # Alternative format:
            #
            # SUPABASE_URL = "..."
            # SUPABASE_KEY = "..."
            # =================================================

            raw_url = st.secrets.get(
                "SUPABASE_URL",
                os.environ.get(
                    "SUPABASE_URL",
                    ""
                )
            )

            raw_key = st.secrets.get(
                "SUPABASE_KEY",
                os.environ.get(
                    "SUPABASE_KEY",
                    ""
                )
            )

    except Exception:

        raw_url = os.environ.get(
            "SUPABASE_URL",
            ""
        )

        raw_key = os.environ.get(
            "SUPABASE_KEY",
            ""
        )


    # ========================================================
    # 2. CLEAN VALUES
    # ========================================================

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
    # 3. VALIDATE URL
    # ========================================================

    if not clean_url:

        st.error(
            "❌ Supabase URL missing है।"
        )

        return None


    if not clean_url.startswith(
        "https://"
    ):

        st.error(
            "❌ Supabase URL गलत है। "
            "URL https:// से शुरू होना चाहिए।"
        )

        return None


    # ========================================================
    # 4. VALIDATE KEY
    # ========================================================

    if not clean_key:

        st.error(
            "❌ Supabase API Key missing है।"
        )

        return None


    # ========================================================
    # 5. CREATE CLIENT
    # ========================================================

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
