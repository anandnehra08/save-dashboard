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
                    # साफ़ और व्यवस्थित कॉलम प्रदर्शन
                    rename_cols = {
                        "sr_no": "SR No",
                        "student_name": "Student Name",
                        "father_name": "Father Name",
                        "mother_name": "Mother Name",
                        "class": "Class",
                        "section": "Section",
                        "roll_no": "Roll No",
                        "gender": "Gender",
                        "mobile": "Mobile",
                        "bus_route": "Bus Route",
                        "drop_point": "Drop Point"
                    }
                    df = df.rename(columns=rename_cols)
                    display_cols = [col for col in list(rename_cols.values()) if col in df.columns]
                    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
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
                        st.session_state['searched_student'] = res.data[0]
                        st.session_state['delete_sr'] = search_sr
                    else:
                        st.warning("Student not found.")
                        st.session_state.pop('searched_student', None)
                        st.session_state.pop('delete_sr', None)
                except Exception as e:
                    st.error(f"Error searching student: {e}")
        
        # ADVANCED CARD DISPLAY (Replacing JSON)
        student = st.session_state.get('searched_student')
        if student and st.session_state.get('delete_sr') == search_sr:
            st.markdown("---")
            st.markdown(f"### 🎯 छात्र प्रोफाइल: **{student.get('student_name', 'N/A')}**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(
                    """
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;">
                        <h4 style="margin-top:0; color: #2C3E50;">👤 व्यक्तिगत विवरण</h4>
                    """, unsafe_allow_html=True
                )
                st.write(f"**SR No:** `{student.get('sr_no', 'N/A')}`")
                st.write(f"**छात्र का नाम:** {student.get('student_name', 'N/A')}")
                st.write(f"**पिता का नाम:** {student.get('father_name', 'N/A')}")
                st.write(f"**माता का नाम:** {student.get('mother_name', 'N/A')}")
                st.write(f"**लिंग:** {student.get('gender', 'N/A')}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(
                    """
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #2196F3;">
                        <h4 style="margin-top:0; color: #2C3E50;">📚 अकादमिक विवरण</h4>
                    """, unsafe_allow_html=True
                )
                st.write(f"**कक्षा:** {student.get('class', 'N/A')}")
                st.write(f"**सेक्शन:** {student.get('section', 'N/A')}")
                st.write(f"**रोल नंबर:** {student.get('roll_no', 'N/A')}")
                st.write(f"**आधार स्टेटस:** {'दर्ज है' if student.get('aadhaar') else 'दर्ज नहीं'}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col3:
                st.markdown(
                    """
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #FF9800;">
                        <h4 style="margin-top:0; color: #2C3E50;">🚌 परिवहन व संपर्क</h4>
                    """, unsafe_allow_html=True
                )
                st.write(f"**मोबाइल:** {student.get('mobile') if student.get('mobile') else 'N/A'}")
                st.write(f"**बस रूट:** {student.get('bus_route') if student.get('bus_route') else 'N/A'}")
                st.write(f"**ड्रॉप पॉइंट:** {student.get('drop_point') if student.get('drop_point') else 'N/A'}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown("---")
            
            # Delete Button
            if st.button(f"🗑️ Confirm Delete Record SR: {search_sr}", key="btn_confirm_delete"):
                if supabase:
                    try:
                        supabase.table("students").delete().eq("sr_no", search_sr).execute()
                        st.success(f"Record for SR {search_sr} deleted successfully!")
                        st.session_state.pop('searched_student', None)
                        st.session_state.pop('delete_sr', None)
                        st.rerun()
                    except Exception as ed:
                        st.error(f"Failed to delete record: {ed}")
