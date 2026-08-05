import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Class 8 Management Dashboard", 
    layout="wide", 
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; padding: 16px; border-radius: 12px;
        text-align: center; margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); 
        color: white; border: none; border-radius: 8px; height: 3.2em; font-weight: bold;
    }
    div[data-testid="stDataEditor"] {
        border-radius: 10px; background: white; overflow-x: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- SQLITE DATABASE SETUP ---
DB_FILE = "school_dashboard.db"

def create_default_students():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS students')
    c.execute('''
        CREATE TABLE students (
            Roll INTEGER PRIMARY KEY,
            Name TEXT,
            Father_Name TEXT,
            Parent_Mobile TEXT,
            Attendance TEXT,
            sub1 INTEGER, sub2 INTEGER, sub3 INTEGER,
            sub4 INTEGER, sub5 INTEGER, sub6 INTEGER,
            Total_Fee INTEGER, Fee_Paid INTEGER
        )
    ''')
    default_data = [
        (i, f"Student {i}", f"Father {i}", f"9198765432{i:02d}", "Present", 75, 80, 70, 65, 85, 78, 15000, 10000)
        for i in range(1, 11)
    ]
    c.executemany("INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", default_data)
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            Roll INTEGER PRIMARY KEY,
            Name TEXT,
            Father_Name TEXT,
            Parent_Mobile TEXT,
            Attendance TEXT,
            sub1 INTEGER, sub2 INTEGER, sub3 INTEGER,
            sub4 INTEGER, sub5 INTEGER, sub6 INTEGER,
            Total_Fee INTEGER, Fee_Paid INTEGER
        )
    ''')
    c.execute("SELECT COUNT(*) FROM students")
    count = c.fetchone()[0]
    conn.close()
    if count == 0:
        create_default_students()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def save_data(df):
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("students", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

init_db()

# --- LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="app-header"><h2>🎓 Class 8 Teacher Portal</h2></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("🔑 Login"):
            if username == "admin" and password == "12345":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Galat Details! Default ID/Pass: admin / 12345")
    st.stop()

# Initialize Configs
if 'subjects_config' not in st.session_state:
    st.session_state.subjects_config = [
        {"code": "sub1", "name": "Maths", "max_marks": 100},
        {"code": "sub2", "name": "Science", "max_marks": 100},
        {"code": "sub3", "name": "English", "max_marks": 100},
        {"code": "sub4", "name": "SST", "max_marks": 100},
        {"code": "sub5", "name": "Hindi", "max_marks": 100},
        {"code": "sub6", "name": "Sanskrit", "max_marks": 100},
    ]

sub_codes = [s["code"] for s in st.session_state.subjects_config]
sub_names = [s["name"] for s in st.session_state.subjects_config]
total_max_marks = sum([s["max_marks"] for s in st.session_state.subjects_config])

# --- PDF GENERATOR FUNCTION ---
def generate_pdf_result(student_row, subjects):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>CLASS 8 ACADEMIC REPORT CARD</b>", styles['Title']))
    elements.append(Spacer(1, 15))

    details_data = [
        [f"Roll No: {student_row['Roll']}", f"Student Name: {student_row['Name']}"],
        [f"Father's Name: {student_row['Father_Name']}", f"Mobile: {student_row['Parent_Mobile']}"]
    ]
    t1 = Table(details_data, colWidths=[200, 250])
    t1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.lightgrey), ('GRID', (0,0), (-1,-1), 1, colors.white)]))
    elements.append(t1)
    elements.append(Spacer(1, 20))

    marks_table_data = [["Subject", "Max Marks", "Marks Obtained"]]
    total_ob = 0
    for s in subjects:
        score = student_row.get(s["code"], 0)
        total_ob += score
        marks_table_data.append([s["name"], str(s["max_marks"]), str(score)])

    marks_table_data.append(["TOTAL", str(total_max_marks), str(total_ob)])
    
    perc = round((total_ob / total_max_marks) * 100, 2)
    marks_table_data.append(["PERCENTAGE", "-", f"{perc}%"])

    t2 = Table(marks_table_data, colWidths=[200, 125, 125])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.navy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,-2), (-1,-1), colors.lightgrey)
    ]))
    elements.append(t2)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- SIDEBAR MENU ---
st.sidebar.markdown("### 🏫 Navigation Options")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.radio(
    "📌 Select Module:", 
    [
        "📊 Results & Data Editor", 
        "📄 Download Result PDF",
        "💻 Online Classes",
        "⚙️ Subject Settings",
        "💳 Fee Management", 
        "📚 Homework Tracker", 
        "📈 Class Analytics", 
        "📅 Class Timetable",
        "📋 Daily Attendance", 
        "📲 WhatsApp Alerts"
    ]
)

# --- MODULE 1: RESULTS & DATA EDITOR ---
if menu == "📊 Results & Data Editor":
    st.markdown('<div class="app-header"><h3>📊 Results & Master Database</h3></div>', unsafe_allow_html=True)

    df = load_data()
    
    for code in sub_codes:
        if code not in df.columns: df[code] = 0
        df[code] = pd.to_numeric(df[code], errors='coerce').fillna(0)

    df['Total_Obtained'] = df[sub_codes].sum(axis=1)
    df['Percentage (%)'] = ((df['Total_Obtained'] / total_max_marks) * 100).round(2)
    df['Rank'] = df['Total_Obtained'].rank(ascending=False, method='min').fillna(0).astype(int)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Students", len(df))
    m2.metric("Max Marks", total_max_marks)
    m3.metric("Class Avg %", f"{df['Percentage (%)'].mean():.2f}%" if len(df) > 0 else "0%")

    st.subheader("✏️ Editable Student Register")
    
    c_btn1, c_btn2 = st.columns([2, 1])
    with c_btn2:
        if st.button("🔄 Reset / Restore Default 10 Students"):
            create_default_students()
            if "master_student_editor_v3" in st.session_state:
                del st.session_state["master_student_editor_v3"]
            st.success("10 Default Students Add ho gaye hain!")
            st.rerun()

    rename_dict = {code: f"{s['name']} ({s['max_marks']})" for code, s in zip(sub_codes, st.session_state.subjects_config)}
    cols_to_show = ["Roll", "Name", "Father_Name", "Parent_Mobile"] + sub_codes
    editable_df = df[cols_to_show].rename(columns=rename_dict)

    edited_data = st.data_editor(
        editable_df, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True,
        key="master_student_editor_v3"
    )

    if st.button("💾 SAVE ALL CHANGES TO DATABASE"):
        inv_rename_dict = {v: k for k, v in rename_dict.items()}
        updated_df = edited_data.rename(columns=inv_rename_dict)
        
        for col in ["Attendance", "Total_Fee", "Fee_Paid"]:
            if col not in updated_df.columns:
                updated_df[col] = df[col] if col in df.columns else 0

        save_data(updated_df)
        if "master_student_editor_v3" in st.session_state:
            del st.session_state["master_student_editor_v3"]
            
        st.success("✅ Database updated!")
        st.rerun()

# --- MODULE 2: DOWNLOAD PDF RESULT CARD ---
elif menu == "📄 Download Result PDF":
    st.markdown('<div class="app-header"><h3>📄 Generate Student Result PDF</h3></div>', unsafe_allow_html=True)
    df = load_data()
    
    if len(df) > 0:
        selected_roll = st.selectbox("Select Student Roll Number / Name:", df["Roll"].astype(str) + " - " + df["Name"])
        roll_num = int(selected_roll.split(" - ")[0])
        student_data = df[df["Roll"] == roll_num].iloc[0]

        st.info(f"**Student:** {student_data['Name']} | **Father:** {student_data['Father_Name']} | **Roll No:** {student_data['Roll']}")

        pdf_file = generate_pdf_result(student_data, st.session_state.subjects_config)
        
        st.download_button(
            label="📥 Download Official Report Card PDF",
            data=pdf_file,
            file_name=f"Result_Roll_{student_data['Roll']}_{student_data['Name']}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Pehle Data Editor me students add karein!")

# --- MODULE 3: ONLINE CLASSES ---
elif menu == "💻 Online Classes":
    st.markdown('<div class="app-header"><h3>💻 Online Live Classes & Links</h3></div>', unsafe_allow_html=True)
    if 'online_classes' not in st.session_state: st.session_state.online_classes = []

    with st.form("class_form"):
        subject = st.selectbox("Subject", sub_names)
        link = st.text_input("Google Meet / Zoom Link", value="https://meet.google.com/")
        time_slot = st.text_input("Timing", value="10:00 AM - 10:45 AM")
        if st.form_submit_button("📢 Publish Online Class") and link:
            st.session_state.online_classes.append({"Subject": subject, "Link": link, "Time": time_slot})
            st.success("Online Class Scheduled!")

    st.subheader("📌 Scheduled Classes")
    for cls in st.session_state.online_classes:
        st.success(f"**Subject:** {cls['Subject']} | ⏰ **Time:** {cls['Time']}\n\n🔗 [Click to Join Class]({cls['Link']})")

# --- MODULE 4: SUBJECT SETTINGS ---
elif menu == "⚙️ Subject Settings":
    st.markdown('<div class="app-header"><h3>⚙️ Subject Configuration</h3></div>', unsafe_allow_html=True)
    with st.form("settings_form"):
        updated_configs = []
        for idx, sub in enumerate(st.session_state.subjects_config):
            c1, c2 = st.columns(2)
            n_name = c1.text_input(f"Subject {idx+1}", value=sub["name"], key=f"sname_{idx}")
            n_max = c2.number_input(f"Max Marks", value=int(sub["max_marks"]), min_value=10, key=f"smax_{idx}")
            updated_configs.append({"code": sub["code"], "name": n_name, "max_marks": n_max})

        if st.form_submit_button("💾 Save Settings"):
            st.session_state.subjects_config = updated_configs
            st.success("Subjects Updated!")
            st.rerun()

# --- MODULE 5: FEE MANAGEMENT ---
elif menu == "💳 Fee Management":
    st.markdown('<div class="app-header"><h3>💳 Fee Ledger</h3></div>', unsafe_allow_html=True)
    df = load_data()
    df['Pending'] = df['Total_Fee'] - df['Fee_Paid']

    edited_fee = st.data_editor(
        df[["Roll", "Name", "Father_Name", "Total_Fee", "Fee_Paid", "Pending"]],
        disabled=["Pending"],
        use_container_width=True,
        hide_index=True,
        key="fee_editor"
    )
    if st.button("💾 Save Fee Ledger"):
        df["Total_Fee"] = edited_fee["Total_Fee"]
        df["Fee_Paid"] = edited_fee["Fee_Paid"]
        save_data(df)
        if "fee_editor" in st.session_state: del st.session_state["fee_editor"]
        st.success("Fee Saved!")
        st.rerun()

# --- MODULE 6: HOMEWORK ---
elif menu == "📚 Homework Tracker":
    st.markdown('<div class="app-header"><h3>📚 Homework Tracker</h3></div>', unsafe_allow_html=True)
    if 'homework' not in st.session_state: st.session_state.homework = []
    
    with st.form("hw_form"):
        subject = st.selectbox("Subject", sub_names)
        details = st.text_area("Homework Details")
        due = st.date_input("Due Date")
        if st.form_submit_button("📢 Publish") and details:
            st.session_state.homework.append({"Subject": subject, "Details": details, "Due": str(due)})
            st.success("Homework Added!")

    for hw in st.session_state.homework:
        st.info(f"📌 **{hw['Subject']}** (Due: {hw['Due']})\n\n{hw['Details']}")
        enc = urllib.parse.quote(f"Homework - {hw['Subject']}: {hw['Details']}")
        st.markdown(f"[📲 Share on WhatsApp](https://api.whatsapp.com/send?text={enc})")

# --- MODULE 7: ANALYTICS ---
elif menu == "📈 Class Analytics":
    st.markdown('<div class="app-header"><h3>📈 Performance Analytics</h3></div>', unsafe_allow_html=True)
    df = load_data()
    if len(df) > 0:
        chart_data = {s["name"]: df[s["code"]].mean() for s in st.session_state.subjects_config if s["code"] in df.columns}
        st.bar_chart(pd.Series(chart_data))

# --- MODULE 8: TIMETABLE ---
elif menu == "📅 Class Timetable":
    st.markdown('<div class="app-header"><h3>📅 Weekly Schedule</h3></div>', unsafe_allow_html=True)
    tb = {
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "9:00 AM": [sub_names[0], sub_names[1], sub_names[2], sub_names[0], sub_names[1], sub_names[4]],
        "10:00 AM": [sub_names[1], sub_names[0], sub_names[4], sub_names[1], sub_names[0], sub_names[3]],
    }
    st.table(pd.DataFrame(tb))

# --- MODULE 9: DAILY ATTENDANCE ---
elif menu == "📋 Daily Attendance":
    st.markdown('<div class="app-header"><h3>📋 Attendance Register</h3></div>', unsafe_allow_html=True)
    df = load_data()
    
    att_df = st.data_editor(
        df[["Roll", "Name", "Father_Name", "Attendance"]],
        column_config={"Attendance": st.column_config.SelectboxColumn("Status", options=["Present", "Absent", "Leave"])},
        use_container_width=True,
        hide_index=True,
        key="att_editor"
    )
    if st.button("💾 Save Attendance"):
        df["Attendance"] = att_df["Attendance"]
        save_data(df)
        if "att_editor" in st.session_state: del st.session_state["att_editor"]
        st.success("Attendance Updated!")
        st.rerun()

# --- MODULE 10: WHATSAPP ALERTS ---
elif menu == "📲 WhatsApp Alerts":
    st.markdown('<div class="app-header"><h3>📲 WhatsApp Absent Alerts</h3></div>', unsafe_allow_html=True)
    df = load_data()
    absents = df[df["Attendance"] == "Absent"]
    if len(absents) == 0:
        st.success("Aaj sabhi students Present hain!")
    else:
        for _, s in absents.iterrows():
            msg = urllib.parse.quote(f"Namaste, Aapka baccha {s['Name']} (Father: {s['Father_Name']}) aaj school me ABSENT hai.")
            st.markdown(f"👤 **{s['Name']}** (Father: {s['Father_Name']}) -> [📲 Send Alert](https://wa.me/{s['Parent_Mobile']}?text={msg})")
