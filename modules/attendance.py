import datetime
import pandas as pd
import streamlit as st
from database.supabase import supabase

classes_list = [f"Class {i}" for i in range(1, 13)]

def render_attendance_module():
    st.markdown("### 📈 Attendance Register")
    
    selected_class = st.selectbox("Select Class for Attendance", classes_list)
    att_date = st.date_input("Attendance Date", datetime.date.today())
    
    if supabase:
        res = supabase.table("students").select("sr_no, roll_no, student_name").eq("class", selected_class).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.write(f"Marking Attendance for **{selected_class}** ({len(df)} Students)")
            
            status_dict = {}
            for index, row in df.iterrows():
                col1, col2 = st.columns([3, 2])
                col1.write(f"**SR {row['sr_no']}** - {row['student_name']} (Roll: {row['roll_no']})")
                status_dict[row['sr_no']] = col2.radio(
                    "Status", 
                    ["Present", "Absent", "Leave"], 
                    key=f"att_{row['sr_no']}", 
                    horizontal=True
                )
            
            if st.button("💾 Submit Class Attendance"):
                records = []
                for sr_no, status in status_dict.items():
                    records.append({
                        "sr_no": sr_no,
                        "class": selected_class,
                        "date": str(att_date),
                        "status": status
                    })
                try:
                    supabase.table("attendance").insert(records).execute()
                    st.success("Attendance saved successfully!")
                except Exception as e:
                    st.error(f"Error saving attendance: {e}")
        else:
            st.info("No students found in this class.")
