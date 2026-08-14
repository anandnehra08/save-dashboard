from datetime import datetime
import pandas as pd
import streamlit as st
from database.supabase import supabase

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]
EXAM_TYPES = ["Unit Test 1", "Mid Term", "Unit Test 2", "Final Exam"]

def get_master_subjects():
    """Supabase की subjects_master टेबल से subjects की dynamic list लाएगा"""
    default_subjects = ["Maths", "Science", "English", "Hindi", "Physics", "Chemistry", "Social Studies"]
    if supabase:
        try:
            res = supabase.table("subjects_master").select("subject_name").order("subject_name").execute()
            if res.data:
                return [item["subject_name"] for item in res.data]
        except Exception as e:
            st.warning(f"⚠️ Master Subjects fetch करने में दिक्कत: {e}")
    return default_subjects

def render_exams_module():
    st.markdown("## 📝 Exam Management & Marks Entry")
    
    # Supabase से Dynamic Subjects लिस्ट निकालें
    all_subjects = get_master_subjects()
    
    # -------------------------------------------------------------
    # 🔒 ROLE & PERMISSION CHECKING (Session State)
    # -------------------------------------------------------------
    user_role = st.session_state.get('user_role', 'admin')
    assigned_class = st.session_state.get('assigned_class', 'Class 10')
    assigned_subjects = st.session_state.get('assigned_subjects', ["Maths", "Science"])
    
    # Restrict permissions for non-admin users
    is_teacher = user_role in ["class_teacher", "subject_teacher"]
    
    if is_teacher:
        st.info(f"🔒 **Teacher Access:** आपके पास **{', '.join(assigned_subjects)}** सब्जेक्ट(स) के मार्क्स मैनेज करने की अनुमति है।")

    tab1, tab2 = st.tabs([
        "✏️ Enter / Edit Marks", 
        "📊 Class Performance & Report Card"
    ])

    # -------------------------------------------------------------
    # TAB 1: MARKS ENTRY
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Enter Marks for Students")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            # Class Selectbox (Locked for Class Teacher if assigned)
            if is_teacher and assigned_class != "ALL":
                default_cls_idx = CLASSES.index(assigned_class) if assigned_class in CLASSES else 0
                selected_class = st.selectbox("Select Class", CLASSES, index=default_cls_idx, disabled=True, key="ex_cls")
            else:
                selected_class = st.selectbox("Select Class", CLASSES, key="ex_cls")
                
        with c2:
            selected_sec = st.selectbox("Select Section", SECTIONS, key="ex_sec")
            
        with c3:
            # 🔒 Subject Selectbox (Dynamic from DB + Teacher filter)
            available_subjects = assigned_subjects if (is_teacher and "ALL" not in assigned_subjects) else all_subjects
            selected_subject = st.selectbox("Select Subject", available_subjects, key="ex_sub")
            
        with c4:
            selected_exam = st.selectbox("Select Exam Type", EXAM_TYPES, key="ex_type")
            
        # -------------------------------------------------------------
        # ➕ DYNAMIC SUBJECT MASTER MANAGER (Admin Only)
        # -------------------------------------------------------------
        if not is_teacher:
            with st.expander("➕ Add New Subject to Master List"):
                col_sub1, col_sub2 = st.columns([3, 1])
                with col_sub1:
                    new_sub_input = st.text_input("Enter New Subject Name", key="new_sub_txt", placeholder="e.g. Computer Science")
                with col_sub2:
                    st.write("") # Alignment spacing
                    st.write("")
                    add_sub_btn = st.button("Save Subject", use_container_width=True)
                
                if add_sub_btn:
                    clean_sub = new_sub_input.strip()
                    if clean_sub and supabase:
                        try:
                            supabase.table("subjects_master").insert({"subject_name": clean_sub}).execute()
                            st.success(f"✅ Subject '{clean_sub}' मास्टर लिस्ट में सफलतापूर्वक जुड़ गया!")
                            st.rerun()
                        except Exception as sub_err:
                            st.error(f"❌ Subject जोड़ने में त्रुटि: {sub_err}")
                    elif not clean_sub:
                        st.warning("कृपया विषय का नाम लिखें।")

        st.write("---")

        if supabase:
            try:
                # Fetch Students for selected class and section
                res = supabase.table("students") \
                    .select("sr_no, student_name, roll_no") \
                    .eq("class", selected_class) \
                    .eq("section", selected_sec) \
                    .order("roll_no") \
                    .execute()
                    
                students = res.data or []

                if not students:
                    st.warning(f"⚠️ No students found in {selected_class} - {selected_sec}.")
                else:
                    # Fetch existing marks for this exam and subject
                    existing_marks = supabase.table("marks") \
                        .select("sr_no, marks_obtained, max_marks") \
                        .eq("class", selected_class) \
                        .eq("section", selected_sec) \
                        .eq("subject", selected_subject) \
                        .eq("exam_type", selected_exam) \
                        .execute()
                        
                    existing_map = {m['sr_no']: (m['marks_obtained'], m['max_marks']) for m in (existing_marks.data or [])}

                    max_marks_input = st.number_input("Maximum Marks for this Test", min_value=10, max_value=100, value=100, step=5)

                    with st.form("marks_entry_form"):
                        marks_payload = []
                        st.markdown(f"**Student Marks List ({selected_subject} - {selected_exam}):**")
                        
                        for st_data in students:
                            sr = st_data["sr_no"]
                            name = st_data.get("student_name", "N/A")
                            roll = st_data.get("roll_no", 0)
                            
                            prev_obtained, _ = existing_map.get(sr, (0.0, max_marks_input))
                            
                            mc1, mc2, mc3 = st.columns([1, 3, 2])
                            mc1.write(f"**Roll #{roll}**")
                            mc2.write(f"**{name}** (SR: {sr})")
                            
                            obtained_marks = mc3.number_input(
                                label=f"Marks for {sr}",
                                min_value=0.0,
                                max_value=float(max_marks_input),
                                value=float(prev_obtained),
                                step=0.5,
                                key=f"marks_{sr}_{selected_subject}",
                                label_visibility="collapsed"
                            )
                            
                            marks_payload.append({
                                "sr_no": sr,
                                "student_name": name,
                                "class": selected_class,
                                "section": selected_sec,
                                "subject": selected_subject,
                                "exam_type": selected_exam,
                                "marks_obtained": obtained_marks,
                                "max_marks": max_marks_input,
                                "entered_by": st.session_state.get('user_email', 'Teacher')
                            })

                        submit_marks = st.form_submit_button("💾 Save / Update Marks")
                        
                        if submit_marks:
                            try:
                                supabase.table("marks").upsert(
                                    marks_payload,
                                    on_conflict="sr_no, subject, exam_type"
                                ).execute()
                                st.success(f"✅ {len(marks_payload)} छात्रों के मार्क्स सफलतापूर्वक सेव हो गए!")
                            except Exception as e:
                                st.error(f"❌ Marks save करने में विफल: {e}")

            except Exception as ex:
                st.error(f"Database Error: {ex}")

    # -------------------------------------------------------------
    # TAB 2: PERFORMANCE REPORT
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Class Marks Summary & Analytics")
        
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            rep_class = st.selectbox("Select Class", CLASSES, key="rep_ex_cls")
        with rc2:
            rep_exam = st.selectbox("Select Exam", EXAM_TYPES, key="rep_ex_type")
        with rc3:
            rep_subject = st.selectbox("Select Subject Filter", ["ALL"] + all_subjects, key="rep_ex_sub")

        if supabase:
            try:
                query = supabase.table("marks") \
                    .select("sr_no, student_name, subject, exam_type, marks_obtained, max_marks") \
                    .eq("class", rep_class) \
                    .eq("exam_type", rep_exam)
                
                if rep_subject != "ALL":
                    query = query.eq("subject", rep_subject)
                    
                res = query.execute()
                marks_data = res.data or []

                if not marks_data:
                    st.warning("चुनी गई क्लास और एग्ज़ाम के लिए कोई मार्क्स डेटा उपलब्ध नहीं है।")
                else:
                    mdf = pd.DataFrame(marks_data)
                    st.dataframe(mdf, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching report: {e}")
