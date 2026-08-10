import streamlit as st
from supabase import create_client, Client
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime

# --- 1. MOBILE ANDROID VIEW CONFIG ---
st.set_page_config(page_title="School Management ERP", page_icon="📱", layout="centered")

# Android UI Styling
st.markdown("""
    <style>
    .main { max-width: 500px; margin: 0 auto; }
    .stButton>button { width: 100%; border-radius: 10px; height: 45px; font-weight: bold; }
    .stSelectbox, .stTextInput, .stNumberInput { margin-bottom: 10px; }
    .card { background-color: #f9f9f9; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SUPABASE DATABASE CONNECTION ---
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Database Connection Failed. Check secrets.toml")
        return None

supabase = init_supabase()

# Session States
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

# --- 3. LOGIN & ONLINE PAYMENT SYSTEM ---
if not st.session_state.logged_in:
    st.title("🔐 School Portal Login")
    login_mode = st.radio("Select Login Mode", ["Admin (Free)", "Teacher / Staff (₹1000 Online Pay)"])

    if login_mode == "Admin (Free)":
        username = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.rerun()
            else:
                st.error("Invalid Admin Credentials!")

    else:
        mobile = st.text_input("Enter 10-digit Mobile Number")
        if mobile:
            st.info("Registration Fee: ₹1000 (One-time)")
            upi_id = "schoolfees@upi"
            pay_link = f"upi://pay?pa={upi_id}&pn=SchoolERP&am=1000&cu=INR"
            st.markdown(f"👉 **[Click Here to Pay ₹1000 via UPI/GPay/PhonePe]({pay_link})**")
            
            otp_input = st.text_input("Enter OTP (Use '1234' for Demo)", type="password")
            if st.button("Verify OTP & Activate Login"):
                if otp_input == "1234":
                    st.session_state.logged_in = True
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    st.error("Incorrect OTP")
    st.stop()

# --- 4. MAIN APP NAVIGATION ---
st.sidebar.markdown(f"### 👤 Role: {st.session_state.role}")
if st.sidebar.button("🔴 Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.selectbox("📋 Menu Options", [
    "📅 Attendance & SMS",
    "✏️ Auto-Fill Roll No Student Edit",
    "💳 Fees Link & Direct Call",
    "📝 Exam Marks (UT, Half-Yearly, Yearly)",
    "📄 Exam Question Paper Generator (PDF)",
    "📚 NCERT Books (Class 1 to 12)"
])

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]

# --- FEATURE 1: ATTENDANCE & SMS RECORD ---
if menu == "📅 Attendance & SMS":
    st.title("📅 Attendance & Daily SMS")
    
    col1, col2 = st.columns(2)
    with col1:
        sel_class = st.selectbox("Class", classes_list)
    with col2:
        sel_sec = st.selectbox("Section", sections_list)
    
    att_date = st.date_input("Date", datetime.date.today())
    roll_no = st.number_input("Student Roll No", min_value=1, step=1)
    status = st.radio("Status", ["Present", "Absent"], horizontal=True)
    parent_mob = st.text_input("Parent Mobile Number")

    if st.button("Save Attendance & Send SMS"):
        msg = f"Dear Parent, your child (Roll No: {roll_no}, {sel_class}-{sel_sec}) is marked {status} on {att_date}."
        encoded_msg = urllib.parse.quote(msg)
        sms_url = f"https://wa.me/91{parent_mob}?text={encoded_msg}"
        
        if supabase:
            try:
                supabase.table("attendance").insert({
                    "roll_no": roll_no, "class": sel_class, "section": sel_sec,
                    "date": str(att_date), "status": status
                }).execute()
            except Exception as e:
                pass
        
        st.success(f"Attendance Recorded as {status}!")
        if parent_mob:
            st.markdown(f"📲 **[Click Here to Send WhatsApp/SMS Alert]({sms_url})**")

# --- FEATURE 2: AUTO-FILL STUDENT EDIT VIA ROLL NO ---
elif menu == "✏️ Auto-Fill Roll No Student Edit":
    st.title("✏️ Add / Edit Student")
    
    search_roll = st.number_input("Enter Roll No to Search/Fill Data", min_value=1, step=1)
    
    existing_data = None
    if st.button("🔍 Fetch Student Details"):
        if supabase:
            res = supabase.table("students").select("*").eq("roll_no", search_roll).execute()
            if res.data:
                existing_data = res.data[0]
                st.success("Student Data Found!")
            else:
                st.warning("New Student Roll No.")

    default_name = existing_data["name"] if existing_data else ""
    default_father = existing_data["father_name"] if existing_data else ""
    default_mobile = existing_data["mobile"] if existing_data else ""

    s_name = st.text_input("Student Name", value=default_name)
    f_name = st.text_input("Father Name", value=default_father)
    s_class = st.selectbox("Class", classes_list)
    s_sec = st.selectbox("Section", sections_list)
    s_mob = st.text_input("Mobile Number", value=default_mobile)

    if st.button("💾 Save / Update Student Details"):
        payload = {
            "roll_no": search_roll, "name": s_name, "father_name": f_name,
            "class": s_class, "section": s_sec, "mobile": s_mob
        }
        if supabase:
            supabase.table("students").upsert(payload).execute()
            st.success("Student details successfully saved in database!")

# --- FEATURE 3: FEES PAYMENT LINK & DIRECT CALL ---
elif menu == "💳 Fees Link & Direct Call":
    st.title("💳 Fees Payment & Call")
    
    student_mob = st.text_input("Parent Mobile Number")
    fee_amount = st.number_input("Fee Due Amount (₹)", min_value=100, value=1000)

    c1, c2 = st.columns(2)
    with c1:
        if student_mob:
            st.markdown(f'<a href="tel:{student_mob}"><button style="background-color:#008CBA;color:white;width:100%;height:45px;border-radius:10px;">📞 Direct Call Parent</button></a>', unsafe_allow_html=True)
    
    with c2:
        upi_pay = f"upi://pay?pa=schoolfees@upi&pn=SchoolName&am={fee_amount}&cu=INR"
        st.markdown(f'👉 **[Send UPI Payment Link (₹{fee_amount})]({upi_pay})**')

# --- FEATURE 4: EXAM MARKS ---
elif menu == "📝 Exam Marks (UT, Half-Yearly, Yearly)":
    st.title("📝 Student Marks Record")
    
    exam_type = st.selectbox("Select Exam Type", ["Unit Test 1", "Unit Test 2", "Half-Yearly Exam", "Yearly Exam"])
    s_class = st.selectbox("Class", classes_list)
    s_roll = st.number_input("Roll No", min_value=1)

    st.subheader("Subject Marks:")
    col1, col2 = st.columns(2)
    with col1:
        m_hindi = st.number_input("Hindi", 0, 100)
        m_english = st.number_input("English", 0, 100)
    with col2:
        m_maths = st.number_input("Maths", 0, 100)
        m_sci = st.number_input("Science", 0, 100)

    if st.button("Save Marks Record"):
        if supabase:
            supabase.table("marks").insert({
                "exam_type": exam_type, "class": s_class, "roll_no": s_roll,
                "hindi": m_hindi, "english": m_english, "maths": m_maths, "science": m_sci
            }).execute()
        st.success(f"Marks saved successfully for {exam_type}!")

# --- FEATURE 5: EXAM QUESTION PAPER GENERATOR ---
elif menu == "📄 Exam Question Paper Generator (PDF)":
    st.title("📄 Generate Question Paper PDF")
    
    p_class = st.selectbox("Paper Class", classes_list)
    p_subject = st.text_input("Subject", "Mathematics")
    p_title = st.text_input("Exam Name", "Half-Yearly Examination 2026")
    
    q1 = st.text_area("Question 1", "Q1. Solve: 2x + 10 = 30")
    q2 = st.text_area("Question 2", "Q2. Define Rational Numbers with examples.")
    q3 = st.text_area("Question 3", "Q3. Draw a triangle and explain its properties.")

    def create_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(180, 750, f"School Exam: {p_title}")
        p.setFont("Helvetica", 12)
        p.drawString(50, 720, f"Class: {p_class} | Subject: {p_subject} | Max Marks: 100")
        p.line(50, 710, 550, 710)
        
        y = 670
        for q in [q1, q2, q3]:
            p.drawString(50, y, q)
            y -= 40
            
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    pdf = create_pdf()
    st.download_button("📥 Download Question Paper PDF", pdf, file_name=f"{p_class}_{p_subject}_Paper.pdf", mime="application/pdf")

# --- FEATURE 6: NCERT BOOKS ---
elif menu == "📚 NCERT Books (Class 1 to 12)":
    st.title("📚 NCERT Book Downloads")
    sel_ncert = st.selectbox("Select Class", classes_list)
    
    st.info(f"Downloading books for {sel_ncert}")
    st.markdown(f"👉 **[Official NCERT Textbooks Direct Download Link](https://ncert.nic.in/textbook.php)**")
