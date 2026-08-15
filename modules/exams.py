# =========================================================
# CAMPUS ERP PRO
# EXAM MANAGEMENT & MARKS
# =========================================================

import io
import html
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
# SAFE FLOAT
# =========================================================

def safe_float(value):

    try:

        if value is None:
            return 0.0

        if pd.isna(value):
            return 0.0

        return float(value)

    except Exception:

        return 0.0


# =========================================================
# SAFE HTML
# =========================================================

def safe_html(value):

    return html.escape(
        str(value)
        if value is not None
        else ""
    )


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

    return "E"


# =========================================================
# RESULT
# =========================================================

def calculate_result(percentage):

    percentage = safe_float(
        percentage
    )

    return (
        "PASS"
        if percentage >= 33
        else "FAIL"
    )


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
                str(item.get("subject_name"))
                for item in response.data
                if item.get("subject_name")
            ]

            if subjects:
                return subjects

    except Exception as e:

        st.warning(
            f"⚠️ Master Subjects fetch करने में दिक्कत: {e}"
        )

    return DEFAULT_SUBJECTS


# =========================================================
# EXAM PERMISSIONS
# =========================================================

def get_exam_permissions():

    user_role = st.session_state.get(
        "user_role",
        "admin"
    )

    assigned_classes = (
        st.session_state.get(
            "assigned_classes"
        )
    )

    if not assigned_classes:

        single_class = (
            st.session_state.get(
                "assigned_class",
                "Class 10"
            )
        )

        assigned_classes = (
            [single_class]
            if single_class
            else CLASSES
        )

    assigned_subjects = (
        st.session_state.get(
            "assigned_subjects",
            ["Maths", "Science"]
        )
    )

    if not assigned_subjects:

        assigned_subjects = [
            "ALL"
        ]

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
# FETCH STUDENTS
# =========================================================

def fetch_students(
    class_name,
    section
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
                class_name
            )
            .eq(
                "section",
                section
            )
            .order(
                "roll_no"
            )
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

def fetch_existing_marks(
    class_name,
    section,
    subject,
    exam_type
):

    if not supabase:
        return {}

    try:

        response = (
            supabase
            .table("marks")
            .select(
                "sr_no, student_name, "
                "class, section, exam_type, "
                "subject, marks_obtained, "
                "max_marks, entered_by, "
                "updated_by, updated_at"
            )
            .eq(
                "class",
                class_name
            )
            .eq(
                "section",
                section
            )
            .eq(
                "subject",
                subject
            )
            .eq(
                "exam_type",
                exam_type
            )
            .execute()
        )

        data = response.data or []

        return {
            int(row["sr_no"]): row
            for row in data
            if row.get("sr_no") is not None
        }

    except Exception:

        try:

            response = (
                supabase
                .table("marks")
                .select(
                    "sr_no, student_name, "
                    "class, section, exam_type, "
                    "subject, marks_obtained, max_marks"
                )
                .eq(
                    "class",
                    class_name
                )
                .eq(
                    "section",
                    section
                )
                .eq(
                    "subject",
                    subject
                )
                .eq(
                    "exam_type",
                    exam_type
                )
                .execute()
            )

            data = response.data or []

            return {
                int(row["sr_no"]): row
                for row in data
                if row.get("sr_no") is not None
            }

        except Exception as retry_error:

            st.error(
                "❌ Existing marks fetch error: "
                f"{retry_error}"
            )

            return {}


# =========================================================
# FETCH REPORT MARKS
# =========================================================

def fetch_report_marks(
    class_name,
    section,
    exam_type,
    subject=None
):

    if not supabase:
        return []

    try:

        query = (
            supabase
            .table("marks")
            .select(
                "sr_no, student_name, "
                "class, section, exam_type, "
                "subject, marks_obtained, "
                "max_marks"
            )
            .eq(
                "class",
                class_name
            )
            .eq(
                "section",
                section
            )
            .eq(
                "exam_type",
                exam_type
            )
        )

        if subject:

            query = query.eq(
                "subject",
                subject
            )

        response = query.execute()

        return response.data or []

    except Exception as e:

        st.error(
            f"❌ Report data fetch error: {e}"
        )

        return []


# =========================================================
# CHECK DUPLICATE MARKS
# =========================================================

