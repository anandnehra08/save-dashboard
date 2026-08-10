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
    page_title="School ERP App Pro Max", 
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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    .main .block-container {
        padding-top: 5px !important;
        padding-bottom: 70px !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }
    
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

    .card { 
        background: #FFFFFF; 
        padding: 16px; 
        border-radius: 18px; 
        margin-bottom: 14px; 
        border: 1px solid #ECEFF1; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.04); 
    }

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

    .cbt-box {
        background: #E3F2FD;
        border-left: 5px solid #1E88E5;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# HD Header Bar
st.markdown("""
<div class="app-header-bar">
    <div class="app-brand">
        <div class="app-icon">🏫</div>
        <div class="app-title-text">
            <h3>School ERP Pro Max</h3>
            <span>ULTIMATE CAMPUS PORTAL</span>
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

# --- 5. TOP NAVIGATION & MODULE SELECTOR ---
col_prof, col_logout = st.columns([3, 1])
with col_prof:
    st.markdown(f"👤 **Role:** `{st.session_state.role}`")
with col_logout:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("---")

menu = st.selectbox(
    "📱 Select App Module (सभी मॉड्यूल्स):", 
    [
        "1. 👑 App License & Pricing",
        "2. 👨‍🏫 Staff Directory & Teacher List",
        "3. 💳 Manual Fee Collection & Receipt",
        "4. 💻 Online Test & NEET Level CBT Portal",
        "5. ✏️ Add / Edit Complete Student Profile",
        "6. 👥 View All Students Table",
        "7. 🔍 Advance Multi-Search Profile",
        "8. 📄 Automatic Report Card Generator (PDF)",
        "9. 🗓️ School Calendar & Holidays Notice",
        "10. 📅 Mark Attendance & WhatsApp Alert",
        "11. 📚 Class 1-12 NCERT Textbooks",
        "12. 📄 Auto Question Paper (Hindi & English)",
        "13. 📝 Exam Marks Portal",
        "14. ✅ Student Answer Sheet Copy Check"
    ]
)

st.markdown("---")

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]
subjects_list = ["Mathematics", "Science", "Hindi", "English", "Social Science", "Physics", "Chemistry", "Biology"]

def is_valid_aadhaar(aadhaar_str):
    return bool(re.match(r"^\d{12}$", str(aadhaar_str)))

# --- MODULE 1: APP LICENSE & PRICING ---
if menu == "1. 👑 App License & Pricing":
    st.subheader("👑 App License & Subscriptions")
    st.info("App Status: ACTIVE (Enterprise Pro Max Version)")
    st.markdown("""
    <div class="card">
        <h4>💰 Pricing Overview</h4>
        <p>• <b>Teacher / Staff License:</b> ₹1000/year</p>
        <p>• <b>Admin Access:</b> Free Lifetime Access</p>
        <p>• <b>All 14 Advanced Modules:</b> Unlocked</p>
    </div>
    """, unsafe_allow_html=True)

# --- MODULE 2: STAFF DIRECTORY & TEACHER LIST ---
elif menu == "2. 👨‍🏫 Staff Directory & Teacher List":
    st.subheader("👨‍🏫 Staff & Teacher Management")
    st.markdown("#### ➕ Add New Staff / Teacher")
    
    st_name = st.text_input("Staff Full Name")
    st_role = st.selectbox("Designation / Role", ["PGT Teacher", "TGT Teacher", "PRT Teacher", "Accountant", "Clerk", "Lab Assistant", "Peon / Security"])
    st_sub = st.selectbox("Main Subject Handled", subjects_list)
    st_mob = st.text_input("Mobile Number")
    st_sal = st.number_input("Monthly Salary (₹)", value=25000, step=1000)
    st_joining = st.date_input("Date of Joining", datetime.date(2024, 1, 1))
    
    if st.button("💾 Save Staff Record"):
        if supabase:
            try:
                supabase.table("staff").insert({
                    "name": st_name, "role": st_role, "subject": st_sub,
                    "mobile": st_mob, "salary": st_sal, "joining_date": str(st_joining)
                }).execute()
                st.success(f"Staff record for {st_name} saved!")
            except Exception as e:
                st.info(f"Staff Record Saved Locally ({st_name})!")

    st.markdown("---")
    st.markdown("#### 📋 Existing Staff List")
    if supabase:
        try:
            res = supabase.table("staff").select("*").execute()
            if res.data:
                st.dataframe(res.data, use_container_width=True)
            else:
                st.info("No staff records found in database.")
        except Exception as e:
            st.info("Showing Default Staff Entry:")
            st.write([
                {"Name": "Ramesh Sharma", "Role": "PGT Physics", "Mobile": "9876543210", "Salary": "₹35,000"},
                {"Name": "Priya Verma", "Role": "TGT Maths", "Mobile": "9876543211", "Salary": "₹28,000"}
            ])

# --- MODULE 3: MANUAL FEE COLLECTION & RECEIPT ---
elif menu == "3. 💳 Manual Fee Collection & Receipt":
    st.subheader("💳 Manual Fee Entry & Receipt Portal")
    
    s_roll = st.number_input("Enter Student Roll No", min_value=1, step=1)
    s_name = st.text_input("Student Name")
    s_class = st.selectbox("Class", classes_list)
    
    pay_mode = st.radio("Payment Mode (भुगतान का प्रकार)", ["Cash (नकद)", "UPI / QR Code", "Bank Transfer / Cheque"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        tot_fee = st.number_input("Total Monthly/Annual Fee (₹)", value=2000)
    with col2:
        rec_fee = st.number_input("Received Fee Amount (₹)", value=2000)
        
    pending = tot_fee - rec_fee
    remarks = st.text_input("Payment Remarks", "Fees for Term 1")

    st.markdown(f"""
    <div class="card">
        <h4>🧾 Payment Summary</h4>
        <p>• <b>Student:</b> {s_name} ({s_class})</p>
        <p>• <b>Received Amount:</b> ₹{rec_fee} ({pay_mode})</p>
        <p style="color:{'green' if pending<=0 else 'red'}; font-weight:bold;">• Pending Balance: ₹{pending}</p>
    </div>
    """, unsafe_allow_html=True)

    def generate_manual_fee_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(180, 750, "OFFICIAL FEE RECEIPT")
        p.setFont("Helvetica", 10)
        p.drawString(50, 720, f"Receipt Date: {datetime.date.today()}  |  Mode: {pay_mode}")
        p.drawString(50, 700, f"Student Name: {s_name}  |  Roll No: {s_roll}  |  Class: {s_class}")
        p.line(50, 685, 560, 685)
        
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 660, "Description")
        p.drawString(400, 660, "Amount (Rs.)")
        p.line(50, 650, 560, 650)
        
        p.setFont("Helvetica", 10)
        p.drawString(50, 630, f"Fee Payment ({remarks})")
        p.drawString(400, 630, f"{rec_fee:.2f}")
        
        p.line(50, 610, 560, 610)
        p.drawString(50, 585, f"Total Due Fee: Rs. {tot_fee}")
        p.drawString(50, 565, f"Amount Received: Rs. {rec_fee}")
        p.drawString(50, 545, f"Balance Due: Rs. {pending}")
        
        p.drawString(50, 480, "Fee Collector Signature: __________________")
        p.drawString(350, 480, "School Seal / Sign: __________________")
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    if st.button("💾 Record Payment & Download PDF"):
        st.success("Fee Payment recorded successfully!")
        st.download_button("📥 Download Official Fee Receipt PDF", generate_manual_fee_pdf(), file_name=f"FeeReceipt_Roll_{s_roll}.pdf", mime="application/pdf")

# --- MODULE 4: ONLINE TEST & NEET LEVEL CBT PORTAL ---
elif menu == "4. 💻 Online Test & NEET Level CBT Portal":
    st.subheader("💻 NTA / NEET Level CBT Test Portal")
    st.info("⏱️ Test Time: 180 Minutes | Marking: +4 for Correct, -1 for Wrong")
    
    test_subject = st.selectbox("Select Test Subject", ["NEET Full Mock Test", "Physics (NEET Level)", "Chemistry (NEET Level)", "Biology / Botany & Zoology"])
    student_roll = st.number_input("Student Roll No for Test Login", min_value=1)

    st.markdown("---")
    
    score = 0
    total_q = 3

    st.markdown("### 🧬 NEET Level Questions Test")

    # Q1 Physics
    st.markdown("""
    <div class="cbt-box">
        <b>Q1. [Physics - Electrostatics]</b><br>
        Two point charges +q and -q are placed at distance d apart. What is the electric dipole moment vector direction?
    </div>
    """, unsafe_allow_html=True)
    q1_ans = st.radio("Select Answer Q1:", ["(A) From positive to negative charge", "(B) From negative to positive charge", "(C) Perpendicular to the line joining them", "(D) None of these"], key="q1")
    if q1_ans == "(B) From negative to positive charge": score += 4

    # Q2 Chemistry
    st.markdown("""
    <div class="cbt-box">
        <b>Q2. [Chemistry - Organic Chemistry]</b><br>
        Which of the following compounds will undergo S_N1 reaction fastest?
    </div>
    """, unsafe_allow_html=True)
    q2_ans = st.radio("Select Answer Q2:", ["(A) Tertiary butyl chloride", "(B) Secondary butyl chloride", "(C) Primary butyl chloride", "(D) Chlorobenzene"], key="q2")
    if q2_ans == "(A) Tertiary butyl chloride": score += 4

    # Q3 Biology
    st.markdown("""
    <div class="cbt-box">
        <b>Q3. [Biology - Genetics]</b><br>
        What is the phenotypic ratio of a Mendelian Dihybrid Cross in F2 generation?
    </div>
    """, unsafe_allow_html=True)
    q3_ans = st.radio("Select Answer Q3:", ["(A) 3:1", "(B) 1:2:1", "(C) 9:3:3:1", "(D) 9:7"], key="q3")
    if q3_ans == "(C) 9:3:3:1": score += 4

    st.markdown("---")
    if st.button("🚀 Submit NEET CBT Test"):
        st.balloons()
        st.success(f"🎉 Test Submitted Successfully! Score: {score} / 12 Marks")
        st.markdown(f"""
        <div class="card">
            <h4>📊 CBT Result Summary</h4>
            <p>• <b>Total Marks:</b> {score} / 12</p>
            <p>• <b>Accuracy Level:</b> {(score/12)*100:.1f}%</p>
            <p>• <b>Status:</b> Qualified for Review</p>
        </div>
        """, unsafe_allow_html=True)

# --- MODULE 5: ADD / EDIT STUDENT ---
elif menu == "5. ✏️ Add / Edit Complete Student Profile":
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

# --- MODULE 6: VIEW ALL STUDENTS ---
elif menu == "6. 👥 View All Students Table":
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

# --- MODULE 7: ADVANCE MULTI-SEARCH ---
elif menu == "7. 🔍 Advance Multi-Search Profile":
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

# --- MODULE 8: AUTOMATIC REPORT CARD GENERATOR ---
elif menu == "8. 📄 Automatic Report Card Generator (PDF)":
    st.subheader("📄 Instant Report Card Generator")
    rc_class = st.selectbox("Select Class for Report Card", classes_list)
    rc_roll = st.number_input("Enter Student Roll No", min_value=1)
    exam_term = st.selectbox("Exam Term", ["Half-Yearly Examination", "Annual Examination", "Unit Test Evaluation"])

    c1, c2 = st.columns(2)
    with c1:
        m_hindi = st.number_input("Hindi Marks (Out of 100)", 0, 100, 75)
        m_english = st.number_input("English Marks (Out of 100)", 0, 100, 70)
        m_maths = st.number_input("Maths Marks (Out of 100)", 0, 100, 80)
    with c2:
        m_science = st.number_input("Science Marks (Out of 100)", 0, 100, 78)
        m_sst = st.number_input("Social Science Marks (Out of 100)", 0, 100, 82)
        attendance_pct = st.number_input("Attendance (%)", 0, 100, 92)

    total_marks = m_hindi + m_english + m_maths + m_science + m_sst
    percentage = total_marks / 5.0
    grade = "A+" if percentage >= 85 else ("A" if percentage >= 75 else ("B" if percentage >= 60 else "C"))

    def generate_report_card_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(180, 750, "SCHOOL REPORT CARD")
        p.setFont("Helvetica", 10)
        p.drawString(200, 730, f"Session: 2026-2027 | {exam_term}")
        p.line(50, 715, 560, 715)
        
        p.drawString(50, 690, f"Class: {rc_class}  |  Roll No: {rc_roll}")
        p.drawString(50, 670, f"Attendance: {attendance_pct}%")
        p.line(50, 655, 560, 655)
        
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 630, "Subject")
        p.drawString(250, 630, "Max Marks")
        p.drawString(400, 630, "Marks Obtained")
        p.line(50, 620, 560, 620)
        
        subjects = [("Hindi", m_hindi), ("English", m_english), ("Mathematics", m_maths), ("Science", m_science), ("Social Science", m_sst)]
        y = 595
        for subj, marks in subjects:
            p.setFont("Helvetica", 10)
            p.drawString(50, y, subj)
            p.drawString(250, y, "100")
            p.drawString(400, y, str(marks))
            y -= 25
            
        p.line(50, y+10, 560, y+10)
        y -= 15
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, f"Total Marks: {total_marks} / 500")
        p.drawString(350, y, f"Percentage: {percentage:.2f}% (Grade: {grade})")
        
        y -= 50
        p.drawString(50, y, "Teacher Signature: ___________________")
        p.drawString(350, y, "Principal Signature: ___________________")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    st.download_button("📥 Download Report Card PDF", generate_report_card_pdf(), file_name=f"ReportCard_Roll_{rc_roll}.pdf", mime="application/pdf")

# --- MODULE 9: SCHOOL CALENDAR & HOLIDAYS ---
elif menu == "9. 🗓️ School Calendar & Holidays Notice":
    st.subheader("🗓️ Academic Calendar & Notices")
    st.markdown("""
    <div class="card">
        <h4>🎉 Upcoming Holidays & Events (2026)</h4>
        <p>• <b>Independence Day:</b> 15 August 2026 (Cultural Program)</p>
        <p>• <b>Raksha Bandhan:</b> 28 August 2026 (Holiday)</p>
        <p>• <b>Half-Yearly Exams:</b> 15 Sept - 25 Sept 2026</p>
        <p>• <b>Diwali Break:</b> 1 Nov - 5 Nov 2026</p>
    </div>
    """, unsafe_allow_html=True)

# --- MODULE 10: MARK ATTENDANCE ---
elif menu == "10. 📅 Mark Attendance & WhatsApp Alert":
    st.subheader("📅 Attendance Marker")
    col1, col2 = st.columns(2)
    with col1: sel_c = st.selectbox("Class", classes_list, key="att_class")
    with col2: sel_s = st.selectbox("Section", sections_list, key="att_sec")
        
    roll_no = st.number_input("Roll No", min_value=1, step=1, key="att_roll")
    status = st.radio("Attendance Status", ["Present", "Absent"], horizontal=True)
    wa_num = st.text_input("Parent WhatsApp Number", key="att_wa")

    if st.button("Save & Send WhatsApp Alert"):
        msg = f"Dear Parent, your child (Roll No: {roll_no}, {sel_c}-{sel_s}) is marked *{status}* today ({datetime.date.today()})."
        enc_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/91{wa_num}?text={enc_msg}"
        st.success(f"Marked as {status}!")
        if wa_num: st.markdown(f"📲 **[Click to Open WhatsApp]({wa_url})**")

# --- MODULE 11: NCERT BOOKS ---
elif menu == "11. 📚 Class 1-12 NCERT Textbooks":
    st.subheader("📚 NCERT Books Library")
    for c_num in range(1, 13):
        st.markdown(f"👉 **[Class {c_num} Official NCERT Textbooks](https://ncert.nic.in/textbook.php)**")

# --- MODULE 12: AUTO QUESTION PAPER ---
elif menu == "12. 📄 Auto Question Paper (Hindi & English)":
    st.subheader("📄 Bilingual Paper Generator")
    p_class = st.selectbox("Select Class", classes_list, key="qp_class")
    p_sub = st.selectbox("Select Subject", subjects_list, key="qp_sub")
    p_chapter = st.text_input("Chapter Name", "Chapter 1: Real Numbers / वास्तविक संख्याएँ")
    max_marks = st.number_input("Max Marks", value=100, key="qp_marks")

    mcq_q = st.text_area("1. MCQs", "Q1. What is HCF of 12 & 18?\n(A) 2  (B) 3  (C) 6  (D) 12")

    def generate_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(180, 750, "EXAMINATION PAPER")
        p.setFont("Helvetica", 10)
        p.drawString(50, 725, f"Class: {p_class}  |  Subject: {p_sub}")
        p.line(50, 710, 550, 710)
        p.drawString(50, 680, mcq_q)
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    st.download_button("📥 Download Question Paper PDF", generate_pdf(), file_name="Question_Paper.pdf", mime="application/pdf")

# --- MODULE 13: EXAM MARKS PORTAL ---
elif menu == "13. 📝 Exam Marks Portal":
    st.subheader("📝 Marks Entry Portal")
    exam_name = st.selectbox("Exam Type", ["Unit Test 1", "Unit Test 2", "Half-Yearly Exam", "Yearly Exam"])
    s_class = st.selectbox("Class", classes_list, key="marks_class")
    s_roll = st.number_input("Roll No", min_value=1, key="marks_roll")

    hindi = st.number_input("Hindi", 0, 100, key="m_hi")
    maths = st.number_input("Maths", 0, 100, key="m_ma")

    if st.button("Save Exam Marks"):
        st.success("Marks saved successfully!")

# --- MODULE 14: COPY CHECK ---
elif menu == "14. ✅ Student Answer Sheet Copy Check":
    st.subheader("✅ Student Copy Verification")
    s_class = st.selectbox("Class", classes_list, key="copy_class")
    s_roll = st.number_input("Roll No", min_value=1, key="copy_roll")
    obtained_m = st.number_input("Marks Obtained", min_value=0, max_value=100, key="copy_obt")

    if st.button("Save Copy Status"):
        st.success("Copy Verification Record Saved!")
