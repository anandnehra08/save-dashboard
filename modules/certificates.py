import datetime
import streamlit as st
from database.supabase import supabase
from utils.certificate_pdf import generate_certificate_pdf

def render_certificates_module():
    st.markdown("### 📜 Certificate Generator (TC / Study / Conduct)")
    
    sr_no = st.number_input("Enter Student SR Number", min_value=1, step=1)
    
    if st.button("🔍 Fetch Student Details"):
        if supabase:
            res = supabase.table("students").select("*").eq("sr_no", sr_no).execute()
            if res.data:
                st.session_state.cert_student = res.data[0]
                st.success("Student details loaded!")
            else:
                st.error("Student not found!")

    if "cert_student" in st.session_state:
        s = st.session_state.cert_student
        st.write(f"**Generating Certificate for:** {s['student_name']} ({s['class']}-{s['section']})")
        
        cert_type = st.selectbox("Certificate Type", ["Transfer Certificate (TC)", "Study / Bonafide Certificate", "Character Certificate"])
        reason = st.text_input("Reason / Remarks", "Good Conduct")
        
        if st.button("🖨️ Generate Certificate PDF"):
            cert_data = {
                "cert_no": f"CERT-{sr_no}-{datetime.datetime.now().strftime('%M%S')}",
                "issue_date": str(datetime.date.today()),
                "cert_type": cert_type,
                "student_name": s['student_name'],
                "father_name": s.get('father_name', 'N/A'),
                "mother_name": s.get('mother_name', 'N/A'),
                "class_sec": f"{s['class']} - {s['section']}",
                "dob": s.get('dob', 'N/A'),
                "reason_conduct": reason
            }
            
            pdf_path = generate_certificate_pdf(cert_data)
            
            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="📥 Download Certificate PDF",
                    data=file,
                    file_name=f"{cert_type}_{sr_no}.pdf",
                    mime="application/pdf"
                )
