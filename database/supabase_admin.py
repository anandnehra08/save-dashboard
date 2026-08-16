# ============================================================
# CAMPUS ERP PRO
# SUPABASE ADMIN CLIENT
#
# IMPORTANT:
# यह client केवल trusted server-side Admin operations के लिए है.
#
# इसमें SUPABASE_SERVICE_ROLE_KEY इस्तेमाल होगी.
# इसे frontend/browser/client-side code में expose नहीं करना है.
# ============================================================

import os
import streamlit as st

from supabase import create_client, Client


# ============================================================
# INITIALIZE SUPABASE ADMIN CLIENT
# ============================================================

@st.cache_resource
def init_supabase_admin() -> Client | None:

    raw_url = ""
    raw_service_key = ""

    # ========================================================
    # 1. READ SUPABASE URL
    # ========================================================

    try:

        if "supabase" in st.secrets:

            raw_url = st.secrets["supabase"].get(
                "SUPABASE_URL",
                ""
            )

            raw_service_key = st.secrets["supabase"].get(
                "SUPABASE_SERVICE_ROLE_KEY",
                ""
            )

        else:

            raw_url = st.secrets.get(
                "SUPABASE_URL",
                os.environ.get(
                    "SUPABASE_URL",
                    ""
                )
            )

            raw_service_key = st.secrets.get(
                "SUPABASE_SERVICE_ROLE_KEY",
                os.environ.get(
                    "SUPABASE_SERVICE_ROLE_KEY",
                    ""
                )
            )

    except Exception:

        raw_url = os.environ.get(
            "SUPABASE_URL",
            ""
        )

        raw_service_key = os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY",
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

    clean_service_key = (
        str(raw_service_key)
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
    # 4. VALIDATE SERVICE ROLE KEY
    # ========================================================

    if not clean_service_key:

        st.warning(
            "⚠️ SUPABASE_SERVICE_ROLE_KEY configured नहीं है। "
            "Teacher Auth Admin operations उपलब्ध नहीं होंगे।"
        )

        return None


    # ========================================================
    # 5. CREATE ADMIN CLIENT
    # ========================================================

    try:

        admin_client = create_client(
            clean_url,
            clean_service_key
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
