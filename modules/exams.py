import streamlit as st
import pandas as pd
import plotly.express as px
from database.supabase import supabase

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]
EXAM_TYPES = ["Unit Test 1", "Mid Term", "Unit Test 2", "Final Exam"]

def render_exams_module():
    st.markdown("## 📚 Exam Marks & Report Card Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Enter Exam Marks", 
        "📚 Manage Subjects",
        "📜 Individual Report Card", 
        "📊 Class Performance"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: ENTER EXAM MARKS
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Enter Student Subject Marks")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            selected_class = st.selectbox("Select Class", CLASSES, key="exam_cls")
        with c2:
            selected_sec = st.selectbox("Select Section", SECTIONS, key="exam_sec")
        with c3:
            selected_exam = st.selectbox("Exam Type", EXAM_TYPES, key="exam_type")
            
        if supabase:
            try:
                # 1. Fetch Subjects safely
                sub_res = supabase.table("subjects").select("subject_name").eq("class", selected_class).execute()
                subject_list = [s["subject_name"] for s in (sub_res.data or []) if "subject_name" in s]
                
                with c4:
                    if subject_list:
                        selected_subject = st.selectbox("Select Subject", subject_list, key="exam_sub")
                    else:
                        selected_subject = None
                
                if not subject_list:
                    st.info(f"💡 {selected_class} के लिए कोई सब्जेक्ट नहीं मिला। कृपया पहले '**📚 Manage Subjects**' टैब में जाकर सब्जेक्ट जोड़ें।")
                else:
                    # 2. Fetch Students safely
                    st_res = supabase.table("students") \
                        .select("sr_no, student_name, roll_no") \
                        .eq("class", selected_class) \
                        .eq("section", selected_sec) \
                        .order("roll_no") \
                        .execute()
                    
                    students = st_res.data or []
                    
                    if not students:
                        st.warning(f"⚠️ No students found in {selected_class} - {selected_sec}. कृपया 'Student Directory' में स्टूडेंट दर्ज करें।")
                    else:
                        st.success(f"📋 Found {len(students)} students for {selected_subject} ({selected_exam})")
                        max_marks = st.number_input("Max Marks", min_value=10, max_value=200, value=100)
                        
                        # Fetch existing marks with error safety
                        existing_marks_map = {}
                        try:
                            existing_marks_res = supabase.table("exam_marks") \
                                .select("*") \
                                .eq("class", selected_class) \
                                .eq("section", selected_sec) \
                                .eq("exam_type", selected_exam) \
                                .eq("subject", selected_subject) \
                                .execute()
                            
                            for item in (existing_marks_res.data or []):
                                sr_val = item.get('sr_no')
                                marks_val = item.get('marks_obtained', item.get('marks', 0))
                                if sr_val is not None:
                                    existing_marks_map[sr_val] = marks_val
                        except Exception:
                            existing_marks_map = {}
                        
                        with st.form("marks_entry_form"):
                            st.write("---")
                            marks_payload = []
                            
                            for st_data in students:
                                sr = st_data["sr_no"]
                                name = st_data.get("student_name", "N/A")
                                roll = st_data.get("roll_no", 0)
                                default_val = float(existing_marks_map.get(sr, 0.0))
                                
                                sc1, sc2, sc3 = st.columns([1, 3, 2])
                                sc1.write(f"**Roll #{roll}**")
                                sc2.write(f"**{name}** (SR: {sr})")
                                
                                marks = sc3.number_input(
                                    label=f"Marks for {sr}",
                                    min_value=0.0,
                                    max_value=float(max_marks),
                                    value=default_val,
                                    key=f"marks_{sr}",
                                    label_visibility="collapsed"
                                )
                                
                                marks_payload.append({
                                    "sr_no": sr,
                                    "student_name": name,
                                    "class": selected_class,
                                    "section": selected_sec,
                                    "exam_type": selected_exam,
                                    "subject": selected_subject,
                                    "marks_obtained": marks,
                                    "max_marks": max_marks
                                })
                            
                            submit_marks = st.form_submit_button("💾 Save Subject Marks")
                            
                            if submit_marks:
                                try:
                                    supabase.table("exam_marks").upsert(
                                        marks_payload, 
                                        on_conflict="sr_no, exam_type, subject"
                                    ).execute()
                                    st.success(f"✅ Marks saved successfully for {selected_subject}!")
                                except Exception as e:
                                    st.error(f"Failed to save marks: {e}")
            except Exception as ex:
                st.error(f"Database Error: {ex}")

    # -------------------------------------------------------------
    # TAB 2: MANAGE SUBJECTS
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Add / Manage Class Subjects")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            add_sub_class = st.selectbox("Select Class to Add Subject", CLASSES, key="add_sub_cls")
        with sc2:
            new_subject_name = st.text_input("Enter Subject Name (e.g., Mathematics, English, Science)")
            
        if st.button("➕ Add Subject"):
            if new_subject_name.strip():
                try:
                    supabase.table("subjects").insert({
                        "class": add_sub_class,
                        "subject_name": new_subject_name.strip()
                    }).execute()
                    st.success(f"✅ Subject '{new_subject_name}' added to {add_sub_class} successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding subject: {e}")
            else:
                st.warning("Please enter a valid subject name.")
                
        st.write("---")
        st.markdown(f"##### Existing Subjects for {add_sub_class}")
        try:
            curr_subs = supabase.table("subjects").select("*").eq("class", add_sub_class).execute()
            if curr_subs.data:
                sub_df = pd.DataFrame(curr_subs.data)
                cols_to_show = [c for c in ["id", "subject_name"] if c in sub_df.columns]
                st.dataframe(sub_df[cols_to_show if cols_to_show else sub_df.columns], use_container_width=True)
            else:
                st.info(f"No subjects registered for {add_sub_class} yet.")
        except Exception as e:
            st.error(f"Error fetching subjects: {e}")

    # -------------------------------------------------------------
    # TAB 3: INDIVIDUAL REPORT CARD
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Generate Student Report Card")
        
        rc1, rc2 = st.columns(2)
        with rc1:
            rep_sr = st.number_input("Enter Student SR Number", min_value=1, step=1, key="rep_sr_no")
        with rc2:
            rep_exam = st.selectbox("Select Exam Type", EXAM_TYPES, key="rep_exam_type")
            
        if st.button("📄 View Report Card"):
            try:
                marks_res = supabase.table("exam_marks") \
                    .select("*") \
                    .eq("sr_no", rep_sr) \
                    .eq("exam_type", rep_exam) \
                    .execute()
                    
                marks_data = marks_res.data or []
                
                if not marks_data:
                    st.warning("No marks records found for this SR Number and Exam.")
                else:
                    df_rep = pd.DataFrame(marks_data)
                    
                    if "marks_obtained" not in df_rep.columns and "marks" in df_rep.columns:
                        df_rep["marks_obtained"] = df_rep["marks"]
                    if "max_marks" not in df_rep.columns:
                        df_rep["max_marks"] = 100
                    if "student_name" not in df_rep.columns:
                        df_rep["student_name"] = "N/A"
                    if "class" not in df_rep.columns:
                        df_rep["class"] = "N/A"
                    if "section" not in df_rep.columns:
                        df_rep["section"] = "N/A"
                    
                    st_name = df_rep["student_name"].iloc[0]
                    st_cls = df_rep["class"].iloc[0]
                    st_sec = df_rep["section"].iloc[0]
                    
                    st.success(f"Report Card Generated for **{st_name}** ({st_cls} - {st_sec})")
                    
                    tot_obtained = df_rep['marks_obtained'].sum()
                    tot_max = df_rep['max_marks'].sum()
                    percentage = (tot_obtained / tot_max * 100) if tot_max > 0 else 0
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Total Marks Obtained", f"{tot_obtained:.0f} / {tot_max:.0f}")
                    col_m2.metric("Percentage", f"{percentage:.2f}%")
                    col_m3.metric("Grade", "A+" if percentage>=90 else "A" if percentage>=75 else "B" if percentage>=60 else "C" if percentage>=33 else "F")
                    
                    display_cols = [c for c in ["subject", "marks_obtained", "max_marks"] if c in df_rep.columns]
                    st.dataframe(df_rep[display_cols], use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching report card: {e}")

    # -------------------------------------------------------------
    # TAB 4: CLASS PERFORMANCE
    # -------------------------------------------------------------
    with tab4:
        st.subheader("Class Exam Analytics")
        p_cls = st.selectbox("Select Class", CLASSES, key="perf_cls")
        p_exam = st.selectbox("Select Exam", EXAM_TYPES, key="perf_exam")
        
        if st.button("📊 Analyze Class Performance"):
            try:
                perf_res = supabase.table("exam_marks") \
                    .select("*") \
                    .eq("class", p_cls) \
                    .eq("exam_type", p_exam) \
                    .execute()
                    
                p_data = perf_res.data or []
                if p_data:
                    pdf = pd.DataFrame(p_data)
                    if "marks_obtained" not in pdf.columns and "marks" in pdf.columns:
                        pdf["marks_obtained"] = pdf["marks"]
                    
                    fig = px.bar(
                        pdf, 
                        x="student_name" if "student_name" in pdf.columns else "sr_no", 
                        y="marks_obtained", 
                        color="subject" if "subject" in pdf.columns else None, 
                        barmode="group", 
                        title=f"Student Performance - {p_cls} ({p_exam})"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No marks data found for this class & exam.")
            except Exception as e:
                st.error(f"Error analyzing performance: {e}")
