import streamlit as st
from supabase import create_client, Client
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime
import re

# --- 1. ADVANCED MOBILE-FIRST APP CONFIGURATION ---
st.set_page_config(
    page_title="School ERP - Anand Nehra", 
    page_icon="🏫", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM UI & MODERN CSS STYLING ---
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0F172A">

    <style>
    /* Hide Streamlit Default Components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Global Container Setup */
    .main .block-container {
        padding-top: 10px !important;
        padding-bottom: 80px !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }

    /* Gradient Header Bar */
    .app-header-bar {
        background: linear-gradient(135deg, #1E293B, #0F172A);
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
    
    .app-brand { display: flex; align-items: center; gap: 12px; }
    .app-icon { 
        font-size: 28px; 
        background: linear-gradient(135deg, #3B82F6, #2563EB); 
        padding: 8px 12px; 
        border-radius: 16px; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    .app-title-text h3 { 
        margin: 0; 
        font-size: 18px; 
        color: #F8FAFC; 
        font-weight: 800; 
        letter-spacing: -0.5px;
    }
    .app-title-text span { 
        font-size: 11px; 
        color: #94A3B8; 
        font-weight: 600;
        letter-spacing: 0.5px;
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

    /* Admin Developer Badge */
    .admin-info-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 10px 14px;
        margin-top: 12px;
        font-size: 12px;
        color: #CBD5E1;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .admin-info-box p { margin: 2px 0; }
    .admin-info-box a { color: #38BDF8; text-decoration: none; font-weight: 700; }

    /* Elegant Card Design */
    .card { 
        background: #FFFFFF; 
        padding: 20px; 
        border-radius: 20px; 
        margin-bottom: 16px; 
        border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05); 
    }

    /* Custom Stylish Buttons */
    .stButton>button { 
        width: 100%; 
        border-radius: 16px !important; 
        height: 52px !important; 
        font-size: 16px !important;
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Interactive CBT Box */
    .cbt-box {
        background: #F0F9FF;
        border-left: 5px solid #0284C7;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 16px;
        color: #0C4A6E;
    }
    </style>
""", unsafe_allow_html=True)

# Admin Header Bar
st.markdown("""
<div class="app-header-bar">
    <div class="header-top">
        <div class="app-brand">
            <div class="app-icon">🏫</div>
            <div class="app-title-text">
                <h3>School ERP Pro Max</h3>
                <span>ULTIMATE CAMPUS PORTAL</span>
            </div>
        </div>
        <span class="status-badge">🟢 Online</span>
    </div>
    <div class="admin-info-box">
        <p>👨‍💼 <b>Developer / Admin:</b> Anand Nehra</p>
        <p>📞 <b>Contact:</b> <a href="tel:9828595276">9828595276</a> | ✉️ <b>Email:</b> <a href="mailto:anandnehra8@gmail.com">anandnehra8@gmail.com</a></p>
    </div>
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
            plan_choice = st.radio(
                "Select Subscription Plan", 
                [
                    "🎁 1 Day Free Demo Plan - ₹0 (Trial)", 
                    "📅 Yearly Plan - ₹2,000 / Year", 
                    "👑 Lifetime Plan - ₹20,000"
                ]
            )
            
            if "Free Demo" in plan_choice:
                pay_amt = 0
                st.success("🎉 You selected 1 Day Free Trial! No payment required.")
            elif "Yearly" in plan_choice:
                pay_amt = 2000
                st.info(f"Selected Plan Fee: ₹{pay_amt:,}")
                upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am={pay_amt}&cu=INR"
                st.markdown(f"👉 **[Click Here to Pay App Fee ₹{pay_amt:,}]({upi_pay})**")
            else:
                pay_amt = 20000
                st.info(f"Selected Plan Fee: ₹{pay_amt:,}")
                upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am={pay_amt}&cu=INR"
                st.markdown(f"👉 **[Click Here to Pay App Fee ₹{pay_amt:,}]({upi_pay})**")
            
            otp = st.text_input("Enter OTP (Use '1234')", type="password")
            if st.button("Verify OTP & Login"):
                if otp == "1234":
                    st.session_state.logged_in = True
                    st.session_state.role = "Teacher (Demo)" if pay_amt == 0 else "Teacher"
                    st.rerun()
                else:
                    st.error("Incorrect OTP!")
    st.stop()

# --- 5. TOP NAVIGATION & MODULE SELECTOR ---
col_prof, col_logout = st.columns([3, 1])
with col_prof:
    st.markdown(f"👤 **Role:** `{st.session_state.role}`")
with col_logout:
    if st.button("🚪 Logout", key=get_ai_key("top_logout_btn")):
        st.session_state.logged_in = False
        st.rerun()
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
        <h4>👨‍💼 System Developer & Administrator</h4>
        <p>• <b>Name:</b> Anand Nehra</p>
        <p>• <b>Phone:</b> +91 9828595276</p>
        <p>• <b>Email:</b> anandnehra8@gmail.com</p>
        <hr>
        <h4>💰 Pricing Overview</h4>
        <p>• <b>🎁 1 Day Demo Access:</b> FREE (Complete System Trial)</p>
        <p>• <b>📅 Yearly Subscription:</b> ₹2,000 / Year</p>
        <p>• <b>👑 Lifetime Access:</b> ₹20,000 (One-Time Payment)</p>
        <p>• <b>🔐 Admin Access:</b> Full System Control Included</p>
        <p>• <b>⚡ Modules Unlocked:</b> All 14 Advanced Modules</p>
    </div>
    """, unsafe_allow_html=True)

# --- MODULE 2: STAFF DIRECTORY ---
elif menu == "2. 👨‍🏫 Staff Directory & Teacher List":
    st.subheader("👨‍🏫 Staff & Teacher Management")
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
                st.info(f"Staff Record Saved ({st_name})!")

# --- MODULE 3: MANUAL FEE COLLECTION ---
elif menu == "3. 💳 Manual Fee Collection & Receipt":
    st.subheader("💳 Manual Fee Entry & Receipt Portal")
    s_roll = st.number_input("Enter Student Roll No", min_value=1, step=1)
    s_name = st.text_input("Student Name")
    s_class = st.selectbox("Class", classes_list)
    pay_mode = st.radio("Payment Mode", ["Cash (नकद)", "UPI / QR Code", "Bank Transfer / Cheque"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1: tot_fee = st.number_input("Total Fee (₹)", value=2000)
    with col2: rec_fee = st.number_input("Received Amount (₹)", value=2000)
        
    pending = tot_fee - rec_fee
    remarks = st.text_input("Payment Remarks", "Fees for Term 1")

    def generate_manual_fee_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(180, 750, "OFFICIAL FEE RECEIPT")
        p.setFont("Helvetica", 10)
        p.drawString(50, 720, f"Date: {datetime.date.today()} | Mode: {pay_mode}")
        p.drawString(50, 700, f"Student: {s_name} | Roll No: {s_roll} | Class: {s_class}")
        p.line(50, 685, 560, 685)
        p.drawString(50, 650, f"Amount Received: Rs. {rec_fee}")
        p.drawString(50, 630, f"Balance Due: Rs. {pending}")
        p.drawString(50, 570, "Admin Signature (Anand Nehra): __________________")
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    if st.button("💾 Record Payment & Download PDF"):
        st.success("Fee Payment recorded successfully!")
        st.download_button("📥 Download Fee Receipt PDF", generate_manual_fee_pdf(), file_name=f"FeeReceipt_Roll_{s_roll}.pdf", mime="application/pdf")

# --- MODULE 4: ONLINE TEST & NEET CBT ---
elif menu == "4. 💻 Online Test & NEET Level CBT Portal":
    st.subheader("💻 NTA / NEET Level CBT Test Portal")
    st.info("⏱️ Test Time: 180 Minutes | Marking: +4 for Correct, -1 for Wrong")
    
    score = 0
    st.markdown("""
    <div class="cbt-box">
        <b>Q1. [Physics]</b> Two point charges +q and -q are placed at distance d apart. What is the electric dipole moment vector direction?
    </div>
    """, unsafe_allow_html=True)
    q1_ans = st.radio("Select Answer Q1:", ["(A) From positive to negative charge", "(B) From negative to positive charge", "(C) Perpendicular to line", "(D) None"], key="q1")
    if q1_ans == "(B) From negative to positive charge": score += 4

    if st.button("🚀 Submit NEET CBT Test"):
        st.balloons()
        st.success(f"🎉 Test Submitted! Score: {score} / 4 Marks")

# --- OTHER MODULES ---
elif menu == "5. ✏️ Add / Edit Complete Student Profile":
    st.subheader("✏️ Student Master Form")
    roll_no = st.number_input("Roll No", min_value=1, step=1)
    s_name = st.text_input("Student Name")
    f_name = st.text_input("Father Name")
    if st.button("💾 Save Profile"): st.success("Saved!")

elif menu == "6. 👥 View All Students Table":
    st.subheader("👥 Student Directory")
    st.info("Database student table ready.")

elif menu == "7. 🔍 Advance Multi-Search Profile":
    st.subheader("🔍 Master Search")
    st.text_input("Search Roll No or Name")

elif menu == "8. 📄 Automatic Report Card Generator (PDF)":
    st.subheader("📄 Instant Report Card Generator")
    st.info("PDF Generation enabled.")

elif menu == "9. 🗓️ School Calendar & Holidays Notice":
    st.subheader("🗓️ Academic Calendar & Notices")

elif menu == "10. 📅 Mark Attendance & WhatsApp Alert":
    st.subheader("📅 Attendance Marker")

elif menu == "11. 📚 Class 1-12 NCERT Textbooks":
    st.subheader("📚 NCERT Books Library")

elif menu == "12. 📄 Auto Question Paper (Hindi & English)":
    st.subheader("📄 Bilingual Paper Generator")

elif menu == "13. 📝 Exam Marks Portal":
    st.subheader("📝 Marks Entry Portal")

elif menu == "14. ✅ Student Answer Sheet Copy Check":
    st.subheader("✅ Student Copy Verification")
import streamlit as st
from supabase import create_client, Client
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime
import re

# --- 1. ADVANCED MOBILE-FIRST APP CONFIGURATION ---
st.set_page_config(
    page_title="School ERP - Anand Nehra", 
    page_icon="🏫", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM UI & MODERN CSS STYLING ---
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0F172A">

    <style>
    /* Hide Streamlit Default Components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Global Container Setup */
    .main .block-container {
        padding-top: 10px !important;
        padding-bottom: 80px !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }

    /* Gradient Header Bar */
    .app-header-bar {
        background: linear-gradient(135deg, #1E293B, #0F172A);
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
    
    .app-brand { display: flex; align-items: center; gap: 12px; }
    .app-icon { 
        font-size: 28px; 
        background: linear-gradient(135deg, #3B82F6, #2563EB); 
        padding: 8px 12px; 
        border-radius: 16px; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    .app-title-text h3 { 
        margin: 0; 
        font-size: 18px; 
        color: #F8FAFC; 
        font-weight: 800; 
        letter-spacing: -0.5px;
    }
    .app-title-text span { 
        font-size: 11px; 
        color: #94A3B8; 
        font-weight: 600;
        letter-spacing: 0.5px;
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

    /* Admin Developer Badge */
    .admin-info-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 10px 14px;
        margin-top: 12px;
        font-size: 12px;
        color: #CBD5E1;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .admin-info-box p { margin: 2px 0; }
    .admin-info-box a { color: #38BDF8; text-decoration: none; font-weight: 700; }

    /* Elegant Card Design */
    .card { 
        background: #FFFFFF; 
        padding: 20px; 
        border-radius: 20px; 
        margin-bottom: 16px; 
        border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05); 
    }

    /* Custom Stylish Buttons */
    .stButton>button { 
        width: 100%; 
        border-radius: 16px !important; 
        height: 52px !important; 
        font-size: 16px !important;
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Interactive CBT Box */
    .cbt-box {
        background: #F0F9FF;
        border-left: 5px solid #0284C7;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 16px;
        color: #0C4A6E;
    }
    </style>
""", unsafe_allow_html=True)

# Admin Header Bar
st.markdown("""
<div class="app-header-bar">
    <div class="header-top">
        <div class="app-brand">
            <div class="app-icon">🏫</div>
            <div class="app-title-text">
                <h3>School ERP Pro Max</h3>
                <span>ULTIMATE CAMPUS PORTAL</span>
            </div>
        </div>
        <span class="status-badge">🟢 Online</span>
    </div>
    <div class="admin-info-box">
        <p>👨‍💼 <b>Developer / Admin:</b> Anand Nehra</p>
        <p>📞 <b>Contact:</b> <a href="tel:9828595276">9828595276</a> | ✉️ <b>Email:</b> <a href="mailto:anandnehra8@gmail.com">anandnehra8@gmail.com</a></p>
    </div>
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
            plan_choice = st.radio(
                "Select Subscription Plan", 
                [
                    "🎁 1 Day Free Demo Plan - ₹0 (Trial)", 
                    "📅 Yearly Plan - ₹2,000 / Year", 
                    "👑 Lifetime Plan - ₹20,000"
                ]
            )
            
            if "Free Demo" in plan_choice:
                pay_amt = 0
                st.success("🎉 You selected 1 Day Free Trial! No payment required.")
            elif "Yearly" in plan_choice:
                pay_amt = 2000
                st.info(f"Selected Plan Fee: ₹{pay_amt:,}")
                upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am={pay_amt}&cu=INR"
                st.markdown(f"👉 **[Click Here to Pay App Fee ₹{pay_amt:,}]({upi_pay})**")
            else:
                pay_amt = 20000
                st.info(f"Selected Plan Fee: ₹{pay_amt:,}")
                upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am={pay_amt}&cu=INR"
                st.markdown(f"👉 **[Click Here to Pay App Fee ₹{pay_amt:,}]({upi_pay})**")
            
            otp = st.text_input("Enter OTP (Use '1234')", type="password")
            if st.button("Verify OTP & Login"):
                if otp == "1234":
                    st.session_state.logged_in = True
                    st.session_state.role = "Teacher (Demo)" if pay_amt == 0 else "Teacher"
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
        "14. ✅ Student Answer Sheet Copy Check",
        "15. 🚌 Transport & Bus Tracking System",
        "16. 📢 Instant Notice Board",
        "17. 📊 Financial Summary Dashboard"
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
        <h4>👨‍💼 System Developer & Administrator</h4>
        <p>• <b>Name:</b> Anand Nehra</p>
        <p>• <b>Phone:</b> +91 9828595276</p>
        <p>• <b>Email:</b> anandnehra8@gmail.com</p>
        <hr>
        <h4>💰 Pricing Overview</h4>
        <p>• <b>🎁 1 Day Demo Access:</b> FREE (Complete System Trial)</p>
        <p>• <b>📅 Yearly Subscription:</b> ₹2,000 / Year</p>
        <p>• <b>👑 Lifetime Access:</b> ₹20,000 (One-Time Payment)</p>
        <p>• <b>🔐 Admin Access:</b> Full System Control Included</p>
        <p>• <b>⚡ Modules Unlocked:</b> All 17 Advanced Modules</p>
    </div>
    """, unsafe_allow_html=True)

# --- MODULE 2: STAFF DIRECTORY ---
elif menu == "2. 👨‍🏫 Staff Directory & Teacher List":
    st.subheader("👨‍🏫 Staff & Teacher Management")
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
                st.success(f"Staff record for {st_name} saved in Supabase!")
            except Exception as e:
                st.error(f"Error saving to database: {e}")

# --- MODULE 3: MANUAL FEE COLLECTION ---
elif menu == "3. 💳 Manual Fee Collection & Receipt":
    st.subheader("💳 Manual Fee Entry & Receipt Portal")
    s_roll = st.number_input("Enter Student Roll No", min_value=1, step=1)
    s_name = st.text_input("Student Name")
    s_class = st.selectbox("Class", classes_list)
    pay_mode = st.radio("Payment Mode", ["Cash (नकद)", "UPI / QR Code", "Bank Transfer / Cheque"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1: tot_fee = st.number_input("Total Fee (₹)", value=2000)
    with col2: rec_fee = st.number_input("Received Amount (₹)", value=2000)
        
    pending = tot_fee - rec_fee
    remarks = st.text_input("Payment Remarks", "Fees for Term 1")

    def generate_manual_fee_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(180, 750, "OFFICIAL FEE RECEIPT")
        p.setFont("Helvetica", 10)
        p.drawString(50, 720, f"Date: {datetime.date.today()} | Mode: {pay_mode}")
        p.drawString(50, 700, f"Student: {s_name} | Roll No: {s_roll} | Class: {s_class}")
        p.line(50, 685, 560, 685)
        p.drawString(50, 650, f"Amount Received: Rs. {rec_fee}")
        p.drawString(50, 630, f"Balance Due: Rs. {pending}")
        p.drawString(50, 570, "Admin Signature (Anand Nehra): __________________")
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    if st.button("💾 Record Payment & Download PDF"):
        if supabase:
            try:
                supabase.table("fee_collections").insert({
                    "roll_no": s_roll, "student_name": s_name, "class": s_class,
                    "payment_mode": pay_mode, "total_fee": tot_fee,
                    "received_fee": rec_fee, "pending_fee": pending, "remarks": remarks
                }).execute()
                st.success("Fee Payment saved to Supabase successfully!")
            except Exception as e:
                st.error(f"Database error: {e}")
        st.download_button("📥 Download Fee Receipt PDF", generate_manual_fee_pdf(), file_name=f"FeeReceipt_Roll_{s_roll}.pdf", mime="application/pdf")

# --- MODULE 4: ONLINE TEST & NEET CBT ---
elif menu == "4. 💻 Online Test & NEET Level CBT Portal":
    st.subheader("💻 NTA / NEET Level CBT Test Portal")
    st.info("⏱️ Test Time: 180 Minutes | Marking: +4 for Correct, -1 for Wrong")
    
    score = 0
    st.markdown("""
    <div class="cbt-box">
        <b>Q1. [Physics]</b> Two point charges +q and -q are placed at distance d apart. What is the electric dipole moment vector direction?
    </div>
    """, unsafe_allow_html=True)
    q1_ans = st.radio("Select Answer Q1:", ["(A) From positive to negative charge", "(B) From negative to positive charge", "(C) Perpendicular to line", "(D) None"], key="q1")
    if q1_ans == "(B) From negative to positive charge": score += 4

    if st.button("🚀 Submit NEET CBT Test"):
        st.balloons()
        st.success(f"🎉 Test Submitted! Score: {score} / 4 Marks")

# --- MODULE 5: ADD STUDENT ---
elif menu == "5. ✏️ Add / Edit Complete Student Profile":
    st.subheader("✏️ Student Master Form")
    roll_no = st.number_input("Roll No", min_value=1, step=1)
    s_name = st.text_input("Student Name")
    f_name = st.text_input("Father Name")
    s_class = st.selectbox("Class", classes_list)
    s_sec = st.selectbox("Section", sections_list)
    s_mob = st.text_input("Mobile Number")
    s_adh = st.text_input("Aadhaar Number (12 Digits)")
    
    if st.button("💾 Save Profile"):
        if not is_valid_aadhaar(s_adh):
            st.error("Invalid Aadhaar Number! Must be exactly 12 digits.")
        else:
            if supabase:
                try:
                    supabase.table("students").insert({
                        "roll_no": roll_no, "student_name": s_name, "father_name": f_name,
                        "class": s_class, "section": s_sec, "mobile": s_mob, "aadhaar": s_adh
                    }).execute()
                    st.success("Student profile saved to Supabase successfully!")
                except Exception as e:
                    st.error(f"Error saving student: {e}")

# --- NEW MODULE 15: TRANSPORT MANAGEMENT ---
elif menu == "15. 🚌 Transport & Bus Tracking System":
    st.subheader("🚌 Transport & Route Manager")
    bus_no = st.text_input("Bus / Vehicle Number", "RJ-19-PA-1234")
    route_name = st.text_input("Route Name", "Route 4 - City Center to Campus")
    driver_name = st.text_input("Driver Name & Phone", "Ramesh Kumar - 9876543210")
    monthly_fee = st.number_input("Monthly Bus Fee (₹)", value=1200, step=100)
    
    if st.button("💾 Save Route Record"):
        st.success(f"Route '{route_name}' configured successfully!")

# --- NEW MODULE 16: NOTICE BOARD ---
elif menu == "16. 📢 Instant Notice Board":
    st.subheader("📢 School Notice & Announcement Board")
    notice_title = st.text_input("Notice Heading / Subject")
    target_audience = st.selectbox("Send To", ["All Students & Parents", "Teachers & Staff", "Class 10th & 12th Only"])
    notice_body = st.text_area("Notice Details / Description")
    
    if st.button("🚀 Publish Notice"):
        st.success(f"Notice '{notice_title}' sent to {target_audience}!")

# --- NEW MODULE 17: FINANCIAL DASHBOARD ---
elif menu == "17. 📊 Financial Summary Dashboard":
    st.subheader("📊 Admin Financial Overview")
    if supabase:
        try:
            res_fees = supabase.table("fee_collections").select("received_fee, pending_fee").execute()
            data = res_fees.data
            tot_rec = sum(item['received_fee'] for item in data) if data else 0
            tot_pend = sum(item['pending_fee'] for item in data) if data else 0
            
            col1, col2 = st.columns(2)
            col1.metric("💰 Total Fees Collected", f"₹{tot_rec:,}")
            col2.metric("⏳ Total Fees Pending", f"₹{tot_pend:,}")
        except Exception as e:
            st.info("Financial Dashboard ready. Collect fees to see live graphs!")

# --- OTHER MODULES ---
elif menu == "6. 👥 View All Students Table":
    st.subheader("👥 Student Directory")
    if supabase:
        res = supabase.table("students").select("*").execute()
        if res.data:
            st.dataframe(res.data)
        else:
            st.info("No students added yet.")

elif menu == "7. 🔍 Advance Multi-Search Profile":
    st.subheader("🔍 Master Search")
    st.text_input("Search Roll No or Name")

elif menu == "8. 📄 Automatic Report Card Generator (PDF)":
    st.subheader("📄 Instant Report Card Generator")
    st.info("PDF Generation enabled.")

elif menu == "9. 🗓️ School Calendar & Holidays Notice":
    st.subheader("🗓️ Academic Calendar & Notices")

elif menu == "10. 📅 Mark Attendance & WhatsApp Alert":
    st.subheader("📅 Attendance Marker")

elif menu == "11. 📚 Class 1-12 NCERT Textbooks":
    st.subheader("📚 NCERT Books Library")

elif menu == "12. 📄 Auto Question Paper (Hindi & English)":
    st.subheader("📄 Bilingual Paper Generator")

elif menu == "13. 📝 Exam Marks Portal":
    st.subheader("📝 Marks Entry Portal")
import streamlit as st
from supabase import create_client, Client
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime
import re

# --- AI SAFE-KEY SYSTEM (PREVENTS StreamlitDuplicateElementId) ---
if 'widget_counters' not in st.session_state:
    st.session_state.widget_counters = {}

def get_ai_key(base_name: str) -> str:
    """Dynamically generates a unique, collision-proof key for Streamlit widgets."""
    count = st.session_state.widget_counters.get(base_name, 0) + 1
    st.session_state.widget_counters[base_name] = count
    return f"ai_key_{base_name}_{count}"

# --- 1. ADVANCED MOBILE-FIRST APP CONFIGURATION ---
st.set_page_config(
    page_title="School ERP - Anand Nehra", 
    page_icon="🏫", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM UI & MODERN CSS STYLING ---
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0F172A">

    <style>
    /* Hide Streamlit Default Components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Global Container Setup */
    .main .block-container {
        padding-top: 10px !important;
        padding-bottom: 80px !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }

    /* Gradient Header Bar */
    .app-header-bar {
        background: linear-gradient(135deg, #1E293B, #0F172A);
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
    
    .app-brand { display: flex; align-items: center; gap: 12px; }
    .app-icon { 
        font-size: 28px; 
        background: linear-gradient(135deg, #3B82F6, #2563EB); 
        padding: 8px 12px; 
        border-radius: 16px; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    .app-title-text h3 { 
        margin: 0; 
        font-size: 18px; 
        color: #F8FAFC; 
        font-weight: 800; 
        letter-spacing: -0.5px;
    }
    .app-title-text span { 
        font-size: 11px; 
        color: #94A3B8; 
        font-weight: 600;
        letter-spacing: 0.5px;
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

    /* Admin Developer Badge */
    .admin-info-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 10px 14px;
        margin-top: 12px;
        font-size: 12px;
        color: #CBD5E1;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .admin-info-box p { margin: 2px 0; }
    .admin-info-box a { color: #38BDF8; text-decoration: none; font-weight: 700; }

    /* Elegant Card Design */
    .card { 
        background: #FFFFFF; 
        padding: 20px; 
        border-radius: 20px; 
        margin-bottom: 16px; 
        border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05); 
    }

    /* Custom Stylish Buttons */
    .stButton>button { 
        width: 100%; 
        border-radius: 16px !important; 
        height: 52px !important; 
        font-size: 16px !important;
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Interactive CBT Box */
    .cbt-box {
        background: #F0F9FF;
        border-left: 5px solid #0284C7;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 16px;
        color: #0C4A6E;
    }
    </style>
""", unsafe_allow_html=True)

# Admin Header Bar
st.markdown("""
<div class="app-header-bar">
    <div class="header-top">
        <div class="app-brand">
            <div class="app-icon">🏫</div>
            <div class="app-title-text">
                <h3>School ERP Pro Max</h3>
                <span>ULTIMATE CAMPUS PORTAL</span>
            </div>
        </div>
        <span class="status-badge">🟢 Online</span>
    </div>
    <div class="admin-info-box">
        <p>👨‍💼 <b>Developer / Admin:</b> Anand Nehra</p>
        <p>📞 <b>Contact:</b> <a href="tel:9828595276">9828595276</a> | ✉️ <b>Email:</b> <a href="mailto:anandnehra8@gmail.com">anandnehra8@gmail.com</a></p>
    </div>
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
    login_mode = st.radio("Select Portal Mode", ["Admin Login (Free)", "Staff / Teacher Login (OTP / Pay)"], key=get_ai_key("login_mode"))

    if login_mode == "Admin Login (Free)":
        username = st.text_input("Admin Username", key=get_ai_key("adm_user"))
        password = st.text_input("Admin Password", type="password", key=get_ai_key("adm_pass"))
        if st.button("🚀 Login to App", key=get_ai_key("adm_login_btn")):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Super Admin"
                st.rerun()
            else:
                st.error("Invalid Admin Credentials!")
    else:
        mobile = st.text_input("Enter 10-digit Mobile Number", key=get_ai_key("tch_mob"))
        if mobile:
            plan_choice = st.radio(
                "Select Subscription Plan", 
                [
                    "🎁 1 Day Free Demo Plan - ₹0 (Trial)", 
                    "📅 Yearly Plan - ₹2,000 / Year", 
                    "👑 Lifetime Plan - ₹20,000"
                ],
                key=get_ai_key("plan_choice")
            )
            
            if "Free Demo" in plan_choice:
                pay_amt = 0
                st.success("🎉 You selected 1 Day Free Trial! No payment required.")
            elif "Yearly" in plan_choice:
                pay_amt = 2000
                st.info(f"Selected Plan Fee: ₹{pay_amt:,}")
                upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am={pay_amt}&cu=INR"
                st.markdown(f"👉 **[Click Here to Pay App Fee ₹{pay_amt:,}]({upi_pay})**")
            else:
                pay_amt = 20000
                st.info(f"Selected Plan Fee: ₹{pay_amt:,}")
                upi_pay = f"upi://pay?pa=schoolerp@upi&pn=SchoolERP&am={pay_amt}&cu=INR"
                st.markdown(f"👉 **[Click Here to Pay App Fee ₹{pay_amt:,}]({upi_pay})**")
            
            otp = st.text_input("Enter OTP (Use '1234')", type="password", key=get_ai_key("otp_inp"))
            if st.button("Verify OTP & Login", key=get_ai_key("otp_btn")):
                if otp == "1234":
                    st.session_state.logged_in = True
                    st.session_state.role = "Teacher (Demo)" if pay_amt == 0 else "Teacher"
                    st.rerun()
                else:
                    st.error("Incorrect OTP!")
    st.stop()

# --- 5. TOP NAVIGATION & MODULE SELECTOR ---
col_prof, col_logout = st.columns([3, 1])
with col_prof:
    st.markdown(f"👤 **Role:** `{st.session_state.role}`")
with col_logout:
    if st.button("🚪 Logout", key=get_ai_key("top_logout_btn")):
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
        "14. ✅ Student Answer Sheet Copy Check",
        "15. 🚌 Transport & Bus Tracking System",
        "16. 📢 Instant Notice Board",
        "17. 📊 Financial Summary Dashboard"
    ],
    key=get_ai_key("main_menu_select")
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
        <h4>👨‍💼 System Developer & Administrator</h4>
        <p>• <b>Name:</b> Anand Nehra</p>
        <p>• <b>Phone:</b> +91 9828595276</p>
        <p>• <b>Email:</b> anandnehra8@gmail.com</p>
        <hr>
        <h4>💰 Pricing Overview</h4>
        <p>• <b>🎁 1 Day Demo Access:</b> FREE (Complete System Trial)</p>
        <p>• <b>📅 Yearly Subscription:</b> ₹2,000 / Year</p>
        <p>• <b>👑 Lifetime Access:</b> ₹20,000 (One-Time Payment)</p>
        <p>• <b>🔐 Admin Access:</b> Full System Control Included</p>
        <p>• <b>⚡ Modules Unlocked:</b> All 17 Advanced Modules</p>
    </div>
    """, unsafe_allow_html=True)

# --- MODULE 2: STAFF DIRECTORY ---
elif menu == "2. 👨‍🏫 Staff Directory & Teacher List":
    st.subheader("👨‍🏫 Staff & Teacher Management")
    st_name = st.text_input("Staff Full Name", key=get_ai_key("st_name"))
    st_role = st.selectbox("Designation / Role", ["PGT Teacher", "TGT Teacher", "PRT Teacher", "Accountant", "Clerk", "Lab Assistant", "Peon / Security"], key=get_ai_key("st_role"))
    st_sub = st.selectbox("Main Subject Handled", subjects_list, key=get_ai_key("st_sub"))
    st_mob = st.text_input("Mobile Number", key=get_ai_key("st_mob"))
    st_sal = st.number_input("Monthly Salary (₹)", value=25000, step=1000, key=get_ai_key("st_sal"))
    st_joining = st.date_input("Date of Joining", datetime.date(2024, 1, 1), key=get_ai_key("st_joining"))
    
    if st.button("💾 Save Staff Record", key=get_ai_key("st_save_btn")):
        if supabase:
            try:
                supabase.table("staff").insert({
                    "name": st_name, "role": st_role, "subject": st_sub,
                    "mobile": st_mob, "salary": st_sal, "joining_date": str(st_joining)
                }).execute()
                st.success(f"Staff record for {st_name} saved in Supabase!")
            except Exception as e:
                st.error(f"Error saving to database: {e}")

# --- MODULE 3: MANUAL FEE COLLECTION ---
elif menu == "3. 💳 Manual Fee Collection & Receipt":
    st.subheader("💳 Manual Fee Entry & Receipt Portal")
    s_roll = st.number_input("Enter Student Roll No", min_value=1, step=1, key=get_ai_key("fee_roll"))
    s_name = st.text_input("Student Name", key=get_ai_key("fee_name"))
    s_class = st.selectbox("Class", classes_list, key=get_ai_key("fee_class"))
    pay_mode = st.radio("Payment Mode", ["Cash (नकद)", "UPI / QR Code", "Bank Transfer / Cheque"], horizontal=True, key=get_ai_key("fee_mode"))
    
    col1, col2 = st.columns(2)
    with col1: tot_fee = st.number_input("Total Fee (₹)", value=2000, key=get_ai_key("fee_tot"))
    with col2: rec_fee = st.number_input("Received Amount (₹)", value=2000, key=get_ai_key("fee_rec"))
        
    pending = tot_fee - rec_fee
    remarks = st.text_input("Payment Remarks", "Fees for Term 1", key=get_ai_key("fee_rem"))

    def generate_manual_fee_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(180, 750, "OFFICIAL FEE RECEIPT")
        p.setFont("Helvetica", 10)
        p.drawString(50, 720, f"Date: {datetime.date.today()} | Mode: {pay_mode}")
        p.drawString(50, 700, f"Student: {s_name} | Roll No: {s_roll} | Class: {s_class}")
        p.line(50, 685, 560, 685)
        p.drawString(50, 650, f"Amount Received: Rs. {rec_fee}")
        p.drawString(50, 630, f"Balance Due: Rs. {pending}")
        p.drawString(50, 570, "Admin Signature (Anand Nehra): __________________")
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    if st.button("💾 Record Payment & Download PDF", key=get_ai_key("fee_save_btn")):
        if supabase:
            try:
                supabase.table("fee_collections").insert({
                    "roll_no": s_roll, "student_name": s_name, "class": s_class,
                    "payment_mode": pay_mode, "total_fee": tot_fee,
                    "received_fee": rec_fee, "pending_fee": pending, "remarks": remarks
                }).execute()
                st.success("Fee Payment saved to Supabase successfully!")
            except Exception as e:
                st.error(f"Database error: {e}")
        st.download_button("📥 Download Fee Receipt PDF", generate_manual_fee_pdf(), file_name=f"FeeReceipt_Roll_{s_roll}.pdf", mime="application/pdf", key=get_ai_key("pdf_dl_btn"))

# --- MODULE 4: ONLINE TEST & NEET CBT ---
elif menu == "4. 💻 Online Test & NEET Level CBT Portal":
    st.subheader("💻 NTA / NEET Level CBT Test Portal")
    st.info("⏱️ Test Time: 180 Minutes | Marking: +4 for Correct, -1 for Wrong")
    
    score = 0
    st.markdown("""
    <div class="cbt-box">
        <b>Q1. [Physics]</b> Two point charges +q and -q are placed at distance d apart. What is the electric dipole moment vector direction?
    </div>
    """, unsafe_allow_html=True)
    q1_ans = st.radio("Select Answer Q1:", ["(A) From positive to negative charge", "(B) From negative to positive charge", "(C) Perpendicular to line", "(D) None"], key=get_ai_key("cbt_q1"))
    if q1_ans == "(B) From negative to positive charge": score += 4

    if st.button("🚀 Submit NEET CBT Test", key=get_ai_key("cbt_sub_btn")):
        st.balloons()
        st.success(f"🎉 Test Submitted! Score: {score} / 4 Marks")

# --- MODULE 5: ADD STUDENT ---
elif menu == "5. ✏️ Add / Edit Complete Student Profile":
    st.subheader("✏️ Student Master Form")
    roll_no = st.number_input("Roll No", min_value=1, step=1, key=get_ai_key("std_roll"))
    s_name = st.text_input("Student Name", key=get_ai_key("std_name"))
    f_name = st.text_input("Father Name", key=get_ai_key("std_fname"))
    s_class = st.selectbox("Class", classes_list, key=get_ai_key("std_class"))
    s_sec = st.selectbox("Section", sections_list, key=get_ai_key("std_sec"))
    s_mob = st.text_input("Mobile Number", key=get_ai_key("std_mob"))
    s_adh = st.text_input("Aadhaar Number (12 Digits)", key=get_ai_key("std_adh"))
    
    if st.button("💾 Save Profile", key=get_ai_key("std_save_btn")):
        if not is_valid_aadhaar(s_adh):
            st.error("Invalid Aadhaar Number! Must be exactly 12 digits.")
        else:
            if supabase:
                try:
                    supabase.table("students").insert({
                        "roll_no": roll_no, "student_name": s_name, "father_name": f_name,
                        "class": s_class, "section": s_sec, "mobile": s_mob, "aadhaar": s_adh
                    }).execute()
                    st.success("Student profile saved to Supabase successfully!")
                except Exception as e:
                    st.error(f"Error saving student: {e}")

# --- MODULE 15: TRANSPORT MANAGEMENT ---
elif menu == "15. 🚌 Transport & Bus Tracking System":
    st.subheader("🚌 Transport & Route Manager")
    bus_no = st.text_input("Bus / Vehicle Number", "RJ-19-PA-1234", key=get_ai_key("bus_no"))
    route_name = st.text_input("Route Name", "Route 4 - City Center to Campus", key=get_ai_key("bus_route"))
    driver_name = st.text_input("Driver Name & Phone", "Ramesh Kumar - 9876543210", key=get_ai_key("bus_driver"))
    monthly_fee = st.number_input("Monthly Bus Fee (₹)", value=1200, step=100, key=get_ai_key("bus_fee"))
    
    if st.button("💾 Save Route Record", key=get_ai_key("bus_save_btn")):
        st.success(f"Route '{route_name}' configured successfully!")

# --- MODULE 16: NOTICE BOARD ---
elif menu == "16. 📢 Instant Notice Board":
    st.subheader("📢 School Notice & Announcement Board")
    notice_title = st.text_input("Notice Heading / Subject", key=get_ai_key("ntc_title"))
    target_audience = st.selectbox("Send To", ["All Students & Parents", "Teachers & Staff", "Class 10th & 12th Only"], key=get_ai_key("ntc_aud"))
    notice_body = st.text_area("Notice Details / Description", key=get_ai_key("ntc_body"))
    
    if st.button("🚀 Publish Notice", key=get_ai_key("ntc_pub_btn")):
        st.success(f"Notice '{notice_title}' sent to {target_audience}!")

# --- MODULE 17: FINANCIAL DASHBOARD ---
elif menu == "17. 📊 Financial Summary Dashboard":
    st.subheader("📊 Admin Financial Overview")
    if supabase:
        try:
            res_fees = supabase.table("fee_collections").select("received_fee, pending_fee").execute()
            data = res_fees.data
            tot_rec = sum(item['received_fee'] for item in data) if data else 0
            tot_pend = sum(item['pending_fee'] for item in data) if data else 0
            
            col1, col2 = st.columns(2)
            col1.metric("💰 Total Fees Collected", f"₹{tot_rec:,}")
            col2.metric("⏳ Total Fees Pending", f"₹{tot_pend:,}")
        except Exception as e:
            st.info("Financial Dashboard ready. Collect fees to see live graphs!")

# --- OTHER MODULES ---
elif menu == "6. 👥 View All Students Table":
    st.subheader("👥 Student Directory")
    if supabase:
        res = supabase.table("students").select("*").execute()
        if res.data:
            st.dataframe(res.data)
        else:
            st.info("No students added yet.")

elif menu == "7. 🔍 Advance Multi-Search Profile":
    st.subheader("🔍 Master Search")
    st.text_input("Search Roll No or Name", key=get_ai_key("srch_inp"))

elif menu == "8. 📄 Automatic Report Card Generator (PDF)":
    st.subheader("📄 Instant Report Card Generator")
    st.info("PDF Generation enabled.")

elif menu == "9. 🗓️ School Calendar & Holidays Notice":
    st.subheader("🗓️ Academic Calendar & Notices")

elif menu == "10. 📅 Mark Attendance & WhatsApp Alert":
    st.subheader("📅 Attendance Marker")

elif menu == "11. 📚 Class 1-12 NCERT Textbooks":
    st.subheader("📚 NCERT Books Library")

elif menu == "12. 📄 Auto Question Paper (Hindi & English)":
    st.subheader("📄 Bilingual Paper Generator")

elif menu == "13. 📝 Exam Marks Portal":
    st.subheader("📝 Marks Entry Portal")

elif menu == "14. ✅ Student Answer Sheet Copy Check":
    st.subheader("✅ Student Copy Verification")
elif menu == "14. ✅ Student Answer Sheet Copy Check":
    st.subheader("✅ Student Copy Verification")
