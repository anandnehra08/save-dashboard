import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    supabase_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    supabase_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("Supabase credentials missing in secrets.toml!")
        return None
        
    return create_client(supabase_url, supabase_key)

supabase = init_supabase()
