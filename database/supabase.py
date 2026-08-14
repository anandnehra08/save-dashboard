import os
import streamlit as st
from supabase import create_client, Client, ClientOptions

@st.cache_resource
def init_supabase() -> Client:
    # 1. secrets.toml या Environment Variables से URL और Key निकालें
    raw_url = ""
    raw_key = ""

    try:
        if "supabase" in st.secrets:
            raw_url = st.secrets["supabase"].get("SUPABASE_URL", "")
            raw_key = st.secrets["supabase"].get("SUPABASE_KEY", "")
        else:
            raw_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL", "")
            raw_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY", "")
    except Exception:
        raw_url = os.environ.get("SUPABASE_URL", "")
        raw_key = os.environ.get("SUPABASE_KEY", "")

    # 2. URL और Key की सफ़ाई (Strip spaces and quotes)
    clean_url = str(raw_url).strip().rstrip("/").replace('"', '').replace("'", "")
    clean_key = str(raw_key).strip().replace('"', '').replace("'", "")

    # 3. Validation Check
    if not clean_url or not clean_key:
        st.error("❌ Supabase URL या Key missing है! कृपया `.streamlit/secrets.toml` फ़ाइल चेक करें।")
        return None

    # 4. HTTPS Protocol सुनिश्चित करें
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"

    # 5. Client Options तैयार करें (401 API Key Error Bypass करने के लिए)
    custom_headers = {
        "apiKey": clean_key,
        "Authorization": f"Bearer {clean_key}"
    }

    # 6. Client Connection स्थापित करें
    try:
        client = create_client(
            clean_url, 
            clean_key, 
            options=ClientOptions(headers=custom_headers)
        )
        return client
    except Exception as e:
        st.error(f"❌ Supabase कनेक्ट करने में विफलता: {e}")
        return None

# Global Supabase Client Instance
supabase = init_supabase()
