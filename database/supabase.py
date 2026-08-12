import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase URL ya Key missing hai Secrets mein!")
        return None
        
    # URL Cleaning to prevent DNS / Name or service not known errors
    url = url.strip().rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
        
    key = key.strip()
    
    return create_client(url, key)

supabase = init_supabase()
