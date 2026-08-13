import pandas as pd
import streamlit as st
from database.supabase import supabase

CLASSES = [f"Class {i}" for i in range(1, 13)]

def render_students_module():
    st.markdown("## 👨‍🎓 Student Admission & Master Directory")
    
    tab1, tab2, tab3 = st.tabs([
        "📝 New Admission", 
        "📋 Live Student Directory", 
        "🔍 Search & Manage"
    ])
    
    # --- TAB 1: NEW ADMISSION ---
    with tab1:
        # Unique Form Key दी गई है ताकि Duplicate Form Key Error न आए
        with st.form(key="student_admission_form_v1", clear_on_submit=True):
            st.subheader("Student Personal & Academic Details")
            c1, c2 = st.columns(2)
            
            with c1:
                sr_no = st.number_input("SR Number*", min_value=1, step=1)
                student_name = st.text_input("Student Full Name*")
                father_name = st.text_input("Father's Name")
                mother_name = st.text_input("Mother's Name")
                class_name = st.selectbox("Class*", CLASSES)
                bus_route = st.text_input("Bus Route (Optional)")
                
            with c2:
                roll_no = st.number_input("Roll Number", min_value=1, step=1)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                section = st.selectbox("Section*", ["A", "B", "C", "D"])
                mobile = st.text_input("Contact Mobile Number")
                aadhaar = st.text_input("Aadhaar / ID Reference (Optional)")
                drop_point = st.text_input("Drop Point (Optional)")
                
            submitted = st.form_submit_button("💾 Save Student Record")
            
            if submitted:
                if not student_name.strip():
                    st.error("Please enter the student's name.")
                else:
                    record = {
                        "sr_no": int(sr_no),
                        "student_name": student_name.strip(),
                        "roll_no": int(roll_no),
                        "gender": gender,
                        "class": class_name,
                        "section": section,
                        "father_name": father_name.strip(),
                        "mother_name": mother_name.strip(),
                        "mobile": mobile.strip(),
                        "bus_route": bus_route.strip(),
                        "drop_point": drop_point.strip(),
                        "aadhaar": aadhaar.strip()
                    }
                    
                    if supabase:
                        try:
                            supabase.table("students").insert(record).execute()
                            st.success(f"✅ Student **{student_name}** (SR: {sr_no}) created successfully!")
                        except Exception as e:
                            st.error(f"❌ Error saving to database: {e}")

    # --- TAB 2: LIVE DIRECTORY ---
    with tab2:
        st.subheader("Real-time Database Directory")
        if supabase:
            try:
                res = supabase.table("students").select("*").execute()
                if res.data:
                    df = pd.DataFrame(res.data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No students found in the database.")
            except Exception as e:
                st.error(f"Error fetching directory: {e}")

    # --- TAB 3: SEARCH & MANAGE ---
    with tab3:
        st.subheader("Search & Delete Student")
        search_sr = st.number_input("Enter SR No to Search", min_value=1, step=1, key="search_sr_input")
        
        if st.button("🔍 Search Student", key="btn_search_student"):
            if supabase:
                try:
                    res = supabase.table("students").select("*").eq("sr_no", search_sr).execute()
                    if res.data:
                        student = res.data[0]
                        st.json(student)
                        st.session_state['delete_sr'] = search_sr
                    else:
                        st.warning("Student not found.")
                        st.session_state.pop('delete_sr', None)
                except Exception as e:
                    st.error(f"Error searching student: {e}")
                    
        if st.session_state.get('delete_sr') == search_sr:
            if st.button(f"🗑️ Confirm Delete Record SR: {search_sr}", key="btn_confirm_delete"):
                if supabase:
                    try:
                        supabase.table("students").delete().eq("sr_no", search_sr).execute()
                        st.success(f"Record for SR {search_sr} deleted successfully!")
                        st.session_state.pop('delete_sr', None)
                    except Exception as ed:
                        st.error(f"Failed to delete record: {ed}")
