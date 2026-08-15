from datetime import datetime
import io

import pandas as pd
import streamlit as st

from database.supabase import supabase


# =========================================================
# CONSTANTS
# =========================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]

SECTIONS = [
    "A",
    "B",
    "C",
    "D"
]

EXAM_TYPES = [
    "Unit Test 1",
    "Mid Term",
    "Unit Test 2",
    "Final Exam"
]

DEFAULT_SUBJECTS = [
    "Maths",
    "Science",
    "English",
    "Hindi",
    "Physics",
    "Chemistry",
    "Social Studies"
]


# =========================================================
# MASTER SUBJECTS
# =========================================================

def get_master_subjects():

    if not supabase:
        return DEFAULT_SUBJECTS

    try:

        response = (
            supabase
            .table("subjects_master")
            .select("subject_name")
            .order("subject_name")
            .execute()
        )

        if response.data:

            subjects = [
                str(item["subject_name"]).strip()
                for item in response.data
                if item.get("subject_name")
            ]

            return subjects or DEFAULT_SUBJECTS

    except Exception as e:

        st.warning(
            f"⚠️ Master Subjects fetch करने में दिक्कत: {e}"
        )

    return DEFAULT_SUBJECTS


# =========================================================
# ROLE / PERMISSION
# =========================================================

def get_exam_permissions():

    user_role = st.session_state.get(
        "user_role",
        "admin"
    )

    assigned_classes = st.session_state.get(
        "assigned_classes"
    )

    if not assigned_classes:

        single_class = st.session_state.get(
            "assigned_class"
        )

        if single_class:

            assigned_classes = [
                single_class
            ]

        else:

            assigned_classes = CLASSES

    assigned_subjects = st.session_state.get(
        "assigned_subjects"
    )

    if not assigned_subjects:

        assigned_subjects = DEFAULT_SUBJECTS

    is_teacher = user_role in [
        "class_teacher",
        "subject_teacher"
    ]

    return (
        user_role,
        assigned_classes,
        assigned_subjects,
        is_teacher
    )


# =========================================================
# SAFE NUMBER
# =========================================================

def safe_int(value, default=0):

    try:

        if pd.isna(value):
            return default

        return int(float(value))

    except Exception:

        return default


def safe_float(value, default=0.0):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except Exception:

        return default


# =========================================================
# GRADE
# =========================================================

def calculate_grade(percentage):

    percentage = safe_float(
        percentage
    )

    if percentage >= 90:
        return "A+"

    if percentage >= 80:
        return "A"

    if percentage >= 70:
        return "B+"

    if percentage >= 60:
        return "B"

    if percentage >= 50:
        return "C"

    if percentage >= 40:
        return "D"

    return "F"


# =========================================================
# PASS / FAIL
# =========================================================

def calculate_result(percentage):

    return (
        "PASS"
        if safe_float(percentage) >= 33
        else "FAIL"
    )


# =========================================================
# FETCH STUDENTS
# =========================================================

def get_students(
    selected_class,
    selected_section
):

    if not supabase:
        return []

    try:

        response = (
            supabase
            .table("students")
            .select(
                "sr_no, student_name, roll_no"
            )
            .eq(
                "class",
                selected_class
            )
            .eq(
                "section",
                selected_section
            )
            .order("roll_no")
            .execute()
        )

        return response.data or []

    except Exception as e:

        st.error(
            f"❌ Students fetch error: {e}"
        )

        return []


# =========================================================
# FETCH EXISTING MARKS
# =========================================================

