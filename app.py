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
    page_title="Dream Shiksha ERP - Sakshi Solution",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- 2. PREMIUM UI & MODERN CUSTOM CSS STYLING ---
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

    /* Custom Section Folders Styling */
    .folder-card {
        background: #F1F5F9;
        border-left: 5px solid #4F46E5;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 15px;
        font-weight: bold;
        color: #1E1B4B;
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
                <h3>Dream Shiksha ERP</h3>
                <span>POWERED BY SAKSHI SOLUTION</span>
            </div>
        </div>
        <span class="status-badge">🟢 Live System</span>
    </div>
    <div class="admin-info-box">
        <p>🏢 <b>Provider:</b> Sakshi Solution</p>
        <p>👨‍💼 <b>Developer:</b> Anand Nehra</p>
        <p>📞 <b>Contact:</b> <a href="tel:9828595276">9828595276</a> | ✉️ <b>Email:</b> <a href="mailto:anandnehra8@gmail.com">anandnehra8@gmail.com</a></p>
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
  login_mode = st.radio(
      "Select Portal Mode", ["Admin Login (Free)", "Staff / Teacher Login"]
  )

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

# --- CUSTOMIZED FOLDER CATEGORIES ---
menu = st.selectbox(
    "📁 Select Module Folder (मॉड्यूल फोल्डर चुनें):",
    [
        "📂 FOLDER 1: Student Admission & SR Master (प्रवेश एवं SR रजिस्टर)",
        "📂 FOLDER 2: Certificates Hub (TC, Character & Study)",
        "📂 FOLDER 3: Fee Manager & Installments (फीस प्रबंधन)",
        "📂 FOLDER 4: Results & Marks Management (परिणाम एवं अंक)",
        "📂 FOLDER 5: Digital Notice & WhatsApp Alerts (नोटीस एवं संदेश)",
        "📂 FOLDER 6: Transport & Bus Tracking (बस एवं परिवहन)",
        "📂 FOLDER 7: Academic Materials & NCERT Paper Setter",
        "📂 FOLDER 8: Accounts & Cash Book (कैश बुक एवं लेजर)",
        "📂 FOLDER 9: Attendance & Student Analytics (उपस्थिति विश्लेषक)",
        "📂 FOLDER 10: Online Exam CBT Portal (NEET Level)",
        "📂 FOLDER 11: Staff Directory & Payroll (स्टाफ प्रबंधन)",
        "📂 FOLDER 12: Financial Summary & Analytics Dashboard",
        "📂 FOLDER 13: App License & Developer Info",
    ],
)

st.markdown("---")

classes_list = [f"Class {i}" for i in range(1, 13)]
sections_list = ["A", "B", "C", "D"]
subjects_list = [
    "Mathematics",
    "Science",
    "Hindi",
    "English",
    "Social Science",
    "Physics",
    "Chemistry",
    "Biology",
]


def is_valid_aadhaar(aadhaar_str):
  return bool(re.match(r"^\d{12}$", str(aadhaar_str)))


# ==========================================
# FOLDER 1: STUDENT ADMISSION & SR MASTER
# ==========================================
if menu == "📂 FOLDER 1: Student Admission & SR Master (प्रवेश एवं SR रजिस्टर)":
  st.markdown(
      '<div class="folder-card">📋 Student Admission Form & Master SR Register</div>',
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns(2)
  with col1:
    sr_no = st.number_input("SR Number / Admission ID", min_value=1, step=1)
    st_name = st.text_input("Student Name")
    gender = st.selectbox("Gender", ["Boy", "Girl", "Other"])
    s_class = st.selectbox("Class Level", classes_list)
    s_sec = st.selectbox("Section", sections_list)
  with col2:
    roll_no = st.number_input("Roll No", min_value=1, step=1)
    f_name = st.text_input("Father's Name")
    m_name = st.text_input("Mother's Name")
    mobile = st.text_input("Parent Mobile Number")
    aadhaar = st.text_input("Aadhaar Card Number (12 Digits)")

  st.markdown("---")
  st.subheader("🚌 Transport Allocation")
  route = st.text_input("Assigned Bus Route", "Route 1 - City Line")
  drop_point = st.text_input("Pickup / Drop Point", "Main Market Bus Stop")

  if st.button("💾 Submit Admission & Register Student"):
    if aadhaar and not is_valid_aadhaar(aadhaar):
      st.error("Invalid Aadhaar Number! Must be 12 digits.")
    else:
      if supabase:
        try:
          supabase.table("students").insert({
              "sr_no": sr_no,
              "roll_no": roll_no,
              "student_name": st_name,
              "father_name": f_name,
              "gender": gender,
              "class": s_class,
              "section": s_sec,
              "mobile": mobile,
              "aadhaar": aadhaar,
              "route": route,
              "drop_point": drop_point,
          }).execute()
          st.success("Student Profile & Admission Successfully Saved!")
        except Exception as e:
          st.error(f"Database Error: {e}")
      else:
        st.success("Demo Mode: Student SR Record Created!")

# ==========================================
# FOLDER 2: CERTIFICATES HUB
# ==========================================
elif menu == "📂 FOLDER 2: Certificates Hub (TC, Character & Study)":
  st.markdown(
      '<div class="folder-card">📜 Official Student Certificate Portal</div>',
      unsafe_allow_html=True,
  )

  cert_type = st.selectbox(
      "Choose Certificate Type",
      [
          "Character Certificate (चरित्र प्रमाण पत्र)",
          "Transfer Certificate (TC)",
          "Study Certificate (अध्ययनरत प्रमाण पत्र)",
      ],
  )

  sr_no = st.text_input("SR / Admission Number")
  st_name = st.text_input("Student Name")
  f_name = st.text_input("Father Name")
  s_class = st.selectbox("Class", classes_list)
  dob = st.date_input("Date of Birth", datetime.date(2010, 1, 1))
  conduct = st.selectbox(
      "Behavior / Conduct", ["Excellent", "Good", "Satisfactory"]
  )

  def generate_cert_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(150, 750, "DREAM SHIKSHA ACADEMY")
    p.setFont("Helvetica", 10)
    p.drawString(200, 735, "Powered by Sakshi Solution")
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

  if st.button("📄 Generate Certificate PDF"):
    st.download_button(
        "📥 Download PDF Document",
        generate_cert_pdf(),
        file_name=f"{cert_type}_{sr_no}.pdf",
        mime="application/pdf",
    )

# ==========================================
# FOLDER 3: FEE MANAGER
# ==========================================
elif menu == "📂 FOLDER 3: Fee Manager & Installments (फीस प्रबंधन)":
  st.markdown(
      '<div class="folder-card">💳 3-Installment Fee Manager & Receipt</div>',
      unsafe_allow_html=True,
  )

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

  def generate_fee_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, 750, "OFFICIAL FEE RECEIPT")
    p.setFont("Helvetica", 10)
    p.drawString(50, 725, f"Date: {datetime.date.today()}")
    p.drawString(50, 705, f"Student: {st_name} | SR No: {sr_no}")
    p.line(50, 690, 560, 690)
    p.drawString(50, 660, f"Total Annual Fee: Rs. {total_fee}")
    p.drawString(50, 640, f"1st Installment: Rs. {inst1}")
    p.drawString(50, 620, f"2nd Installment: Rs. {inst2}")
    p.drawString(50, 600, f"3rd Installment: Rs. {inst3}")
    p.drawString(50, 570, f"Total Paid Fee: Rs. {total_paid}")
    p.drawString(50, 550, f"Remaining Pending Balance: Rs. {pending}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

  if st.button("💾 Save Fee & Download Receipt PDF"):
    st.download_button(
        "📥 Download Fee Receipt PDF",
        generate_fee_pdf(),
        file_name=f"FeeReceipt_SR_{sr_no}.pdf",
        mime="application/pdf",
    )

# ==========================================
# FOLDER 4: RESULTS & MARKS MANAGEMENT
# ==========================================
elif menu == "📂 FOLDER 4: Results & Marks Management (परिणाम एवं अंक)":
  st.markdown(
      '<div class="folder-card">📊 Marks Entry & Result Generator</div>',
      unsafe_allow_html=True,
  )

  tab1, tab2 = st.tabs(["📊 Generate Result Sheet", "📝 Enter Exam Marks"])

  with tab1:
    data = {
        "SR No": [101, 102, 103, 104],
        "Student Name": ["Aarav Sharma", "Priya Verma", "Rahul Singh", "Neha"],
        "Gender": ["Boy", "Girl", "Boy", "Girl"],
        "Hindi": [85, 92, 78, 88],
        "English": [88, 90, 74, 85],
        "Maths": [95, 88, 65, 92],
        "Science": [90, 94, 70, 89],
    }
    df = pd.DataFrame(data)
    df["Total Marks"] = (
        df["Hindi"] + df["English"] + df["Maths"] + df["Science"]
    )
    df["Percentage (%)"] = (df["Total Marks"] / 400) * 100

    st.dataframe(df)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      df.to_excel(writer, index=False, sheet_name="ResultSheet")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Export Result Sheet to Excel (.xlsx)",
        data=excel_data,
        file_name="Hiralal_Result_Sheet_2026.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  with tab2:
    sr = st.number_input("Student SR No", min_value=1)
    sub = st.selectbox("Select Subject", subjects_list)
    marks = st.number_input("Marks (Out of 100)", 0, 100, 85)
    if st.button("Save Marks Entry"):
      st.success("Marks saved successfully!")

# ==========================================
# FOLDER 5: NOTICE & WHATSAPP ALERTS
# ==========================================
elif menu == "📂 FOLDER 5: Digital Notice & WhatsApp Alerts (नोटीस एवं संदेश)":
  st.markdown(
      '<div class="folder-card">📢 Instant School Notice Board & WhatsApp</div>',
      unsafe_allow_html=True,
  )

  notice = st.text_area(
      "Write Notice Message",
      "Dear Parents, Tomorrow is a holiday on account of heavy rainfall.",
  )
  parent_phone = st.text_input("Parent Mobile Number (10 Digits)", "9828595276")

  if st.button("Publish Notice to Board"):
    st.success("Notice published to school notice board!")

  if parent_phone and notice:
    encoded_notice = urllib.parse.quote(notice)
    whatsapp_url = f"https://wa.me/91{parent_phone}?text={encoded_notice}"
    st.markdown(
        f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; background-color:#25D366; color:white; font-weight:bold; border:none; border-radius:12px; cursor:pointer; margin-top:10px;">📲 Direct Send via WhatsApp</button></a>',
        unsafe_allow_html=True,
    )

# ==========================================
# FOLDER 6: TRANSPORT & BUS TRACKING
# ==========================================
elif menu == "📂 FOLDER 6: Transport & Bus Tracking (बस एवं परिवहन)":
  st.markdown(
      '<div class="folder-card">🚌 Transport, Route & Pickup Point Portal</div>',
      unsafe_allow_html=True,
  )

  route_no = st.selectbox("Select Route Number", ["Route 1", "Route 2"])

  if route_no == "Route 1":
    bus_data = {
        "SR No": [101, 103],
        "Student Name": ["Aarav Sharma", "Rahul Singh"],
        "Pickup/Drop Point": ["Main Bus Stop", "Station Road"],
        "Bus Fee (₹)": [1200, 1000],
    }
  else:
    bus_data = {
        "SR No": [102, 104],
        "Student Name": ["Priya Verma", "Neha"],
        "Pickup/Drop Point": ["Civil Lines", "Airport Circle"],
        "Bus Fee (₹)": [1500, 1500],
    }

  st.dataframe(pd.DataFrame(bus_data))

# ==========================================
# FOLDER 7: NCERT & ACADEMIC MATERIALS
# ==========================================
elif menu == "📂 FOLDER 7: Academic Materials & NCERT Paper Setter":
  st.markdown(
      '<div class="folder-card">📚 Chapter-Wise NCERT PDF & Paper Generator</div>',
      unsafe_allow_html=True,
  )

  s_class = st.selectbox("Select Class Level", classes_list)
  subject = st.selectbox("Select Subject", subjects_list)

  st.markdown("### 📖 Chapter-Wise Books")
  st.write(
      f"1. **Chapter 1: Fundamentals of {subject}** 👉 [Download Chapter PDF](https://ncert.nic.in/textbook.php)"
  )
  st.write(
      f"2. **Chapter 2: Advanced Topics in {subject}** 👉 [Download Chapter PDF](https://ncert.nic.in/textbook.php)"
  )

  st.markdown("---")
  st.subheader("⚡ Auto Question Paper Generator")
  if st.button("📄 Generate Test Paper"):
    st.write(f"**Subject:** {subject} | **Class:** {s_class} | **Time:** 2 Hours")
    st.write("Q1. Explain the fundamental laws of Chapter 1. (3 Marks)")
    st.write(
        "Q2. Differentiate between primary and secondary processes. (5 Marks)"
    )

# ==========================================
# FOLDER 8: ACCOUNTS & CASH BOOK
# ==========================================
elif menu == "📂 FOLDER 8: Accounts & Cash Book (कैश बुक एवं लेजर)":
  st.markdown(
      '<div class="folder-card">💼 Busy Software Style Cash Book & Ledger</div>',
      unsafe_allow_html=True,
  )

  entry_type = st.radio(
      "Transaction Type", ["Cash In (Receipt)", "Cash Out (Payment)"], horizontal=True
  )
  category = st.text_input("Head / Category", "Tuition Fees Collection")
  amount = st.number_input("Amount (₹)", value=5000, step=500)
  remarks = st.text_input("Voucher Remarks", "Receipt No #1042")

  if st.button("💾 Save Ledger Voucher"):
    st.success(f"Voucher saved! Amount ₹{amount} logged in Cash Book.")

# ==========================================
# FOLDER 9: ATTENDANCE & ANALYTICS
# ==========================================
elif menu == "📂 FOLDER 9: Attendance & Student Analytics (उपस्थिति विश्लेषक)":
  st.markdown(
      '<div class="folder-card">📈 Daily Boys/Girls Attendance Analytics</div>',
      unsafe_allow_html=True,
  )

  c1, c2 = st.columns(2)
  c1.metric("👦 Boys Present", "240 / 250", "96%")
  c2.metric("👧 Girls Present", "210 / 220", "95.4%")

  st.markdown("---")

  att_df = pd.DataFrame({
      "Category": ["Boys Present", "Boys Absent", "Girls Present", "Girls Absent"],
      "Count": [240, 10, 210, 10],
  })

  fig_att = px.pie(
      att_df,
      values="Count",
      names="Category",
      hole=0.4,
      color="Category",
      color_discrete_map={
          "Boys Present": "#4F46E5",
          "Boys Absent": "#93C5FD",
          "Girls Present": "#EC4899",
          "Girls Absent": "#FBCFE8",
      },
  )
  fig_att.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
  st.plotly_chart(fig_att, use_container_width=True)

# ==========================================
# FOLDER 10: ONLINE CBT EXAM
# ==========================================
elif menu == "📂 FOLDER 10: Online Exam CBT Portal (NEET Level)":
  st.markdown(
      '<div class="folder-card">💻 NEET Level Online CBT Exam Portal</div>',
      unsafe_allow_html=True,
  )

  st.info("⏱️ Test Time: 180 Minutes | Marking: +4, -1")
  st.markdown("**Q1. [Physics]** What is the unit of Electric Dipole Moment?")
  st.radio("Options:", ["Coulomb-meter", "Volt/meter", "Tesla", "Weber"])
  if st.button("Submit CBT Exam"):
    st.balloons()
    st.success("Test Submitted Successfully!")

# ==========================================
# FOLDER 11: STAFF DIRECTORY & PAYROLL
# ==========================================
elif menu == "📂 FOLDER 11: Staff Directory & Payroll (स्टाफ प्रबंधन)":
  st.markdown(
      '<div class="folder-card">👨‍🏫 Staff Directory & Payroll</div>',
      unsafe_allow_html=True,
  )

  st_name = st.text_input("Staff Name")
  st_role = st.selectbox("Designation", ["PGT", "TGT", "PRT", "Accountant"])
  st_sal = st.number_input("Monthly Salary (₹)", value=25000)
  if st.button("Save Staff Record"):
    st.success(f"Staff record for {st_name} saved.")

# ==========================================
# FOLDER 12: FINANCIAL DASHBOARD
# ==========================================
elif menu == "📂 FOLDER 12: Financial Summary & Analytics Dashboard":
  st.markdown(
      '<div class="folder-card">📊 Complete Financial Analytics Dashboard</div>',
      unsafe_allow_html=True,
  )

  c1, c2 = st.columns(2)
  c1.metric("Total Fees Collected", "₹12,45,000", "+83%")
  c2.metric("Pending Fees", "₹2,55,000", "-17%")

  st.markdown("---")

  fee_df = pd.DataFrame({
      "Status": ["Collected Fee", "Pending Fee"],
      "Amount": [1245000, 255000],
  })

  fig_fee = px.pie(
      fee_df,
      values="Amount",
      names="Status",
      color="Status",
      color_discrete_map={
          "Collected Fee": "#4F46E5",
          "Pending Fee": "#EF4444",
      },
      hole=0.4,
  )
  fig_fee.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260)
  st.plotly_chart(fig_fee, use_container_width=True)

  st.markdown("### 📈 Monthly Collection Trend")
  monthly_trend = pd.DataFrame({
      "Month": ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
      "Collection (₹)": [180000, 220000, 150000, 310000, 245000, 140000],
  })
  fig_trend = px.line(
      monthly_trend,
      x="Month",
      y="Collection (₹)",
      markers=True,
  )
  fig_trend.update_traces(line_color="#10B981", line_width=3)
  fig_trend.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10))
  st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# FOLDER 13: APP LICENSE & DEVELOPER INFO
# ==========================================
elif menu == "📂 FOLDER 13: App License & Developer Info":
  st.markdown(
      '<div class="folder-card">👑 App License & Provider Details</div>',
      unsafe_allow_html=True,
  )

  st.markdown(
      """
    <div style="background:#F1F5F9; padding:15px; border-radius:15px; border:1px solid #CBD5E1">
        <h4>🏢 Powered by: Sakshi Solution</h4>
        <p><b>Developer:</b> Anand Nehra</p>
        <p><b>Contact:</b> 9828595276 | anandnehra8@gmail.com</p>
        <hr>
        <p><b>License Status:</b> Activated Enterprise Version</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