def check_existing_mark(
    sr_no,
    subject,
    exam_type
):

    if not supabase:
        return None

    try:

        response = (
            supabase
            .table("marks")
            .select("id, sr_no")
            .eq(
                "sr_no",
                int(sr_no)
            )
            .eq(
                "subject",
                subject
            )
            .eq(
                "exam_type",
                exam_type
            )
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception:

        pass

    return None


# =========================================================
# DELETE SINGLE MARK
# =========================================================

def delete_mark_record(
    sr_no,
    subject,
    exam_type
):

    if not supabase:
        return False

    try:

        (
            supabase
            .table("marks")
            .delete()
            .eq(
                "sr_no",
                int(sr_no)
            )
            .eq(
                "subject",
                subject
            )
            .eq(
                "exam_type",
                exam_type
            )
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"❌ Delete failed: {e}"
        )

        return False


# =========================================================
# TAB 1
# ENTER / EDIT MARKS
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
    # TEACHER INFORMATION
    # =====================================================

    if is_teacher:

        class_text = (
            ", ".join(
                assigned_classes
            )
        )

        subject_text = (
            ", ".join(
                assigned_subjects
            )
        )

        st.info(
            f"🔒 **Teacher Access:** "
            f"Classes: **{class_text}** | "
            f"Subjects: **{subject_text}**"
        )

    # =====================================================
    # FILTERS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        if (
            is_teacher
            and "ALL"
            not in assigned_classes
        ):

            available_classes = [
                c
                for c in assigned_classes
                if c in CLASSES
            ]

            if not available_classes:
                available_classes = CLASSES

        else:

            available_classes = CLASSES

        selected_class = st.selectbox(
            "Select Class",
            available_classes,
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
            and "ALL"
            not in assigned_subjects
        ):

            available_subjects = [
                s
                for s in assigned_subjects
                if s
            ]

            if not available_subjects:
                available_subjects = all_subjects

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
                    key="new_subject_name",
                    placeholder="e.g. Computer Science"
                )

            with sub_col2:

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
                        "कृपया subject name लिखें।"
                    )

                elif not supabase:

                    st.error(
                        "❌ Supabase connection नहीं है."
                    )

                else:

                    try:

                        existing = (
                            supabase
                            .table("subjects_master")
                            .select("subject_name")
                            .eq(
                                "subject_name",
                                clean_subject
                            )
                            .execute()
                        )

                        if existing.data:

                            st.warning(
                                "⚠️ यह subject पहले से मौजूद है।"
                            )

                        else:

                            (
                                supabase
                                .table("subjects_master")
                                .insert(
                                    {
                                        "subject_name":
                                            clean_subject
                                    }
                                )
                                .execute()
                            )

                            st.success(
                                f"✅ Subject "
                                f"**{clean_subject}** "
                                "successfully added."
                            )

                            st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Subject add error: {e}"
                        )

    st.markdown("---")

    # =====================================================
    # STUDENTS
    # =====================================================

    students = fetch_students(
        selected_class,
        selected_section
    )

    if not students:

        st.warning(
            f"⚠️ {selected_class} - "
            f"{selected_section} में "
            "कोई student नहीं मिला."
        )

        return

    # =====================================================
    # EXISTING MARKS
    # =====================================================

    existing_marks = fetch_existing_marks(
        selected_class,
        selected_section,
        selected_subject,
        selected_exam
    )

    # =====================================================
    # MAX MARKS
    # =====================================================

    existing_max_values = [
        safe_float(
            row.get("max_marks")
        )
        for row in existing_marks.values()
        if safe_float(
            row.get("max_marks")
        ) > 0
    ]

    default_max = (
        existing_max_values[0]
        if existing_max_values
        else 100
    )

    max_marks = st.number_input(
        "Maximum Marks for this Test",
        min_value=1.0,
        max_value=1000.0,
        value=float(default_max),
        step=1.0,
        key="maximum_marks_input"
    )

    st.markdown(
        f"### 👨‍🎓 Student Marks List "
        f"({selected_subject} - {selected_exam})"
    )

    # =====================================================
    # MARKS FORM
    # =====================================================

    with st.form(
        key=(
            f"marks_entry_"
            f"{selected_class}_"
            f"{selected_section}_"
            f"{selected_subject}_"
            f"{selected_exam}"
        )
    ):

        marks_payload = []

        for student in students:

            sr_no = int(
                student.get(
                    "sr_no",
                    0
                )
            )

            student_name = str(
                student.get(
                    "student_name",
                    "N/A"
                )
            )

            roll_no = student.get(
                "roll_no",
                0
            ) or 0

            previous = existing_marks.get(
                sr_no,
                {}
            )

            previous_marks = safe_float(
                previous.get(
                    "marks_obtained",
                    0
                )
            )

            previous_max = safe_float(
                previous.get(
                    "max_marks",
                    max_marks
                )
            )

            if previous_max <= 0:
                previous_max = max_marks

            if previous_marks > max_marks:
                previous_marks = max_marks

            mc1, mc2, mc3 = st.columns(
                [1, 4, 2]
            )

            with mc1:

                st.markdown(
                    f"**Roll #{roll_no}**"
                )

            with mc2:

                st.markdown(
                    f"**{student_name}**  \n"
                    f"SR No: `{sr_no}`"
                )

            with mc3:

                obtained = st.number_input(
                    f"Marks for {sr_no}",
                    min_value=0.0,
                    max_value=float(
                        max_marks
                    ),
                    value=float(
                        previous_marks
                    ),
                    step=0.5,
                    key=(
                        f"mark_"
                        f"{selected_class}_"
                        f"{selected_section}_"
                        f"{selected_subject}_"
                        f"{selected_exam}_"
                        f"{sr_no}"
                    ),
                    label_visibility="collapsed"
                )

            marks_payload.append(
                {
                    "sr_no": sr_no,
                    "student_name":
                        student_name,
                    "class":
                        selected_class,
                    "section":
                        selected_section,
                    "exam_type":
                        selected_exam,
                    "subject":
                        selected_subject,
                    "marks_obtained":
                        float(obtained),
                    "max_marks":
                        float(max_marks)
                }
            )

        submitted = st.form_submit_button(
            "💾 Save / Update All Marks",
            use_container_width=True,
            type="primary"
        )

        if submitted:

            if not supabase:

                st.error(
                    "❌ Supabase connection नहीं है."
                )

                return

            success_count = 0
            error_count = 0
            errors = []

            current_user = st.session_state.get(
                "user_email",
                st.session_state.get(
                    "username",
                    "Admin"
                )
            )

            for record in marks_payload:

                try:

                    existing = check_existing_mark(
                        record["sr_no"],
                        record["subject"],
                        record["exam_type"]
                    )

                    # =================================================
                    # UPDATE
                    # =================================================

                    if existing:

                        update_data = {
                            "student_name":
                                record["student_name"],
                            "class":
                                record["class"],
                            "section":
                                record["section"],
                            "marks_obtained":
                                record["marks_obtained"],
                            "max_marks":
                                record["max_marks"],
                            "updated_by":
                                current_user,
                            "updated_at":
                                datetime.utcnow().isoformat()
                        }

                        try:

                            (
                                supabase
                                .table("marks")
                                .update(update_data)
                                .eq(
                                    "id",
                                    existing["id"]
                                )
                                .execute()
                            )

                        except Exception:

                            fallback_data = {
                                "student_name":
                                    record["student_name"],
                                "class":
                                    record["class"],
                                "section":
                                    record["section"],
                                "marks_obtained":
                                    record["marks_obtained"],
                                "max_marks":
                                    record["max_marks"]
                            }

                            (
                                supabase
                                .table("marks")
                                .update(
                                    fallback_data
                                )
                                .eq(
                                    "id",
                                    existing["id"]
                                )
                                .execute()
                            )

                    # =================================================
                    # INSERT
                    # =================================================

                    else:

                        insert_data = {
                            "sr_no":
                                record["sr_no"],
                            "student_name":
                                record["student_name"],
                            "class":
                                record["class"],
                            "section":
                                record["section"],
                            "exam_type":
                                record["exam_type"],
                            "subject":
                                record["subject"],
                            "marks_obtained":
                                record["marks_obtained"],
                            "max_marks":
                                record["max_marks"],
                            "entered_by":
                                current_user
                        }

                        try:

                            (
                                supabase
                                .table("marks")
                                .insert(
                                    insert_data
                                )
                                .execute()
                            )

                        except Exception:

                            fallback_data = {
                                "sr_no":
                                    record["sr_no"],
                                "student_name":
                                    record["student_name"],
                                "class":
                                    record["class"],
                                "section":
                                    record["section"],
                                "exam_type":
                                    record["exam_type"],
                                "subject":
                                    record["subject"],
                                "marks_obtained":
                                    record["marks_obtained"],
                                "max_marks":
                                    record["max_marks"]
                            }

                            (
                                supabase
                                .table("marks")
                                .insert(
                                    fallback_data
                                )
                                .execute()
                            )

                    success_count += 1

                except Exception as e:

                    error_count += 1

                    errors.append(
                        f"SR {record['sr_no']}: {e}"
                    )

            # =====================================================
            # RESULT
            # =====================================================

            if success_count:

                st.success(
                    f"✅ {success_count} students "
                    "के marks save/update हो गए."
                )

            if error_count:

                st.error(
                    f"❌ {error_count} records में error आया."
                )

                with st.expander(
                    "Error Details"
                ):

                    for error in errors:

                        st.write(
                            f"- {error}"
                        )

            if success_count:

                st.rerun()

    # =====================================================
    # SAVED MARKS MANAGEMENT
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 🗑️ Saved Marks Management"
    )

    saved_marks = fetch_report_marks(
        selected_class,
        selected_section,
        selected_exam,
        selected_subject
    )

    if saved_marks:

        delete_options = {
            (
                f"SR {row.get('sr_no')} - "
                f"{row.get('student_name', 'N/A')} "
                f"— {safe_float(row.get('marks_obtained')):g}/"
                f"{safe_float(row.get('max_marks')):g}"
            ):
            row.get("sr_no")
            for row in saved_marks
        }

        selected_delete_label = st.selectbox(
            "Select Student for Delete",
            list(
                delete_options.keys()
            ),
            key=(
                f"delete_mark_student_"
                f"{selected_class}_"
                f"{selected_section}_"
                f"{selected_subject}_"
                f"{selected_exam}"
            )
        )

        delete_sr = delete_options[
            selected_delete_label
        ]

        confirm_delete_key = (
            f"confirm_delete_"
            f"{selected_class}_"
            f"{selected_section}_"
            f"{selected_subject}_"
            f"{selected_exam}_"
            f"{delete_sr}"
        )

        if not st.session_state.get(
            confirm_delete_key,
            False
        ):

            if st.button(
                "🗑️ Delete Selected Marks",
                type="secondary",
                use_container_width=True,
                key=(
                    f"delete_btn_"
                    f"{selected_class}_"
                    f"{selected_section}_"
                    f"{selected_subject}_"
                    f"{selected_exam}_"
                    f"{delete_sr}"
                )
            ):

                st.session_state[
                    confirm_delete_key
                ] = True

                st.rerun()

        else:

            st.warning(
                f"⚠️ क्या आप वास्तव में "
                f"**{selected_delete_label}** "
                "के marks delete करना चाहते हैं?"
            )

            dc1, dc2 = st.columns(2)

            with dc1:

                if st.button(
                    "✅ Yes, Delete",
                    type="primary",
                    use_container_width=True,
                    key=(
                        f"confirm_yes_"
                        f"{delete_sr}"
                    )
                ):

                    if delete_mark_record(
                        delete_sr,
                        selected_subject,
                        selected_exam
                    ):

                        st.success(
                            "✅ Marks deleted successfully."
                        )

                        st.session_state[
                            confirm_delete_key
                        ] = False

                        st.rerun()

            with dc2:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True,
                    key=(
                        f"confirm_no_"
                        f"{delete_sr}"
                    )
                ):

                    st.session_state[
                        confirm_delete_key
                    ] = False

                    st.rerun()

    else:

        st.info(
            "इस Subject और Exam के लिए अभी "
            "कोई saved marks नहीं हैं."
        )