def get_existing_marks(
    selected_class,
    selected_section,
    selected_subject,
    selected_exam
):

    if not supabase:
        return {}

    try:

        response = (
            supabase
            .table("marks")
            .select(
                "sr_no, student_name, class, section, "
                "subject, exam_type, marks_obtained, "
                "max_marks, entered_by"
            )
            .eq(
                "class",
                selected_class
            )
            .eq(
                "section",
                selected_section
            )
            .eq(
                "subject",
                selected_subject
            )
            .eq(
                "exam_type",
                selected_exam
            )
            .execute()
        )

        return {
            row["sr_no"]: row
            for row in (
                response.data or []
            )
        }

    except Exception as e:

        # entered_by missing होने पर भी module crash न हो
        try:

            response = (
                supabase
                .table("marks")
                .select(
                    "sr_no, student_name, class, "
                    "section, subject, exam_type, "
                    "marks_obtained, max_marks"
                )
                .eq(
                    "class",
                    selected_class
                )
                .eq(
                    "section",
                    selected_section
                )
                .eq(
                    "subject",
                    selected_subject
                )
                .eq(
                    "exam_type",
                    selected_exam
                )
                .execute()
            )

            return {
                row["sr_no"]: row
                for row in (
                    response.data or []
                )
            }

        except Exception as second_error:

            st.error(
                "❌ Existing marks fetch error: "
                f"{second_error}"
            )

            return {}


# =========================================================
# TAB 1
# MARKS ENTRY
# =========================================================

