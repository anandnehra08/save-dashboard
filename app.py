import textwrap
import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
from supabase import create_client, Client
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Class 8 Management Dashboard",
    page_icon="🏫",
    layout="wide"
)

# --- SUPABASE CONNECTION SETUP ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"❌ Supabase Connection Failed: {e}")
    st.stop()

# --- CACHE REFRESH UTILITY ---
def refresh_cache():
    st.cache_data.clear()

# --- FETCH DATA FROM SUPABASE ---
@st.cache_data(ttl=60)
def load_data():
    try:
        response = supabase.table("class_8_students").select("*").execute()
        data = response.data
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Ensure numerical types
        num_cols = ["roll_no", "english", "hindi", "science", "sst", "maths", "sanskrit", "max_marks", "total_fee", "fee_paid", "attendance_%"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Dynamic Calculations
        df["max_marks"] = df["max_marks"].replace(0, 100)
        df["Total Marks"] = df["english"] + df["hindi"] + df["science"] + df["sst"] + df["maths"] + df["sanskrit"]
        df["Total Max Marks"] = df["max_marks"] * 6
        df["Percentage (%)"] = ((df["Total Marks"] / df["Total Max Marks"]) * 100).round(2)
        df["Pending Fee"] = df["total_fee"] - df["fee_paid"]

        # Rank Calculation
        df["Rank"] = df["Total Marks"].rank(ascending=False, method="min").astype(int)
        
        return df
    except Exception as e:
        st.error(f"Error fetching data from Supabase: {e}")
        return pd.DataFrame()

# Load Data
df = load_data()

# --- BACKEND FUNCTION: SAVE / UPDATE STUDENT DATA ---
# --- BACKEND FUNCTION: SAVE / UPDATE STUDENT DATA ---
def save_student_data(
    rno, name, fname, mobile, att_status, att_pct, cond, 
    eng, hin, sci, sst, math, sans, max_m, tfee, fpaid, date_val,
    gender="Male", category="General", blood="Unknown", aadhaar="", address=""
):
    try:
        eng = int(eng) if eng else 0
        hin = int(hin) if hin else 0
        sci = int(sci) if sci else 0
        sst = int(sst) if sst else 0
        math = int(math) if math else 0
        sans = int(sans) if sans else 0
        max_m = max(10, int(max_m))

        tot_m = eng + hin + sci + sst + math + sans
        tot_max_m = max_m * 6
        pct = round((tot_m / tot_max_m) * 100, 2)

        payload = {
            "roll_no": int(rno),
            "name": str(name).strip(),
            "father_name": str(fname).strip(),
            "parent_mobile": str(mobile).strip(),
            "attendance": att_status,
            "attendance_%": int(att_pct),
            "conduct": cond,
            "english": eng,
            "hindi": hin,
            "science": sci,
            "sst": sst,
            "maths": math,
            "sanskrit": sans,
            "max_marks": max_m,
            "total_fee": float(tfee),
            "fee_paid": float(fpaid),
            "date": str(date_val),
            # Optional extra fields
            "gender": str(gender),
            "category": str(category),
            "blood_group": str(blood),
            "aadhaar_no": str(aadhaar),
            "address": str(address)
        }

        # Fix: Specified 'on_conflict="roll_no"' so existing Roll Numbers get UPDATED
        supabase.table("class_8_students").upsert(payload, on_conflict="roll_no").execute()
        refresh_cache()
        return True
    except Exception as e:
        st.error(f"❌ Error saving student record: {e}")
        return False
# --- SMART REMARKS & ALERTS HELPERS ---
# --- AI DATA AUDIT & AUTO-FIX HELPER ---
def audit_and_fix_student_data(df):
    """Data mein galat values dhoondhta hai aur unhe automatic fix karta hai"""
    fixed_df = df.copy()
    errors_found = []

    for idx, row in fixed_df.iterrows():
        roll = row.get("roll_no", "N/A")
        name = row.get("name", "Unknown")
        max_m = float(row.get("max_marks", 100)) if row.get("max_marks") else 100.0

        # Check & Fix Marks (0 se kam na ho, max_marks se zyada na ho)
        for sub in ["english", "hindi", "science", "sst", "maths", "sanskrit"]:
            val = float(row.get(sub, 0)) if row.get(sub) is not None else 0.0
            if val < 0:
                errors_found.append(f"Roll {roll} ({name}): {sub.capitalize()} marks were negative ({val}). Set to 0.")
                fixed_df.at[idx, sub] = 0
            elif val > max_m:
                errors_found.append(f"Roll {roll} ({name}): {sub.capitalize()} marks ({val}) exceeded Max Marks ({max_m}). Set to {max_m}.")
                fixed_df.at[idx, sub] = max_m

        # Recalculate Total & Percentage
        tot = sum([float(fixed_df.at[idx, s]) for s in ["english", "hindi", "science", "sst", "maths", "sanskrit"]])
        tot_max = max_m * 6
        pct = round((tot / tot_max) * 100, 2) if tot_max > 0 else 0.0

        if fixed_df.at[idx, "Total Marks"] != tot:
            fixed_df.at[idx, "Total Marks"] = tot
        if fixed_df.at[idx, "Percentage (%)"] != pct:
            errors_found.append(f"Roll {roll} ({name}): Percentage recalculated from {fixed_df.at[idx, 'Percentage (%)']}% to {pct}%.")
            fixed_df.at[idx, "Percentage (%)"] = pct

        # Check Mobile Number Format
        mob = str(row.get("parent_mobile", "")).strip()
        mob_clean = "".join(filter(str.isdigit, mob))
        if len(mob_clean) != 10:
            errors_found.append(f"Roll {roll} ({name}): Parent mobile ({mob}) is not 10 digits.")

    return fixed_df, errors_found
def generate_student_remark(pct, min_subject, eng, math, sci):
    """Marks ke hisab se automatic performance remark generate karta hai"""
    if pct >= 85:
        remark = "🌟 Outstanding academic performance! Keep up the excellent work."
    elif pct >= 70:
        remark = "👍 Very good performance. With a little more focus, top grade is easily achievable."
    elif pct >= 50:
        remark = "📈 Satisfactory progress. Needs consistent practice in weak subjects."
    else:
        remark = "⚠️ Needs immediate academic attention and regular homework tracking."

    # Subject-specific feedback
    weak_subs = []
    if math < 40: weak_subs.append("Maths")
    if eng < 40: weak_subs.append("English")
    if sci < 40: weak_subs.append("Science")

    if weak_subs:
        remark += f" Special focus required in: {', '.join(weak_subs)}."
        
    return remark
# --- PDF GENERATION HELPERS ---
def generate_student_pdf(student):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title Style
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=15)
    story.append(Paragraph("Class 8 Report Card", title_style))
    story.append(Spacer(1, 10))

    normal_style = styles['Normal']

    # Student Info Table
    info_data = [
        [
            Paragraph(f"<b>Name:</b> {student.get('name', 'N/A')}", normal_style),
            Paragraph(f"<b>Roll No:</b> {student.get('roll_no', 'N/A')}", normal_style)
        ],
        [
            Paragraph(f"<b>Father's Name:</b> {student.get('father_name', 'N/A')}", normal_style),
            Paragraph(f"<b>Date:</b> {student.get('date', 'N/A')}", normal_style)
        ],
        [
            Paragraph(f"<b>Attendance:</b> {student.get('attendance_%', 0)}%", normal_style),
            Paragraph(f"<b>Conduct:</b> {student.get('conduct', 'N/A')}", normal_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[240, 240])
    t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # Marks Table
    max_m = int(student.get('max_marks', 100))
    marks_data = [
        ["Subject", "Marks Obtained", "Maximum Marks"],
        ["English", str(student.get('english', 0)), str(max_m)],
        ["Hindi", str(student.get('hindi', 0)), str(max_m)],
        ["Science", str(student.get('science', 0)), str(max_m)],
        ["Social Science", str(student.get('sst', 0)), str(max_m)],
        ["Maths", str(student.get('maths', 0)), str(max_m)],
        ["Sanskrit", str(student.get('sanskrit', 0)), str(max_m)],
        ["Total Score", str(student.get('Total Marks', 0)), str(max_m * 6)],
        ["Percentage", f"{student.get('Percentage (%)', 0)}%", "100%"]
    ]
    t_marks = Table(marks_data, colWidths=[180, 150, 150])
    t_marks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BACKGROUND', (0,-2), (-1,-1), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,-2), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_marks)
    story.append(Spacer(1, 15))

    # Performance Remark Box in PDF
    pct_val = student.get('Percentage (%)', 0)
    remark_txt = generate_student_remark(
        pct_val,
        min(student.get('english',0), student.get('maths',0), student.get('science',0)),
        student.get('english',0), student.get('maths',0), student.get('science',0)
    )
    
    remark_style = ParagraphStyle('RemarkStyle', parent=normal_style, fontSize=10, leading=14)
    story.append(Paragraph(f"<b>Teacher Remarks:</b> {remark_txt}", remark_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
    # Marks Table
    max_m = int(student.get('max_marks', 100))
    marks_data = [
        ["Subject", "Marks Obtained", "Maximum Marks"],
        ["English", str(student.get('english', 0)), str(max_m)],
        ["Hindi", str(student.get('hindi', 0)), str(max_m)],
        ["Science", str(student.get('science', 0)), str(max_m)],
        ["Social Science", str(student.get('sst', 0)), str(max_m)],
        ["Maths", str(student.get('maths', 0)), str(max_m)],
        ["Sanskrit", str(student.get('sanskrit', 0)), str(max_m)],
        ["Total Score", str(student.get('Total Marks', 0)), str(max_m * 6)],
        ["Percentage", f"{student.get('Percentage (%)', 0)}%", "100%"]
    ]
    t_marks = Table(marks_data, colWidths=[180, 150, 150])
    t_marks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BACKGROUND', (0,-2), (-1,-1), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,-2), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_marks)
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_class_pdf(df_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=15)
    story.append(Paragraph("Class 8 Full Class Academic Result Sheet", title_style))
    story.append(Spacer(1, 10))

    headers = ["Rank", "Roll", "Name", "Eng", "Hin", "Sci", "SST", "Math", "Sans", "Total", "%"]
    table_data = [headers]

    sorted_df = df_data.sort_values(by="Rank") if "Rank" in df_data.columns else df_data
    for _, row in sorted_df.iterrows():
        table_data.append([
            str(row.get('Rank', '')),
            str(int(row.get('roll_no', 0))),
            str(row.get('name', ''))[:12],
            str(int(row.get('english', 0))),
            str(int(row.get('hindi', 0))),
            str(int(row.get('science', 0))),
            str(int(row.get('sst', 0))),
            str(int(row.get('maths', 0))),
            str(int(row.get('sanskrit', 0))),
            str(int(row.get('Total Marks', 0))),
            f"{row.get('Percentage (%)', 0)}%"
        ])

    t_class = Table(table_data, colWidths=[35, 35, 80, 35, 35, 35, 35, 35, 35, 45, 45])
    t_class.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    story.append(t_class)

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- APP HEADER ---
st.title("🏫 Class 8 Student Management System")
st.markdown("Centralized dashboard for Student Profiles, Marks, Fees, Calls & Notebook Tracking.")

# --- MAIN APP TABS CONFIGURATION ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📝 Data Register",
    "📊 Academic Results",
    "👤 Profiles & WhatsApp",
    "💳 Fee Manager",
    "📞 Parent Calls",
    "📓 Notebook Tracker",
    "🪪 Student ID Cards"
])
# ==================== TAB 1: DATA REGISTER ====================
# ==================== TAB 1: DATA REGISTER ====================
with tab1:
    st.markdown("### 🤖 AI Data Auditor & Error Fixer")
    
    if not df.empty:
        audited_df, detected_errors = audit_and_fix_student_data(df)
        
        col_ai1, col_ai2 = st.columns([2, 1])
        
        with col_ai1:
            if detected_errors:
                st.warning(f"⚠️ **AI ne {len(detected_errors)} Data Errors/Mismatches dhoondhe hain!**")
                with st.expander("🔍 Dekhein kahan-kahan error hai:"):
                    for err in detected_errors:
                        st.write(f"- {err}")
            else:
                st.success("✅ **Sabhi student records bilkul accurate hain! Koi error nahi mila.**")
                
        with col_ai2:
            if detected_errors:
                if st.button("⚡ AI Auto-Fix All Errors", type="primary", width="stretch"):
                    try:
                        records_to_update = audited_df.to_dict(orient="records")
                        supabase.table("class8_students").upsert(records_to_update).execute()
                        st.success("🎉 Sabhi errors AI dwara auto-correct kar diye gaye hain!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Save karne me error aaya: {e}")
    
    st.markdown("---")

    # --- NEW FEATURE 1: BULK IMPORT / EXPORT (CSV / EXCEL) ---
    with st.expander("📁 Bulk Import / Export (Excel & CSV)", expanded=False):
        col_imp, col_exp = st.columns(2)
        with col_imp:
            st.markdown("##### 📥 Upload Bulk Data")
            uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        bulk_df = pd.read_csv(uploaded_file)
                    else:
                        bulk_df = pd.read_excel(uploaded_file)
                    
                    if st.button("🚀 Process & Insert Bulk Records"):
                        bulk_records = bulk_df.to_dict(orient="records")
                        supabase.table("class_8_students").upsert(bulk_records).execute()
                        st.success("🎉 Bulk Data Successfully Uploaded!")
                        refresh_cache()
                        st.rerun()
                except Exception as ex:
                    st.error(f"File process karne me error: {ex}")

        with col_exp:
            st.markdown("##### 📤 Download Current Register")
            if not df.empty:
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Download CSV Register",
                    data=csv_data,
                    file_name="Class_8_Student_Register.csv",
                    mime="text/csv",
                    type="secondary"
                )
            else:
                st.info("Download ke liye koi data nahi hai.")

    st.markdown("---")

    # --- ADD / EDIT FORM (OLD DATA INTACT + NEW FIELDS ADDED) ---
    with st.expander("➕ Add / Edit Student Record", expanded=False):
        with st.form("quick_add_form", clear_on_submit=False):
            st.markdown("##### 📝 Basic Student Details & Daily Attendance")

            r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([1, 2, 2, 2])
            with r1_c1:
                q_rno = st.number_input("Roll No *", min_value=1, step=1, value=len(df) + 1 if not df.empty else 1, key="q_rno")
            with r1_c2:
                q_name = st.text_input("Student Name *", key="q_name")
            with r1_c3:
                q_fname = st.text_input("Father Name", key="q_fname")
            with r1_c4:
                q_date = st.date_input("Date 📅", value=date.today(), key="q_date")

            r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
            with r2_c1:
                q_mobile = st.text_input("Parent Mobile", key="q_mobile")
            with r2_c2:
                q_att_status = st.selectbox("Today's Attendance Status 📍", ["Present", "Absent", "Leave"], key="q_att_status")
            with r2_c3:
                q_att_pct = st.number_input("Overall Attendance (%)", 0, 100, 90, key="q_att_pct")
            with r2_c4:
                q_cond = st.selectbox("Conduct", ["Good", "Excellent", "Outstanding", "Needs Improvement"], key="q_cond")

            # --- NEW EXTENDED FIELDS ---
            st.markdown("##### 👤 Additional Personal Information")
            r_ext1, r_ext2, r_ext3, r_ext4 = st.columns(4)
            with r_ext1:
                q_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="q_gender")
            with r_ext2:
                q_category = st.selectbox("Category", ["General", "OBC", "SC", "ST"], key="q_category")
            with r_ext3:
                q_blood = st.selectbox("Blood Group", ["Unknown", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], key="q_blood")
            with r_ext4:
                q_aadhaar = st.text_input("Aadhaar Number (12 Digits)", max_chars=12, key="q_aadhaar")

            q_address = st.text_area("Home Address", key="q_address")

            st.markdown("##### 📚 Academic Marks & Max Marks Option")
            q_max_marks = st.number_input("🎯 Subject Maximum Marks (Out of)", min_value=10, max_value=500, value=100, step=5, key="q_max_marks")

            r3_c1, r3_c2, r3_c3 = st.columns(3)
            with r3_c1:
                q_eng = st.number_input("1. English", 0, int(q_max_marks), value=0, key="q_eng")
                q_hin = st.number_input("2. Hindi", 0, int(q_max_marks), value=0, key="q_hin")
            with r3_c2:
                q_sci = st.number_input("3. Science", 0, int(q_max_marks), value=0, key="q_sci")
                q_sst = st.number_input("4. Social Science", 0, int(q_max_marks), value=0, key="q_sst")
            with r3_c3:
                q_math = st.number_input("5. Maths", 0, int(q_max_marks), value=0, key="q_math")
                q_sans = st.number_input("6. Sanskrit", 0, int(q_max_marks), value=0, key="q_sans")

            st.markdown("##### 💳 Fee Details")
            r4_c1, r4_c2 = st.columns(2)
            with r4_c1:
                q_tfee = st.number_input("Total Fee (₹)", min_value=0.0, value=15000.0, key="q_tfee")
            with r4_c2:
                q_fpaid = st.number_input("Fee Paid (₹)", min_value=0.0, value=0.0, key="q_fpaid")

            q_submitted = st.form_submit_button("💾 Save / Update Student Data")
            if q_submitted:
                if not q_name.strip():
                    st.error("⚠️ Student Name bharna zaroori hai!")
                else:
                    if save_student_data(
                        q_rno, q_name, q_fname, q_mobile, q_att_status, q_att_pct, q_cond,
                        q_eng, q_hin, q_sci, q_sst, q_math, q_sans, q_max_marks, q_tfee, q_fpaid, q_date,
                        q_gender, q_category, q_blood, q_aadhaar, q_address
                    ):
                        st.toast("✅ Student Record Updated Successfully!", icon="💾")
                        st.rerun()

    st.markdown("---")
    st.subheader("🗑️ Delete Student Record")
    if not df.empty:
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            del_roll = st.selectbox(
                "Select Roll No to Delete:",
                options=df["roll_no"].tolist(),
                format_func=lambda x: f"Roll No {x}: {df[df['roll_no']==x]['name'].values[0]}",
                key="direct_delete_select",
            )
        with col_del2:
            st.write(" ")
            st.write(" ")
            if st.button("❌ Delete Student", type="primary", width="stretch"):
                try:
                    supabase.table("class_8_students").delete().eq("roll_no", int(del_roll)).execute()
                    refresh_cache()
                    st.toast(f"Successfully deleted Roll No {del_roll}!", icon="🗑️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting record: {e}")
    else:
        st.info("No students available to delete.")

    st.markdown("---")
    # --- SMART ALERTS PANEL ---
    if not df.empty:
        low_att_df = df[df["attendance_%"] < 75]
        weak_marks_df = df[df["Percentage (%)"] < 40]

        if not low_att_df.empty or not weak_marks_df.empty:
            st.markdown("##### 🚨 Smart Attention Alerts")
            a_col1, a_col2 = st.columns(2)
            
            with a_col1:
                if not low_att_df.empty:
                    st.warning(f"⚠️ **Low Attendance (< 75%):** {len(low_att_df)} Students")
                    st.dataframe(low_att_df[["roll_no", "name", "parent_mobile", "attendance_%"]], hide_index=True, width="stretch")
            
            with a_col2:
                if not weak_marks_df.empty:
                    st.error(f"🔴 **Academic Risk (< 40%):** {len(weak_marks_df)} Students")
                    st.dataframe(weak_marks_df[["roll_no", "name", "parent_mobile", "Percentage (%)"]], hide_index=True, width="stretch")
            st.markdown("---")

    # --- SEARCH & FILTER BAR FOR REGISTER TABLE ---
    st.subheader("📋 Class 8 Student Information & Attendance Register")

    if not df.empty:
        search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
        with search_col1:
            search_term = st.text_input("🔍 Search Student (Name / Roll No / Phone):", "", key="reg_search")
        with search_col2:
            cat_filter = st.selectbox("Category Filter", ["All"] + list(df["category"].unique()) if "category" in df.columns else ["All"], key="reg_cat_filter")
        with search_col3:
            att_filter = st.selectbox("Status Filter", ["All", "Present", "Absent", "Leave"], key="reg_att_filter")

        # Apply Filters
        filtered_df = df.copy()
        if search_term.strip():
            st_term = search_term.strip().lower()
            filtered_df = filtered_df[
                filtered_df["name"].astype(str).str.lower().str.contains(st_term) |
                filtered_df["roll_no"].astype(str).str.contains(st_term) |
                filtered_df["parent_mobile"].astype(str).str.contains(st_term)
            ]
        if cat_filter != "All" and "category" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["category"] == cat_filter]
        if att_filter != "All" and "attendance" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["attendance"] == att_filter]

        reg_cols = ["roll_no", "name", "father_name", "gender", "category", "parent_mobile", "date", "attendance", "attendance_%", "conduct"]
        available_reg_cols = [c for c in reg_cols if c in filtered_df.columns]
        sorted_reg_df = filtered_df.sort_values(by="roll_no")[available_reg_cols]
        st.dataframe(sorted_reg_df, width="stretch", hide_index=True)
    else:
        st.info("Abhi koi student add nahi hai.")

