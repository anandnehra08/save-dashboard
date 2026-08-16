# =========================================================
# CAMPUS ERP PRO
# SUPABASE ADMIN CLIENT
#
# IMPORTANT:
# SERVICE ROLE KEY केवल SERVER-SIDE पर रखें।
# इसे frontend/client/browser में expose न करें।
# =========================================================

import os
import streamlit as st

from supabase import create_client, Client


# =========================================================
# LOAD SECRET
# =========================================================

def get_secret_value(name: str) -> str:

    value = ""

    # 1. [supabase] section
    try:
        if "supabase" in st.secrets:

            value = st.secrets["supabase"].get(
                name,
                ""
            )

    except Exception:
        pass

    # 2. Root-level secret
    if not value:

        try:

            value = st.secrets.get(
                name,
                ""
            )

        except Exception:
            pass

    # 3. Environment variable
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
        .rstrip("/")
    )


# =========================================================
# INITIALIZE ADMIN CLIENT
# =========================================================

@st.cache_resource
def init_supabase_admin() -> Client:

    # -----------------------------------------------------
    # SUPABASE URL
    # -----------------------------------------------------

    raw_url = get_secret_value(
        "SUPABASE_URL"
    )

    # -----------------------------------------------------
    # SERVICE ROLE KEY
    # -----------------------------------------------------

    raw_key = get_secret_value(
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    # -----------------------------------------------------
    # URL CHECK
    # -----------------------------------------------------

    if not raw_url:

        st.error(
            "❌ SUPABASE_URL missing है।"
        )

        return None

    if not raw_url.startswith(
        "https://"
    ):

        st.error(
            "❌ SUPABASE_URL गलत है। "
            "यह https:// से शुरू होना चाहिए।"
        )

        return None

    # -----------------------------------------------------
    # SERVICE ROLE KEY CHECK
    # -----------------------------------------------------

    if not raw_key:

        st.error(
            "❌ SUPABASE_SERVICE_ROLE_KEY missing है।"
        )

        st.info(
            "Supabase Dashboard → "
            "Project Settings → API में "
            "service_role key configure करें।"
        )

        return None

    # -----------------------------------------------------
    # CREATE ADMIN CLIENT
    # -----------------------------------------------------

    try:

        client = create_client(
            raw_url,
            raw_key
        )

        return client

    except Exception as e:

        st.error(
            f"❌ Supabase Admin connection failed: {e}"
        )

        return None


# =========================================================
# GLOBAL ADMIN CLIENT
# =========================================================

supabase_admin = init_supabase_admin()
