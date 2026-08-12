import pandas as pd
import streamlit as st
from database.supabase import supabase

def render_staff_module():
    st.markdown("### 👨‍🏫 Staff Directory & Payroll")
    
    tab1, tab2 = st.tabs(["➕ Add Staff", "📋 Staff List"])
    
    with tab1:
        with st.form("staff_form"):
            c1, c2 = st.columns(2)
            with c1:
                staff_id = st.text_input("Staff ID (Unique)", "EMP-101")
                name = st.text_input("Full Name *")
                role = st.selectbox("Role", ["Teacher", "Administrator", "Accountant", "Support Staff"])
            with c2:
                mobile = st.text_input("Mobile Number")
                salary = st.number_input("Monthly Salary (₹)", min_value=0.0, step=1000.0)
            
            if st.form_submit_button("💾 Save Staff Member"):
                record = {
                    "staff_id": staff_id,
                    "name": name,
                    "role": role,
                    "mobile": mobile,
                    "salary": salary
                }
                try:
                    if supabase:
                        supabase.table("staff").insert(record).execute()
                        st.success(f"Staff member {name} added!")
                except Exception as e:
                    st.error(f"Error saving staff: {e}")

    with tab2:
        if supabase:
            res = supabase.table("staff").select("*").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
            else:
                st.info("No staff records found.")
