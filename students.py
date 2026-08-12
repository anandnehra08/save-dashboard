import streamlit as st
from database.supabase import supabase

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]

def render_student_module():
    st.markdown("### 📖 Student Admission & SR Register")
    
    with st.form("student_admission_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            sr_no = st.number_input("SR Number (Unique)", min_value=1, step=1)
            roll_no = st.number_input("Roll Number", min_value=1, step=1)
            student_name = st.text_input("Student Full Name *")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with c2:
            student_class = st.selectbox("Class *", classes_list)
            section = st.selectbox("Section *", sections_list)
            father_name = st.text_input("Father's Name")
            mother_name = st.text_input("Mother's Name")
        with c3:
            mobile = st.text_input("Mobile Number")
            aadhaar = st.text_input("Aadhaar Number")
            bus_route = st.text_input("Bus Route / Stop")
            drop_point = st.text_input("Drop Point")

        if st.form_submit_button("💾 Save Student Record"):
            if not student_name:
                st.error("Student Name is mandatory!")
            else:
                record = {
                    "sr_no": sr_no,
                    "roll_no": roll_no,
                    "student_name": student_name,
                    "gender": gender,
                    "class": student_class,
                    "section": section,
                    "father_name": father_name,
                    "mother_name": mother_name,
                    "mobile": mobile,
                    "aadhaar": aadhaar,
                    "bus_route": bus_route,
                    "drop_point": drop_point
                }
                try:
                    if supabase:
                        supabase.table("students").insert(record).execute()
                        st.success(f"Student '{student_name}' registered successfully with SR No: {sr_no}")
                except Exception as e:
                    st.error(f"Error saving student: {e}")
