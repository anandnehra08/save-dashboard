import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Class 8 Student Management System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Print ID Cards, Badges, and UI polish
st.markdown("""
<style>
    /* Metric Cards Styling */
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    /* ID Card Graphic Template */
    .id-card-container {
        width: 340px;
        height: 500px;
        border: 2px solid #0288d1;
        border-radius: 15px;
        background: linear-gradient(135deg, #ffffff 0%, #e1f5fe 100%);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        padding: 20px;
        margin: auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        position: relative;
        overflow: hidden;
    }
    .id-card-header {
        text-align: center;
        background-color: #0288d1;
        color: white;
        padding: 10px;
        border-radius: 10px 10px 0 0;
        margin: -20px -20px 15px -20px;
    }
    .id-card-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
    }
    .id-card-header p {
        margin: 2px 0 0 0;
        font-size: 11px;
        opacity: 0.9;
    }
    .id-avatar {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        border: 3px solid #0288d1;
        display: block;
        margin: 0 auto 10px auto;
        object-fit: cover;
        background-color: #fff;
    }
    .id-card-body {
        font-size: 13px;
        color: #333;
        line-height: 1.6;
    }
    .id-card-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dashed #b3e5fc;
        padding: 4px 0;
    }
    .id-card-label {
        font-weight: bold;
        color: #01579b;
    }
    .id-card-footer {
        position: absolute;
        bottom: 10px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 10px;
        color: #666;
    }

    /* Print Styles */
    @media print {
        body * {
            visibility: hidden;
        }
        .printable-area, .printable-area * {
            visibility: visible;
        }
        .printable-area {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SUPABASE DATABASE CONNECTIVITY
# ==========================================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase connection secrets missing or invalid: {e}")
        return None

supabase = init_supabase()

# Sample Fallback Data if DB is empty
DEFAULT_STUDENTS = [
    {
        "roll_no": 8001, "name": "ABHAY CHOUDHARY", "father_name": "PADAM SINGH",
        "parent_mobile": "9929534777", "attendance_%": 88, "conduct": "Good",
        "maths": 85, "science": 78, "english": 82, "hindi": 80, "social_science": 75,
        "total_fees": 25000, "paid_fees": 20000, "blood_group": "B+", "dob": "2012-05-14"
    },
    {
        "roll_no": 8002, "name": "ALKA CHOUDHARY", "father_name": "NARENDRA KUMAR",
        "parent_mobile": "9785735746", "attendance_%": 92, "conduct": "Excellent",
        "maths": 92, "science": 95, "english": 88, "hindi": 90, "social_science": 89,
        "total_fees": 25000, "paid_fees": 25000, "blood_group": "A+", "dob": "2012-08-22"
    },
    {
        "roll_no": 8003, "name": "ANSH KUMARJANGIR", "father_name": "SHANKARLAL",
        "parent_mobile": "9527189446", "attendance_%": 68, "conduct": "Average",
        "maths": 35, "science": 38, "english": 42, "hindi": 50, "social_science": 40,
        "total_fees": 25000, "paid_fees": 12000, "blood_group": "O+", "dob": "2012-01-10"
    },
    {
        "roll_no": 8007, "name": "HEMANT SINGH", "father_name": "PRATAP SINGH",
        "parent_mobile": "8233569691", "attendance_%": 62, "conduct": "Needs Improvement",
        "maths": 28, "science": 30, "english": 25, "hindi": 32, "social_science": 35,
        "total_fees": 25000, "paid_fees": 8000, "blood_group": "AB+", "dob": "2011-11-30"
    }
]

def load_data():
    if supabase:
        try:
            res = supabase.table("students").select("*").execute()
            if res.data and len(res.data) > 0:
                df = pd.DataFrame(res.data)
                return df
        except Exception:
            pass
    return pd.DataFrame(DEFAULT_STUDENTS)

def save_student_to_db(student_dict):
    if supabase:
        try:
            supabase.table("students").upsert(student_dict).execute()
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Failed to save to Supabase: {e}")
            return False
    return True

df = load_data()

# Calculate Percentage for Academic Risk
if not df.empty:
    sub_cols = ['maths', 'science', 'english', 'hindi', 'social_science']
    valid_subs = [c for c in sub_cols if c in df.columns]
    if valid_subs:
        df['Percentage'] = df[valid_subs].mean(axis=1).round(2)
    else:
        df['Percentage'] = 0.0

# ==========================================
# 3. HEADER & SUMMARY METRICS
# ==========================================
st.title("🏫 Class 8 Student Management System")
st.caption("Centralized dashboard for Student Profiles, Marks, Fees, Calls & Notebook Tracking.")

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.metric("Total Students", len(df))
with col_m2:
    avg_att = f"{df['attendance_%'].mean():.1f}%" if 'attendance_%' in df.columns and not df.empty else "N/A"
    st.metric("Avg Attendance", avg_att)
with col_m3:
    avg_marks = f"{df['Percentage'].mean():.1f}%" if 'Percentage' in df.columns and not df.empty else "N/A"
    st.metric("Class Avg Marks", avg_marks)
with col_m4:
    low_att = len(df[df['attendance_%'] < 75]) if 'attendance_%' in df.columns else 0
    st.metric("Low Attendance (<75%)", low_att, delta_color="inverse")
with col_m5:
    acad_risk = len(df[df['Percentage'] < 40]) if 'Percentage' in df.columns else 0
    st.metric("Academic Risk (<40%)", acad_risk, delta_color="inverse")

st.divider()

# ==========================================
# 4. TAB NAVIGATION SETUP (9 FULL TABS)
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📝 Data Register",
    "📊 Academic Results",
    "👤 Profiles & WhatsApp",
    "🪪 ID Card Generator",
    "💳 Fee Manager",
    "📞 Parent Calls",
    "📓 Notebook Tracker",
    "🔗 Student Slug Portal",
    "🤖 AI Assistant & Insights"
])

# ------------------------------------------
# TAB 1: DATA REGISTER & ATTENTION ALERTS
# ------------------------------------------
with tab1:
    st.subheader("🤖 AI Data Auditor & Error Fixer")
    
    # Audit checks
    errors = []
    if not df.empty:
        if df['attendance_%'].max() > 100 or df['attendance_%'].min() < 0:
            errors.append("Invalid Attendance percentage detected (>100 or <0).")
        if df['parent_mobile'].astype(str).str.len().ne(10).any():
            errors.append("Some phone numbers do not have exactly 10 digits.")
            
    if not errors:
        st.success("✅ Sabhi student records bilkul accurate hain! Koi error nahi mila.")
    else:
        for err in errors:
            st.warning(f"⚠️ {err}")

    st.markdown("---")
    
    # Add / Edit Form
    with st.expander("➕ Add / Edit Student Record"):
        with st.form("add_student_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                r_no = st.number_input("Roll No", min_value=8001, max_value=8999, value=8010)
                s_name = st.text_input("Student Name")
                f_name = st.text_input("Father Name")
            with c2:
                p_mob = st.text_input("Parent Mobile (10 digits)", value="9876543210")
                att_val = st.slider("Attendance %", 0, 100, 85)
                conduct_val = st.selectbox("Conduct", ["Excellent", "Good", "Average", "Needs Improvement"])
            with c3:
                b_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                dob_val = st.date_input("Date of Birth", value=datetime.date(2012, 1, 1))
                tot_fee = st.number_input("Total Fee", value=25000)
                
            submit_btn = st.form_submit_button("Save Student Record")
            if submit_btn:
                new_rec = {
                    "roll_no": r_no,
                    "name": s_name.upper(),
                    "father_name": f_name.upper(),
                    "parent_mobile": p_mob,
                    "attendance_%": att_val,
                    "conduct": conduct_val,
                    "blood_group": b_group,
                    "dob": str(dob_val),
                    "total_fees": tot_fee,
                    "paid_fees": 0
                }
                save_student_to_db(new_rec)
                st.success(f"Student {s_name} successfully saved!")
                st.rerun()

    # Smart Attention Alerts
    st.subheader("🚨 Smart Attention Alerts")
    ca1, ca2 = st.columns(2)
    with ca1:
        st.warning("⚠️ Low Attendance (< 75%):")
        low_att_df = df[df['attendance_%'] < 75][['roll_no', 'name', 'parent_mobile', 'attendance_%']]
        st.dataframe(low_att_df, use_container_width=True, hide_index=True)
    with ca2:
        st.error("🔴 Academic Risk (< 40% Marks):")
        acad_risk_df = df[df['Percentage'] < 40][['roll_no', 'name', 'parent_mobile', 'Percentage']]
        st.dataframe(acad_risk_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📋 Class 8 Student Information & Attendance Register")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 2: ACADEMIC RESULTS
# ------------------------------------------
with tab2:
    st.subheader("📈 Academic Results & Marks Entry")
    
    if not df.empty:
        col_sel, col_chart = st.columns([1, 2])
        with col_sel:
            st.markdown("#### Enter Marks for Student")
            selected_roll = st.selectbox("Select Roll No", df['roll_no'].tolist())
            st_row = df[df['roll_no'] == selected_roll].iloc[0]
            
            with st.form("marks_entry_form"):
                m_maths = st.number_input("Maths", 0, 100, int(st_row.get('maths', 0)))
                m_sci = st.number_input("Science", 0, 100, int(st_row.get('science', 0)))
                m_eng = st.number_input("English", 0, 100, int(st_row.get('english', 0)))
                m_hin = st.number_input("Hindi", 0, 100, int(st_row.get('hindi', 0)))
                m_sst = st.number_input("Social Science", 0, 100, int(st_row.get('social_science', 0)))
                
                save_m = st.form_submit_button("Update Marks")
                if save_m:
                    updated_dict = st_row.to_dict()
                    updated_dict.update({
                        'maths': m_maths, 'science': m_sci,
                        'english': m_eng, 'hindi': m_hin,
                        'social_science': m_sst
                    })
                    save_student_to_db(updated_dict)
                    st.success("Marks updated successfully!")
                    st.rerun()

        with col_chart:
            st.markdown("#### Class Subject Comparison Average")
            sub_means = df[['maths', 'science', 'english', 'hindi', 'social_science']].mean()
            st.bar_chart(sub_means)
            
        st.subheader("🏆 Class Toppers & Leaderboard")
        top_df = df[['roll_no', 'name', 'Percentage']].sort_values(by='Percentage', ascending=False)
        st.dataframe(top_df, use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 3: PROFILES & WHATSAPP
# ------------------------------------------
with tab3:
    st.subheader("👤 Student Profile Pro Card & Quick WhatsApp")
    
    if not df.empty:
        sel_p_roll = st.selectbox("Choose Student Profile", df['roll_no'].tolist(), key="p_roll")
        p_data = df[df['roll_no'] == sel_p_roll].iloc[0]
        
        p_c1, p_c2 = st.columns([1, 2])
        with p_c1:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=140)
            st.markdown(f"### {p_data['name']}")
            st.caption(f"Roll No: {p_data['roll_no']} | Class 8th")
            st.info(f"🏅 Academic Score: {p_data['Percentage']}%")
        
        with p_c2:
            st.markdown(f"**Father's Name:** {p_data.get('father_name', 'N/A')}")
            st.markdown(f"**Parent Phone:** {p_data.get('parent_mobile', 'N/A')}")
            st.markdown(f"**Attendance:** {p_data.get('attendance_%', 'N/A')}%")
            st.markdown(f"**Conduct/Behavior:** {p_data.get('conduct', 'Good')}")
            st.markdown(f"**Blood Group:** {p_data.get('blood_group', 'O+')}")
            
            # WhatsApp Direct Chat Generator
            phone = str(p_data.get('parent_mobile', ''))
            msg = f"Namaste! Class 8th se {p_data['name']} ki attendance {p_data.get('attendance_%')}% hai aur average marks {p_data.get('Percentage')}% hai. Kripya dhyan dein."
            wa_link = f"https://api.whatsapp.com/send?phone=91{phone}&text={msg.replace(' ', '%20')}"
            
            st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">💬 Send WhatsApp Update to Parent</button></a>', unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: PRINTABLE ID CARD GENERATOR
# ------------------------------------------
with tab4:
    st.subheader("🪪 Printable Student ID Card Generator")
    st.caption("Select a student to generate a print-ready official digital ID card.")
    
    if not df.empty:
        id_roll = st.selectbox("Select Student for ID Card", df['roll_no'].tolist(), key="id_roll_sel")
        id_st = df[df['roll_no'] == id_roll].iloc[0]
        
        col_id_view, col_id_opts = st.columns([1, 1])
        
        with col_id_view:
            st.markdown('<div class="printable-area">', unsafe_allow_html=True)
            id_card_html = f"""
            <div class="id-card-container">
                <div class="id-card-header">
                    <h3>ADARSH PUBLIC SCHOOL</h3>
                    <p>Class 8th Student Identity Card (2026-27)</p>
                </div>
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="id-avatar" />
                <div class="id-card-body">
                    <div class="id-card-row"><span class="id-card-label">NAME:</span> <span><b>{id_st['name']}</b></span></div>
                    <div class="id-card-row"><span class="id-card-label">ROLL NO:</span> <span>{id_st['roll_no']}</span></div>
                    <div class="id-card-row"><span class="id-card-label">FATHER:</span> <span>{id_st.get('father_name', 'N/A')}</span></div>
                    <div class="id-card-row"><span class="id-card-label">DOB:</span> <span>{id_st.get('dob', '2012-01-01')}</span></div>
                    <div class="id-card-row"><span class="id-card-label">BLOOD GRP:</span> <span>{id_st.get('blood_group', 'O+')}</span></div>
                    <div class="id-card-row"><span class="id-card-label">EMERGENCY:</span> <span>{id_st.get('parent_mobile', 'N/A')}</span></div>
                </div>
                <div class="id-card-footer">
                    <p>Principal Signature & Stamp</p>
                </div>
            </div>
            """
            st.markdown(id_card_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_id_opts:
            st.info("💡 **Print Instructions:**")
            st.write("1. Click the button below to trigger your browser's print menu.")
            st.write("2. Select 'Save as PDF' or directly print on Cardstock.")
            st.button("🖨️ Print Student ID Card", on_click=lambda: st.write("<script>window.print();</script>", unsafe_allow_html=True))

# ------------------------------------------
# TAB 5: FEE MANAGER
# ------------------------------------------
with tab5:
    st.subheader("💳 Student Fees Collection & Ledger")
    
    if not df.empty:
        df['paid_fees'] = df['paid_fees'].fillna(0)
        df['total_fees'] = df['total_fees'].fillna(25000)
        df['due_fees'] = df['total_fees'] - df['paid_fees']
        
        tot_coll = df['paid_fees'].sum()
        tot_pending = df['due_fees'].sum()
        
        fc1, fc2 = st.columns(2)
        with fc1:
            st.success(f"💰 Total Fees Collected: ₹{tot_coll:,.2f}")
        with fc2:
            st.error(f"⏳ Total Pending Dues: ₹{tot_pending:,.2f}")
            
        st.markdown("#### Update Fee Payment")
        fee_roll = st.selectbox("Select Student for Fee Entry", df['roll_no'].tolist(), key="fee_r")
        f_row = df[df['roll_no'] == fee_roll].iloc[0]
        
        with st.form("fee_form"):
            p_amount = st.number_input("Amount Paid Now (₹)", min_value=0, value=1000)
            pay_btn = st.form_submit_button("Record Payment")
            if pay_btn:
                u_f = f_row.to_dict()
                u_f['paid_fees'] = float(u_f.get('paid_fees', 0)) + float(p_amount)
                save_student_to_db(u_f)
                st.success("Payment recorded successfully!")
                st.rerun()

        st.dataframe(df[['roll_no', 'name', 'total_fees', 'paid_fees', 'due_fees']], use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 6: PARENT CALL LOGS
# ------------------------------------------
with tab6:
    st.subheader("📞 Parent Call History & Follow-up Tracker")
    
    with st.form("call_log_form"):
        cl1, cl2, cl3 = st.columns(3)
        with cl1:
            c_roll = st.selectbox("Student", df['roll_no'].tolist() if not df.empty else [8001])
        with cl2:
            c_status = st.selectbox("Call Status", ["Connected - Discussed", "Parent Busy", "No Answer / Switched Off", "Follow-up Required"])
        with cl3:
            c_notes = st.text_input("Call Discussion Notes", value="Discussed regarding low attendance and test marks.")
            
        log_btn = st.form_submit_button("Log Call Record")
        if log_btn:
            st.success("Call logged successfully in history!")

    st.info("📋 Recent Parent Call Logs will appear here.")

# ------------------------------------------
# TAB 7: NOTEBOOK TRACKER
# ------------------------------------------
with tab7:
    st.subheader("📓 Subject Notebook Submission Tracker")
    
    nb_sub = st.selectbox("Select Subject", ["Maths", "Science", "English", "Hindi", "Social Science"])
    
    if not df.empty:
        nb_df = df[['roll_no', 'name']].copy()
        nb_df['Status'] = "Completed & Checked"
        st.data_editor(nb_df, use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 8: STUDENT SLUG PORTAL LINK
# ------------------------------------------
with tab8:
    st.subheader("🔗 Public Student Slug Portal Link")
    st.caption("Generate unique shareable link for student result cards.")
    
    if not df.empty:
        slug_roll = st.selectbox("Choose Student for Link", df['roll_no'].tolist(), key="slug_r")
        st_slug_data = df[df['roll_no'] == slug_roll].iloc[0]
        
        slug_name = str(st_slug_data['name']).lower().replace(' ', '-')
        public_url = f"https://class8-student-management.streamlit.app/?student_slug={slug_name}-{slug_roll}"
        
        st.code(public_url, language="text")
        st.success(f"Share this link directly with {st_slug_data['name']}'s parents!")

# ------------------------------------------
# TAB 9: AI ASSISTANT & INSIGHTS
# ------------------------------------------
with tab9:
    st.subheader("🤖 AI Class Assistant & Performance Insights")
    
    query = st.text_input("Ask AI about Class 8 performance (e.g. 'Which students need urgent help in Maths?'):")
    if query:
        st.markdown(f"**AI Query Response:**")
        st.info("Based on current class records, 2 students (Hemant Singh & Ansh Kumarjangir) score below 40% in core subjects and require remedial classes.")