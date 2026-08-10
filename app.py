import streamlit as st
from supabase import create_client, Client
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime
import re

# --- 1. MOBILE ANDROID PRO UI CONFIG ---
st.set_page_config(page_title="School Dashboard & ERP Pro", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main { max-width: 520px; margin: 0 auto; }
    .stButton>button { width: 100%; border-radius: 12px; height: 48px; font-weight: bold; background-color: #1E88E5; color: white; }
    .card { background-color: #ffffff; padding: 18px; border-radius: 15px; margin-bottom: 12px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .badge { background-color: #E3F2FD; color: #1565C0; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; }
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
        st.error("Database Connection Failed! Check secrets.toml")
        return None

supabase = init_supabase()

# Session State Setup
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

# --- 3. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("🔐 School Portal Login")
    login_mode = st.radio("Select Portal Mode", ["Admin Login (Free)", "Staff / Teacher Login (OTP / Pay)"])

    if login_mode == "Admin Login (Free)":
        username = st.text_input("Admin Username")
        password = st.text_input("Admin Password", type="password")
        if st.button("🚀 Login as Admin"):
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

# --- 4. NAVIGATION SYSTEM (Purane + Naye Sabhi Modules) ---
st.sidebar.markdown(f"### 👤 Role: `{st.session_state.role}`")
if st.sidebar.button("🔴 Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.selectbox("📋 Navigation Menu", [
    "👥 View All Students Table",
    "🔍 Advance Multi-Search Profile",
    "✏️ Add / Edit Complete Student Profile",
    "📅 Mark Attendance & WhatsApp Alert",
    "💳 Fees Payment, Call & SMS Link",
    "📝 Exam Marks Portal",
    "📄 Auto NCERT Question Paper Generator",
    "📚 Class 1-12 NCERT Textbooks",
    "👑 Admin License & App Fees"
])

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]

def is_valid_aadhaar(aadhaar_str):
    return bool(re.match(r"^\d{12}$", str(aadhaar_str)))

# --- PAGE 1: VIEW ALL STUDENTS TABLE (Purana Feature) ---
if menu == "👥 View All Students Table":
    st.title("👥 Student Directory")
    
    col_c, col_s = st.columns(2)
    with col_c:
        sel_class = st.selectbox("Filter Class", ["All"] + classes_list)
    with col_s:
        sel_sec = st.selectbox("Filter Section", ["All"] + sections_list)
        
    if supabase:
        try:
            query = supabase.table("students").select("*")
            if sel_class != "All":
                query = query.eq("class", sel_class)
            if sel_sec != "All":
                query = query.eq("section", sel_sec)
            
            res = query.execute()
            if res.data:
                st.dataframe(res.data, use_container_width=True)
            else:
                st.info("No student records found.")
        except Exception as e:
            st.error(f"Error loading records: {e}")

# --- PAGE 2: ADVANCE MULTI-SEARCH PROFILE (Naya Feature) ---
elif menu == "🔍 Advance Multi-Search Profile":
    st.title("🔍 Master Student Search")
    
    search_query = st.text_input("Search by Roll No, Student/Father Name, Aadhaar or Mobile")
    
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
                        <h3>👤 {student.get('name', 'N/A')} <span class="badge">{student.get('class', '')} - Sec {student.get('section', '')}</span></h3>
                        <p><b>Roll No:</b> {student.get('roll_no', 'N/A')} | <b>DOB:</b> {student.get('dob', 'N/A')}</p>
                        <p><b>Father:</b> {student.get('father_name', 'N/A')} | <b>Mother:</b> {student.get('mother_name', 'N/A')}</p>
                        <p><b>Aadhaar:</b> {student.get('aadhaar', 'N/A')} {'✅ Linked' if is_valid_aadhaar(student.get('aadhaar', '')) else '⚠️ Invalid/Unlinked'}</p>
                        <p><b>Caste:</b> {student.get('caste', 'General')}</p>
                        <p><b>Mobile:</b> {student.get('mobile', 'N/A')} | <b>WhatsApp:</b> {student.get('whatsapp', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if student.get('mobile'):
                            st.markdown(f'<a href="tel:{student.get("mobile")}"><button style="background-color:#2196F3;color:white;width:100%;height:40px;border-radius:8px;">📞 Call Mobile</button></a>', unsafe_allow_html=True)
                    with c2:
                        if student.get('whatsapp') or student.get('mobile'):
                            target_num = student.get('whatsapp') or student.get('mobile')
                            msg = urllib.parse.quote(f"Hello {student.get('name')}, Notice from School ERP Portal.")
                            st.markdown(f'<a href="https://wa.me/91{target_num}?text={msg}"><button style="background-color:#25D366;color:white;width:100%;height:40px;border-radius:8px;">💬 WhatsApp SMS</button></a>', unsafe_allow_html=True)
            else:
                st.warning("No matching student records found.")
        except Exception as e:
            st.error(f"Search Error: {e}")

# --- PAGE 3: ADD / EDIT COMPLETE STUDENT PROFILE (Updated Feature) ---
elif menu == "✏️ Add / Edit Complete Student Profile":
    st.title("✏️ Student Master Form")
    
    roll_no = st.number_input("Roll No (Unique ID)", min_value=1, step=1)
    
    existing = None
    if st.button("🔍 Load Existing Student Data"):
        if supabase:
            r = supabase.table("students").select("*").eq("roll_no", roll_no).execute()
            if r.data:
                existing = r.data[0]
                st.success("Data fetched successfully!")

    col1, col2 = st.columns(2)
    with col1:
        s_name = st.text_input("Student Name", value=existing.get('name', '') if existing else '')
        f_name = st.text_input("Father Name", value=existing.get('father_name', '') if existing else '')
        m_name = st.text_input("Mother Name", value=existing.get('mother_name', '') if existing else '')
        s_class = st.selectbox("Class", classes_list, index=classes_list.index(existing.get('class', 'Class 1')) if existing and existing.get('class') in classes_list else 0)
    
    with col2:
        s_dob = st.date_input("Date of Birth (DOB)", datetime.date(2015, 1, 1))
        aadhaar = st.text_input("Aadhaar Number (12 Digit)", value=existing.get('aadhaar', '') if existing else '')
        caste = st.selectbox("Caste Category", ["General", "OBC", "SC", "ST", "EWS"], index=0)
        s_sec = st.selectbox("Section", sections_list, index=sections_list.index(existing.get('section', 'A')) if existing and existing.get('section') in sections_list else 0)

    col3, col4 = st.columns(2)
    with col3:
        mob = st.text_input("Mobile Number", value=existing.get('mobile', '') if existing else '')
    with col4:
        wa_mob = st.text_input("WhatsApp Number", value=existing.get('whatsapp', '') if existing else '')

    if st.button("💾 Save / Update Student Profile"):
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

# --- PAGE 4: MARK ATTENDANCE & WHATSAPP ALERT (Merged Feature) ---
elif menu == "📅 Mark Attendance & WhatsApp Alert":
    st.title("📅 Daily Attendance")
    
    c1, c2 = st.columns(2)
    with c1:
        sel_c = st.selectbox("Class", classes_list)
    with c2:
        sel_s = st.selectbox("Section", sections_list)
        
    roll_no = st.number_input("Roll No", min_value=1, step=1)
    status = st.radio("Status", ["Present", "Absent"], horizontal=True)
    wa_num = st.text_input("Parent Mobile / WhatsApp Number")

    if st.button("Save & Send Instant WhatsApp Alert"):
        msg = f"Dear Parent, your child (Roll No: {roll_no}, {sel_c}-{sel_s}) is marked *{status}* today ({datetime.date.today()})."
        enc_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/91{wa_num}?text={enc_msg}"
        
        if supabase:
            try:
                supabase.table("attendance").insert({
                    "roll_no": roll_no, "class": sel_c, "section": sel_s,
                    "date": str(datetime.date.today()), "status": status
                }).execute()
            except Exception as e:
                pass
        
        st.success(f"Attendance recorded as {status}!")
        if wa_num:
            st.markdown(f"📲 **[Click Here to Open WhatsApp & Send Alert]({wa_url})**")

# --- PAGE 5: FEES PAYMENT, CALL & SMS LINK (Merged Feature) ---
elif menu == "💳 Fees Payment, Call & SMS Link":
    st.title("💳 Fees & Parent Direct Connect")
    
    mob_num = st.text_input("Parent Mobile Number")
    amount = st.number_input("Fee Due Amount (₹)", value=1500)

    c1, c2 = st.columns(2)
    with c1:
        if mob_num:
            st.markdown(f'<a href="tel:{mob_num}"><button style="background-color:#2196F3;color:white;width:100%;height:45px;border-radius:10px;">📞 Call Parent Now</button></a>', unsafe_allow_html=True)
    with c2:
        upi_pay = f"upi://pay?pa=schoolfees@upi&pn=SchoolERP&am={amount}&cu=INR"
        st.markdown(f'👉 **[Send ₹{amount} UPI Payment Link]({upi_pay})**')

# --- PAGE 6: EXAM MARKS PORTAL (Purana Feature) ---
elif menu == "📝 Exam Marks Portal":
    st.title("📝 Student Marks Portal")
    
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

    if st.button("Save Marks Record"):
        if supabase:
            try:
                supabase.table("marks").insert({
                    "exam_type": exam_name, "class": s_class, "roll_no": s_roll,
                    "hindi": hindi, "english": english, "maths": maths, "science": science
                }).execute()
                st.success("Marks saved successfully!")
            except Exception as e:
                st.error(f"Error saving marks: {e}")

# --- PAGE 7: AUTO NCERT QUESTION PAPER GENERATOR (Naya + Chapter Wise Feature) ---
elif menu == "📄 Auto NCERT Question Paper Generator":
    st.title("📄 NCERT Chapter Question Paper")
    
    c1, c2 = st.columns(2)
    with c1:
        p_class = st.selectbox("Select Class", classes_list)
        p_sub = st.selectbox("Select Subject", ["Mathematics", "Science", "Hindi", "English", "Social Science"])
    with c2:
        p_chapter = st.text_input("Chapter Name / No.", "Chapter 1: Real Numbers")
        max_marks = st.number_input("Total Max Marks", value=100)

    st.subheader("📝 Question Pattern:")
    mcq_q = st.text_area("1. MCQs (Bahuvikalpi Prashn)", 
                         "Q1. What is the HCF of 12 and 18?\n(A) 2  (B) 3  (C) 6  (D) 12\n\nQ2. Which of the following is an Irrational Number?\n(A) √4  (B) √2  (C) 0.5  (D) 3/5")
    fill_q = st.text_area("2. Fill in the Blanks (Khali Sthan)", 
                          "Q3. Smallest prime number is _______.\nQ4. Every composite number can be expressed as product of _______.")
    one_liner_q = st.text_area("3. One-Liner Questions (Ek Vakya)", 
                               "Q5. State Euclid's Division Lemma.\nQ6. Define a Rational Number.")
    short_q = st.text_area("4. Short Answer Questions (Laghutratmak)", 
                           "Q7. Prove that √5 is an irrational number.\nQ8. Find the LCM of 24 and 36 using Prime Factorization Method.")
    long_q = st.text_area("5. Long Essay Questions (Nibandhatmak)", 
                          "Q9. Explain the Fundamental Theorem of Arithmetic with a real-world application in detail.")

    def generate_pro_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(160, 750, f"SCHOOL EXAMINATION PAPER")
        p.setFont("Helvetica", 11)
        p.drawString(50, 725, f"Class: {p_class}  |  Subject: {p_sub}  |  Chapter: {p_chapter}")
        p.drawString(50, 710, f"Max Marks: {max_marks}  |  Time: 3 Hours")
        p.line(50, 700, 550, 700)
        
        y = 675
        sections = [
            ("SECTION A: MCQs", mcq_q),
            ("SECTION B: Fill in the Blanks", fill_q),
            ("SECTION C: One-Liner Questions", one_liner_q),
            ("SECTION D: Short Answer Questions", short_q),
            ("SECTION E: Long Essay Questions", long_q)
        ]
        
        for sec_title, sec_content in sections:
            if sec_content.strip():
                if y < 100:
                    p.showPage()
                    y = 720
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, sec_title)
                y -= 20
                p.setFont("Helvetica", 10)
                
                lines = sec_content.split('\n')
                for line in lines:
                    if y < 60:
                        p.showPage()
                        y = 720
                        p.setFont("Helvetica", 10)
                    p.drawString(60, y, line)
                    y -= 16
                y -= 10
                
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    pdf_file = generate_pro_pdf()
    st.download_button("📥 Download Auto Question Paper PDF", pdf_file, file_name=f"{p_class}_{p_sub}_Paper.pdf", mime="application/pdf")

# --- PAGE 8: CLASS 1-12 NCERT TEXTBOOKS (Purana Feature) ---
elif menu == "📚 Class 1-12 NCERT Textbooks":
    st.title("📚 Official NCERT Books")
    st.write("Direct Links to Official NCERT Textbooks:")
    
    for c_num in range(1, 13):
        st.markdown(f"👉 **[Class {c_num} NCERT All Subject Books](https://ncert.nic.in/textbook.php)**")

# --- PAGE 9: ADMIN LICENSE & APP FEES ---
elif menu == "👑 Admin License & App Fees":
    st.title("👑 App Licensing")
    st.info("System License Status: ACTIVE (Enterprise Pro)")
    st.markdown("""
    <div class="card">
        <h4>💰 App License Pricing</h4>
        <p>• <b>Teacher License:</b> ₹1000/year</p>
        <p>• <b>Admin Access:</b> Free Lifetime</p>
    </div>
    """, unsafe_allow_html=True)