def render_marks_entry():

    st.subheader(
        "✏️ Enter / Edit Marks"
    )

    (
        user_role,
        assigned_classes,
        assigned_subjects,
        is_teacher
    ) = get_exam_permissions()

    all_subjects = get_master_subjects()

    # =====================================================
    # TEACHER INFO
    # =====================================================

    if is_teacher:

        st.info(
            "🔒 Teacher Access: "
            f"{', '.join(assigned_classes)} | "
            f"{', '.join(assigned_subjects)}"
        )

    # =====================================================
    # FILTERS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        if (
            is_teacher
            and "ALL" not in assigned_classes
        ):

            class_options = [
                c
                for c in assigned_classes
                if c in CLASSES
            ]

        else:

            class_options = CLASSES

        if not class_options:
            class_options = CLASSES

        selected_class = st.selectbox(
            "Select Class",
            class_options,
            key="ex_cls"
        )

    with c2:

        selected_section = st.selectbox(
            "Select Section",
            SECTIONS,
            key="ex_sec"
        )

    with c3:

        if (
            is_teacher
            and "ALL" not in assigned_subjects
        ):

            available_subjects = [
                s
                for s in assigned_subjects
                if s in all_subjects
            ]

            if not available_subjects:
                available_subjects = assigned_subjects

        else:

            available_subjects = all_subjects

        selected_subject = st.selectbox(
            "Select Subject",
            available_subjects,
            key="ex_sub"
        )

    with c4:

        selected_exam = st.selectbox(
            "Select Exam Type",
            EXAM_TYPES,
            key="ex_type"
        )

    # =====================================================
    # SUBJECT MASTER
    # =====================================================

    if not is_teacher:

        with st.expander(
            "➕ Add New Subject to Master List"
        ):

            sub_col1, sub_col2 = st.columns(
                [3, 1]
            )

            with sub_col1:

                new_subject = st.text_input(
                    "Enter New Subject Name",
                    key="new_subject_input",
                    placeholder="e.g. Computer Science"
                )

            with sub_col2:

                st.write("")

                st.write("")

                add_subject = st.button(
                    "Save Subject",
                    use_container_width=True,
                    key="save_new_subject"
                )

            if add_subject:

                clean_subject = (
                    new_subject.strip()
                )

                if not clean_subject:

                    st.warning(
                        "कृपया विषय का नाम लिखें।"
                    )

                elif not supabase:

                    st.error(
                        "❌ Supabase connection नहीं है."
                    )

                elif clean_subject.lower() in [
                    s.lower()
                    for s in all_subjects
                ]:

                    st.warning(
                        "⚠️ यह subject पहले से मौजूद है।"
                    )

                else:

                    try:

                        (
                            supabase
                            .table("subjects_master")
                            .insert({
                                "subject_name":
                                    clean_subject
                            })
                            .execute()
                        )

                        st.success(
                            f"✅ Subject "
                            f"'{clean_subject}' "
                            "successfully added."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Subject add error: {e}"
                        )

    st.markdown("---")

    # =====================================================
    # MAX MARKS
    # =====================================================

    max_marks_input = st.number_input(
        "Maximum Marks for this Test",
        min_value=1,
        max_value=1000,
        value=100,
        step=5,
        key="maximum_marks"
    )

    # =====================================================
    # STUDENTS
    # =====================================================

    students = get_students(
        selected_class,
        selected_section
    )

    if not students:

        st.warning(
            f"⚠️ No students found in "
            f"{selected_class} - "
            f"{selected_section}."
        )

        return

    # =====================================================
    # EXISTING MARKS
    # =====================================================

    existing_marks = get_existing_marks(
        selected_class,
        selected_section,
        selected_subject,
        selected_exam
    )

    st.markdown(
        f"### Student Marks List "
        f"({selected_subject} - {selected_exam})"
    )

    # =====================================================
    # MARKS FORM
    # =====================================================

    with st.form(
        "marks_entry_form"
    ):

        marks_payload = []

        for student in students:

            sr_no = safe_int(
                student.get("sr_no")
            )

            name = str(
                student.get(
                    "student_name",
                    "N/A"
                )
            )

            roll_no = safe_int(
                student.get(
                    "roll_no"
                )
            )

            old_data = existing_marks.get(
                sr_no,
                {}
            )

            old_marks = safe_float(
                old_data.get(
                    "marks_obtained",
                    0
                )
            )

            # Existing max marks को priority
            old_max = safe_float(
                old_data.get(
                    "max_marks",
                    max_marks_input
                )
            )

            if old_max > 0:

                current_max = old_max

            else:

                current_max = float(
                    max_marks_input
                )

            # -------------------------------------------------
            # Student row
            # -------------------------------------------------

            mc1, mc2, mc3 = st.columns(
                [1, 3, 2]
            )

            with mc1:

                st.write(
                    f"**Roll #{roll_no}**"
                )

            with mc2:

                st.write(
                    f"**{name}** "
                    f"(SR: {sr_no})"
                )

            with mc3:

                obtained_marks = st.number_input(
                    label=f"Marks for {sr_no}",
                    min_value=0.0,
                    max_value=float(
                        max_marks_input
                    ),
                    value=min(
                        old_marks,
                        float(max_marks_input)
                    ),
                    step=0.5,
                    key=(
                        f"marks_"
                        f"{sr_no}_"
                        f"{selected_subject}_"
                        f"{selected_exam}"
                    ),
                    label_visibility="collapsed"
                )

            marks_payload.append({
                "sr_no": sr_no,
                "student_name": name,
                "class": selected_class,
                "section": selected_section,
                "subject": selected_subject,
                "exam_type": selected_exam,
                "marks_obtained": obtained_marks,
                "max_marks": max_marks_input,
                "entered_by": st.session_state.get(
                    "user_email",
                    user_role
                )
            })

        st.markdown("---")

        submit_marks = st.form_submit_button(
            "💾 Save / Update Marks",
            use_container_width=True,
            type="primary"
        )

        if submit_marks:

            if not supabase:

                st.error(
                    "❌ Supabase connection नहीं है."
                )

                return

            try:

                (
                    supabase
                    .table("marks")
                    .upsert(
                        marks_payload,
                        on_conflict=(
                            "sr_no,subject,exam_type"
                        )
                    )
                    .execute()
                )

                st.success(
                    f"✅ {len(marks_payload)} "
                    "students के marks "
                    "save/update हो गए."
                )

                st.session_state[
                    "marks_saved_message"
                ] = True

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Marks save करने में विफल: {e}"
                )


# =========================================================
# SAVED MARKS MANAGEMENT
# =========================================================

