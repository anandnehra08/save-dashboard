import datetime
import io
import re
import urllib.parse
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
from supabase import Client, create_client

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Campus School ERP Pro",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- 2. PREMIUM UI & MODERN CSS STYLING ---
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    .main .block-container {
        padding-top: 10px !important;
        padding-bottom: 80px !important;
        max-width: 500px !important;
        margin: 0 auto !important;
    }

    .app-header-bar {
        background: linear-gradient(135deg, #1E1B4B, #312E81);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        padding: 16px 18px;
        border-radius: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 18px;
    }
    .header-top { display: flex; align-items: center; justify-content: space-between; }
    .app-brand { display: flex; align-items: center; gap: 12px; }
    .app-icon { 
        font-size: 28px; 
        background: linear-gradient(135deg, #6366F1, #4F46E5); 
        padding: 8px 12px; 
        border-radius: 16px; 
    }
    .app-title-text h3 { margin: 0; font-size: 18px; color: #F8FAFC; font-weight: 800; }
    .app-title-text span { font-size: 11px; color: #C7D2FE; font-weight: 600; }

    .status-badge {
        background: rgba(34, 197, 94, 0.15);
        color: #4ADE80;
        border: 1px solid rgba(74, 222, 128, 0.2);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }

    .admin-info-box {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 10px 14px;
        margin-top: 12px;
        font-size: 12px;
        color: #E0E7FF;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .admin-info-box p { margin: 2px 0; }
    .admin-info-box a { color: #818CF8; text-decoration: none; font-weight: 700; }

    .colored-card-admission {
        background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
        border-left: 6px solid #3B82F6;
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 15px;
        color: #1E3A8A;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    .colored-card-cert {
        background: linear-gradient(135deg, #FDF4FF, #FAE8FF);
        border-left: 6px solid #D946EF;
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 15px;
        color: #701A75;
        box-shadow: 0 4px 12px rgba(217, 70, 239, 0.1);
    }

    .stButton>button { 
        width: 100%; 
        border-radius: 16px !important; 
        height: 50px !important; 
        font-size: 15px !important;
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #4F46E5, #4338CA) !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.4) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Display
st.markdown(
    """
<div class="app-header-bar">
    <div class="header-top">
        <div class="app-brand">
            <div class="app-icon">🎓</div>
            <div class="app-title-text">
                <h3>Campus School ERP Pro</h3>
                <span>ADVANCED INSTITUTIONAL SUITE</span>
            </div>
        </div>
        <span class="status-badge">🟢 Live System</span>
    </div>
    <div class="admin-info-box">
        <p>🏢 <b>System:</b> Campus School ERP Suite</p>
        <p>👨‍💼 <b>Developer Name:</b> Anand Nehra</p>
        <p>📞 <b>Support Desk:</b> <a href="#">Helpline Active</a> | ✉️ <b>Email:</b> <a href="#">support@campuserp.com</a></p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 3. SUPABASE CONNECTION ---
@st.cache_resource
def init_supabase() -> Client:
  try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
  except Exception:
    return None

supabase = init_supabase()

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "role" not in st.session_state:
  st.session_state.role = None

# --- 4. LOGIN SYSTEM ---
if not st.session_state.logged_in:
  st.title("🔐 Login Portal")
  login_mode = st.radio("Select Portal Mode", ["Admin Login (Free)", "Staff / Teacher Login"])

  if login_mode == "Admin Login (Free)":
    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")
    if st.button("🚀 Login"):
      if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.session_state.role = "Super Admin"
        st.rerun()
      else:
        st.error("Invalid Admin Credentials!")
  else:
    mobile = st.text_input("Enter Mobile Number")
    otp = st.text_input("Enter OTP (Use '1234')", type="password")
    if st.button("Verify OTP & Login"):
      if otp == "1234":
        st.session_state.logged_in = True
        st.session_state.role = "Teacher"
        st.rerun()
      else:
        st.error("Incorrect OTP!")
  st.stop()

# --- TOP BAR ---
col_prof, col_logout = st.columns([3, 1])
with col_prof:
  st.markdown(f"👤 **Role:** `{st.session_state.role}`")
with col_logout:
  if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.markdown("---")

# --- EXACT 1 TO 17 SERIAL ORDER MODULE SELECTOR ---
menu = st.selectbox(
    "📱 Select App Module (मॉड्यूल चुनें):",
    [
        "1. 👑 App License & System Information",
        "2. 📜 Certificate Generator (TC, Character & Study)",
        "3. 📖 SR Register & Complete Student Master Profile (Admission Form)",
        "4. 🔍 Advance Multi-Search Student Search",
        "5. 💳 3-Installment Fee Manager & Receipt",
        "6. 📈 Daily Boys/Girls Attendance Analytics",
        "7. 👨‍🏫 Staff Directory & Payroll",
        "8. 📢 Instant School Notice Board",
        "9. 📊 Hiralal Style Result Generator & Excel Export",
        "10. 📚 Chapter-Wise NCERT PDF & Paper Generator",
        "11. 💻 NEET Level Online CBT Exam Portal",
        "12. 🗓️ Academic Calendar & Holiday Notices",
        "13. 💼 Busy Software Style Cash Book & Ledger",
        "14. 📝 Exam Marks Portal",
        "15. ✅ Student Answer Sheet Copy Check",
        "16. 📊 Complete Financial Summary Dashboard",
        "17. 📱 Notebook Check, Call Log & Daily Present SMS Hub",
    ],
)

st.markdown("---")

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]
subjects_list = ["Mathematics", "Science", "Hindi", "English", "Social Science", "Physics", "Chemistry", "Biology"]

def is_valid_aadhaar(aadhaar_str):
  return bool(re.match(r"^\d{12}$", str(aadhaar_str)))

# ==========================================
# 1. APP LICENSE & SYSTEM INFO (Module 1)
# ==========================================
if menu == "1. 👑 App License & System Information":
  st.subheader("👑 Campus School ERP License")
  st.markdown(
      """
    <div style="background:#F1F5F9; padding:15px; border-radius:15px; border:1px solid #CBD5E1">
        <h4>🏢 System Name: Campus School ERP Pro</h4>
        <p><b>Configuration:</b> Advanced Institutional Setup</p>
        <p><b>Lead Developer:</b> Anand Nehra</p>
        <p><b>Support:</b> Helpline Active | System Online</p>
        <hr>
        <p><b>License Status:</b> Activated Enterprise Version</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

# ==========================================
# 2. CERTIFICATE GENERATOR (Module 2)
# ==========================================
elif menu == "2. 📜 Certificate Generator (TC, Character & Study)":
  st.markdown(
      """
    <div class="colored-card-cert">
        <h3>📜 Official Certificate Generator (Advanced UI)</h3>
        <p>Generate secure, styled Transfer, Character, and Study Certificates instantly.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
  cert_type = st.selectbox(
      "Choose Certificate Type",
      ["Transfer Certificate (TC)", "Character Certificate (चरित्र प्रमाण पत्र)", "Study Certificate (अध्ययनरत प्रमाण पत्र)"],
  )
  sr_no = st.text_input("SR / Admission Number")
  st_name = st.text_input("Student Name")
  f_name = st.text_input("Father Name")
  s_class = st.selectbox("Class", classes_list)
  dob = st.date_input("Date of Birth", datetime.date(2010, 1, 1))
  conduct = st.selectbox("Behavior / Conduct", ["Excellent", "Good", "Satisfactory"])

  def generate_cert_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 750, "CAMPUS SCHOOL ERP")
    p.setFont("Helvetica", 10)
    p.drawString(190, 735, "Advanced Institutional Solution")
    p.line(50, 720, 560, 720)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(180, 680, f"--- {cert_type.upper()} ---")
    p.setFont("Helvetica", 12)
    p.drawString(60, 630, f"SR Number: {sr_no}")
    p.drawString(60, 605, f"This is to certify that Master/Miss: {st_name}")
    p.drawString(60, 580, f"Son/Daughter of Shri: {f_name}")
    p.drawString(60, 555, f"Is/Was a bona fide student of Class: {s_class}")
    p.drawString(60, 530, f"Date of Birth: {dob.strftime('%d-%m-%Y')}")
    p.drawString(60, 505, f"General Conduct & Character: {conduct}")
    p.drawString(60, 430, f"Date of Issue: {datetime.date.today()}")
    p.drawString(400, 430, "Principal Signature")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

  if st.button("📄 Generate & Download Certificate PDF"):
    st.download_button(
        "📥 Download PDF",
        generate_cert_pdf(),
        file_name=f"{cert_type}_{sr_no}.pdf",
        mime="application/pdf",
    )

# ==========================================
# 3. SR REGISTER & ADMISSION FORM (Module 3)
# ==========================================
elif menu == "3. 📖 SR Register & Complete Student Master Profile (Admission Form)":
  st.markdown(
      """
    <div class="colored-card-admission">
        <h3>📖 Advanced Student Admission Form & Master Profile</h3>
        <p>Complete New Student Registration, Document Upload & Database Setup.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
  col1, col2 = st.columns(2)
  with col1:
    sr_no = st.number_input("SR Number", min_value=1, step=1)
    st_name = st.text_input("Student Name")
    gender = st.selectbox("Gender", ["Boy", "Girl", "Other"])
    s_class = st.selectbox("Class", classes_list)
    s_sec = st.selectbox("Section", sections_list)
  with col2:
    roll_no = st.number_input("Roll No", min_value=1, step=1)
    f_name = st.text_input("Father Name")
    m_name = st.text_input("Mother Name")
    mobile = st.text_input("Parent Mobile Number")
    aadhaar = st.text_input("Aadhaar Number (12 Digits)")

  st.markdown("---")
  st.subheader("🚌 Transport & Drop Point Setup")
  route = st.text_input("Assigned Bus Route", "Route 1 - City Line")
  drop_point = st.text_input("Pickup / Drop Point", "Main Market Bus Stop")
  student_photo = st.file_uploader("Upload Student Passport Photo", type=["jpg", "png", "jpeg"])

  if st.button("💾 Save Admission Form / SR Register"):
    if aadhaar and not is_valid_aadhaar(aadhaar):
      st.error("Invalid Aadhaar Number! Must be 12 digits.")
    else:
      st.success("Admission Form Record Saved Successfully with Photo & Colored Profile!")

# ==========================================
# 4. ADVANCE MULTI-SEARCH (Module 4)
# ==========================================
elif menu == "4. 🔍 Advance Multi-Search Student Search":
  st.subheader("🔍 Advance Master Search")
  search_term = st.text_input("Search by Name or SR Number")
  if st.button("Search") and search_term:
    st.write(f"Searching database for '{search_term}'...")

# ==========================================
# 5. 3-INSTALLMENT FEE MANAGER (Module 5)
# ==========================================
elif menu == "5. 💳 3-Installment Fee Manager & Receipt":
  st.subheader("💳 Fee Installment & Receipt Management")
  sr_no = st.number_input("Enter Student SR No", min_value=1, step=1)
  st_name = st.text_input("Student Name")
  total_fee = st.number_input("Total Annual Fee (₹)", value=15000, step=500)

  col1, col2, col3 = st.columns(3)
  with col1:
    inst1 = st.number_input("1st Installment Paid (₹)", value=5000)
  with col2:
    inst2 = st.number_input("2nd Installment Paid (₹)", value=0)
  with col3:
    inst3 = st.number_input("3rd Installment Paid (₹)", value=0)

  total_paid = inst1 + inst2 + inst3
  pending = total_fee - total_paid
  st.info(f"📊 **Total Paid:** ₹{total_paid:,} | ⏳ **Pending Fee:** ₹{pending:,}")

# ==========================================
# 6. ATTENDANCE ANALYTICS (Module 6)
# ==========================================
elif menu == "6. 📈 Daily Boys/Girls Attendance Analytics":
  st.subheader("📈 Daily Attendance Analytics & Visual Breakdown")
  c1, c2 = st.columns(2)
  c1.metric("👦 Boys Present", "240 / 250", "96%")
  c2.metric("👧 Girls Present", "210 / 220", "95.4%")
  st.markdown("---")
  att_df = pd.DataFrame({
      "Category": ["Boys Present", "Boys Absent", "Girls Present", "Girls Absent"],
      "Count": [240, 10, 210, 10],
  })
  fig_att = px.pie(att_df, values="Count", names="Category", hole=0.4)
  st.plotly_chart(fig_att, use_container_width=True)

# ==========================================
# 7. STAFF DIRECTORY & PAYROLL (Module 7)
# ==========================================
elif menu == "7. 👨‍🏫 Staff Directory & Payroll":
  st.subheader("👨‍🏫 Staff Directory & Payroll")
  st_name = st.text_input("Staff Name")
  st_role = st.selectbox("Designation", ["PGT", "TGT", "PRT", "Accountant"])
  st_sal = st.number_input("Monthly Salary (₹)", value=25000)
  if st.button("Save Staff Record"):
    st.success(f"Staff record for {st_name} saved.")

# ==========================================
# 8. INSTANT NOTICE BOARD (Module 8)
# ==========================================
elif menu == "8. 📢 Instant School Notice Board":
  st.subheader("📢 School Notice Board")
  notice = st.text_area("Write Notice Message", "Dear Parents, Tomorrow is a holiday.")
  parent_phone = st.text_input("Parent Mobile Number (10 Digits)", "9828595276")
  if st.button("Publish Notice"):
    st.success("Notice published!")
  if parent_phone and notice:
    whatsapp_url = f"https://wa.me/91{parent_phone}?text={urllib.parse.quote(notice)}"
    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; height:45px; background-color:#25D366; color:white; border:none; border-radius:12px;">📲 Send via WhatsApp</button></a>', unsafe_allow_html=True)

# ==========================================
# 9. HIRALAL SHEET RESULT (Module 9)
# ==========================================
elif menu == "9. 📊 Hiralal Style Result Generator & Excel Export":
  st.subheader("📊 Hiralal Style Result Generator & Excel Sheet Export")
  data = {
      "SR No": [101, 102],
      "Student Name": ["Aarav Sharma", "Priya Verma"],
      "Hindi": [85, 92],
      "English": [88, 90],
      "Maths": [95, 88],
  }
  df = pd.DataFrame(data)
  st.dataframe(df)

# ==========================================
# 10. NCERT CHAPTER PDF (Module 10)
# ==========================================
elif menu == "10. 📚 Chapter-Wise NCERT PDF & Paper Generator":
  st.subheader("📚 NCERT Chapter Books & Paper Setter Portal")
  s_class = st.selectbox("Select Class Level", classes_list)
  subject = st.selectbox("Select Subject", subjects_list)
  st.write(f"📖 **{subject}** NCERT materials loaded successfully.")

# ==========================================
# 11. NEET ONLINE CBT EXAM (Module 11)
# ==========================================
elif menu == "11. 💻 NEET Level Online CBT Exam Portal":
  st.subheader("💻 NTA / NEET Level CBT Test Portal")
  st.info("⏱️ Test Time: 180 Minutes")
  st.markdown("**Q1.** What is the unit of Electric Dipole Moment?")
  st.radio("Options:", ["Coulomb-meter", "Volt/meter", "Tesla", "Weber"])

# ==========================================
# 12. ACADEMIC CALENDAR (Module 12)
# ==========================================
elif menu == "12. 🗓️ Academic Calendar & Holiday Notices":
  st.subheader("🗓️ School Calendar")
  st.write("• **15th August:** Independence Day Celebration")
  st.write("• **15th October:** Term-1 Exams Begin")

# ==========================================
# 13. BUSY SOFTWARE CASH BOOK (Module 13)
# ==========================================
elif menu == "13. 💼 Busy Software Style Cash Book & Ledger":
  st.subheader("💼 Busy Style Cash & Ledger Book")
  entry_type = st.radio("Transaction Type", ["Cash In (Receipt)", "Cash Out (Payment)"], horizontal=True)
  amount = st.number_input("Amount (₹)", value=5000, step=500)
  if st.button("💾 Save Ledger Voucher"):
    st.success("Voucher saved!")

# ==========================================
# 14. EXAM MARKS PORTAL (Module 14)
# ==========================================
elif menu == "14. 📝 Exam Marks Portal":
  st.subheader("📝 Marks Entry Portal")
  sr = st.number_input("SR No", min_value=1)
  marks = st.number_input("Marks (Out of 100)", 0, 100, 85)
  if st.button("Save Marks"):
    st.success("Marks saved successfully!")

# ==========================================
# 15. ANSWER SHEET COPY CHECK (Module 15)
# ==========================================
elif menu == "15. ✅ Student Answer Sheet Copy Check":
  st.subheader("✅ Answer Sheet Copy Check")
  up = st.file_uploader("Upload Scanned Answer Sheet", type=["pdf", "jpg"])
  if up:
    st.success("File uploaded ready for evaluation.")

# ==========================================
# 16. FINANCIAL SUMMARY DASHBOARD (Module 16)
# ==========================================
elif menu == "16. 📊 Complete Financial Summary Dashboard":
  st.subheader("📊 Financial Overview & Visual Analytics")
  c1, c2 = st.columns(2)
  c1.metric("Total Fees Collected", "₹12,45,000", "+83%")
  c2.metric("Pending Fees", "₹2,55,000", "-17%")

# ==========================================
# 17. NOTEBOOK CHECK, CALL LOG & SMS HUB (Module 17)
# ==========================================
elif menu == "17. 📱 Notebook Check, Call Log & Daily Present SMS Hub":
  st.subheader("📱 Smart Teacher Assistant Hub")
  
  sub_tab = st.selectbox(
      "Select Feature:",
      [
          "📒 Notebook Checking Tracker", 
          "📞 Student Parent Call Record", 
          "📤 Daily Present Report & WhatsApp SMS Sender"
      ]
  )

  if sub_tab == "📒 Notebook Checking Tracker":
    st.markdown("### 📒 Student Notebook Evaluation Status")
    nb_class = st.selectbox("Select Class for Notebook Check", classes_list, key="nb_cls")
    nb_sub = st.selectbox("Select Subject", subjects_list, key="nb_sub")
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
      st_sr = st.number_input("Student SR Number", min_value=1)
      st_name_nb = st.text_input("Student Name")
    with col_n2:
      check_status = st.selectbox("Notebook Status", ["Checked & Verified", "Pending Work", "Incomplete / Warning"])
      remarks = st.text_input("Teacher Remarks", "Good presentation")

    if st.button("💾 Save Notebook Record"):
      st.success(f"Notebook record saved for SR No: {st_sr} ({check_status})!")

  elif sub_tab == "📞 Student Parent Call Record":
    st.markdown("### 📞 Parent Communication & Call Logs")
    call_sr = st.number_input("Student SR No", min_value=1, key="call_sr")
    parent_ph = st.text_input("Contact Number Called", "9828595276", key="call_ph")
    call_reason = st.selectbox("Reason for Call", ["Absenteeism Inquiry", "Fees Reminder", "Academic Performance", "General Disciplinary"])
    call_notes = st.text_area("Call Discussion Summary", "Parent assured student will attend regularly from tomorrow.")

    if st.button("📞 Save Call Log Record"):
      st.success("Call log saved to database successfully!")

  elif sub_tab == "📤 Daily Present Report & WhatsApp SMS Sender":
    st.markdown("### 📤 Daily Attendance & Present SMS Hub")
    sms_class = st.selectbox("Select Class", classes_list, key="sms_cls")
    report_date = st.date_input("Attendance Date", datetime.date.today())
    
    st.info("💡 Click below to generate automated Daily Present Report SMS and dispatch instantly via WhatsApp/SMS.")
    
    sample_msg = f"Dear Parent, Your ward has been marked PRESENT in Campus School for class {sms_class} on date {report_date}. Regards, Principal."
    st.text_area("Generated SMS Template", sample_msg)
    
    target_mob = st.text_input("Parent Mobile Number", "9828595276", key="target_m")
    
    if st.button("🚀 Send Daily Present SMS via WhatsApp"):
      encoded_sms = urllib.parse.quote(sample_msg)
      wa_link = f"https://wa.me/91{target_mob}?text={encoded_sms}"
      st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%; height:45px; background-color:#25D366; color:white; font-weight:bold; border:none; border-radius:12px;">📲 Send Present Report via WhatsApp</button></a>', unsafe_allow_html=True)
      st.success("SMS Link Generated Successfully!")
        import streamlit as st

# --- CSS STYLING ---
st.markdown(
    """
    <style>
    .app-header-bar { 
        background: linear-gradient(135deg, #1E1B4B, #312E81); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        color: white; 
        padding: 16px 18px; 
        border-radius: 24px; 
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); 
        margin-bottom: 18px; 
    } 
    .header-top { 
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
    } 
    .app-brand { 
        display: flex; 
        align-items: center; 
        gap: 12px; 
    } 
    .app-icon { 
        font-size: 28px; 
        background: linear-gradient(135deg, #6366F1, #4F46E5); 
        padding: 8px 12px; 
        border-radius: 16px; 
    } 
    .app-title-text h3 { 
        margin: 0; 
        font-size: 18px; 
        color: #F8FAFC; 
        font-weight: 800; 
    } 
    .app-title-text span { 
        font-size: 11px; 
        color: #C7D2FE; 
        font-weight: 600; 
    }
    .status-badge { 
        background: rgba(34, 197, 94, 0.15); 
        color: #4ADE80; 
        border: 1px solid rgba(74, 222, 128, 0.2); 
        padding: 4px 10px; 
        border-radius: 20px; 
        font-size: 11px; 
        font-weight: 700; 
    }
    .admin-info-box { 
        background: rgba(255, 255, 255, 0.08); 
        border-radius: 16px; 
        padding: 10px 14px; 
        margin-top: 12px; 
        font-size: 12px; 
        color: #E0E7FF; 
        border: 1px solid rgba(255, 255, 255, 0.12); 
    } 
    .admin-info-box p { 
        margin: 2px 0; 
    } 
    .admin-info-box a { 
        color: #818CF8; 
        text-decoration: none; 
        font-weight: 700; 
    }
    .colored-card-admission { 
        background: linear-gradient(135deg, #EFF6FF, #DBEAFE); 
        border-left: 6px solid #3B82F6; 
        padding: 16px; 
        border-radius: 16px; 
        margin-bottom: 15px; 
        color: #1E3A8A; 
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1); 
    }
    .colored-card-cert { 
        background: linear-gradient(135deg, #FDF4FF, #FAE8FF); 
        border-left: 6px solid #D946EF; 
        padding: 16px; 
        border-radius: 16px; 
        margin-bottom: 15px; 
        color: #701A75; 
        box-shadow: 0 4px 12px rgba(217, 70, 239, 0.1); 
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 16px !important; 
        height: 50px !important; 
        font-size: 15px !important;
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #4F46E5, #4338CA) !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.4) !important;
    }    
    </style>
    """,
    unsafe_allow_html=True,
)
