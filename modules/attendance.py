from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from database.supabase import supabase

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]
STATUS_OPTIONS = ["Present", "Absent", "Late", "Leave"]

def render_attendance_module():
    st.markdown("## 📅 Daily Class Attendance & Monthly Analytics")
    
    # -------------------------------------------------------------
    # 🔒 ROLE & PERMISSION CHECKING (Session State)
    # -------------------------------------------------------------
    user_role = st.session_state.get('user_role', 'admin')
    assigned_class = st.session_state.get('assigned_class', 'Class 10-A')
    
    # Check if user is restricted to a single assigned class
    is_teacher_restricted = (user_role in ["class_teacher", "subject_teacher"]) and (assigned_class != "ALL")
    
    if is_teacher_restricted:
        st.info(f"🔒 **Teacher Access:** आपकी असाइन की गई क्लास **{assigned_class}** है।")

    tab1, tab2, tab3 = st.tabs([
        "📝 Daily Attendance Entry", 
        "📊 Monthly Analytics & Report", 
        "🔍 Student Attendance History"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: DAILY ATTENDANCE MARKING
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Mark Daily Attendance")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            att_date = st.date_input("Attendance Date", value=datetime.today())
            
        with c2:
            # 🔒 Role-based Class Selection
            if is_teacher_restricted:
                # Assign default class and disable selectbox
                default_cls_index = CLASSES.index(assigned_class) if assigned_class in CLASSES else 0
                selected_class = st.selectbox("Select Class", CLASSES, index=default_cls_index, disabled=True, key="att_cls")
            else:
                selected_class = st.selectbox("Select Class", CLASSES, key="att_cls")
                
        with c3:
            selected_sec = st.selectbox("Select Section", SECTIONS, key="att_sec")
            
        if supabase:
            try:
                # Fetch Students for selected Class and Section
                res = supabase.table("students") \
                    .select("sr_no, student_name, roll_no, gender") \
                    .eq("class", selected_class) \
                    .eq("section", selected_sec) \
                    .order("roll_no") \
                    .execute()
                
                students = res.data or []
                
                if not students:
                    st.warning(f"⚠️ No students found in {selected_class} - {selected_sec}.")
                else:
                    st.info(f"📋 Total Students in {selected_class} ({selected_sec}): **{len(students)}**")
                    
                    # Bulk Action Button
                    col_btn1, col_btn2 = st.columns([1, 4])
                    bulk_present = col_btn1.button("✅ Mark All Present")
                    
                    # Fetch Existing Attendance for this date if already marked
                    existing_att = supabase.table("attendance") \
                        .select("sr_no, status") \
                        .eq("date", str(att_date)) \
                        .eq("class", selected_class) \
                        .eq("section", selected_sec) \
                        .execute()
                    
                    existing_map = {item['sr_no']: item['status'] for item in (existing_att.data or [])}
                    
                    # Form to submit attendance
                    with st.form("attendance_marking_form"):
                        attendance_payload = []
                        
                        st.write("---")
                        st.markdown("**Student List:**")
                        
                        for index, st_data in enumerate(students):
                            sr = st_data["sr_no"]
                            name = st_data.get("student_name", "N/A")
                            roll = st_data.get("roll_no", 0)
                            
                            # Set default status based on existing data or bulk action
                            default_status = existing_map.get(sr, "Present" if bulk_present else "Present")
                            default_index = STATUS_OPTIONS.index(default_status) if default_status in STATUS_OPTIONS else 0
                            
                            sc1, sc2, sc3 = st.columns([1, 3, 2])
                            sc1.write(f"**Roll #{roll}**")
                            sc2.write(f"**{name}** (SR: {sr})")
                            
                            status = sc3.radio(
                                label=f"Status for {sr}",
                                options=STATUS_OPTIONS,
                                index=default_index,
                                horizontal=True,
                                key=f"att_radio_{sr}",
                                label_visibility="collapsed"
                            )
                            
                            # Payload containing student_name to prevent NOT NULL constraint error
                            attendance_payload.append({
                                "date": str(att_date),
                                "sr_no": sr,
                                "student_name": name,
                                "class": selected_class,
                                "section": selected_sec,
                                "status": status,
                                "marked_by": st.session_state.get('user_email', 'Teacher')
                            })
                        
                        submit_att = st.form_submit_button("💾 Save / Update Attendance")
                        
                        if submit_att:
                            try:
                                # Upsert operation to save or overwrite
                                supabase.table("attendance").upsert(
                                    attendance_payload, 
                                    on_conflict="date, sr_no"
                                ).execute()
                                st.success(f"✅ Attendance saved successfully for {len(attendance_payload)} students on {att_date}!")
                            except Exception as e:
                                st.error(f"❌ Failed to save attendance: {e}")
            except Exception as ex:
                st.error(f"Database error: {ex}")

    # -------------------------------------------------------------
    # TAB 2: MONTHLY ANALYTICS & REPORTS
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Monthly Class Analytics")
        
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            sel_month = st.selectbox("Select Month", range(1, 13), index=datetime.now().month - 1)
        with ac2:
            sel_year = st.number_input("Select Year", min_value=2024, max_value=2030, value=datetime.now().year)
        with ac3:
            # 🔒 Role-based Class Selection for Analytics
            if is_teacher_restricted:
                default_rep_index = CLASSES.index(assigned_class) if assigned_class in CLASSES else 0
                rep_class = st.selectbox("Select Class for Report", CLASSES, index=default_rep_index, disabled=True, key="rep_cls")
            else:
                rep_class = st.selectbox("Select Class for Report", CLASSES, key="rep_cls")
            
        if supabase:
            start_date = f"{sel_year}-{sel_month:02d}-01"
            end_date = f"{sel_year}-{sel_month:02d}-31"
            
            try:
                res = supabase.table("attendance") \
                    .select("date, sr_no, status, class, section, student_name, students(gender)") \
                    .eq("class", rep_class) \
                    .gte("date", start_date) \
                    .lte("date", end_date) \
                    .execute()
                    
                att_records = res.data or []
                
                if not att_records:
                    st.warning(f"No attendance data found for {rep_class} in the selected month.")
                else:
                    df = pd.DataFrame(att_records)
                    
                    # Fallback for student name and gender
                    if 'student_name' not in df.columns:
                        df['student_name'] = df['students'].apply(lambda x: x.get('student_name') if x else 'N/A')
                    df['gender'] = df['students'].apply(lambda x: x.get('gender') if x else 'N/A')
                    
                    # Overall Summary Metrics
                    total_entries = len(df)
                    p_count = len(df[df['status'] == 'Present'])
                    a_count = len(df[df['status'] == 'Absent'])
                    l_count = len(df[df['status'] == 'Leave'])
                    p_pct = (p_count / total_entries * 100) if total_entries > 0 else 0
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Overall Attendance Rate", f"{p_pct:.1f}%")
                    m2.metric("Total Presents", p_count)
                    m3.metric("Total Absents", a_count)
                    m4.metric("Leaves/Late", l_count)
                    
                    st.write("---")
                    
                    # Visual Charts
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        st.markdown("##### Attendance Distribution")
                        fig_pie = px.pie(
                            df, names="status", 
                            color="status",
                            color_discrete_map={"Present": "#2ecc71", "Absent": "#e74c3c", "Late": "#f39c12", "Leave": "#3498db"}
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                    with chart_col2:
                        st.markdown("##### Gender-wise Attendance Breakdown")
                        fig_bar = px.histogram(
                            df, x="status", color="gender", barmode="group",
                            title="Present/Absent Count by Gender"
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                    st.write("---")
                    st.markdown("##### Monthly Student Summary Table")
                    
                    # Pivot Table for Monthly Attendance Sheet
                    summary_df = df.groupby(['sr_no', 'student_name', 'status']).size().unstack(fill_value=0)
                    if 'Present' not in summary_df.columns: summary_df['Present'] = 0
                    if 'Absent' not in summary_df.columns: summary_df['Absent'] = 0
                    
                    summary_df['Total Days'] = summary_df.sum(axis=1)
                    summary_df['Attendance %'] = ((summary_df['Present'] / summary_df['Total Days']) * 100).round(1)
                    
                    st.dataframe(summary_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching report data: {e}")

    # -------------------------------------------------------------
    # TAB 3: INDIVIDUAL STUDENT SEARCH
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Student Individual Attendance Search")
        st_sr = st.number_input("Enter Student SR Number", min_value=1, step=1)
        
        if st.button("🔍 Get Attendance History"):
            if supabase:
                try:
                    history_res = supabase.table("attendance") \
                        .select("date, class, section, status, marked_by") \
                        .eq("sr_no", st_sr) \
                        .order("date", desc=True) \
                        .execute()
                        
                    history_data = history_res.data or []
                    
                    if history_data:
                        hdf = pd.DataFrame(history_data)
                        st.success(f"Record found for SR Number: {st_sr}")
                        st.dataframe(hdf, use_container_width=True)
                    else:
                        st.warning("No attendance records found for this SR Number.")
                except Exception as e:
                    st.error(f"Error retrieving history: {e}")