def render_saved_marks_management():

    st.markdown("---")

    st.subheader(
        "🗑️ Saved Marks Management"
    )

    if not supabase:
        return

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        delete_class = st.selectbox(
            "Class",
            CLASSES,
            key="delete_marks_class"
        )

    with c2:

        delete_section = st.selectbox(
            "Section",
            SECTIONS,
            key="delete_marks_section"
        )

    with c3:

        delete_exam = st.selectbox(
            "Exam",
            EXAM_TYPES,
            key="delete_marks_exam"
        )

    with c4:

        delete_subject = st.selectbox(
            "Subject",
            get_master_subjects(),
            key="delete_marks_subject"
        )

    try:

        response = (
            supabase
            .table("marks")
            .select(
                "id, sr_no, student_name, "
                "marks_obtained, max_marks"
            )
            .eq(
                "class",
                delete_class
            )
            .eq(
                "section",
                delete_section
            )
            .eq(
                "exam_type",
                delete_exam
            )
            .eq(
                "subject",
                delete_subject
            )
            .order("sr_no")
            .execute()
        )

        saved_marks = response.data or []

    except Exception as e:

        st.error(
            f"❌ Saved marks fetch error: {e}"
        )

        return

    if not saved_marks:

        st.info(
            "📭 इस selection के लिए कोई saved marks नहीं हैं."
        )

        return

    options = {
        f"SR {row['sr_no']} - "
        f"{row.get('student_name', 'N/A')} "
        f"({row.get('marks_obtained', 0)}/"
        f"{row.get('max_marks', 0)})":
        row
        for row in saved_marks
    }

    selected_label = st.selectbox(
        "Select Student for Delete",
        list(options.keys()),
        key="delete_marks_student"
    )

    selected_record = options[
        selected_label
    ]

    d1, d2 = st.columns(2)

    with d1:

        st.info(
            f"Student: **{selected_record.get('student_name', 'N/A')}**\n\n"
            f"SR No: **{selected_record.get('sr_no')}**\n\n"
            f"Marks: **{selected_record.get('marks_obtained', 0)} / "
            f"{selected_record.get('max_marks', 0)}**"
        )

    with d2:

        delete_key = (
            f"confirm_delete_marks_"
            f"{selected_record.get('id')}"
        )

        confirm_delete = st.checkbox(
            "I confirm delete",
            key=delete_key
        )

        if st.button(
            "🗑️ Delete Selected Marks",
            type="secondary",
            use_container_width=True,
            key=f"delete_marks_btn_{selected_record.get('id')}"
        ):

            if not confirm_delete:

                st.warning(
                    "पहले 'I confirm delete' select करें."
                )

            else:

                try:

                    (
                        supabase
                        .table("marks")
                        .delete()
                        .eq(
                            "id",
                            selected_record["id"]
                        )
                        .execute()
                    )

                    st.success(
                        "✅ Selected marks deleted successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Delete failed: {e}"
                    )


# =========================================================
# EXCEL EXPORT
# =========================================================

def create_marks_excel(data):

    if not data:
        return None

    df = pd.DataFrame(data)

    preferred_columns = [
        "sr_no",
        "student_name",
        "class",
        "section",
        "subject",
        "exam_type",
        "marks_obtained",
        "max_marks"
    ]

    columns = [
        c
        for c in preferred_columns
        if c in df.columns
    ]

    df = df[columns]

    rename_map = {
        "sr_no": "SR No",
        "student_name": "Student Name",
        "class": "Class",
        "section": "Section",
        "subject": "Subject",
        "exam_type": "Exam Type",
        "marks_obtained": "Marks Obtained",
        "max_marks": "Maximum Marks"
    }

    df = df.rename(
        columns=rename_map
    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ):

        df.to_excel(
            index=False,
            sheet_name="Marks"
        )

    return output.getvalue()


# =========================================================
# EXCEL TOOLS
# =========================================================