# =========================================================
# BUILD REPORT DATA
# =========================================================

def build_report_data(student_marks):

    report_rows = []

    for row in student_marks:

        obtained = safe_float(
            row.get("marks_obtained")
        )

        maximum = safe_float(
            row.get("max_marks")
        )

        subject_percentage = (
            obtained /
            maximum *
            100
            if maximum > 0
            else 0
        )

        report_rows.append(
            {
                "Subject":
                    str(
                        row.get(
                            "subject",
                            ""
                        )
                    ),
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
            }
        )

    return report_rows


# =========================================================
# GENERATE PDF
# =========================================================

def generate_report_card_pdf(
    student_name,
    sr_no,
    class_name,
    section,
    exam_type,
    report_rows,
    total_obtained,
    total_max,
    percentage,
    grade,
    result
):

    try:

        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle
        )
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )

    except ImportError:

        return None

    output = io.BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    school_style = ParagraphStyle(
        "SchoolTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=5
    )

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=13,
        leading=17,
        spaceAfter=4
    )

    exam_style = ParagraphStyle(
        "ExamTitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14
    )

    normal_style = ParagraphStyle(
        "NormalReport",
        parent=styles["Normal"],
        fontSize=9,
        leading=12
    )

    story = []

    story.append(
        Paragraph(
            "CAMPUS ERP PRO",
            school_style
        )
    )

    story.append(
        Paragraph(
            "STUDENT REPORT CARD",
            title_style
        )
    )

    story.append(
        Paragraph(
            safe_html(exam_type),
            exam_style
        )
    )

    story.append(
        Spacer(1, 8)
    )

    student_info = [
        [
            Paragraph(
                "<b>Student Name</b>",
                normal_style
            ),
            Paragraph(
                safe_html(student_name),
                normal_style
            ),
            Paragraph(
                "<b>SR No</b>",
                normal_style
            ),
            Paragraph(
                safe_html(sr_no),
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Class</b>",
                normal_style
            ),
            Paragraph(
                safe_html(class_name),
                normal_style
            ),
            Paragraph(
                "<b>Section</b>",
                normal_style
            ),
            Paragraph(
                safe_html(section),
                normal_style
            )
        ]
    ]

    info_table = Table(
        student_info,
        colWidths=[
            32 * mm,
            70 * mm,
            25 * mm,
            45 * mm
        ]
    )

    info_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#eef2ff")
                ),
                (
                    "BACKGROUND",
                    (2, 0),
                    (2, -1),
                    colors.HexColor("#eef2ff")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    story.append(info_table)

    story.append(
        Spacer(1, 12)
    )

    subject_data = [
        [
            Paragraph("<b>Subject</b>", normal_style),
            Paragraph("<b>Obtained</b>", normal_style),
            Paragraph("<b>Maximum</b>", normal_style),
            Paragraph("<b>Percentage</b>", normal_style),
            Paragraph("<b>Grade</b>", normal_style)
        ]
    ]

    for row in report_rows:

        subject_data.append(
            [
                Paragraph(
                    safe_html(row["Subject"]),
                    normal_style
                ),
                f"{row['Marks Obtained']:g}",
                f"{row['Maximum Marks']:g}",
                f"{row['Percentage']:.2f}%",
                row["Grade"]
            ]
        )

    subject_table = Table(
        subject_data,
        colWidths=[
            65 * mm,
            27 * mm,
            27 * mm,
            32 * mm,
            20 * mm
        ],
        repeatRows=1
    )

    subject_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1e3a8a")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    story.append(subject_table)

    story.append(
        Spacer(1, 12)
    )

    summary_data = [
        [
            Paragraph(
                "<b>Total Marks</b>",
                normal_style
            ),
            Paragraph(
                "<b>Percentage</b>",
                normal_style
            ),
            Paragraph(
                "<b>Grade</b>",
                normal_style
            ),
            Paragraph(
                "<b>Result</b>",
                normal_style
            )
        ],
        [
            f"{total_obtained:g} / {total_max:g}",
            f"{percentage:.2f}%",
            grade,
            result
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            42 * mm,
            42 * mm,
            42 * mm,
            42 * mm
        ]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#eef2ff")
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ]
        )
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 40)
    )

    signature_data = [
        [
            "Parent / Guardian",
            "Class Teacher",
            "Principal"
        ],
        [
            "\n\n________________",
            "\n\n________________",
            "\n\n________________"
        ]
    ]

    signature_table = Table(
        signature_data,
        colWidths=[
            55 * mm,
            55 * mm,
            55 * mm
        ]
    )

    signature_table.setStyle(
        TableStyle(
            [
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ]
        )
    )

    story.append(signature_table)

    doc.build(story)

    output.seek(0)

    return output.getvalue()


