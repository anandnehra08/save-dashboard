import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource(ttl=600)
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase URL or Key is missing in Secrets!")
        return None
        
    return create_client(url, key)

supabase = init_supabase()
