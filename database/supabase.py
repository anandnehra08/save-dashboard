import os
import streamlit as st
from supabase import create_client, Client

# Supabase Secrets / Credentials Management
@st.cache_resource
def init_supabase() -> Client:
    try:
        # Check Streamlit Secrets first
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            return create_client(url, key)
        # Fallback to Environment Variables
        elif "SUPABASE_URL" in os.environ and "SUPABASE_KEY" in os.environ:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            return create_client(url, key)
        else:
            st.error("Supabase credentials missing! Set SUPABASE_URL & SUPABASE_KEY in Streamlit Secrets.")
            return None
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return None

supabase = init_supabase()
