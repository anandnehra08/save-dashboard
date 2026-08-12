import pandas as pd
import streamlit as st
from database.supabase import supabase

def render_search_module():
    st.markdown("### 🔍 Live Student Directory & Search")
    
    if not supabase:
        st.warning("Database connection unavailable.")
        return

    search_query = st.text_input("Search Student by Name, SR No, or Class", "")
    
    res = supabase.table("students").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        
        if search_query:
            df = df[
                df['student_name'].str.contains(search_query, case=False, na=False) |
                df['sr_no'].astype(str).str.contains(search_query, case=False, na=False) |
                df['class'].str.contains(search_query, case=False, na=False)
            ]
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No student records found.")
