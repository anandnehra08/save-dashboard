import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    raw_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    raw_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY") or ""
    
    clean_url = str(raw_url).strip().rstrip("/")
    clean_key = str(raw_key).strip()
    
    if not clean_url or not clean_key:
        st.error("⚠️ Supabase Credentials missing in Streamlit Secrets!")
        return None

    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"
        
    try:
        return create_client(clean_url, clean_key)
    except Exception as e:
        st.error(f"Failed to establish Supabase connection: {e}")
        return None

supabase = get_supabase_client()
