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
        if "supabase" in st.secrets:
            raw_url = st.secrets["supabase"].get("SUPABASE_URL", "")
            raw_key = st.secrets["supabase"].get("SUPABASE_KEY", "")
        else:
            raw_url = st.secrets.get(
                "SUPABASE_URL",
                os.environ.get("SUPABASE_URL", "")
            )
            raw_key = st.secrets.get(
                "SUPABASE_KEY",
                os.environ.get("SUPABASE_KEY", "")
            )

    except Exception:
        raw_url = os.environ.get("SUPABASE_URL", "")
        raw_key = os.environ.get("SUPABASE_KEY", "")

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
    # 3. Validation
    # =========================================================
    if not clean_url:
        st.error("❌ Supabase URL missing है।")
        return None

    if not clean_key:
        st.error("❌ Supabase API Key missing है।")
        return None

    if not clean_url.startswith("https://"):
        st.error("❌ Supabase URL गलत है।")
        return None

    # =========================================================
    # 4. Create Supabase Client
    # =========================================================
   client = create_client(
    clean_url,
    clean_key
)

# =========================================================
# SUPABASE CONNECTION TEST
# =========================================================
try:
    test_response = (
        client
        .table("students")
        .select("sr_no")
        .limit(1)
        .execute()
    )

    st.success(
        f"✅ Supabase connected successfully | "
        f"Students rows: {len(test_response.data or [])}"
    )

except Exception as e:
    st.error(
        f"❌ Supabase connection test failed: {e}"
    )

return client

        return client

    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
        return None


# =============================================================
# Global Supabase Client
# =============================================================
supabase = init_supabase()
