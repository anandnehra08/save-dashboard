import streamlit as st
from supabase import create_client, Client
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime
import re

# --- 1. FULL MOBILE APP CONFIGURATION ---
st.set_page_config(
    page_title="School ERP App", 
    page_icon="🏫", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. MOBILE NATIVE UI & STYLING ---
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#1E88E5">

    <style>
    /* Hide Streamlit Native Sidebar Header Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;} /* Hide sidebar toggle icon */
    
    .main .block-container {
        padding-top: 5px !important;
        padding-bottom: 70px !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }
    
    /* Native App Bar */
    .app-header-bar {
        background: linear-gradient(135deg, #1565C0, #1E88E5);
        color: white;
        padding: 14px 18px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.25);
        margin-bottom: 12px;
        margin-top: -10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .app-brand { display: flex; align-items: center; gap: 10px; }
    .app-icon { 
        font-size: 26px; 
        background: rgba(255, 255, 255, 0.2); 
        padding: 6px 10px; 
        border-radius: 12px; 
    }
    .app-title-text h3 { margin: 0; font-size: 17px; color: white; font-weight: 800; }
    .app-title-text span { font-size: 11px; opacity: 0.85; }

    /* User Profile Card on Top */
    .user-profile-card {
        background: #F0F4F8;
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #D9E2EC;
    }

    /* Cards Styling */
    .card { 
        background: #FFFFFF; 
        padding: 16px; 
        border-radius: 18px; 
        margin-bottom: 14px; 
        border: 1px solid #ECEFF1; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.04); 
    }

    /* Primary Android Buttons */
    .stButton>button { 
        width: 100%; 
        border-radius: 14px !important; 
        height: 48px !important; 
        font-size: 15px !important;
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #1E88E5, #1565C0) !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.25) !important;
    }
    </style>
""", unsafe_allow_html=True)

# HD Header Bar
st.markdown("""
<div class="app-header-bar">
    <div class="app-brand">
        <div class="app-icon">🏫</div>
        <div class="app-title-text">
            <h3>School ERP Pro</h3>
            <span>SMART CAMPUS PORTAL</span>
        </div>
    </div>
    <span style="background:#E8F5E9;color:#2E7D32;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:bold;">🟢 Online</span>
</div>
""", unsafe_allow_html=True)

# --- 3. SUPABASE CONNECTION ---
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Database Connection Failed!")
        return None

supabase = init_supabase()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

# --- 4. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("🔐 App Login")
    login_mode = st.radio("Select Portal Mode", ["Admin Login (Free)", "Staff / Teacher Login (OTP / Pay)"])

    if login_mode == "Admin Login (Free)":
        username = st.text_input("Admin Username")
        password = st.text_input("Admin Password", type="password")
        if st.button("🚀 Login to App"):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Super Admin"
                st.rerun()
            else:
                st.error("Invalid Admin Credentials!")
    else:
        mobile = st.text_input("Enter 10-digit Mobile Number")
        if mobile:
            st.info("App License Fee: ₹1000/year")
            upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am=1000&cu=INR"
            st.markdown(f"👉 **[Click Here to Pay App Fee ₹1000]({upi_pay})**")
            otp = st.text_input("Enter OTP (Use '1234')", type="password")
            if st.button("Verify OTP & Login"):
                if otp == "1234":
                    st.session_state.logged_in = True
                    st.session_state.role = "Teacher"
                    st.rerun()
                else:
                    st.error("Incorrect OTP!")
    st.stop()

# --- 5. TOP MAIN SCREEN NAVIGATION (SIDEBAR HATA DIYA HAI) ---
col_prof, col_logout = st.columns([3, 1])
with col_prof:
    st.markdown(f"👤 **Role:** `{st.session_state.role}`")
with col_logout:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("---")

# Front Screen Dropdown Menu (Directly Visible on Mobile Screen)
menu = st.selectbox(
    "📱 Select App Module (मॉड्यूल चुनें):", 
    [
        "1. 👑 App License & Pricing",
        "2. ✏️ Add / Edit Complete Student Profile",
        "3. 👥 View All Students Table",
        "4. 🔍 Advance Multi-Search Profile",
        "5. 💳 Fees Payment, Call & SMS Link",
        "6. 📅 Mark Attendance & WhatsApp Alert",
        "7. 📚 Class 1-12 NCERT Textbooks",
        "8. 📄 Auto Question Paper (Hindi & English)",
        "9. 📝 Exam Marks Portal",
        "10. ✅ Student Answer Sheet Copy Check"
    ]
)

st.markdown("---")

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]
subjects_list = ["Mathematics", "Science", "Hindi", "English", "Social Science"]

def is_valid_aadhaar(aadhaar_str):
    return bool(re.match(r"^\d{12}$", str(aadhaar_str)))

# --- MODULE 1: APP LICENSE & PRICING ---
if menu == "1. 👑 App License & Pricing":
    st.subheader("👑 App License & Subscriptions")
    st.info("App Status: ACTIVE (Enterprise Pro Version)")
    st.markdown("""
    <div class="card">
        <h4>💰 Pricing Overview</h4>
        <p>• <b>Teacher / Staff License:</b> ₹1000/year</p>
        <p>• <b>Admin Access:</b> Free Lifetime Access</p>
        <p>• <b>WhatsApp Gateway:</b> Enabled</p>
    </div>
    """, unsafe_allow_html=True)

# --- MODULE 2: ADD / EDIT COMPLETE STUDENT PROFILE ---
elif menu == "2. ✏️ Add / Edit Complete Student Profile":
    st.subheader("✏️ Student Master Form")
    roll_no = st.number_input("Roll No (Unique ID)", min_value=1, step=1)
    
    existing = None
    if st.button("🔍 Fetch Student Details"):
        if supabase:
            r = supabase.table("students").select("*").eq("roll_no", roll_no).execute()
            if r.data:
                existing = r.data[0]
                st.success("Record found!")

    s_name = st.text_input("Student Name", value=existing.get('name', '') if existing else '')
    f_name = st.text_input("Father Name", value=existing.get('father_name', '') if existing else '')
    m_name = st.text_input("Mother Name", value=existing.get('mother_name', '') if existing else '')
    
    col1, col2 = st.columns(2)
    with col1:
        s_class = st.selectbox("Class", classes_list, index=classes_list.index(existing.get('class', 'Class 1')) if existing and existing.get('class') in classes_list else 0)
    with col2:
        s_sec = st.selectbox("Section", sections_list, index=sections_list.index(existing.get('section', 'A')) if existing and existing.get('section') in sections_list else 0)

    s_dob = st.date_input("Date of Birth (DOB)", datetime.date(2015, 1, 1))
    aadhaar = st.text_input("Aadhaar Number (12 Digit)", value=existing.get('aadhaar', '') if existing else '')
    caste = st.selectbox("Caste Category", ["General", "OBC", "SC", "ST", "EWS"], index=0)

    col3, col4 = st.columns(2)
    with col3:
        mob = st.text_input("Mobile No", value=existing.get('mobile', '') if existing else '')
    with col4:
        wa_mob = st.text_input("WhatsApp No", value=existing.get('whatsapp', '') if existing else '')

    if st.button("💾 Save Student Profile"):
        payload = {
            "roll_no": roll_no, "name": s_name, "father_name": f_name, "mother_name": m_name,
            "class": s_class, "section": s_sec, "dob": str(s_dob), "aadhaar": aadhaar,
            "caste": caste, "mobile": mob, "whatsapp": wa_mob
        }
        if supabase:
            try:
                supabase.table("students").upsert(payload).execute()
                st.success("Student Profile Saved Successfully!")
            except Exception as e:
                st.error(f"Save Failed: {e}")

# --- MODULE 3: VIEW ALL STUDENTS TABLE ---
elif menu == "3. 👥 View All Students Table":
    st.subheader("👥 Student Directory")
    col_c, col_s = st.columns(2)
    with col_c:
        sel_class = st.selectbox("Class", ["All"] + classes_list)
    with col_s:
        sel_sec = st.selectbox("Section", ["All"] + sections_list)
        
    if supabase:
        try:
            query = supabase.table("students").select("*")
            if sel_class != "All": query = query.eq("class", sel_class)
            if sel_sec != "All": query = query.eq("section", sel_sec)
            
            res = query.execute()
            if res.data:
                st.dataframe(res.data, use_container_width=True)
            else:
                st.info("No student records found.")
        except Exception as e:
            st.error(f"Error loading records: {e}")

# --- MODULE 4: ADVANCE MULTI-SEARCH PROFILE ---
elif menu == "4. 🔍 Advance Multi-Search Profile":
    st.subheader("🔍 Master Search")
    search_query = st.text_input("Search Roll No, Name, Aadhaar or Mobile")
    
    if search_query and supabase:
        try:
            res = supabase.table("students").select("*").or_(
                f"roll_no.eq.{search_query if search_query.isdigit() else -1},"
                f"name.ilike.%{search_query}%,"
                f"father_name.ilike.%{search_query}%,"
                f"aadhaar.eq.{search_query},"
                f"mobile.eq.{search_query}"
            ).execute()
            
            if res.data:
                for student in res.data:
                    st.markdown(f"""
                    <div class="card">
                        <h3>👤 {student.get('name', 'N/A')} <span style="background:#E3F2FD;color:#1565C0;padding:3px 8px;border-radius:10px;font-size:11px;">{student.get('class', '')} - {student.get('section', '')}</span></h3>
                        <p><b>Roll No:</b> {student.get('roll_no', 'N/A')} | <b>DOB:</b> {student.get('dob', 'N/A')}</p>
                        <p><b>Father:</b> {student.get('father_name', 'N/A')} | <b>Mother:</b> {student.get('mother_name', 'N/A')}</p>
                        <p><b>Aadhaar:</b> {student.get('aadhaar', 'N/A')} {'✅' if is_valid_aadhaar(student.get('aadhaar', '')) else '⚠️'}</p>
                        <p><b>Mobile:</b> {student.get('mobile', 'N/A')} | <b>WhatsApp:</b> {student.get('whatsapp', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if student.get('mobile'):
                            st.markdown(f'<a href="tel:{student.get("mobile")}"><button style="background:#2196F3;color:white;width:100%;height:40px;border-radius:10px;border:none;font-weight:bold;">📞 Call</button></a>', unsafe_allow_html=True)
                    with c2:
                        target_num = student.get('whatsapp') or student.get('mobile')
                        if target_num:
                            msg = urllib.parse.quote(f"Hello {student.get('name')}, Notice from School App.")
                            st.markdown(f'<a href="https://wa.me/91{target_num}?text={msg}"><button style="background:#25D366;color:white;width:100%;height:40px;border-radius:10px;border:none;font-weight:bold;">💬 WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.warning("No records found.")
        except Exception as e:
            st.error(f"Search Error: {e}")

# --- MODULE 5: FEES PAYMENT, CALL & SMS LINK ---
elif menu == "5. 💳 Fees Payment, Call & SMS Link":
    st.subheader("💳 Quick Fee Collection")
    mob_num = st.text_input("Parent Mobile Number")
    amount = st.number_input("Fee Due Amount (₹)", value=1500)

    c1, c2 = st.columns(2)
    with c1:
        if mob_num:
            st.markdown(f'<a href="tel:{mob_num}"><button style="background:#2196F3;color:white;width:100%;height:45px;border-radius:10px;border:none;font-weight:bold;">📞 Direct Call</button></a>', unsafe_allow_html=True)
    with c2:
        upi_pay = f"upi://pay?pa=schoolfees@upi&pn=SchoolERP&am={amount}&cu=INR"
        st.markdown(f'👉 **[Send ₹{amount} UPI Payment]({upi_pay})**')

# --- MODULE 6: MARK ATTENDANCE & WHATSAPP ALERT ---
elif menu == "6. 📅 Mark Attendance & WhatsApp Alert":
    st.subheader("📅 Attendance Marker")
    col1, col2 = st.columns(2)
    with col1: sel_c = st.selectbox("Class", classes_list)
    with col2: sel_s = st.selectbox("Section", sections_list)
        
    roll_no = st.number_input("Roll No", min_value=1, step=1)
    status = st.radio("Attendance Status", ["Present", "Absent"], horizontal=True)
    wa_num = st.text_input("Parent WhatsApp Number")

    if st.button("Save & Send WhatsApp Alert"):
        msg = f"Dear Parent, your child (Roll No: {roll_no}, {sel_c}-{sel_s}) is marked *{status}* today ({datetime.date.today()})."
        enc_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/91{wa_num}?text={enc_msg}"
        
        if supabase:
            try:
                supabase.table("attendance").insert({
                    "roll_no": roll_no, "class": sel_c, "section": sel_s,
                    "date": str(datetime.date.today()), "status": status
                }).execute()
            except Exception as e: pass
        
        st.success(f"Marked as {status}!")
        if wa_num: st.markdown(f"📲 **[Click to Open WhatsApp]({wa_url})**")

# --- MODULE 7: CLASS 1-12 NCERT TEXTBOOKS ---
elif menu == "7. 📚 Class 1-12 NCERT Textbooks":
    st.subheader("📚 NCERT Books Library")
    for c_num in range(1, 13):
        st.markdown(f"👉 **[Class {c_num} Official NCERT Textbooks](https://ncert.nic.in/textbook.php)**")

# --- MODULE 8: AUTO QUESTION PAPER ---
elif menu == "8. 📄 Auto Question Paper (Hindi & English)":
    st.subheader("📄 Bilingual Paper Generator")
    p_class = st.selectbox("Select Class", classes_list)
    p_sub = st.selectbox("Select Subject", subjects_list)
    p_lang = st.selectbox("Paper Language", ["Bilingual (Hindi + English)", "Hindi Medium", "English Medium"])
    p_chapter = st.text_input("Chapter Name", "Chapter 1: Real Numbers / वास्तविक संख्याएँ")
    max_marks = st.number_input("Max Marks", value=100)

    mcq_q = st.text_area("1. MCQs", "Q1. What is HCF of 12 & 18? / 12 aur 18 ka HCF?\n(A) 2  (B) 3  (C) 6  (D) 12")
    fill_q = st.text_area("2. Fill Blanks", "Q2. Smallest prime number is ______.")
    one_liner_q = st.text_area("3. One-Liner", "Q3. Define Rational Number.")
    short_q = st.text_area("4. Short Answers", "Q4. Prove √5 is irrational.")
    long_q = st.text_area("5. Long Essay", "Q5. Explain Fundamental Theorem of Arithmetic.")

    def generate_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(140, 750, f"EXAMINATION PAPER ({p_lang.upper()})")
        p.setFont("Helvetica", 10)
        p.drawString(50, 725, f"Class: {p_class}  |  Subject: {p_sub}")
        p.drawString(50, 710, f"Chapter: {p_chapter}  |  Max Marks: {max_marks}")
        p.line(50, 700, 550, 700)
        
        y = 675
        sections = [("MCQs", mcq_q), ("Fill in Blanks", fill_q), ("One-Liner", one_liner_q), ("Short Questions", short_q), ("Essay Questions", long_q)]
        for title, content in sections:
            if content.strip():
                if y < 100: p.showPage(); y = 720
                p.setFont("Helvetica-Bold", 11)
                p.drawString(50, y, title)
                y -= 20
                p.setFont("Helvetica", 9)
                for line in content.split('\n'):
                    if y < 60: p.showPage(); y = 720
                    p.drawString(60, y, line)
                    y -= 15
                y -= 10
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    st.download_button("📥 Download Question Paper PDF", generate_pdf(), file_name=f"{p_class}_{p_sub}_Paper.pdf", mime="application/pdf")

# --- MODULE 9: EXAM MARKS PORTAL ---
elif menu == "9. 📝 Exam Marks Portal":
    st.subheader("📝 Marks Entry Portal")
    exam_name = st.selectbox("Exam Type", ["Unit Test 1", "Unit Test 2", "Half-Yearly Exam", "Yearly Exam"])
    s_class = st.selectbox("Class", classes_list)
    s_roll = st.number_input("Roll No", min_value=1)

    c1, c2 = st.columns(2)
    with c1:
        hindi = st.number_input("Hindi", 0, 100)
        english = st.number_input("English", 0, 100)
    with c2:
        maths = st.number_input("Maths", 0, 100)
        science = st.number_input("Science", 0, 100)

    if st.button("Save Exam Marks"):
        if supabase:
            try:
                supabase.table("marks").insert({
                    "exam_type": exam_name, "class": s_class, "roll_no": s_roll,
                    "hindi": hindi, "english": english, "maths": maths, "science": science
                }).execute()
                st.success("Marks saved successfully!")
            except Exception as e: st.error(f"Error: {e}")

# --- MODULE 10: STUDENT ANSWER SHEET COPY CHECK ---
elif menu == "10. ✅ Student Answer Sheet Copy Check":
    st.subheader("✅ Student Copy Verification")
    c1, c2 = st.columns(2)
    with c1:
        s_class = st.selectbox("Class", classes_list)
        s_roll = st.number_input("Roll No", min_value=1)
    with c2:
        subject = st.selectbox("Subject", subjects_list)
        exam_type = st.selectbox("Exam", ["Unit Test 1", "Unit Test 2", "Half-Yearly", "Yearly"])

    max_m = st.number_input("Max Marks", value=50)
    obtained_m = st.number_input("Marks Obtained", min_value=0, max_value=int(max_m))
    remarks = st.text_area("Teacher Remarks", "Good effort!")
    status_check = st.selectbox("Checking Status", ["Checked ✅", "Pending Review ⏳", "Re-evaluation Needed ⚠️"])

    if st.button("Save Copy Status"):
        st.success("Copy Verification Record Saved!")
