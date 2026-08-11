import streamlit as st
import urllib.parse

st.set_page_config(page_title="School ERP Dashboard", layout="wide")

# Sidebar Navigation (NEET CBT aur Aadhar Link Hata Diya Hai)
menu = st.sidebar.selectbox(
    "Navigation Menu", 
    [
        "Home", 
        "Mark Attendance & WhatsApp Alert", 
        "Bilingual Paper Generator", 
        "NCERT Books"
    ]
)

# 1. HOME SECTION
if menu == "Home":
    st.title("🏫 School ERP Dashboard")
    st.write("Welcome! Select an option from the sidebar to manage school tasks.")

# 2. MARK ATTENDANCE & WHATSAPP ALERT
elif menu == "Mark Attendance & WhatsApp Alert":
    st.header("📲 Attendance & WhatsApp Notification")
    
    with st.form("attendance_form"):
        student_name = st.text_input("Student Name / छात्र का नाम")
        parent_phone = st.text_input("Parent Phone Number (e.g. 919876543210)")
        status = st.radio("Status", ["Present", "Absent"])
        submitted = st.form_submit_button("Mark Attendance")
        
    if submitted:
        if student_name and parent_phone:
            message = f"Namaste! Aapke bachhe {student_name} ki aaj ki attendance status hai: {status}."
            encoded_msg = urllib.parse.quote(message)
            whatsapp_url = f"https://api.whatsapp.com/send?phone={parent_phone}&text={encoded_msg}"
            
            st.success(f"Attendance marked for {student_name} ({status})")
            st.markdown(f"👉 **[Click Here to Send WhatsApp Alert to Parent]({whatsapp_url})**")
        else:
            st.warning("Please fill in Student Name and Phone Number.")

# 3. BILINGUAL PAPER GENERATOR
elif menu == "Bilingual Paper Generator":
    st.header("📝 Bilingual Question Paper Generator")
    
    st.subheader("Add Questions")
    q_en = st.text_area("Question in English", "What is Photosynthesis?")
    q_hi = st.text_area("Question in Hindi", "प्रकाश संश्लेषण क्या है?")
    marks = st.number_input("Marks", min_value=1, max_value=10, value=2)
    
    if st.button("Generate Paper Preview"):
        st.markdown("---")
        st.subheader("Question Paper Preview")
        st.write(f"**Q. {q_en}** [{marks} Marks]")
        st.write(f"**प्र. {q_hi}** [{marks} अंक]")
        st.markdown("---")

# 4. NCERT BOOKS VIEWER
elif menu == "NCERT Books":
    st.header("📚 NCERT Book Viewer")
    pdf_url = st.text_input(
        "Enter NCERT PDF Link", 
        "https://ncert.nic.in/textbook/pdf/keph101.pdf"
    )
    
    if pdf_url:
        st.info("Loading NCERT Document...")
        iframe_src = f"https://docs.google.com/gview?url={pdf_url}&embedded=true"
        st.components.v1.iframe(iframe_src, height=650, scrolling=True)