# ==================== TAB 2: ACADEMIC RESULTS ====================
with tab2:
    st.subheader("📊 Class 8 Academic Results & Rank Register")

    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Students", len(df))
        if "Percentage (%)" in df.columns:
            m2.metric("Class Average Percentage", f"{df['Percentage (%)'].mean():.1f}%")
        
        if "Total Marks" in df.columns and not df["Total Marks"].empty:
            top_scorer = df.loc[df["Total Marks"].idxmax()]
            max_possible = top_scorer.get("max_marks", 100) * 6
            m3.metric("Class Topper 🏆", f"{top_scorer['name']} ({top_scorer['Total Marks']}/{max_possible})")

        class_pdf_data = generate_class_pdf(df)
        st.download_button(
            label="📥 Download Full Class Result (PDF)",
            data=class_pdf_data,
            file_name=f"Class_8_Result_Sheet_{date.today()}.pdf",
            mime="application/pdf",
            width="stretch",
        )

        st.markdown("---")

        def highlight_performance(val):
            if isinstance(val, (int, float)):
                if val >= 75:
                    return "background-color: #d4edda; color: #155724;"
                elif val < 40:
                    return "background-color: #f8d7da; color: #721c24;"
            return ""

        result_cols = [
            "Rank", "roll_no", "name", "english", "hindi", "science",
            "sst", "maths", "sanskrit", "Total Marks", "max_marks", "Percentage (%)",
        ]
        available_res_cols = [c for c in result_cols if c in df.columns]

        if "Rank" in df.columns:
            sorted_res_df = df.sort_values(by="Rank")[available_res_cols]
        else:
            sorted_res_df = df[available_res_cols]

        styled_res_df = sorted_res_df.style.map(
            highlight_performance,
            subset=[c for c in ["english", "hindi", "science", "sst", "maths", "sanskrit", "Percentage (%)"] if c in available_res_cols],
        )
        st.dataframe(styled_res_df, width="stretch", hide_index=True)
    else:
        st.info("Results dekhne ke liye pehle Student Data Register tab mein student record add karein.")

