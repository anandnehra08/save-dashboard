# =========================================================
# CAMPUS ERP PRO
# EXAM MANAGEMENT & MARKS
# PHASE 1 + 2 + 3 + 4 COMPLETE
# =========================================================

import io
import html
from datetime import datetime

import pandas as pd
import streamlit as st

from database.supabase import supabase


# =========================================================
# CONSTANTS
# =========================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]

EXAM_TYPES = [
    "Unit Test 1",
    "Mid Term",
    "Unit Test 2",
    "Final Exam",
]

DEFAULT_SUBJECTS = [
    "Maths",
    "Science",
    "English",
    "Hindi",
    "Physics",
    "Chemistry",
    "Social Studies",
]


# =========================================================
# COMMON HELPERS
# =========================================================

def safe_float(value):
    try:
        if value is None or pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def safe_int(value, default=0):
    try:
        if value is None or pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def safe_html(value):
    return html.escape("" if value is None else str(value))


def current_user():
    return st.session_state.get(
        "user_email",
        st.session_state.get("username", "Admin")
    )


def calculate_grade(percentage):
    p = safe_float(percentage)
    if p >= 90:
        return "A+"
    if p >= 80:
        return "A"
    if p >= 70:
        return "B+"
    if p >= 60:
        return "B"
    if p >= 50:
        return "C"
    if p >= 40:
        return "D"
    return "E"


def calculate_result(percentage):
    return "PASS" if safe_float(percentage) >= 33 else "FAIL"


def result_class(result):
    return "pass-result" if str(result).upper() == "PASS" else "fail-result"


# =========================================================
# PERMISSIONS
# =========================================================

def get_exam_permissions():
    user_role = st.session_state.get("user_role", "admin")

    assigned_classes = st.session_state.get("assigned_classes")
    if not assigned_classes:
        single_class = st.session_state.get("assigned_class")
        assigned_classes = [single_class] if single_class else CLASSES

    assigned_subjects = st.session_state.get(
        "assigned_subjects",
        ["ALL"]
    )
    if not assigned_subjects:
        assigned_subjects = ["ALL"]

    is_teacher = user_role in ["class_teacher", "subject_teacher"]

    return user_role, assigned_classes, assigned_subjects, is_teacher


def class_allowed(class_name):
    role, classes, _, _ = get_exam_permissions()
    if role == "admin" or "ALL" in classes:
        return True
    return class_name in classes


def subject_allowed(subject):
    role, _, subjects, _ = get_exam_permissions()
    if role == "admin" or "ALL" in subjects:
        return True
    return subject in subjects


# =========================================================
# SUBJECT MASTER
# =========================================================

def get_master_subjects():
    if not supabase:
        return DEFAULT_SUBJECTS

    try:
        response = (
            supabase.table("subjects_master")
            .select("subject_name")
            .order("subject_name")
            .execute()
        )
        subjects = [
            str(x.get("subject_name"))
            for x in (response.data or [])
            if x.get("subject_name")
        ]
        return subjects or DEFAULT_SUBJECTS
    except Exception as e:
        st.warning(f"⚠️ Subject Master fetch समस्या: {e}")
        return DEFAULT_SUBJECTS


# =========================================================
# STUDENTS
# =========================================================

def fetch_students(class_name, section):
    if not supabase:
        return []

    try:
        response = (
            supabase.table("students")
            .select("sr_no, student_name, roll_no")
            .eq("class", class_name)
            .eq("section", section)
            .order("roll_no")
            .execute()
        )
        return response.data or []
    except Exception as e:
        st.error(f"❌ Students fetch error: {e}")
        return []


# =========================================================
# MARKS DATABASE
# =========================================================

MARKS_COLUMNS = (
    "id, sr_no, student_name, class, section, exam_type, "
    "subject, marks_obtained, max_marks, entered_by, "
    "updated_by, updated_at"
)


def fetch_existing_marks(class_name, section, subject, exam_type):
    if not supabase:
        return {}

    try:
        response = (
            supabase.table("marks")
            .select(MARKS_COLUMNS)
            .eq("class", class_name)
            .eq("section", section)
            .eq("subject", subject)
            .eq("exam_type", exam_type)
            .execute()
        )
        data = response.data or []
        return {
            safe_int(row.get("sr_no")): row
            for row in data
            if row.get("sr_no") is not None
        }
    except Exception:
        try:
            response = (
                supabase.table("marks")
                .select(
                    "id, sr_no, student_name, class, section, "
                    "exam_type, subject, marks_obtained, max_marks"
                )
                .eq("class", class_name)
                .eq("section", section)
                .eq("subject", subject)
                .eq("exam_type", exam_type)
                .execute()
            )
            return {
                safe_int(x.get("sr_no")): x
                for x in (response.data or [])
                if x.get("sr_no") is not None
            }
        except Exception as e:
            st.error(f"❌ Existing marks fetch error: {e}")
            return {}


