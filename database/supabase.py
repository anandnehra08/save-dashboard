import os
import streamlit as st
from supabase import create_client, Client


# =========================================================
# Helper: Read Secret / Environment Variable
# =========================================================

def _get_config(key: str) -> str:
    value = ""

    try:
        # Streamlit secrets
        if key in st.secrets:
            value = st.secrets[key]
        elif "supabase" in st.secrets:
            value = st.secrets["supabase"].get(key, "")
    except Exception:
        pass

    # Environment fallback
    if not value:
        value = os.getenv(key, "")

    return str(value).strip().strip('"').strip("'").rstrip("/")


# =========================================================
# Public / Normal Supabase Client
# =========================================================

@st.cache_resource
def init_supabase() -> Client | None:

    url = _get_config("SUPABASE_URL")

    # Prefer publishable/anon key for normal application work
    key = (
        _get_config("SUPABASE_PUBLISHABLE_KEY")
        or _get_config("SUPABASE_ANON_KEY")
        or _get_config("SUPABASE_KEY")
    )

    if not url:
        st.error("❌ SUPABASE_URL missing है।")
        return None

    if not key:
        st.error("❌ Supabase Publishable/Anon Key missing है।")
        return None

    if not url.startswith("https://"):
        st.error("❌ SUPABASE_URL गलत है।")
        return None

    try:
        return create_client(url, key)

    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
        return None


# =========================================================
# Admin Supabase Client
# =========================================================
# IMPORTANT:
# Service Role Key केवल trusted server-side operations
# के लिए इस्तेमाल होगी।
#
# इसे browser/client-side code में कभी expose नहीं करना है.
# =========================================================

@st.cache_resource
def init_supabase_admin() -> Client | None:

    url = _get_config("SUPABASE_URL")

    service_key = (
        _get_config("SUPABASE_SERVICE_ROLE_KEY")
        or _get_config("SUPABASE_SERVICE_KEY")
    )

    if not url:
        return None

    if not service_key:
        # Admin client optional है।
        # Normal login इसके बिना भी चल सकता है।
        return None

    try:
        return create_client(
            url,
            service_key
        )

    except Exception as e:
        st.error(
            f"❌ Supabase Admin connection failed: {e}"
        )
        return None


# =========================================================
# GLOBAL CLIENTS
# =========================================================

supabase = init_supabase()

# केवल trusted Streamlit server-side admin operations
supabase_admin = init_supabase_admin()
