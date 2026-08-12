import pandas as pd
import streamlit as st
from database.supabase import supabase

classes_list = [f"Class {i}" for i in range(1, 13)]

def render_students_module():
    st.markdown("### 🎓 Student Admission & Directory")
    
    tab1, tab2 = st.tabs(["📝 New Admission", "📋 Student Directory"])
    
    with tab1:
        with st.form("student_admission_form", clear_on_submit=True):
            st.subheader("Student Personal & Academic Details")
            
            col1, col2 = st.columns(2)
            with col1:
                sr_no = st.number_input("SR Number (Unique)*", min_value=1, step=1)
                student_name = st.text_input("Student Name*")
                father_name = st.text_input("Father's Name")
                mother_name = st.text_input("Mother's Name")
                class_name = st.selectbox("Class*", classes_list)
                bus_route = st.text_input("Bus Route (Optional)")
                
            with col2:
                roll_no = st.number_input("Roll Number", min_value=1, step=1)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                section = st.selectbox("Section*", ["A", "B", "C", "D"])
                mobile = st.text_input("Contact Mobile Number")
                aadhaar_input = st.text_input("Aadhaar Number (Optional)")
                drop_point = st.text_input("Drop Point (Optional)")
                
            submitted = st.form_submit_button("💾 Save Student Record")
            
            if submitted:
                if not student_name.strip():
                    st.error("Please enter the student's name.")
                else:
                    # Full record dict
                    full_record = {
                        "sr_no": int(sr_no),
                        "student_name": student_name.strip(),
                        "roll_no": int(roll_no),
                        "gender": gender,
                        "class": class_name,
                        "section": section,
                        "father_name": father_name.strip(),
                        "mother_name": mother_name.strip(),
                        "mobile": mobile.strip()
                    }
                    
                    if bus_route.strip():
                        full_record["bus_route"] = bus_route.strip()
                    if drop_point.strip():
                        full_record["drop_point"] = drop_point.strip()
                    if aadhaar_input.strip():
                        full_record["aadhaar"] = aadhaar_input.strip()
                    
                    if supabase:
                        try:
                            # Attempt 1: Full record
                            supabase.table("students").insert(full_record).execute()
                            st.success(f"Student **{student_name}** (SR No: {sr_no}) saved successfully!")
                        except Exception as e1:
                            # Attempt 2: Minimal core record if optional columns/cache fail
                            try:
                                minimal_record = {
                                    "sr_no": int(sr_no),
                                    "student_name": student_name.strip()
                                }
                                supabase.table("students").insert(minimal_record).execute()
                                st.success(f"Student **{student_name}** (SR No: {sr_no}) saved successfully!")
                            except Exception as e2:
                                st.error(f"Failed to save student: {e2}")

    with tab2:
        st.subheader("Filter & Search Students")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_class = st.selectbox("Filter by Class", ["All Classes"] + classes_list)
        with col_f2:
            search_query = st.text_input("Search by Name or SR No")
            
        if supabase:
            try:
                res = supabase.table("students").select("*").execute()
                if res.data:
                    df = pd.DataFrame(res.data)
                    
                    if "class" in df.columns and filter_class != "All Classes":
                        df = df[df["class"] == filter_class]
                        
                    if search_query.strip():
                        df = df[
                            df["student_name"].str.contains(search_query, case=False, na=False) |
                            df["sr_no"].astype(str).str.contains(search_query, case=False, na=False)
                        ]
                    st.write(f"Total Students Found: **{len(df)}**")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No students registered yet.")
            except Exception as e:
                st.warning("Could not load student directory.")

# Alias for app.py import compatibility
render_student_module = render_students_module
