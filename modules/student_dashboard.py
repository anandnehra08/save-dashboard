import streamlit as st
import pandas as pd
from database.supabase import supabase

def render_student_dashboard():
    st.markdown("## 🎓 Student & Parent Portal")
    st.write("यहाँ छात्र और अभिभावक अपना रिजल्ट और अटेंडेंस देख सकते हैं।")
    
    sr_number = st.number_input("Enter Student SR Number:", min_value=1, value=101)
    
    if st.button("🔍 View Details"):
        if supabase:
            try:
                res = supabase.table("students").select("*").eq("sr_no", sr_number).execute()
                data = res.data or []
                if data:
                    st.success(f"Student Found: {data[0].get('student_name')}")
                    st.json(data[0])
                else:
                    st.warning("No record found for this SR Number.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
        else:
            st.info("Demo Mode: Supabase connection not configured.")