def render_marks_excel_tools():

    st.markdown("---")

    st.subheader(
        "📥📤 Excel Tools"
    )

    if not supabase:
        return

    c1, c2 = st.columns(2)

    with c1:

        export_class = st.selectbox(
            "Export Class",
            CLASSES,
            key="marks_export_class"
        )

    with c2:

        export_section = st.selectbox(
            "Export Section",
            SECTIONS,
            key="marks_export_section"
        )

    if st.button(
        "📤 Load Marks for Excel Export",
        use_container_width=True,
        key="load_marks_excel"
    ):

        try:

            response = (
                supabase
                .table("marks")
                .select(
                    "sr_no, student_name, class, "
                    "section, subject, exam_type, "
                    "marks_obtained, max_marks"
                )
                .eq(
                    "class",
                    export_class
                )
                .eq(
                    "section",
                    export_section
                )
                .order("sr_no")
                .execute()
            )

            export_data = response.data or []

            if not export_data:

                st.warning(
                    "इस class/section के लिए marks नहीं मिले."
                )

            else:

                excel_bytes = create_marks_excel(
                    export_data
                )

                st.download_button(
                    "📥 Download Marks Excel",
                    data=excel_bytes,
                    file_name=(
                        f"marks_"
                        f"{export_class.replace(' ', '_')}_"
                        f"{export_section}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                    key="download_marks_excel"
                )

                st.dataframe(
                    pd.DataFrame(
                        export_data
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:

            st.error(
                f"❌ Excel export error: {e}"
            )


# =========================================================
# FETCH REPORT MARKS
# =========================================================

def fetch_report_marks(
    selected_class,
    selected_section,
    selected_exam,
    selected_subject=None
):

    if not supabase:
        return []

    try:

        query = (
            supabase
            .table("marks")
            .select(
                "sr_no, student_name, class, "
                "section, subject, exam_type, "
                "marks_obtained, max_marks"
            )
            .eq(
                "class",
                selected_class
            )
            .eq(
                "section",
                selected_section
            )
            .eq(
                "exam_type",
                selected_exam
            )
        )

        if selected_subject:
            query = query.eq(
                "subject",
                selected_subject
            )

        response = query.execute()

        return response.data or []

    except Exception as e:

        st.error(
            f"❌ Report data fetch error: {e}"
        )

        return []


# =========================================================
# REPORT CARD
# =========================================================

def render_report_card(
    student_name,
    sr_no,
    class_name,
    section,
    exam_type,
    student_marks
):

    if not student_marks:
        return

    total_obtained = sum(
        safe_float(
            x.get("marks_obtained")
        )
        for x in student_marks
    )

    total_max = sum(
        safe_float(
            x.get("max_marks")
        )
        for x in student_marks
    )

    percentage = (
        (total_obtained / total_max) * 100
        if total_max > 0
        else 0
    )

    grade = calculate_grade(
        percentage
    )

    result = calculate_result(
        percentage
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div style="
            border:2px solid #1e3a8a;
            border-radius:12px;
            padding:20px;
            background:white;
        ">

        <div style="
            text-align:center;
            border-bottom:2px solid #1e3a8a;
            padding-bottom:12px;
        ">

            <h1 style="margin:0;color:#1e3a8a;">
                🏫 CAMPUS ERP PRO
            </h1>

            <h3 style="margin:8px 0;">
                STUDENT REPORT CARD
            </h3>

            <p style="margin:0;">
                {exam_type}
            </p>

        </div>

        <br>

        <table style="width:100%;border-collapse:collapse;">

            <tr>
                <td style="padding:8px;">
                    <b>Student Name:</b>
                    {student_name}
                </td>

                <td style="padding:8px;">
                    <b>SR No:</b>
                    {sr_no}
                </td>
            </tr>

            <tr>
                <td style="padding:8px;">
                    <b>Class:</b>
                    {class_name}
                </td>

                <td style="padding:8px;">
                    <b>Section:</b>
                    {section}
                </td>
            </tr>

        </table>

        </div>
        """,
        unsafe_allow_html=True
    )

    report_rows = []

    for row in student_marks:

        obtained = safe_float(
            row.get("marks_obtained")
        )

        maximum = safe_float(
            row.get("max_marks")
        )

        subject_percentage = (
            obtained / maximum * 100
            if maximum > 0
            else 0
        )

        report_rows.append({
            "Subject":
                row.get("subject", ""),
            "Marks Obtained":
                obtained,
            "Maximum Marks":
                maximum,
            "Percentage":
                round(
                    subject_percentage,
                    2
                ),
            "Grade":
                calculate_grade(
                    subject_percentage
                )
        })

    report_df = pd.DataFrame(
        report_rows
    )

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.metric(
            "Total Marks",
            f"{total_obtained:g} / {total_max:g}"
        )

    with m2:

        st.metric(
            "Percentage",
            f"{percentage:.2f}%"
        )

    with m3:

        st.metric(
            "Grade",
            grade
        )

    with m4:

        st.metric(
            "Result",
            result
        )


# =========================================================
# TAB 2
# CLASS PERFORMANCE & REPORT CARD
# =========================================================

def render_performance_report():

    st.subheader(
        "📊 Class Performance & Report Card"
    )

    (
        user_role,
        assigned_classes,
        assigned_subjects,
        is_teacher
    ) = get_exam_permissions()

    all_subjects = get_master_subjects()

    if (
        is_teacher
        and "ALL" not in assigned_classes
    ):

        report_classes = [
            c
            for c in assigned_classes
            if c in CLASSES
        ]

    else:

        report_classes = CLASSES

    if not report_classes:
        report_classes = CLASSES

    if (
        is_teacher
        and "ALL" not in assigned_subjects
    ):

        report_subjects = [
            s
            for s in assigned_subjects
        ]

    else:

        report_subjects = all_subjects

    rc1, rc2, rc3, rc4 = st.columns(4)

    with rc1:

        report_class = st.selectbox(
            "Select Class",
            report_classes,
            key="rep_ex_cls"
        )

    with rc2:

        report_section = st.selectbox(
            "Select Section",
            SECTIONS,
            key="rep_ex_sec"
        )

    with rc3:

        report_exam = st.selectbox(
            "Select Exam",
            EXAM_TYPES,
            key="rep_ex_type"
        )

    with rc4:

        subject_options = [
            "ALL"
        ] + report_subjects

        report_subject = st.selectbox(
            "Select Subject Filter",
            subject_options,
            key="rep_ex_sub"
        )

    marks_data = fetch_report_marks(
        report_class,
        report_section,
        report_exam,
        None
        if report_subject == "ALL"
        else report_subject
    )

    if not marks_data:

        st.warning(
            "चुनी गई Class, Section और Exam के लिए "
            "कोई marks data उपलब्ध नहीं है."
        )

        return

    df = pd.DataFrame(
        marks_data
    )

    # =====================================================
    # CLASS SUMMARY
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 📈 Class Performance"
    )

    total_obtained = df[
        "marks_obtained"
    ].apply(
        safe_float
    ).sum()

    total_max = df[
        "max_marks"
    ].apply(
        safe_float
    ).sum()

    class_percentage = (
        total_obtained /
        total_max *
        100
        if total_max > 0
        else 0
    )

    student_count = df[
        "sr_no"
    ].nunique()

    subject_count = df[
        "subject"
    ].nunique()

    avg_percentage = (
        df.assign(
            pct=df.apply(
                lambda x:
                (
                    safe_float(
                        x["marks_obtained"]
                    )
                    /
                    safe_float(
                        x["max_marks"]
                    )
                    *
                    100
                )
                if safe_float(
                    x["max_marks"]
                ) > 0
                else 0,
                axis=1
            )
        )["pct"].mean()
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:

        st.metric(
            "👨‍🎓 Students",
            student_count
        )

    with p2:

        st.metric(
            "📚 Subjects",
            subject_count
        )

    with p3:

        st.metric(
            "📊 Average",
            f"{avg_percentage:.2f}%"
        )

    with p4:

        st.metric(
            "🏫 Class Performance",
            f"{class_percentage:.2f}%"
        )

    # =====================================================
    # SUBJECT-WISE SUMMARY
    # =====================================================

    st.markdown(
        "### 📚 Subject-wise Performance"
    )

    subject_summary = []

    for subject, group in df.groupby(
        "subject"
    ):

        obtained = group[
            "marks_obtained"
        ].apply(
            safe_float
        ).sum()

        maximum = group[
            "max_marks"
        ].apply(
            safe_float
        ).sum()

        percentage = (
            obtained /
            maximum *
            100
            if maximum > 0
            else 0
        )

        subject_summary.append({
            "Subject": subject,
            "Marks Obtained":
                round(obtained, 2),
            "Maximum Marks":
                round(maximum, 2),
            "Percentage":
                round(
                    percentage,
                    2
                ),
            "Grade":
                calculate_grade(
                    percentage
                )
        })

    subject_df = pd.DataFrame(
        subject_summary
    )

    st.dataframe(
        subject_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # STUDENT SUMMARY
    # =====================================================

    st.markdown(
        "### 🏆 Student-wise Result"
    )

    student_summary = []

    for sr_no, group in df.groupby(
        "sr_no"
    ):

        name = str(
            group.iloc[0].get(
                "student_name",
                "N/A"
            )
        )

        obtained = group[
            "marks_obtained"
        ].apply(
            safe_float
        ).sum()

        maximum = group[
            "max_marks"
        ].apply(
            safe_float
        ).sum()

        percentage = (
            obtained /
            maximum *
            100
            if maximum > 0
            else 0
        )

        student_summary.append({
            "SR No":
                sr_no,
            "Student Name":
                name,
            "Total Marks":
                round(
                    obtained,
                    2
                ),
            "Maximum Marks":
                round(
                    maximum,
                    2
                ),
            "Percentage":
                round(
                    percentage,
                    2
                ),
            "Grade":
                calculate_grade(
                    percentage
                ),
            "Result":
                calculate_result(
                    percentage
                )
        })

    summary_df = pd.DataFrame(
        student_summary
    )

    summary_df = summary_df.sort_values(
        by="Percentage",
        ascending=False
    ).reset_index(
        drop=True
    )

    summary_df.insert(
        0,
        "Rank",
        range(
            1,
            len(summary_df) + 1
        )
    )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # EXCEL DOWNLOAD
    # =====================================================

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            index=False,
            sheet_name="Student Result"
        )

        subject_df.to_excel(
            writer,
            index=False,
            sheet_name="Subject Summary"
        )

    st.download_button(
        "📥 Download Class Result Excel",
        data=output.getvalue(),
        file_name=(
            f"{report_class}_"
            f"{report_section}_"
            f"{report_exam}_Result.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
        key="download_class_result_excel"
    )

    # =====================================================
    # INDIVIDUAL REPORT CARD
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 🎓 Individual Student Report Card"
    )

    student_options = {
        f"SR {row['SR No']} - "
        f"{row['Student Name']}":
        row["SR No"]
        for _, row in summary_df.iterrows()
    }

    if student_options:

        selected_student_label = st.selectbox(
            "Select Student",
            list(
                student_options.keys()
            ),
            key="report_student_select"
        )

        selected_sr = student_options[
            selected_student_label
        ]

        student_data = df[
            df["sr_no"] == selected_sr
        ]

        if not student_data.empty:

            student_name = str(
                student_data.iloc[0].get(
                    "student_name",
                    "N/A"
                )
            )

            render_report_card(
                student_name,
                selected_sr,
                report_class,
                report_section,
                report_exam,
                student_data.to_dict(
                    "records"
                )
            )


# =========================================================
# MAIN EXAMS MODULE
# =========================================================

def render_exams_module():

    st.markdown(
        "## 📝 Exam Management & Marks Entry"
    )

    tab1, tab2 = st.tabs([
        "✏️ Enter / Edit Marks",
        "📊 Class Performance & Report Card"
    ])

    # =====================================================
    # TAB 1
    # =====================================================

    with tab1:

        render_marks_entry()

        render_saved_marks_management()

        render_marks_excel_tools()

    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        render_performance_report()