# =========================================================
# PRINT HTML
# =========================================================

def build_print_html(
    student_name,
    sr_no,
    class_name,
    section,
    exam_type,
    report_rows,
    total_obtained,
    total_max,
    percentage,
    grade,
    result
):

    report_rows_html = ""

    for row in report_rows:

        report_rows_html += f"""
        <tr>
            <td>{safe_html(row["Subject"])}</td>
            <td>{row["Marks Obtained"]:g}</td>
            <td>{row["Maximum Marks"]:g}</td>
            <td>{row["Percentage"]:.2f}%</td>
            <td>{safe_html(row["Grade"])}</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<title>
Student Report Card
</title>

<style>

* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    padding:25px;
    background:#f1f5f9;
    font-family:Arial, Helvetica, sans-serif;
    color:#111827;
}}

.report-card {{
    width:100%;
    max-width:850px;
    margin:auto;
    background:white;
    border:2px solid #1e3a8a;
    border-radius:14px;
    padding:28px;
    box-shadow:0 8px 25px rgba(0,0,0,0.10);
}}

.header {{
    text-align:center;
    border-bottom:2px solid #1e3a8a;
    padding-bottom:15px;
}}

.school-name {{
    margin:0;
    font-size:28px;
    color:#1e3a8a;
    letter-spacing:0.5px;
}}

.report-title {{
    margin:7px 0;
    font-size:19px;
}}

.exam-name {{
    margin:0;
    font-size:14px;
    font-weight:bold;
}}

.student-info {{
    width:100%;
    border-collapse:collapse;
    margin-top:22px;
}}

.student-info td {{
    border:1px solid #cbd5e1;
    padding:11px;
}}

.label {{
    width:17%;
    background:#eef2ff;
    font-weight:bold;
}}

.value {{
    width:33%;
}}

.section-title {{
    margin-top:24px;
    margin-bottom:10px;
    font-size:17px;
    color:#1e3a8a;
}}

.marks-table {{
    width:100%;
    border-collapse:collapse;
}}

.marks-table th {{
    background:#1e3a8a;
    color:white;
    padding:11px 8px;
    border:1px solid #1e3a8a;
}}

.marks-table td {{
    padding:10px 8px;
    text-align:center;
    border:1px solid #cbd5e1;
}}

.marks-table td:first-child {{
    text-align:left;
    font-weight:600;
}}

.summary {{
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    gap:10px;
    margin-top:18px;
}}

.summary-box {{
    border:1px solid #cbd5e1;
    border-radius:8px;
    padding:12px;
    text-align:center;
    background:#f8fafc;
}}

.summary-label {{
    font-size:12px;
    color:#64748b;
    font-weight:bold;
}}

.summary-value {{
    margin-top:5px;
    font-size:17px;
    font-weight:bold;
}}

.signatures {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:30px;
    margin-top:65px;
    text-align:center;
}}

.signature-line {{
    border-top:1px solid #111827;
    padding-top:8px;
    font-size:13px;
}}

.print-button {{
    display:block;
    width:100%;
    margin-top:25px;
    padding:13px;
    border:0;
    border-radius:8px;
    background:#1e3a8a;
    color:white;
    font-size:16px;
    font-weight:bold;
    cursor:pointer;
}}

@media(max-width:650px) {{

    body {{
        padding:8px;
    }}

    .report-card {{
        padding:15px;
    }}

    .school-name {{
        font-size:21px;
    }}

    .summary {{
        grid-template-columns:repeat(2,1fr);
    }}

    .signatures {{
        grid-template-columns:1fr;
        gap:35px;
    }}

}}

@media print {{

    body {{
        padding:0;
        background:white;
    }}

    .report-card {{
        max-width:none;
        border:2px solid #1e3a8a;
        box-shadow:none;
        border-radius:0;
    }}

    .print-button {{
        display:none;
    }}

    @page {{
        size:A4;
        margin:10mm;
    }}

}}

</style>

</head>

<body>

<div class="report-card">

    <div class="header">

        <h1 class="school-name">
            🏫 CAMPUS ERP PRO
        </h1>

        <div class="report-title">
            STUDENT REPORT CARD
        </div>

        <p class="exam-name">
            {safe_html(exam_type)}
        </p>

    </div>

    <table class="student-info">

        <tr>

            <td class="label">
                Student Name
            </td>

            <td class="value">
                {safe_html(student_name)}
            </td>

            <td class="label">
                SR No
            </td>

            <td class="value">
                {safe_html(sr_no)}
            </td>

        </tr>

        <tr>

            <td class="label">
                Class
            </td>

            <td class="value">
                {safe_html(class_name)}
            </td>

            <td class="label">
                Section
            </td>

            <td class="value">
                {safe_html(section)}
            </td>

        </tr>

    </table>

    <div class="section-title">
        📚 Subject-wise Marks
    </div>

    <table class="marks-table">

        <thead>

            <tr>
                <th>Subject</th>
                <th>Obtained</th>
                <th>Maximum</th>
                <th>Percentage</th>
                <th>Grade</th>
            </tr>

        </thead>

        <tbody>

            {report_rows_html}

        </tbody>

    </table>

    <div class="summary">

        <div class="summary-box">
            <div class="summary-label">
                TOTAL MARKS
            </div>
            <div class="summary-value">
                {total_obtained:g} / {total_max:g}
            </div>
        </div>

        <div class="summary-box">
            <div class="summary-label">
                PERCENTAGE
            </div>
            <div class="summary-value">
                {percentage:.2f}%
            </div>
        </div>

        <div class="summary-box">
            <div class="summary-label">
                GRADE
            </div>
            <div class="summary-value">
                {safe_html(grade)}
            </div>
        </div>

        <div class="summary-box">
            <div class="summary-label">
                RESULT
            </div>
            <div class="summary-value">
                {safe_html(result)}
            </div>
        </div>

    </div>

    <div class="signatures">

        <div class="signature-line">
            Parent / Guardian Signature
        </div>

        <div class="signature-line">
            Class Teacher Signature
        </div>

        <div class="signature-line">
            Principal Signature
        </div>

    </div>

    <button
        class="print-button"
        onclick="window.print()"
    >
        🖨️ Print A4 Report Card
    </button>

</div>

</body>

</html>
"""


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
        (
            total_obtained /
            total_max
        ) * 100
        if total_max > 0
        else 0
    )

    grade = calculate_grade(
        percentage
    )

    result = calculate_result(
        percentage
    )

    report_rows = build_report_data(
        student_marks
    )

    st.markdown("---")

    # =====================================================
    # PROFESSIONAL STREAMLIT REPORT CARD
    # =====================================================

    st.markdown(
        """
        <style>

        .erp-report-wrapper {
            border: 2px solid #1e3a8a;
            border-radius: 16px;
            padding: 24px;
            background: #ffffff;
            margin-top: 10px;
            margin-bottom: 15px;
        }

        .erp-report-header {
            text-align: center;
            border-bottom: 2px solid #1e3a8a;
            padding-bottom: 15px;
        }

        .erp-school-title {
            color: #1e3a8a;
            font-size: 27px;
            font-weight: 800;
            margin: 0;
        }

        .erp-report-title {
            font-size: 19px;
            font-weight: 700;
            margin-top: 7px;
        }

        .erp-exam-title {
            font-size: 14px;
            font-weight: 600;
            margin-top: 4px;
        }

        .erp-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }

        .erp-info-box {
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 11px;
            background: #f8fafc;
        }

        .erp-info-label {
            color: #64748b;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .erp-info-value {
            margin-top: 4px;
            font-size: 15px;
            font-weight: 700;
        }

        @media(max-width:650px) {
            .erp-report-wrapper {
                padding: 14px;
            }

            .erp-school-title {
                font-size: 21px;
            }

            .erp-info-grid {
                grid-template-columns: 1fr;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # Header and student info are HTML-rendered deliberately,
    # while printable HTML is never directly displayed as text.

    st.markdown(
        f"""
        <div class="erp-report-wrapper">

            <div class="erp-report-header">

                <div class="erp-school-title">
                    🏫 CAMPUS ERP PRO
                </div>

                <div class="erp-report-title">
                    STUDENT REPORT CARD
                </div>

                <div class="erp-exam-title">
                    {safe_html(exam_type)}
                </div>

            </div>

            <div class="erp-info-grid">

                <div class="erp-info-box">

                    <div class="erp-info-label">
                        Student Name
                    </div>

                    <div class="erp-info-value">
                        {safe_html(student_name)}
                    </div>

                </div>

                <div class="erp-info-box">

                    <div class="erp-info-label">
                        SR No
                    </div>

                    <div class="erp-info-value">
                        {safe_html(sr_no)}
                    </div>

                </div>

                <div class="erp-info-box">

                    <div class="erp-info-label">
                        Class
                    </div>

                    <div class="erp-info-value">
                        {safe_html(class_name)}
                    </div>

                </div>

                <div class="erp-info-box">

                    <div class="erp-info-label">
                        Section
                    </div>

                    <div class="erp-info-value">
                        {safe_html(section)}
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # SUBJECT TABLE
    # =====================================================

    st.markdown(
        "### 📚 Subject-wise Marks"
    )

    report_df = pd.DataFrame(
        report_rows,
        columns=[
            "Subject",
            "Marks Obtained",
            "Maximum Marks",
            "Percentage",
            "Grade"
        ]
    )

    if not report_df.empty:

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Subject": st.column_config.TextColumn(
                    "Subject"
                ),
                "Marks Obtained": st.column_config.NumberColumn(
                    "Marks Obtained",
                    format="%.1f"
                ),
                "Maximum Marks": st.column_config.NumberColumn(
                    "Maximum Marks",
                    format="%.1f"
                ),
                "Percentage": st.column_config.NumberColumn(
                    "Percentage",
                    format="%.2f%%"
                ),
                "Grade": st.column_config.TextColumn(
                    "Grade"
                )
            }
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    st.markdown(
        "### 📊 Result Summary"
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

    # =====================================================
    # ACTION BUTTONS
    # =====================================================

    st.markdown(
        "### 🖨️ Report Card Actions"
    )

    ac1, ac2 = st.columns(2)

    # -----------------------------------------------------
    # PRINT
    # -----------------------------------------------------

    print_html = build_print_html(
        student_name,
        sr_no,
        class_name,
        section,
        exam_type,
        report_rows,
        total_obtained,
        total_max,
        percentage,
        grade,
        result
    )

    with ac1:

        print_button = st.button(
            "🖨️ Print A4 Report Card",
            use_container_width=True,
            type="primary",
            key=(
                f"print_report_"
                f"{sr_no}_"
                f"{class_name}_"
                f"{section}_"
                f"{exam_type}"
            )
        )

        if print_button:

            # HTML is sent only to the browser iframe.
            # It is NOT displayed as Streamlit markdown text.
            components.html(
                f"""
                <script>

                const reportWindow =
                    window.open(
                        "",
                        "_blank",
                        "width=950,height=900"
                    );

                if (reportWindow) {{

                    reportWindow.document.open();

                    reportWindow.document.write(
                        {print_html!r}
                    );

                    reportWindow.document.close();

                    reportWindow.focus();

                    setTimeout(
                        function() {{
                            reportWindow.print();
                        }},
                        700
                    );

                }} else {{

                    document.body.innerHTML +=
                        "<p style='color:red;'>"
                        "Please allow pop-ups for printing."
                        "</p>";

                }}

                </script>
                """,
                height=0
            )

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    pdf_data = generate_report_card_pdf(
        student_name,
        sr_no,
        class_name,
        section,
        exam_type,
        report_rows,
        total_obtained,
        total_max,
        percentage,
        grade,
        result
    )

    with ac2:

        if pdf_data:

            st.download_button(
                "📥 Download PDF Report Card",
                data=pdf_data,
                file_name=(
                    f"Report_Card_"
                    f"{str(student_name).replace(' ', '_')}_"
                    f"{exam_type.replace(' ', '_')}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
                type="secondary",
                key=(
                    f"download_report_pdf_"
                    f"{sr_no}_"
                    f"{class_name}_"
                    f"{section}_"
                    f"{exam_type}"
                )
            )

        else:

            st.warning(
                "PDF सुविधा के लिए reportlab install करें."
            )

    # =====================================================
    # PRINT PREVIEW
    # =====================================================

    with st.expander(
        "👁️ A4 Print Preview",
        expanded=False
    ):

        components.html(
            print_html,
            height=850,
            scrolling=True
        )


# =========================================================
# PERFORMANCE REPORT
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

    # =====================================================
    # CLASSES
    # =====================================================

    if (
        is_teacher
        and "ALL"
        not in assigned_classes
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

    # =====================================================
    # SUBJECTS
    # =====================================================

    if (
        is_teacher
        and "ALL"
        not in assigned_subjects
    ):

        report_subjects = [
            s
            for s in assigned_subjects
            if s
        ]

    else:

        report_subjects = all_subjects

    # =====================================================
    # FILTERS
    # =====================================================

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

        subject_options = (
            ["ALL"] +
            report_subjects
        )

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
    # NUMERIC CONVERSION
    # =====================================================

    df["marks_obtained"] = (
        df["marks_obtained"]
        .apply(safe_float)
    )

    df["max_marks"] = (
        df["max_marks"]
        .apply(safe_float)
    )

    df["percentage"] = df.apply(
        lambda row:
            (
                row["marks_obtained"] /
                row["max_marks"] *
                100
            )
            if row["max_marks"] > 0
            else 0,
        axis=1
    )

    # =====================================================
    # CLASS SUMMARY
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 📈 Class Performance"
    )

    total_obtained = (
        df["marks_obtained"].sum()
    )

    total_max = (
        df["max_marks"].sum()
    )

    class_percentage = (
        total_obtained /
        total_max *
        100
        if total_max > 0
        else 0
    )

    student_count = (
        df["sr_no"].nunique()
    )

    subject_count = (
        df["subject"].nunique()
    )

    avg_percentage = (
        df["percentage"].mean()
        if not df.empty
        else 0
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
    # SUBJECT SUMMARY
    # =====================================================

    st.markdown(
        "### 📚 Subject-wise Performance"
    )

    subject_summary = []

    for subject, group in df.groupby(
        "subject"
    ):

        obtained = (
            group["marks_obtained"].sum()
        )

        maximum = (
            group["max_marks"].sum()
        )

        percentage = (
            obtained /
            maximum *
            100
            if maximum > 0
            else 0
        )

        subject_summary.append(
            {
                "Subject":
                    subject,
                "Marks Obtained":
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
                    )
            }
        )

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

        obtained = (
            group["marks_obtained"].sum()
        )

        maximum = (
            group["max_marks"].sum()
        )

        percentage = (
            obtained /
            maximum *
            100
            if maximum > 0
            else 0
        )

        student_summary.append(
            {
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
            }
        )

    summary_df = pd.DataFrame(
        student_summary
    )

    summary_df = (
        summary_df
        .sort_values(
            by="Percentage",
            ascending=False
        )
        .reset_index(
            drop=True
        )
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
    # EXCEL
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

        df.to_excel(
            writer,
            index=False,
            sheet_name="Marks Data"
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
        (
            f"Rank {row['Rank']} | "
            f"SR {row['SR No']} - "
            f"{row['Student Name']}"
        ):
        row["SR No"]
        for _, row in summary_df.iterrows()
    }

    if not student_options:
        return

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

    if student_data.empty:
        return

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
# MAIN EXAM MODULE
# =========================================================

def render_exams_module():

    st.markdown(
        "## 📝 Exam Management & Marks Entry"
    )

    tab1, tab2 = st.tabs(
        [
            "✏️ Enter / Edit Marks",
            "📊 Class Performance & Report Card"
        ]
    )

    with tab1:

        render_marks_entry()

    with tab2:

        render_performance_report()