def fetch_report_marks(class_name, section, exam_type, subject=None):
    if not supabase:
        return []

    try:
        query = (
            supabase.table("marks")
            .select(
                "id, sr_no, student_name, class, section, exam_type, "
                "subject, marks_obtained, max_marks"
            )
            .eq("class", class_name)
            .eq("section", section)
            .eq("exam_type", exam_type)
        )
        if subject:
            query = query.eq("subject", subject)

        return query.execute().data or []
    except Exception as e:
        st.error(f"❌ Report data fetch error: {e}")
        return []


def find_existing_mark(sr_no, class_name, section, subject, exam_type):
    if not supabase:
        return None

    try:
        response = (
            supabase.table("marks")
            .select("id, sr_no, class, section, subject, exam_type")
            .eq("sr_no", int(sr_no))
            .eq("class", class_name)
            .eq("section", section)
            .eq("subject", subject)
            .eq("exam_type", exam_type)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception:
        return None


def delete_mark_record(sr_no, class_name, section, subject, exam_type):
    if not supabase:
        return False

    try:
        (
            supabase.table("marks")
            .delete()
            .eq("sr_no", int(sr_no))
            .eq("class", class_name)
            .eq("section", section)
            .eq("subject", subject)
            .eq("exam_type", exam_type)
            .execute()
        )
        return True
    except Exception as e:
        st.error(f"❌ Delete failed: {e}")
        return False


def validate_marks(records):
    errors = []

    for r in records:
        obtained = safe_float(r["marks_obtained"])
        maximum = safe_float(r["max_marks"])

        if maximum <= 0:
            errors.append(f"SR {r['sr_no']}: Maximum marks must be > 0.")
        elif obtained < 0:
            errors.append(f"SR {r['sr_no']}: Marks cannot be negative.")
        elif obtained > maximum:
            errors.append(
                f"SR {r['sr_no']}: {obtained:g} cannot exceed "
                f"maximum {maximum:g}."
            )

    return errors


def save_marks_batch(records):
    """Phase 1: reliable insert/update with per-record error isolation."""
    if not supabase:
        return 0, 0, []

    validation_errors = validate_marks(records)
    if validation_errors:
        return 0, len(records), validation_errors

    success = 0
    failed = 0
    errors = []
    user = current_user()
    now = datetime.utcnow().isoformat()

    for record in records:
        try:
            existing = find_existing_mark(
                record["sr_no"],
                record["class"],
                record["section"],
                record["subject"],
                record["exam_type"],
            )

            if existing:
                payload = {
                    "student_name": record["student_name"],
                    "marks_obtained": record["marks_obtained"],
                    "max_marks": record["max_marks"],
                    "updated_by": user,
                    "updated_at": now,
                }

                # If audit columns don't exist, retry without them.
                try:
                    (
                        supabase.table("marks")
                        .update(payload)
                        .eq("id", existing["id"])
                        .execute()
                    )
                except Exception:
                    fallback = {
                        "student_name": record["student_name"],
                        "marks_obtained": record["marks_obtained"],
                        "max_marks": record["max_marks"],
                    }
                    (
                        supabase.table("marks")
                        .update(fallback)
                        .eq("id", existing["id"])
                        .execute()
                    )
            else:
                payload = {
                    "sr_no": record["sr_no"],
                    "student_name": record["student_name"],
                    "class": record["class"],
                    "section": record["section"],
                    "exam_type": record["exam_type"],
                    "subject": record["subject"],
                    "marks_obtained": record["marks_obtained"],
                    "max_marks": record["max_marks"],
                    "entered_by": user,
                }

                try:
                    supabase.table("marks").insert(payload).execute()
                except Exception:
                    fallback = {
                        k: payload[k]
                        for k in [
                            "sr_no", "student_name", "class", "section",
                            "exam_type", "subject", "marks_obtained",
                            "max_marks"
                        ]
                    }
                    supabase.table("marks").insert(fallback).execute()

            success += 1

        except Exception as e:
            failed += 1
            errors.append(f"SR {record['sr_no']}: {e}")

    return success, failed, errors


# =========================================================
# PHASE 4: EXAM SETUP / CONFIGURATION
# =========================================================

def exam_setup_ui():
    st.markdown("### ⚙️ Exam Setup & Configuration")

    st.caption(
        "यह configuration screen future exam-wise settings के लिए है। "
        "Current marks table को बिना तोड़े काम करती है।"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        setup_class = st.selectbox(
            "Class",
            CLASSES,
            key="setup_class"
        )

    with c2:
        setup_exam = st.selectbox(
            "Exam",
            EXAM_TYPES,
            key="setup_exam"
        )

    with c3:
        setup_subject = st.selectbox(
            "Subject",
            get_master_subjects(),
            key="setup_subject"
        )

    max_marks = st.number_input(
        "Default Maximum Marks",
        min_value=1.0,
        max_value=1000.0,
        value=100.0,
        step=1.0,
        key="setup_max_marks"
    )

    st.info(
        f"📌 Configuration: {setup_class} • "
        f"{setup_exam} • {setup_subject} • "
        f"Max Marks: {max_marks:g}"
    )


# =========================================================
# PHASE 1: ENTER / EDIT MARKS
# =========================================================

def render_marks_entry():
    st.subheader("✏️ Enter / Edit Marks")

    user_role, assigned_classes, assigned_subjects, is_teacher = (
        get_exam_permissions()
    )
    all_subjects = get_master_subjects()

    if is_teacher:
        st.info(
            "🔒 Teacher Access | Classes: "
            + ", ".join(map(str, assigned_classes))
            + " | Subjects: "
            + ", ".join(map(str, assigned_subjects))
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        available_classes = (
            [c for c in assigned_classes if c in CLASSES]
            if is_teacher and "ALL" not in assigned_classes
            else CLASSES
        ) or CLASSES
        selected_class = st.selectbox(
            "Select Class", available_classes, key="ex_cls"
        )

    with c2:
        selected_section = st.selectbox(
            "Select Section", SECTIONS, key="ex_sec"
        )

    with c3:
        available_subjects = (
            [s for s in assigned_subjects if s]
            if is_teacher and "ALL" not in assigned_subjects
            else all_subjects
        ) or all_subjects
        selected_subject = st.selectbox(
            "Select Subject", available_subjects, key="ex_sub"
        )

    with c4:
        selected_exam = st.selectbox(
            "Select Exam Type", EXAM_TYPES, key="ex_type"
        )

    if not class_allowed(selected_class):
        st.error("❌ आपको इस class के marks access करने की permission नहीं है.")
        return

    if not subject_allowed(selected_subject):
        st.error("❌ आपको इस subject के marks access करने की permission नहीं है.")
        return

    # Subject master for admin
    if user_role == "admin":
        with st.expander("➕ Add New Subject"):
            a, b = st.columns([3, 1])
            with a:
                new_subject = st.text_input(
                    "New Subject Name",
                    key="new_subject_name",
                    placeholder="e.g. Computer Science"
                )
            with b:
                st.write("")
                add_subject = st.button(
                    "Save Subject",
                    use_container_width=True,
                    key="save_new_subject"
                )

            if add_subject:
                clean = new_subject.strip()
                if not clean:
                    st.warning("कृपया subject name लिखें.")
                elif not supabase:
                    st.error("❌ Supabase connection नहीं है.")
                else:
                    try:
                        existing = (
                            supabase.table("subjects_master")
                            .select("subject_name")
                            .eq("subject_name", clean)
                            .execute()
                        )
                        if existing.data:
                            st.warning("⚠️ यह subject पहले से मौजूद है.")
                        else:
                            (
                                supabase.table("subjects_master")
                                .insert({"subject_name": clean})
                                .execute()
                            )
                            st.success(f"✅ {clean} added.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Subject add error: {e}")

    st.markdown("---")

    students = fetch_students(selected_class, selected_section)
    if not students:
        st.warning(
            f"⚠️ {selected_class} - {selected_section} में कोई student नहीं मिला."
        )
        return

    existing_marks = fetch_existing_marks(
        selected_class,
        selected_section,
        selected_subject,
        selected_exam,
    )

    existing_max_values = [
        safe_float(row.get("max_marks"))
        for row in existing_marks.values()
        if safe_float(row.get("max_marks")) > 0
    ]

    default_max = existing_max_values[0] if existing_max_values else 100.0

    max_marks = st.number_input(
        "Maximum Marks for this Test",
        min_value=1.0,
        max_value=1000.0,
        value=float(default_max),
        step=1.0,
        key="maximum_marks_input"
    )

    st.markdown(
        f"### 👨‍🎓 {selected_subject} — {selected_exam} "
        f"({selected_class}-{selected_section})"
    )

    with st.form(
        key=(
            f"marks_entry_{selected_class}_{selected_section}_"
            f"{selected_subject}_{selected_exam}"
        )
    ):
        marks_payload = []

        for student in students:
            sr_no = safe_int(student.get("sr_no"))
            name = str(student.get("student_name", "N/A"))
            roll = student.get("roll_no") or 0

            previous = existing_marks.get(sr_no, {})
            previous_marks = safe_float(previous.get("marks_obtained"))

            if previous_marks > max_marks:
                previous_marks = max_marks

            m1, m2, m3 = st.columns([1, 4, 2])

            with m1:
                st.markdown(f"**Roll #{roll}**")

            with m2:
                st.markdown(f"**{name}**  \nSR No: `{sr_no}`")

            with m3:
                obtained = st.number_input(
                    f"Marks {sr_no}",
                    min_value=0.0,
                    max_value=float(max_marks),
                    value=float(previous_marks),
                    step=0.5,
                    key=(
                        f"mark_{selected_class}_{selected_section}_"
                        f"{selected_subject}_{selected_exam}_{sr_no}"
                    ),
                    label_visibility="collapsed"
                )

            marks_payload.append({
                "sr_no": sr_no,
                "student_name": name,
                "class": selected_class,
                "section": selected_section,
                "exam_type": selected_exam,
                "subject": selected_subject,
                "marks_obtained": float(obtained),
                "max_marks": float(max_marks),
            })

        submitted = st.form_submit_button(
            "💾 Save / Update All Marks",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if not supabase:
            st.error("❌ Supabase connection नहीं है.")
            return

        success, failed, errors = save_marks_batch(marks_payload)

        if success:
            st.success(f"✅ {success} records successfully saved/updated.")

        if failed:
            st.error(f"❌ {failed} records में error आया.")
            with st.expander("Error Details"):
                for e in errors:
                    st.write(f"- {e}")

        if success and not failed:
            st.rerun()

    # Delete management
    st.markdown("---")
    st.markdown("### 🗑️ Saved Marks Management")

    saved = fetch_report_marks(
        selected_class,
        selected_section,
        selected_exam,
        selected_subject
    )

    if not saved:
        st.info("इस Subject और Exam के लिए अभी कोई saved marks नहीं हैं.")
        return

    delete_options = {}
    for row in saved:
        label = (
            f"SR {row.get('sr_no')} - "
            f"{row.get('student_name', 'N/A')} — "
            f"{safe_float(row.get('marks_obtained')):g}/"
            f"{safe_float(row.get('max_marks')):g}"
        )
        delete_options[label] = safe_int(row.get("sr_no"))

    selected_label = st.selectbox(
        "Select Student for Delete",
        list(delete_options),
        key=(
            f"delete_select_{selected_class}_{selected_section}_"
            f"{selected_subject}_{selected_exam}"
        )
    )

    delete_sr = delete_options[selected_label]
    confirm_key = (
        f"confirm_delete_{selected_class}_{selected_section}_"
        f"{selected_subject}_{selected_exam}_{delete_sr}"
    )

    if not st.session_state.get(confirm_key, False):
        if st.button(
            "🗑️ Delete Selected Marks",
            use_container_width=True,
            key=f"delete_btn_{delete_sr}"
        ):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        st.warning(f"⚠️ क्या आप **{selected_label}** के marks delete करना चाहते हैं?")
        d1, d2 = st.columns(2)

        with d1:
            if st.button(
                "✅ Yes, Delete",
                type="primary",
                use_container_width=True,
                key=f"confirm_yes_{delete_sr}"
            ):
                if delete_mark_record(
                    delete_sr,
                    selected_class,
                    selected_section,
                    selected_subject,
                    selected_exam
                ):
                    st.session_state[confirm_key] = False
                    st.success("✅ Marks deleted.")
                    st.rerun()

        with d2:
            if st.button(
                "❌ Cancel",
                use_container_width=True,
                key=f"confirm_no_{delete_sr}"
            ):
                st.session_state[confirm_key] = False
                st.rerun()


# =========================================================
# PHASE 2: ANALYTICS ENGINE
# =========================================================

def prepare_marks_dataframe(marks_data):
    df = pd.DataFrame(marks_data)

    if df.empty:
        return df

    for col in ["marks_obtained", "max_marks"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].apply(safe_float)

    df["sr_no"] = df["sr_no"].apply(safe_int)
    df["percentage"] = df.apply(
        lambda r: (
            r["marks_obtained"] / r["max_marks"] * 100
            if r["max_marks"] > 0 else 0
        ),
        axis=1
    )
    df["grade"] = df["percentage"].apply(calculate_grade)
    df["result"] = df["percentage"].apply(calculate_result)

    return df


def build_student_summary(df):
    rows = []

    if df.empty:
        return pd.DataFrame()

    for sr_no, group in df.groupby("sr_no"):
        name = str(group.iloc[0].get("student_name", "N/A"))
        obtained = group["marks_obtained"].sum()
        maximum = group["max_marks"].sum()
        pct = obtained / maximum * 100 if maximum > 0 else 0

        rows.append({
            "SR No": sr_no,
            "Student Name": name,
            "Total Marks": round(obtained, 2),
            "Maximum Marks": round(maximum, 2),
            "Percentage": round(pct, 2),
            "Grade": calculate_grade(pct),
            "Result": calculate_result(pct),
        })

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    result = result.sort_values(
        ["Percentage", "Student Name"],
        ascending=[False, True]
    ).reset_index(drop=True)

    result.insert(0, "Rank", range(1, len(result) + 1))
    return result


def build_subject_summary(df):
    rows = []

    if df.empty:
        return pd.DataFrame()

    for subject, group in df.groupby("subject"):
        obtained = group["marks_obtained"].sum()
        maximum = group["max_marks"].sum()
        pct = obtained / maximum * 100 if maximum > 0 else 0

        rows.append({
            "Subject": subject,
            "Marks Obtained": round(obtained, 2),
            "Maximum Marks": round(maximum, 2),
            "Percentage": round(pct, 2),
            "Grade": calculate_grade(pct),
        })

    return pd.DataFrame(rows).sort_values(
        "Percentage", ascending=False
    ).reset_index(drop=True)


def build_exam_statistics(df, student_summary):
    if df.empty:
        return {
            "students": 0,
            "subjects": 0,
            "average": 0,
            "pass": 0,
            "fail": 0,
            "pass_rate": 0,
            "highest": 0,
            "lowest": 0,
        }

    percentages = student_summary["Percentage"]
    passed = int((student_summary["Result"] == "PASS").sum())
    failed = int((student_summary["Result"] == "FAIL").sum())

    return {
        "students": len(student_summary),
        "subjects": int(df["subject"].nunique()),
        "average": float(percentages.mean()) if len(percentages) else 0,
        "pass": passed,
        "fail": failed,
        "pass_rate": (passed / len(student_summary) * 100)
        if len(student_summary) else 0,
        "highest": float(percentages.max()) if len(percentages) else 0,
        "lowest": float(percentages.min()) if len(percentages) else 0,
    }


# =========================================================
# PHASE 3: REPORT CARD PDF
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
    result,
    rank=None,
):
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        return None

    output = io.BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()

    center_title = ParagraphStyle(
        "CenterTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
    )

    center_subtitle = ParagraphStyle(
        "CenterSubtitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=13,
        leading=17,
    )

    normal = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
    )

    story = [
        Paragraph("CAMPUS ERP PRO", center_title),
        Paragraph("STUDENT REPORT CARD", center_subtitle),
        Paragraph(safe_html(exam_type), center_subtitle),
        Spacer(1, 8),
    ]

    info = [
        ["Student Name", safe_html(student_name), "SR No", safe_html(sr_no)],
        ["Class", safe_html(class_name), "Section", safe_html(section)],
        ["Rank", safe_html(rank if rank is not None else "-"), "Result", safe_html(result)],
    ]

    info_table = Table(
        info,
        colWidths=[28*mm, 67*mm, 25*mm, 55*mm]
    )
    info_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), .5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eef2ff")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#eef2ff")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [info_table, Spacer(1, 10)]

    table_data = [
        ["#", "Subject", "Obtained", "Maximum", "Percentage", "Grade"]
    ]

    for i, row in enumerate(report_rows, 1):
        table_data.append([
            i,
            Paragraph(safe_html(row["Subject"]), normal),
            f"{row['Marks Obtained']:g}",
            f"{row['Maximum Marks']:g}",
            f"{row['Percentage']:.2f}%",
            row["Grade"],
        ])

    marks_table = Table(
        table_data,
        colWidths=[10*mm, 60*mm, 27*mm, 27*mm, 30*mm, 20*mm],
        repeatRows=1,
    )
    marks_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), .5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [marks_table, Spacer(1, 10)]

    summary = [
        ["Total Marks", "Percentage", "Grade", "Result"],
        [
            f"{total_obtained:g} / {total_max:g}",
            f"{percentage:.2f}%",
            grade,
            result,
        ],
    ]

    summary_table = Table(
        summary,
        colWidths=[42*mm, 42*mm, 42*mm, 48*mm]
    )
    summary_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), .5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eef2ff")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story += [summary_table, Spacer(1, 35)]

    signatures = Table(
        [
            ["Parent / Guardian", "Class Teacher", "Principal"],
            ["________________", "________________", "________________"],
        ],
        colWidths=[58*mm, 58*mm, 58*mm]
    )
    signatures.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(signatures)

    doc.build(story)
    output.seek(0)
    return output.getvalue()


