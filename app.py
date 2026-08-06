import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# 1. Streamlit Page Configuration & Custom CSS
st.set_page_config(page_title="School Management Dashboard", layout="wide")

st.markdown("""
    <style>
    html { scroll-behavior: smooth; }
    .stTable, .stDataFrame { border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0; }
    div[data-testid="stMetricValue"] { font-size: 20px; }
    .stButton button { border-radius: 6px; transition: all 0.3s ease; }
    .stButton button:hover { transform: translateY(-2px); }
    .app-header { background-color: #1f77b4; padding: 10px; border-radius: 5px; color: white; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. Supabase Connection
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Helper Function: Safe Float to Int Conversion
def safe_int(val):
    try:
        return int(float(str(val)))
    except:
        return 0

# 3. Data Load & Save Functions
def load_data():
    try:
        response = supabase.table('class_8_students').select('*').order('roll_no').execute()
        df = pd.DataFrame(response.data)
        
        # Standardize Columns mapping if needed
        col_map = {
            'roll_no': 'Roll',
            'name': 'Name',
            'father_name': 'Father_Name',
            'parent_mobile': 'Parent_Mobile',
            'maths': 'Maths',
            'science': 'Science',
            'english': 'English',
            'total_fee': 'Total_Fee',
            'fee_paid': 'Fee_Paid',
            'attendance': 'Attendance',
            'attendance_%': 'Attendance_%',
            'conduct': 'Conduct'
        }
        df = df.rename(columns=col_map)
        
        # Ensure default required columns exist
        defaults = {
            'Roll': 0, 'Name': '', 'Father_Name': '', 'Parent_Mobile': '',
            'Maths': 0, 'Science': 0, 'English': 0, 'Total_Fee': 0, 
            'Fee_Paid': 0, 'Pending': 0, 'Attendance': 'Present', 
            'Attendance_%': 100, 'Conduct': 'Good'
        }
        for col, default_val in defaults.items():
            if col not in df.columns:
                df[col] = default_val

        # Fix types
        df['Roll'] = df['Roll'].apply(safe_int)
        df['Total_Fee'] = pd.to_numeric(df['Total_Fee'], errors='coerce').fillna(0)
        df['Fee_Paid'] = pd.to_numeric(df['Fee_Paid'], errors='coerce').fillna(0)
        df['Pending'] = df['Total_Fee'] - df['Fee_Paid']
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

def save_data(df):
    try:
        data_to_save = []
        for _, row in df.iterrows():
            item = {
                "roll_no": safe_int(row.get('Roll', 0)),
                "name": str(row.get('Name', '')),
                "father_name": str(row.get('Father_Name', '')),
                "parent_mobile": str(row.get('Parent_Mobile', '')),
                "maths": safe_int(row.get('Maths', 0)),
                "science": safe_int(row.get('Science', 0)),
                "english": safe_int(row.get('English', 0)),
                "total_fee": float(row.get('Total_Fee', 0)),
                "fee_paid": float(row.get('Fee_Paid', 0)),
                "attendance": str(row.get('Attendance', 'Present')),
                "attendance_%": safe_int(row.get('Attendance_%', 100)),
                "conduct": str(row.get('Conduct', 'Good'))
            }
            data_to_save.append(item)
        supabase.table('class_8_students').upsert(data_to_save).execute()
    except Exception as e:
        st.error(f"Data Save Error: {e}")

# Subject Configurations
if 'subjects_config' not in st.session_state:
    st.session_state.subjects_config = [
        {"name": "Maths", "code": "Maths"},
        {"name": "Science", "code": "Science"},
        {"name": "English", "code": "English"},
        {"name": "Hindi", "code": "Hindi"},
        {"name": "Social Science", "code": "Social_Science"}
    ]

sub_names = [s["name"] for s in st.session_state.subjects_config]

# Navigation Sidebar
st.sidebar.title("🏫 School System")
menu = st.sidebar.radio(
    "Select Module:",
    [
        "📊 Results & Data Editor",
        "📄 Download Result PDF",
        "👤 Student Profiles",
        "⚙️ Subject Settings",
        "💳 Fee Management",
        "📚 Homework Tracker",
        "📈 Class Analytics",
        "📅 Class Timetable",
        "📋 Daily Attendance",
        "📲 WhatsApp Alerts"
    ]
)

df = load_data()

# --- MODULE 1: RESULTS & DATA EDITOR ---
if menu == "📊 Results & Data Editor":
    st.markdown('<div class="app-header"><h3>📊 Results & Data Register</h3></div>', unsafe_allow_html=True)
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total Students", len(df))
        col2.metric("Max Marks Per Subject", 100)
        
        edited_df = st.data_editor(df, width="stretch", hide_index=True, key="main_editor")
        if st.button("💾 Save Changes"):
            save_data(edited_df)
            st.success("Data successfully saved!")
            st.rerun()

# --- MODULE 2: DOWNLOAD RESULT PDF ---
elif menu == "📄 Download Result PDF":
    st.markdown('<div class="app-header"><h3>📄 Marks Card Generator</h3></div>', unsafe_allow_html=True)
    if not df.empty:
        roll_options = [f"{safe_int(r)} - {n}" for r, n in zip(df['Roll'], df['Name'])]
        selected_roll_str = st.selectbox("Select Student:", roll_options)
        
        # SAFE STRING SPLIT & FLOAT TO INT CONVERSION
        roll_num = safe_int(selected_roll_str.split(" - ")[0])
        student = df[df['Roll'] == roll_num].iloc[0]
        
        st.write(f"**Name:** {student['Name']} | **Roll No:** {student['Roll']}")
        st.write(f"**Maths:** {student.get('Maths', 0)} | **Science:** {student.get('Science', 0)} | **English:** {student.get('English', 0)}")
        
        report_text = f"STUDENT REPORT CARD\nName: {student['Name']}\nRoll: {student['Roll']}\nMaths: {student.get('Maths',0)}\nScience: {student.get('Science',0)}\nEnglish: {student.get('English',0)}"
        st.download_button("📥 Download Report (TXT)", data=report_text, file_name=f"Report_{student['Roll']}.txt")

# --- MODULE 3: STUDENT PROFILES ---
elif menu == "👤 Student Profiles":
    st.markdown('<div class="app-header"><h3>👤 Student Detail Cards</h3></div>', unsafe_allow_html=True)
    if not df.empty:
        if 'student_idx' not in st.session_state: st.session_state.student_idx = 0
        
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ Previous", width="stretch"):
                if st.session_state.student_idx > 0:
                    st.session_state.student_idx -= 1
                    st.rerun()
        with col_next:
            if st.button("Next ➔", width="stretch"):
                if st.session_state.student_idx < len(df) - 1:
                    st.session_state.student_idx += 1
                    st.rerun()
                    
        st.info(f"Student {st.session_state.student_idx + 1} of {len(df)}")
        student = df.iloc[st.session_state.student_idx]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Roll & Name", f"#{student['Roll']} {student['Name']}")
        c2.metric("Father Name", str(student.get('Father_Name', 'N/A')))
        c3.metric("Parent Mobile", str(student.get('Parent_Mobile', 'N/A')))

# --- MODULE 4: SUBJECT SETTINGS ---
elif menu == "⚙️ Subject Settings":
    st.markdown('<div class="app-header"><h3>⚙️ Subject Configuration</h3></div>', unsafe_allow_html=True)
    st.write("Configured Subjects:")
    for sub in st.session_state.subjects_config:
        st.write(f"- {sub['name']} (`{sub['code']}`)")

# --- MODULE 5: FEE MANAGEMENT ---
elif menu == "💳 Fee Management":
    st.markdown('<div class="app-header"><h3>💳 Fee Ledger</h3></div>', unsafe_allow_html=True)
    if not df.empty:
        edited_fee = st.data_editor(
            df[["Roll", "Name", "Father_Name", "Total_Fee", "Fee_Paid", "Pending"]],
            disabled=["Pending"],
            width="stretch",
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

# --- MODULE 6: HOMEWORK TRACKER ---
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
    if len(df) > 0:
        chart_data = {s["name"]: pd.to_numeric(df[s["code"]], errors='coerce').mean() for s in st.session_state.subjects_config if s["code"] in df.columns}
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
    if not df.empty:
        att_df = st.data_editor(
            df[["Roll", "Name", "Father_Name", "Attendance"]],
            column_config={"Attendance": st.column_config.SelectboxColumn("Status", options=["Present", "Absent", "Leave"])},
            width="stretch",
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
    if not df.empty:
        absents = df[df["Attendance"] == "Absent"]
        if len(absents) == 0:
            st.success("Aaj sabhi students Present hain!")
        else:
            for _, s in absents.iterrows():
                msg = urllib.parse.quote(f"Namaste, Aapka baccha {s['Name']} (Father: {s['Father_Name']}) aaj school me ABSENT hai.")
                st.markdown(f"👤 **{s['Name']}** (Father: {s['Father_Name']}) -> [📲 Send Alert](https://wa.me/{s['Parent_Mobile']}?text={msg})")
