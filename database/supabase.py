import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    # Fetch values from Streamlit Secrets or Environment Variables
    raw_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    raw_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY") or ""
    
    # Strip spaces and invisible formatting characters
    clean_url = str(raw_url).strip().rstrip("/")
    clean_key = str(raw_key).strip()
    
    if not clean_url or not clean_key:
        st.error("Supabase URL or Key is missing in Secrets!")
        return None

    # Ensure valid HTTPS scheme
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"
        
    try:
        return create_client(clean_url, clean_key)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return None

supabase = init_supabase()
import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    # URL and Key cleaning to prevent runtime connection errors
    raw_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    raw_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY") or ""
    
    clean_url = str(raw_url).strip().rstrip("/")
    clean_key = str(raw_key).strip()
    
    if not clean_url or not clean_key:
        st.error("❌ Supabase URL ya Key missing hai Secrets mein!")
        return None

    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"
        
    try:
        return create_client(clean_url, clean_key)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return None

supabase = init_supabase()
