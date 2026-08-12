import pandas as pd
import streamlit as st
from database.supabase import supabase

def render_exams_module():
    st.markdown("### 📝 Exam Marks Entry")
    
    with st.form("exam_marks_form"):
        c1, c2 = st.columns(2)
        with c1:
            sr_no = st.number_input("Student SR Number", min_value=1, step=1)
            exam_term = st.selectbox("Exam Term", ["Unit Test 1", "Half Yearly", "Unit Test 2", "Annual Exam"])
        with c2:
            subject = st.selectbox("Subject", ["English", "Hindi", "Mathematics", "Science", "Social Science"])
            marks_obtained = st.number_input("Marks Obtained", min_value=0.0, max_value=100.0, step=1.0)
            max_marks = st.number_input("Max Marks", value=100.0, disabled=True)
            
        if st.form_submit_button("💾 Save Marks"):
            record = {
                "sr_no": sr_no,
                "exam_term": exam_term,
                "subject": subject,
                "marks_obtained": marks_obtained,
                "max_marks": max_marks
            }
            try:
                if supabase:
                    supabase.table("exams").insert(record).execute()
                    st.success("Marks recorded successfully!")
            except Exception as e:
                st.error(f"Error saving exam marks: {e}")
