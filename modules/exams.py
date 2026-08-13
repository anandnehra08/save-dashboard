import pandas as pd
import plotly.express as px
import streamlit as st
from database.supabase import supabase

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]
EXAM_TYPES = ["Unit Test 1", "Unit Test 2", "Half Yearly", "Final Exam"]
SUBJECTS = ["Mathematics", "Science", "English", "Hindi", "Social Studies", "Computer"]

def render_exams_module():
    st.markdown("## 📚 Exam Marks & Report Card Management")
    
    tab1, tab2, tab3 = st.tabs([
        "📝 Enter Exam Marks", 
        "📜 Individual Report Card", 
        "📊 Class Performance"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: MARKS ENTRY
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Enter Student Subject Marks")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sel_class = st.selectbox("Select Class", CLASSES, key="ex_cls")
        with c2:
            sel_sec = st.selectbox("Select Section", SECTIONS, key="ex_sec")
        with c3:
            sel_exam = st.selectbox("Exam Type", EXAM_TYPES, key="ex_type")
        with c4:
            sel_subject = st.selectbox("Subject", SUBJECTS, key="ex_sub")
            
        if supabase:
            try:
                # Fetch Students for selected class
                res = supabase.table("students") \
                    .select("sr_no, student_name, roll_no") \
                    .eq("class", sel_class) \
                    .eq("section", sel_sec) \
                    .order("roll_no") \
                    .execute()
                
                students = res.data or []
                
                if not students:
                    st.warning(f"No students found in {sel_class} - {sel_sec}.")
                else:
                    st.info(f"Adding marks for **{sel_subject}** ({sel_exam}) — Total Students: **{len(students)}**")
                    
                    with st.form("marks_entry_form"):
                        marks_payload = []
                        
                        for st_data in students:
                            sr = st_data["sr_no"]
                            name = st_data["student_name"]
                            roll = st_data["roll_no"]
                            
                            m_col1, m_col2 = st.columns([3, 2])
                            m_col1.write(f"**Roll #{roll}** - {name} (SR: {sr})")
                            marks = m_col2.number_input(
                                f"Marks (Out of 100) for SR {sr}", 
                                min_value=0.0, max_value=100.0, value=0.0, step=1.0,
                                key=f"marks_{sr}_{sel_subject}",
                                label_visibility="collapsed"
                            )
                            
                            marks_payload.append({
                                "sr_no": sr,
                                "exam_type": sel_exam,
                                "subject": sel_subject,
                                "marks_obtained": marks,
                                "max_marks": 100.0
                            })
                            
                        submit_marks = st.form_submit_button("💾 Save Exam Marks")
                        
                        if submit_marks:
                            try:
                                supabase.table("marks").upsert(marks_payload).execute()
                                st.success(f"✅ Marks for {sel_subject} saved successfully!")
                            except Exception as e:
                                st.error(f"Failed to save marks: {e}")
            except Exception as ex:
                st.error(f"Database error: {ex}")

    # -------------------------------------------------------------
    # TAB 2: REPORT CARD GENERATOR
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Generate Student Report Card")
        
        search_sr = st.number_input("Enter Student SR Number", min_value=1, step=1, key="rep_card_sr")
        sel_rep_exam = st.selectbox("Select Exam", EXAM_TYPES, key="rep_exam_sel")
        
        if st.button("🔍 Generate Report Card"):
            if supabase:
                try:
                    # Get Student Info
                    st_res = supabase.table("students").select("*").eq("sr_no", search_sr).execute()
                    
                    if not st_res.data:
                        st.warning("Student record not found.")
                    else:
                        student = st_res.data[0]
                        
                        # Get Marks Info
                        m_res = supabase.table("marks") \
                            .select("subject, marks_obtained, max_marks") \
                            .eq("sr_no", search_sr) \
                            .eq("exam_type", sel_rep_exam) \
                            .execute()
                            
                        marks_data = m_res.data or []
                        
                        if not marks_data:
                            st.warning(f"No marks found for {sel_rep_exam}.")
                        else:
                            # Display Report Card Header
                            st.markdown("---")
                            st.markdown(f"### 🏫 Campus ERP Pro - Official Report Card")
                            
                            ic1, ic2 = st.columns(2)
                            ic1.write(f"**Name:** {student.get('student_name')}")
                            ic1.write(f"**SR No:** {student.get('sr_no')} | **Roll No:** {student.get('roll_no')}")
                            ic2.write(f"**Class:** {student.get('class')} ({student.get('section')})")
                            ic2.write(f"**Exam:** {sel_rep_exam}")
                            
                            st.write("---")
                            
                            df_marks = pd.DataFrame(marks_data)
                            st.dataframe(df_marks, use_container_width=True)
                            
                            total_obtained = df_marks['marks_obtained'].sum()
                            total_max = df_marks['max_marks'].sum()
                            percentage = (total_obtained / total_max) * 100 if total_max > 0 else 0
                            
                            rc1, rc2, rc3 = st.columns(3)
                            rc1.metric("Total Marks", f"{total_obtained} / {total_max}")
                            rc2.metric("Percentage", f"{percentage:.2f}%")
                            rc3.metric("Result Status", "PASSED" if percentage >= 33 else "NEEDS IMPROVEMENT")
                except Exception as e:
                    st.error(f"Error fetching report card: {e}")

    # -------------------------------------------------------------
    # TAB 3: CLASS PERFORMANCE
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Class Marks & Subject Analytics")
        st.info("यहाँ आप परीक्षा के अनुसार पूरी क्लास का ओवरऑल परफॉर्मेंस देख सकते हैं।")