# =========================================================
# PHASE 3: REPORT CARD HTML
# =========================================================

def build_report_card_html(
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
    result,
    rank=None,
):
    rows = ""
    for i, row in enumerate(report_rows, 1):
        rows += f"""
        <tr>
            <td>{i}</td>
            <td class="subject">{safe_html(row["Subject"])}</td>
            <td>{row["Marks Obtained"]:g}</td>
            <td>{row["Maximum Marks"]:g}</td>
            <td>{row["Percentage"]:.2f}%</td>
            <td>{safe_html(row["Grade"])}</td>
        </tr>
        """

    rc = result_class(result)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Student Report Card</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f1f5f9;font-family:Arial,sans-serif;color:#172033}}
.card{{max-width:900px;margin:auto;background:#fff;border:2px solid #1e3a8a;border-radius:15px;overflow:hidden}}
.top{{height:7px;background:linear-gradient(90deg,#1e3a8a,#2563eb,#60a5fa)}}
.header{{text-align:center;padding:24px;border-bottom:1px solid #dbe3ef}}
.school{{font-size:29px;font-weight:800;color:#1e3a8a}}
.title{{font-size:21px;font-weight:700;margin-top:6px}}
.exam{{display:inline-block;margin-top:9px;padding:7px 18px;border-radius:20px;background:#eff6ff;color:#1d4ed8;font-weight:700}}
.info{{padding:20px;display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
.info-box{{border:1px solid #dbe3ef;border-radius:8px;padding:11px;background:#f8fafc}}
.label{{font-size:10px;color:#64748b;font-weight:700;text-transform:uppercase}}
.value{{margin-top:4px;font-size:14px;font-weight:700}}
.section{{margin:0 20px 10px;color:#1e3a8a;font-size:17px;font-weight:800}}
.table-wrap{{padding:0 20px;overflow-x:auto}}
table{{width:100%;border-collapse:collapse}}
th{{background:#1e3a8a;color:white;padding:10px;border:1px solid #1e3a8a;font-size:12px}}
td{{padding:9px;border:1px solid #dbe3ef;text-align:center;font-size:13px}}
td.subject{{text-align:left;font-weight:700}}
tr:nth-child(even){{background:#f8fafc}}
.summary{{padding:0 20px;display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:20px}}
.box{{border:1px solid #dbe3ef;border-radius:9px;padding:13px;text-align:center;background:#f8fafc}}
.box-label{{font-size:10px;color:#64748b;font-weight:700}}
.box-value{{margin-top:5px;font-size:17px;font-weight:800}}
.pass-result{{color:#15803d}} .fail-result{{color:#dc2626}}
.sign{{padding:55px 20px 25px;display:grid;grid-template-columns:repeat(3,1fr);gap:25px;text-align:center}}
.sign div{{border-top:1px solid #475569;padding-top:8px;font-size:12px;font-weight:700}}
.actions{{padding:0 20px 25px;display:grid;grid-template-columns:1fr 1fr;gap:10px}}
button{{padding:12px;border:0;border-radius:8px;background:#1e3a8a;color:#fff;font-weight:700;cursor:pointer}}
@media(max-width:650px){{.info{{grid-template-columns:repeat(2,1fr)}}.summary{{grid-template-columns:repeat(2,1fr)}}.sign{{grid-template-columns:1fr;gap:35px}}}}
@media print{{body{{background:#fff}}.card{{max-width:none;border-radius:0;box-shadow:none}}.actions{{display:none}}@page{{size:A4;margin:10mm}}}}
</style>
</head>
<body>
<div class="card">
<div class="top"></div>
<div class="header">
<div class="school">🏫 CAMPUS ERP PRO</div>
<div class="title">STUDENT REPORT CARD</div>
<div class="exam">{safe_html(exam_type)}</div>
</div>

<div class="info">
<div class="info-box"><div class="label">Student Name</div><div class="value">{safe_html(student_name)}</div></div>
<div class="info-box"><div class="label">SR No</div><div class="value">{safe_html(sr_no)}</div></div>
<div class="info-box"><div class="label">Class / Section</div><div class="value">{safe_html(class_name)} / {safe_html(section)}</div></div>
<div class="info-box"><div class="label">Rank</div><div class="value">{safe_html(rank if rank is not None else "-")}</div></div>
</div>

<div class="section">📚 Subject-wise Marks</div>
<div class="table-wrap">
<table>
<thead><tr><th>#</th><th>Subject</th><th>Obtained</th><th>Maximum</th><th>Percentage</th><th>Grade</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>

<div class="section" style="margin-top:22px">📊 Result Summary</div>
<div class="summary">
<div class="box"><div class="box-label">TOTAL MARKS</div><div class="box-value">{total_obtained:g} / {total_max:g}</div></div>
<div class="box"><div class="box-label">PERCENTAGE</div><div class="box-value">{percentage:.2f}%</div></div>
<div class="box"><div class="box-label">GRADE</div><div class="box-value">{safe_html(grade)}</div></div>
<div class="box"><div class="box-label">RESULT</div><div class="box-value {rc}">{safe_html(result)}</div></div>
</div>

<div class="sign">
<div>Parent / Guardian</div><div>Class Teacher</div><div>Principal</div>
</div>

<div class="actions">
<button onclick="window.print()">🖨️ Print A4 Report Card</button>
<button onclick="window.print()">📥 Save / Download PDF</button>
</div>
</div>
</body>
</html>
"""


# =========================================================
# PHASE 2 + 3: PERFORMANCE REPORT
# =========================================================

def render_performance_report():
    st.subheader("📊 Class Performance & Report Card")

    user_role, assigned_classes, assigned_subjects, is_teacher = (
        get_exam_permissions()
    )
    all_subjects = get_master_subjects()

    report_classes = (
        [c for c in assigned_classes if c in CLASSES]
        if is_teacher and "ALL" not in assigned_classes
        else CLASSES
    ) or CLASSES

    report_subjects = (
        [s for s in assigned_subjects if s]
        if is_teacher and "ALL" not in assigned_subjects
        else all_subjects
    ) or all_subjects

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        report_class = st.selectbox(
            "Select Class", report_classes, key="rep_ex_cls"
        )
    with c2:
        report_section = st.selectbox(
            "Select Section", SECTIONS, key="rep_ex_sec"
        )
    with c3:
        report_exam = st.selectbox(
            "Select Exam", EXAM_TYPES, key="rep_ex_type"
        )
    with c4:
        report_subject = st.selectbox(
            "Select Subject Filter",
            ["ALL"] + report_subjects,
            key="rep_ex_sub"
        )

    marks_data = fetch_report_marks(
        report_class,
        report_section,
        report_exam,
        None if report_subject == "ALL" else report_subject
    )

    if not marks_data:
        st.warning("चुनी गई Class, Section और Exam के लिए marks data उपलब्ध नहीं है.")
        return

    df = prepare_marks_dataframe(marks_data)
    student_summary = build_student_summary(df)
    subject_summary = build_subject_summary(df)
    stats = build_exam_statistics(df, student_summary)

    # KPI
    st.markdown("---")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("👨‍🎓 Students", stats["students"])
    k2.metric("📚 Subjects", stats["subjects"])
    k3.metric("📊 Average", f"{stats['average']:.2f}%")
    k4.metric("✅ Pass", stats["pass"])
    k5.metric("❌ Fail", stats["fail"])
    k6.metric("🏆 Pass Rate", f"{stats['pass_rate']:.2f}%")

    # Topper
    if not student_summary.empty:
        topper = student_summary.iloc[0]
        st.success(
            f"🏆 Topper: **{topper['Student Name']}** | "
            f"Rank 1 | {topper['Percentage']:.2f}%"
        )

    t1, t2, t3 = st.tabs([
        "🏆 Student Result",
        "📚 Subject Analysis",
        "📈 Detailed Data",
    ])

    with t1:
        st.dataframe(
            student_summary,
            use_container_width=True,
            hide_index=True
        )

    with t2:
        st.dataframe(
            subject_summary,
            use_container_width=True,
            hide_index=True
        )

        if not subject_summary.empty:
            best = subject_summary.iloc[0]
            st.info(
                f"⭐ Best Subject: **{best['Subject']}** "
                f"({best['Percentage']:.2f}%)"
            )

    with t3:
        display = df.copy()
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

    # Export workbook
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        student_summary.to_excel(
            writer, index=False, sheet_name="Student Result"
        )
        subject_summary.to_excel(
            writer, index=False, sheet_name="Subject Summary"
        )
        df.to_excel(
            writer, index=False, sheet_name="Marks Data"
        )

    st.download_button(
        "📥 Download Complete Result Excel",
        data=output.getvalue(),
        file_name=(
            f"{report_class}_{report_section}_"
            f"{report_exam}_Complete_Result.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
        key="download_complete_class_result"
    )

    # Individual report
    st.markdown("---")
    st.markdown("### 🎓 Individual Student Report Card")

    options = {
        (
            f"Rank {row['Rank']} | SR {row['SR No']} - "
            f"{row['Student Name']} | {row['Percentage']:.2f}%"
        ): row["SR No"]
        for _, row in student_summary.iterrows()
    }

    selected_label = st.selectbox(
        "Select Student",
        list(options),
        key="report_student_select"
    )
    selected_sr = options[selected_label]

    student_data = df[df["sr_no"] == selected_sr]
    if student_data.empty:
        return

    row_summary = student_summary[
        student_summary["SR No"] == selected_sr
    ].iloc[0]

    student_name = str(
        student_data.iloc[0].get("student_name", "N/A")
    )

    report_rows = []
    for row in student_data.to_dict("records"):
        obtained = safe_float(row.get("marks_obtained"))
        maximum = safe_float(row.get("max_marks"))
        pct = obtained / maximum * 100 if maximum > 0 else 0

        report_rows.append({
            "Subject": str(row.get("subject", "")),
            "Marks Obtained": obtained,
            "Maximum Marks": maximum,
            "Percentage": pct,
            "Grade": calculate_grade(pct),
        })

    total_obtained = sum(x["Marks Obtained"] for x in report_rows)
    total_max = sum(x["Maximum Marks"] for x in report_rows)
    percentage = total_obtained / total_max * 100 if total_max > 0 else 0
    grade = calculate_grade(percentage)
    result = calculate_result(percentage)
    rank = safe_int(row_summary["Rank"])

    html_report = build_report_card_html(
        student_name,
        selected_sr,
        report_class,
        report_section,
        report_exam,
        report_rows,
        total_obtained,
        total_max,
        percentage,
        grade,
        result,
        rank,
    )

    st.components.v1.html(
        html_report,
        height=950,
        scrolling=True
    )

    pdf = generate_report_card_pdf(
        student_name,
        selected_sr,
        report_class,
        report_section,
        report_exam,
        report_rows,
        total_obtained,
        total_max,
        percentage,
        grade,
        result,
        rank,
    )

    if pdf:
        st.download_button(
            "📥 Download Student Report Card PDF",
            data=pdf,
            file_name=(
                f"{student_name}_{report_class}_"
                f"{report_exam}_Report_Card.pdf"
            ),
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_report_{selected_sr}"
        )


# =========================================================
# PHASE 4: BULK EXCEL IMPORT
# =========================================================

def bulk_marks_import():
    st.markdown("### 📥 Bulk Marks Import")

    st.caption(
        "Excel columns: sr_no, student_name, class, section, "
        "exam_type, subject, marks_obtained, max_marks"
    )

    uploaded = st.file_uploader(
        "Upload Marks Excel",
        type=["xlsx", "xls"],
        key="bulk_marks_upload"
    )

    if uploaded is None:
        return

    try:
        imported = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"❌ Excel read error: {e}")
        return

    required = [
        "sr_no",
        "student_name",
        "class",
        "section",
        "exam_type",
        "subject",
        "marks_obtained",
        "max_marks",
    ]

    missing = [x for x in required if x not in imported.columns]
    if missing:
        st.error("❌ Missing columns: " + ", ".join(missing))
        return

    imported = imported[required].copy()

    for col in ["marks_obtained", "max_marks"]:
        imported[col] = imported[col].apply(safe_float)

    imported["sr_no"] = imported["sr_no"].apply(safe_int)

    validation = []
    for _, r in imported.iterrows():
        if not class_allowed(r["class"]):
            validation.append(
                f"SR {r['sr_no']}: class permission denied."
            )
        if not subject_allowed(r["subject"]):
            validation.append(
                f"SR {r['sr_no']}: subject permission denied."
            )
        if r["max_marks"] <= 0:
            validation.append(
                f"SR {r['sr_no']}: invalid max_marks."
            )
        if r["marks_obtained"] < 0 or r["marks_obtained"] > r["max_marks"]:
            validation.append(
                f"SR {r['sr_no']}: invalid marks."
            )

    st.dataframe(
        imported,
        use_container_width=True,
        hide_index=True
    )

    if validation:
        st.error("❌ Validation errors found.")
        with st.expander("Validation Details"):
            for x in validation:
                st.write(f"- {x}")
        return

    if st.button(
        "💾 Import / Update All Marks",
        type="primary",
        use_container_width=True,
        key="bulk_import_save"
    ):
        records = imported.to_dict("records")
        success, failed, errors = save_marks_batch(records)

        if success:
            st.success(f"✅ {success} marks imported/updated.")
        if failed:
            st.error(f"❌ {failed} records failed.")
            with st.expander("Errors"):
                for x in errors:
                    st.write(f"- {x}")

        if success and not failed:
            st.rerun()


# =========================================================
# PHASE 4: EXPORT TEMPLATE
# =========================================================

def download_marks_template():
    template = pd.DataFrame(columns=[
        "sr_no",
        "student_name",
        "class",
        "section",
        "exam_type",
        "subject",
        "marks_obtained",
        "max_marks",
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        template.to_excel(
            writer,
            index=False,
            sheet_name="Marks Import"
        )

    st.download_button(
        "📄 Download Marks Import Template",
        data=output.getvalue(),
        file_name="Campus_ERP_Marks_Import_Template.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
        key="download_marks_template"
    )


# =========================================================
# PHASE 4: ADMIN TOOLS
# =========================================================

def render_advanced_exam_tools():
    st.subheader("🛠️ Advanced Exam Tools")

    role, _, _, _ = get_exam_permissions()

    if role != "admin":
        st.warning("🔒 Advanced Exam Tools केवल Admin के लिए उपलब्ध हैं.")
        return

    a1, a2 = st.tabs([
        "⚙️ Exam Setup",
        "📥 Bulk Import",
    ])

    with a1:
        exam_setup_ui()
        st.markdown("---")
        st.markdown("### 📄 Import Template")
        download_marks_template()

    with a2:
        bulk_marks_import()


# =========================================================
# MAIN EXAM MODULE
# =========================================================

def render_exams_module():
    st.markdown("## 📝 Exam Management & Marks")

    tab1, tab2, tab3 = st.tabs([
        "✏️ Enter / Edit Marks",
        "📊 Performance & Report Card",
        "🛠️ Advanced Exam Tools",
    ])

    with tab1:
        render_marks_entry()

    with tab2:
        render_performance_report()

    with tab3:
        render_advanced_exam_tools()