# ==================== TAB 3: PROFILES & WHATSAPP ====================
with tab3:
    st.subheader("👤 Student Profile Pro Card")

    if not df.empty:
        if "student_idx" not in st.session_state:
            st.session_state.student_idx = 0

        if st.session_state.student_idx >= len(df):
            st.session_state.student_idx = 0

        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("⬅️ Pichla Student", width="stretch"):
                if st.session_state.student_idx > 0:
                    st.session_state.student_idx -= 1
                    st.rerun()

        with col_next:
            if st.button("Agle Student ➔", width="stretch"):
                if st.session_state.student_idx < len(df) - 1:
                    st.session_state.student_idx += 1
                    st.rerun()

        student = df.iloc[st.session_state.student_idx]
        max_m = int(student.get("max_marks", 100))
        total_max_m = max_m * 6

        with col_info:
            st.info(f"Viewing Profile {st.session_state.student_idx + 1} of {len(df)}")

        st.markdown(
            f"""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div>
                        <span style="font-size: 22px; font-weight: bold;">👤 {student.get('name', 'N/A')}</span>
                        <span style="background-color: #fef08a; padding: 4px 10px; border-radius: 12px; font-weight: bold; margin-left: 10px;">🏆 Rank #{student.get('Rank', 'N/A')}</span>
                    </div>
                    <div>
                        <span style="font-size: 16px; font-weight: 600;">Roll No: #{int(student.get('roll_no', 0))}</span>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                    <div>
                        <div style="color: #64748b; font-size: 13px;">Father's Name</div>
                        <div style="font-weight: 600;">{student.get('father_name', 'N/A')}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 13px;">Date</div>
                        <div style="font-weight: 600;">📅 {student.get('date', 'N/A')}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 13px;">Status</div>
                        <div style="font-weight: 600;">📌 {student.get('attendance', 'Present')}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 13px;">Parent Mobile</div>
                        <div style="font-weight: 600;">📱 {student.get('parent_mobile', 'N/A')}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 13px;">Attendance %</div>
                        <div style="font-weight: 600;">🗓️ {student.get('attendance_%', 0)}%</div>
                    </div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        m_col1, m_col2, m_col3, m_col4, m_col5, m_col6, m_col7 = st.columns(7)
        m_col1.metric("English", f"{student.get('english', 0)}/{max_m}")
        m_col2.metric("Hindi", f"{student.get('hindi', 0)}/{max_m}")
        m_col3.metric("Science", f"{student.get('science', 0)}/{max_m}")
        m_col4.metric("SST", f"{student.get('sst', 0)}/{max_m}")
        m_col5.metric("Maths", f"{student.get('maths', 0)}/{max_m}")
        m_col6.metric("Sanskrit", f"{student.get('sanskrit', 0)}/{max_m}")
        
        tot_m = student.get('Total Marks', 0)
        pct_m = student.get('Percentage (%)', 0)
        m_col7.metric(
            "Total Score",
            f"{tot_m}/{total_max_m}",
            f"{pct_m}%",
        )
# AI Auto Remark Display
        remark_text = generate_student_remark(
            pct_m, 
            min(student.get('english',0), student.get('maths',0), student.get('science',0)),
            student.get('english',0), student.get('maths',0), student.get('science',0)
        )
        st.success(f"🤖 **Auto Performance Remark:** {remark_text}")
        st.markdown("---")

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            st.markdown("##### 📄 Report Card PDF Download")
            student_pdf = generate_student_pdf(student)
            st.download_button(
                label="📄 Download Report Card PDF",
                data=student_pdf,
                file_name=f"Report_Card_{student.get('roll_no')}_{student.get('name')}.pdf",
                mime="application/pdf",
                width="stretch",
            )

        with btn_col2:
            st.markdown("##### 📲 Direct WhatsApp Share")
            default_mobile = str(student.get("parent_mobile", "")).strip()
            if default_mobile and not default_mobile.startswith("91"):
                default_mobile = "91" + default_mobile
            elif not default_mobile:
                default_mobile = "91"

            msg_text = (
                f"Namaste! Class 8 Update for *{student.get('name', '')}* (Date: {student.get('date', '')}):\n\n"
                f"🏆 *Class Rank:* #{student.get('Rank', 'N/A')}\n"
                f"📌 *Today's Attendance Status:* {student.get('attendance', 'Present')}\n"
                f"📊 *Total Marks:* {tot_m}/{total_max_m} ({pct_m}%)\n\n"
                f"*Subject Breakdown (Out of {max_m}):*\n"
                f"- English: {student.get('english', 0)}/{max_m}\n"
                f"- Hindi: {student.get('hindi', 0)}/{max_m}\n"
                f"- Science: {student.get('science', 0)}/{max_m}\n"
                f"- Social Science: {student.get('sst', 0)}/{max_m}\n"
                f"- Maths: {student.get('maths', 0)}/{max_m}\n"
                f"- Sanskrit: {student.get('sanskrit', 0)}/{max_m}\n\n"
                f"🗓️ *Overall Attendance:* {student.get('attendance_%', 0)}%\n"
                f"⭐ *Conduct:* {student.get('conduct', 'Good')}\n\n"
                f"Thank you!"
            )

            encoded_msg = urllib.parse.quote(msg_text)
            whatsapp_url = f"https://wa.me/{default_mobile}?text={encoded_msg}"
            st.link_button(
                "💬 WhatsApp Par Result Send Karein",
                whatsapp_url,
                width="stretch",
            )

    else:
        st.info("Abhi koi student profile show karne ke liye data available nahi hai.")

# ==================== TAB 4: FEE MANAGER ====================
with tab4:
    st.subheader("💳 Student Fee Details Register")
    if not df.empty:
        f1, f2, f3 = st.columns(3)
        f1.metric("Total Expected Fees", f"₹{df['total_fee'].sum():,.2f}" if "total_fee" in df.columns else "₹0.00")
        f2.metric("Total Collected Fees", f"₹{df['fee_paid'].sum():,.2f}" if "fee_paid" in df.columns else "₹0.00")
        f3.metric("Total Pending Fees ⚠️", f"₹{df['Pending Fee'].sum():,.2f}" if "Pending Fee" in df.columns else "₹0.00")

        st.markdown("---")

        fee_cols = ["roll_no", "name", "father_name", "parent_mobile", "total_fee", "fee_paid", "Pending Fee"]
        fee_df = df[[c for c in fee_cols if c in df.columns]]
        st.dataframe(fee_df, width="stretch", hide_index=True)
    else:
        st.info("Abhi koi student register nahi hua hai.")

# ==================== TAB 5: PARENT CALLS ====================
with tab5:
    st.subheader("📞 Parent Call Communication Log")

    if not df.empty:
        selected_student_call = st.selectbox(
            "Select Student for Call Logging:",
            options=df["roll_no"].tolist(),
            format_func=lambda x: f"Roll No {x}: {df[df['roll_no']==x]['name'].values[0]}",
        )

        student_info = df[df["roll_no"] == selected_student_call].iloc[0]

        st.info(f"**Parent Mobile:** 📱 {student_info.get('parent_mobile', 'N/A')} | **Father Name:** {student_info.get('father_name', 'N/A')}")

        with st.form("call_log_form"):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                call_status = st.selectbox(
                    "Call Status 📲",
                    [
                        "Connected - Discovered Issue",
                        "Connected - Satisfied",
                        "Unreachable",
                        "Switched Off / Busy",
                        "Follow-up Scheduled",
                    ],
                )
            with c_col2:
                call_date = st.date_input("Call Date 📅", value=date.today())

            call_remarks = st.text_area(
                "Call Discussion / Remarks 📝",
                placeholder="Discussed absenteeism, homework delay, performance etc...",
            )
            submit_call = st.form_submit_button("💾 Save Call Log")

            if submit_call:
                try:
                    update_data = {
                        "last_call_date": str(call_date),
                        "last_call_status": call_status,
                        "call_remarks": call_remarks.strip(),
                    }
                    supabase.table("class_8_students").update(update_data).eq("roll_no", int(selected_student_call)).execute()
                    refresh_cache()
                    st.toast(f"✅ Call Log updated for {student_info['name']}!", icon="📞")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating call log: {e}")

        st.markdown("---")
        st.markdown("##### 📜 Call Log History Register")
        call_cols = ["roll_no", "name", "parent_mobile", "last_call_date", "last_call_status", "call_remarks"]
        available_call_cols = [c for c in call_cols if c in df.columns]
        st.dataframe(df[available_call_cols], width="stretch", hide_index=True)
    else:
        st.info("Abhi koi student register nahi hua hai.")

# ==================== TAB 6: NOTEBOOK TRACKER ====================
with tab6:
    st.subheader("📓 Notebook Completion Tracker")

    if not df.empty:
        selected_student_nb = st.selectbox(
            "Select Student for Notebook Tracking:",
            options=df["roll_no"].tolist(),
            format_func=lambda x: f"Roll No {x}: {df[df['roll_no']==x]['name'].values[0]}",
            key="nb_select",
        )

        student_nb_info = df[df["roll_no"] == selected_student_nb].iloc[0]
        nb_statuses = ["Completed", "Incomplete", "Pending Checking", "Correction Needed"]

        with st.form("notebook_tracker_form"):
            nb_col1, nb_col2, nb_col3 = st.columns(3)

            with nb_col1:
                eng_nb = st.selectbox(
                    "English Notebook",
                    nb_statuses,
                    index=nb_statuses.index(student_nb_info.get("eng_nb", "Incomplete")) if student_nb_info.get("eng_nb") in nb_statuses else 1,
                )
                hindi_nb = st.selectbox(
                    "Hindi Notebook",
                    nb_statuses,
                    index=nb_statuses.index(student_nb_info.get("hindi_nb", "Incomplete")) if student_nb_info.get("hindi_nb") in nb_statuses else 1,
                )

            with nb_col2:
                sci_nb = st.selectbox(
                    "Science Notebook",
                    nb_statuses,
                    index=nb_statuses.index(student_nb_info.get("sci_nb", "Incomplete")) if student_nb_info.get("sci_nb") in nb_statuses else 1,
                )
                sst_nb = st.selectbox(
                    "Social Science Notebook",
                    nb_statuses,
                    index=nb_statuses.index(student_nb_info.get("sst_nb", "Incomplete")) if student_nb_info.get("sst_nb") in nb_statuses else 1,
                )

            with nb_col3:
                math_nb = st.selectbox(
                    "Maths Notebook",
                    nb_statuses,
                    index=nb_statuses.index(student_nb_info.get("math_nb", "Incomplete")) if student_nb_info.get("math_nb") in nb_statuses else 1,
                )
                sans_nb = st.selectbox(
                    "Sanskrit Notebook",
                    nb_statuses,
                    index=nb_statuses.index(student_nb_info.get("sans_nb", "Incomplete")) if student_nb_info.get("sans_nb") in nb_statuses else 1,
                )

            submit_nb = st.form_submit_button("💾 Save Notebook Status")

            if submit_nb:
                try:
                    update_nb_data = {
                        "eng_nb": eng_nb,
                        "hindi_nb": hindi_nb,
                        "sci_nb": sci_nb,
                        "sst_nb": sst_nb,
                        "math_nb": math_nb,
                        "sans_nb": sans_nb,
                    }
                    supabase.table("class_8_students").update(update_nb_data).eq("roll_no", int(selected_student_nb)).execute()
                    refresh_cache()
                    st.toast(f"✅ Notebook status updated for {student_nb_info['name']}!", icon="📓")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating notebook status: {e}")

        st.markdown("---")
        st.markdown("##### 📜 Notebook Status Register")

        def highlight_notebook(val):
            if val == "Completed":
                return "background-color: #d4edda; color: #155724;"
            elif val in ["Incomplete", "Correction Needed"]:
                return "background-color: #f8d7da; color: #721c24;"
            elif val == "Pending Checking":
                return "background-color: #fff3cd; color: #856404;"
            return ""
# ==================== TAB 7: STUDENT ID CARDS ====================
with tab7:
    st.subheader("🪪 Student ID Card Generator")
    
    if not df.empty:
        col_id_select, col_id_preview = st.columns([1, 2])
        
        with col_id_select:
            st.markdown("##### ⚙️ ID Card Details")
            school_name = st.text_input("School / Academy Name", value="M.K MEMORIAL SR. SEC. SCHOOL, SIKAR", key="id_school")
            academic_year = st.text_input("Academic Session", value="2026-2027", key="id_session")
            
            selected_id_roll = st.selectbox(
                "Select Student for ID Card:",
                options=df["roll_no"].tolist(),
                format_func=lambda x: f"Roll No {x}: {df[df['roll_no']==x]['name'].values[0]}",
                key="id_card_select"
            )
            
            student_id_data = df[df["roll_no"] == selected_id_roll].iloc[0]
            
            # Print PDF Helper for Single ID Card
            def generate_id_card_pdf(stu, sch_name, session):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=(250, 160), leftMargin=10, rightMargin=10, topMargin=10, bottomMargin=10)
                styles = getSampleStyleSheet()
                story = []
                
                sch_style = ParagraphStyle('SchStyle', parent=styles['Heading1'], fontSize=11, alignment=1, textColor=colors.HexColor("#0f172a"))
                sess_style = ParagraphStyle('SessStyle', parent=styles['Normal'], fontSize=7, alignment=1, textColor=colors.HexColor("#475569"))
                name_style = ParagraphStyle('NameStyle', parent=styles['Heading2'], fontSize=10, alignment=1, textColor=colors.HexColor("#1e3a8a"))
                
                story.append(Paragraph(f"<b>{sch_name.upper()}</b>", sch_style))
                story.append(Paragraph(f"STUDENT ID CARD ({session})", sess_style))
                story.append(Spacer(1, 6))
                
                story.append(Paragraph(f"<b>{stu.get('name', '').upper()}</b>", name_style))
                story.append(Spacer(1, 6))
                
                info_text = [
                    [Paragraph(f"<b>Roll No:</b> {stu.get('roll_no', '')}", styles['Normal']), Paragraph(f"<b>Class:</b> 8th", styles['Normal'])],
                    [Paragraph(f"<b>Father:</b> {stu.get('father_name', '')}", styles['Normal']), Paragraph(f"<b>Mobile:</b> {stu.get('parent_mobile', '')}", styles['Normal'])],
                ]
                t_id = Table(info_text, colWidths=[115, 115])
                t_id.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('FONTSIZE', (0,0), (-1,-1), 7),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(t_id)
                
                doc.build(story)
                buffer.seek(0)
                return buffer

            id_pdf = generate_id_card_pdf(student_id_data, school_name, academic_year)
            st.download_button(
                label="🖨️ Download Printable ID Card (PDF)",
                data=id_pdf,
                file_name=f"ID_Card_{student_id_data.get('roll_no')}_{student_id_data.get('name')}.pdf",
                mime="application/pdf",
                width="stretch"
            )

        with col_id_preview:
            st.markdown("##### 👁️ Live Digital Card Preview")
            
            card_html = textwrap.dedent(f"""
            <div style="width: 320px; border: 2px solid #1e293b; border-radius: 12px; padding: 15px; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 0 auto; font-family: Arial, sans-serif;">
                <div style="text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 8px; margin-bottom: 12px;">
                    <div style="font-size: 13px; font-weight: bold; color: #0f172a; text-transform: uppercase;">{school_name}</div>
                    <div style="font-size: 9px; color: #2563eb; font-weight: 600;">STUDENT IDENTITY CARD • {academic_year}</div>
                </div>
                <div style="text-align: center; margin-bottom: 12px;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background-color: #e2e8f0; display: inline-block; line-height: 50px; font-size: 22px; border: 2px solid #2563eb; margin: 0 auto;">👤</div>
                    <div style="font-size: 15px; font-weight: bold; color: #1e3a8a; margin-top: 6px;">{student_id_data.get('name', 'N/A').upper()}</div>
                    <div style="font-size: 10px; color: #64748b; font-weight: 600;">CLASS 8th STUDENT</div>
                </div>
                <div style="background-color: #edf2f7; padding: 10px; border-radius: 8px; font-size: 11px; color: #334155; text-align: left;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span><b>Roll No:</b> #{int(student_id_data.get('roll_no', 0))}</span>
                        <span><b>Conduct:</b> {student_id_data.get('conduct', 'Good')}</span>
                    </div>
                    <div style="margin-bottom: 4px;"><b>Father Name:</b> {student_id_data.get('father_name', 'N/A')}</div>
                    <div><b>Parent Mobile:</b> 📱 {student_id_data.get('parent_mobile', 'N/A')}</div>
                </div>
            </div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)

    else:
        st.info("ID Card generate karne ke liye pehle student record add karein.")
        import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. CONFIGURATION & LOGIN SYSTEM
