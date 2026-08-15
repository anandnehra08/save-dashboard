import os
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def init_supabase() -> Client:

    raw_url = ""
    raw_key = ""

    # =========================================================
    # 1. Read Supabase credentials
    # =========================================================

    try:

        # [supabase] section मौजूद है
        if "supabase" in st.secrets:

            raw_url = st.secrets["supabase"].get(
                "SUPABASE_URL",
                ""
            )

            raw_key = st.secrets["supabase"].get(
                "SUPABASE_KEY",
                ""
            )

        # Root-level secrets
        else:

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

    # =========================================================
    # 2. Clean credentials
    # =========================================================

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

    # =========================================================
    # 3. TEMPORARY DIAGNOSTIC
    # =========================================================

    st.info(
        f"Supabase URL: {clean_url}\n\n"
        f"Key loaded: {'YES' if clean_key else 'NO'}\n"
        f"Key prefix: {clean_key[:15] if clean_key else 'NONE'}..."
    )

    # =========================================================
    # 4. Validate
    # =========================================================

    if not clean_url:

        st.error(
            "❌ Supabase URL missing है।"
        )

        return None

    if not clean_key:

        st.error(
            "❌ Supabase API Key missing है।"
        )

        return None

    # =========================================================
    # 5. URL validation
    # =========================================================

    if not clean_url.startswith("https://"):

        st.error(
            "❌ Supabase URL गलत है। "
            "URL https:// से शुरू होना चाहिए।"
        )

        return None

    # =========================================================
    # 6. Create Supabase Client
    # =========================================================

    try:

        client = create_client(
            clean_url,
            clean_key
        )

        return client

    try:

    client = create_client(
        clean_url,
        clean_key
    )

    # =====================================================
    # SUPABASE CONNECTION TEST
    # =====================================================

    try:
        test_response = (
            client
            .table("students")
            .select("sr_no")
            .limit(1)
            .execute()
        )

        st.success(
            f"✅ Supabase Data API Connected! "
            f"Rows: {len(test_response.data or [])}"
        )

    except Exception as test_error:

        st.error(
            f"❌ Supabase Data API Test Failed: {test_error}"
        )

    return client

except Exception as e:

    st.error(
        f"❌ Supabase connection failed: {e}"
    )

    return None
    except Exception as e:

        st.error(
            f"❌ Supabase connection failed: {e}"
        )

        return None


# =============================================================
# Global Supabase Client
# =============================================================

supabase = init_supabase()