# ==========================================
st.set_page_config(page_title="Multi-Class School Management System", page_icon="🏫", layout="wide")

# Session State for Authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Simple Login System
if not st.session_state.logged_in:
    st.title("🔐 School Dashboard Login")
    user_type = st.radio("Login As:", ["Admin (Full Access)", "Other User (Paid Access)"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", type="primary"):
        if user_type == "Admin (Full Access)" and username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success("Admin Login Successful!")
            st.rerun()
        elif user_type == "Other User (Paid Access)":
            st.warning("⚠️ Other Users: Subscription Plan Active (UPI Payment Required for Full Features)")
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.rerun()
        else:
            st.error("Invalid Username or Password!")
    st.stop()

# Logout Button in Sidebar
st.sidebar.title("👤 Session Info")
st.sidebar.write(f"Role: **{'Admin (Free)' if st.session_state.is_admin else 'Standard User'}**")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ==========================================
# 2. GLOBAL CLASS & SECTION SELECTOR
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🏫 Class & Section Filter")
selected_class = st.sidebar.selectbox("Select Class:", [f"Class {i}" for i in range(1, 13)], index=7) # Default Class 8
selected_section = st.sidebar.selectbox("Select Section:", ["Section A", "Section B", "Section C", "Section D"])

st.title(f"🏫 {selected_class} ({selected_section}) Management System")

# Sample Multi-Class Database (In Session State)
if 'students_db' not in st.session_state:
    st.session_state.students_db = pd.DataFrame([
        {"roll_no": 8001, "name": "ABHAY CHOUDHARY", "father_name": "PADAM SINGH", "parent_mobile": "9929534777", "class": "Class 8", "section": "Section A", "photo": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"},
        {"roll_no": 8002, "name": "ALKA CHOUDHARY", "father_name": "NARENDRA KUMAR", "parent_mobile": "9785735746", "class": "Class 8", "section": "Section A", "photo": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"},
    ])

df = st.session_state.students_db
filtered_df = df[(df['class'] == selected_class) & (df['section'] == selected_section)]

# ==========================================
# 3. TABS NAVIGATION
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Daily Attendance & SMS", 
    "➕ Add / Edit Student", 
    "💳 Subscription & Payments", 
    "📞 Student Directory & Call"
])

# ------------------------------------------
# TAB 1: DAILY ATTENDANCE & SMS
# ------------------------------------------
with tab1:
    st.subheader(f"📅 Per Day Attendance Record - {datetime.date.today().strftime('%d/%m/%Y')}")
    
    if not filtered_df.empty:
        att_data = []
        for idx, row in filtered_df.iterrows():
            col_a, col_b, col_c, col_d = st.columns([1, 2, 2, 2])
            with col_a:
                st.write(f"**{row['roll_no']}**")
            with col_b:
                st.write(f"**{row['name']}**")
            with col_c:
                status = st.selectbox("Status", ["Present", "Absent"], key=f"att_{row['roll_no']}")
            with col_d:
                if status == "Absent":
                    msg = f"Namaste! Aapka baccha {row['name']} aaj school me Absent hai."
                    wa_url = f"https://api.whatsapp.com/send?phone=91{row['parent_mobile']}&text={msg.replace(' ', '%20')}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:4px 8px; border-radius:4px;">📲 Send Absent SMS</button></a>', unsafe_allow_html=True)
    else:
        st.info("Is Class aur Section mein abhi koi student add nahi hai.")

# ------------------------------------------
# TAB 2: SMART ADD / EDIT STUDENT (AUTO-FILL BY ROLL NO)
# ------------------------------------------
with tab2:
    st.subheader("➕ Add or Edit Student Record")
    
    search_roll = st.number_input("Enter Roll No to Auto-Fetch Data:", min_value=100, max_value=9999, value=8001)
    
    # Auto Fetching Existing Details
    existing_student = df[df['roll_no'] == search_roll]
    
    default_name = ""
    default_father = ""
    default_mobile = ""
    
    if not existing_student.empty:
        st.success(f"✅ Record Found for Roll No {search_roll}! Details loaded below for editing.")
        default_name = existing_student.iloc[0]['name']
        default_father = existing_student.iloc[0]['father_name']
        default_mobile = existing_student.iloc[0]['parent_mobile']
    else:
        st.info(f"ℹ️ New Roll No {search_roll}. Fill below details to add new student.")
    
    with st.form("student_form"):
        s_name = st.text_input("Student Name", value=default_name)
        f_name = st.text_input("Father Name", value=default_father)
        p_mob = st.text_input("Parent Mobile", value=default_mobile)
        
        # Profile Picture Upload Option
        uploaded_file = st.file_uploader("Upload Profile Picture (PP)", type=["jpg", "png", "jpeg"])
        
        save_btn = st.form_submit_button("Save / Update Student Record")
        
        if save_btn:
            photo_url = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            new_data = {
                "roll_no": search_roll,
                "name": s_name,
                "father_name": f_name,
                "parent_mobile": p_mob,
                "class": selected_class,
                "section": selected_section,
                "photo": photo_url
            }
            
            # Remove old record if exists and append new
            st.session_state.students_db = st.session_state.students_db[st.session_state.students_db['roll_no'] != search_roll]
            st.session_state.students_db = pd.concat([st.session_state.students_db, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"Student Roll No {search_roll} saved successfully!")
            st.rerun()

# ------------------------------------------
# TAB 3: PAYMENT & SUBSCRIPTION GATEWAY
# ------------------------------------------
with tab3:
    st.subheader("💳 App Access & Subscription Plans")
    if st.session_state.is_admin:
        st.success("👑 You are logged in as **ADMIN**. All features are 100% FREE for you lifetime!")
    else:
        st.warning("🔒 Standard Account Mode. Unlock All Features via Payment.")
        st.markdown("""
        ### Premium ERP Subscription
        * **Monthly Access:** ₹299 / Month
        * **Annual School Pass:** ₹2,499 / Year
        """)
        st.button("💳 Pay via UPI / QR Code")

# ------------------------------------------
# TAB 4: DIRECT CALL & DIRECTORY
# ------------------------------------------
with tab4:
    st.subheader(f"📞 {selected_class} ({selected_section}) Student Directory")
    for idx, row in filtered_df.iterrows():
        c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
        with c1:
            st.image(row['photo'], width=50)
        with c2:
            st.write(f"**{row['name']}** (Roll: {row['roll_no']})")
            st.caption(f"Father: {row['father_name']}")
        with c3:
            st.write(f"📱 {row['parent_mobile']}")
        with c4:
            st.markdown(f'<a href="tel:{row["parent_mobile"]}"><button style="background-color:#007BFF; color:white; border:none; padding:6px 12px; border-radius:4px;">📞 Call Parent</button></a>', unsafe_allow_html=True)
        import streamlit as st
from supabase import create_client, Client
import random
import datetime

# --- Mobile UI Config ---
st.set_page_config(page_title="School ERP App", page_icon="📱", layout="centered")

# CSS for Android Mobile View Style
st.markdown("""
    <style>
    .stApp { max-width: 480px; margin: 0 auto; border-radius: 20px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 48px; background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

# Supabase Client Initialisation
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Session State for Authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# --- FEATURE 1: LOGIN & OTP PAYMENT SYSTEM (₹1000) ---
def login_screen():
    st.title("🔐 Login / Register")
    login_type = st.radio("Login As", ["Admin (Free)", "Other User / Teacher"])
    
    if login_type == "Admin (Free)":
        user = st.text_input("Admin Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if user == "admin" and pwd == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_role = "Admin"
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")
    else:
        mobile = st.text_input("Mobile Number")
        if st.button("Send OTP & Pay ₹1000"):
            # Here integrate Razorpay / Payment Link API
            st.info(f"Payment Link Sent to {mobile}. (Dummy Demo Mode)")
            st.session_state.logged_in = True
            st.session_state.user_role = "Paid User"
            st.rerun()

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- MAIN DASHBOARD (Post-Login) ---
st.sidebar.title("🏫 App Navigation")
st.sidebar.text(f"Logged in as: {st.session_state.user_role}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.selectbox("Select Option", [
    "📅 Daily Attendance & SMS",
    "✏️ Auto-fill Student Edit (Roll No)",
    "💳 Payment Link & Call",
    "📝 Exam Marks (Unit Test / Yearly)",
    "📄 Exam Paper Generator (PDF)",
    "📚 NCERT Books Links"
])

# --- FEATURE 2: DAILY ATTENDANCE & SMS ---
if menu == "📅 Daily Attendance & SMS":
    st.subheader("Daily Attendance Record")
    selected_class = st.selectbox("Class", [f"Class {i}" for i in range(1, 13)])
    selected_sec = st.selectbox("Section", ["A", "B", "C", "D"])
    
    st.write(f"Marking Attendance for {selected_class} - Sec {selected_sec}")
    # Sample Roll Call List
    roll = st.number_input("Roll No", min_value=1)
    status = st.radio("Status", ["Present", "Absent"])
    
    if st.button("Save Attendance & Send SMS"):
        # Fast2SMS or Twilio API Integration Point
        st.success(f"Attendance recorded for Roll {roll}. SMS sent to parent: 'Your child was {status} today.'")

# --- FEATURE 3: ROLL NUMBER AUTO-FILL STUDENT EDIT ---
elif menu == "✏️ Auto-fill Student Edit (Roll No)":
    st.subheader("Add / Update Student")
    search_roll = st.number_input("Enter Roll No to Search/Edit", min_value=1)
    
    # Auto-fetch logic from Supabase
    if st.button("Fetch Details"):
        # res = supabase.table("students").select("*").eq("roll_no", search_roll).execute()
        st.info(f"Loaded records for Roll No: {search_roll}")
    
    s_name = st.text_input("Student Name")
    s_class = st.selectbox("Class", [f"Class {i}" for i in range(1, 13)])
    s_sec = st.selectbox("Section", ["A", "B", "C"])
    
    if st.button("Save/Update Student"):
        st.success("Student details updated successfully!")

# --- FEATURE 4: PAYMENT LINK GENERATOR & CALL ---
elif menu == "💳 Payment Link & Call":
    st.subheader("Fees Payment Link & Calling")
    mob = st.text_input("Parent Mobile Number")
    amt = st.number_input("Amount (₹)", value=1000)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 Direct Call"):
            st.markdown(f'<a href="tel:{mob}">Click to Call {mob}</a>', unsafe_allow_html=True)
    with col2:
        if st.button("📲 Send UPI Payment Link"):
            upi_url = f"upi://pay?pa=school@upi&pn=SchoolFees&am={amt}"
            st.write(f"UPI Link Created: `{upi_url}`")

# --- FEATURE 5: EXAM MARKS (Unit Test, Half Yearly, Yearly) ---
elif menu == "📝 Exam Marks (Unit Test / Yearly)":
    st.subheader("Student Examination Marks")
    exam_type = st.selectbox("Exam Type", ["Unit Test 1", "Unit Test 2", "Half Yearly", "Yearly Exam"])
    st.selectbox("Class", [f"Class {i}" for i in range(1, 13)])
    st.number_input("Roll No")
    
    hindi = st.number_input("Hindi Marks", 0, 100)
    english = st.number_input("English Marks", 0, 100)
    maths = st.number_input("Maths Marks", 0, 100)
    
    if st.button("Save Marks"):
        st.success(f"Marks saved successfully for {exam_type}!")

# --- FEATURE 6: NCERT BOOKS LINKS ---
elif menu == "📚 NCERT Books Links":
    st.subheader("NCERT Textbooks (Class 1 to 12)")
    c_ncert = st.selectbox("Select Class for NCERT Books", [f"Class {i}" for i in range(1, 13)])
    st.markdown(f"👉 [Click Here to Download Official NCERT PDFs for {c_ncert}](https://ncert.nic.in/textbook.php)")

# --- FEATURE 7: EXAM PAPER GENERATOR (PDF) ---
elif menu == "📄 Exam Paper Generator (PDF)":
    st.subheader("Generate Question Paper PDF")
    p_class = st.selectbox("Paper Class", [f"Class {i}" for i in range(1, 13)])
    p_sub = st.text_input("Subject Name", "Mathematics")
    q1 = st.text_area("Question 1", "Solve: 2x + 5 = 15")
    q2 = st.text_area("Question 2", "Write the definition of Prime Numbers.")
    
    if st.button("Generate Paper PDF"):
        st.success("Exam Paper Generated Successfully!")
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

# --- 3. LOGIN & ONLINE PAYMENT (1000 RS OTP) SYSTEM ---
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

    else: # OTP & ₹1000 Mobile Login
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
        
        # Save to database
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

    # Form Fields (Auto-filled if found)
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

# --- FEATURE 4: EXAM MARKS (UT, HALF-YEARLY, YEARLY) ---
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

# --- FEATURE 5: EXAM QUESTION PAPER GENERATOR (PDF) ---
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

# --- FEATURE 6: NCERT BOOKS LINKS (CLASS 1 TO 12) ---
elif menu == "📚 NCERT Books (Class 1 to 12)":
    st.title("📚 NCERT Book Downloads")
    sel_ncert = st.selectbox("Select Class", classes_list)
    
    st.info(f"Downloading books for {sel_ncert}")
    st.markdown(f"👉 **[Official NCERT Textbooks Direct Download Link](https://ncert.nic.in/textbook.php)**")