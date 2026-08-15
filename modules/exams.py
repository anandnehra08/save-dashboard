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

        res = (
            supabase
            .table("subjects_master")
            .select("subject_name")
            .order("subject_name")
            .execute()
        )

        if res.data:

            subjects = [
                item.get("subject_name")
                for item in res.data
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
# ROLE / PERMISSION HELPERS
# =========================================================

def get_user_permissions():

    user_role = st.session_state.get(
        "user_role",
        "admin"
    )

    assigned_classes = st.session_state.get(
        "assigned_classes"
    )

    if not assigned_classes:

        single_cls = st.session_state.get(
            "assigned_class",
            "Class 10"
        )

        assigned_classes = (
            [single_cls]
            if single_cls
            else CLASSES
        )

    assigned_subjects = st.session_state.get(
        "assigned_subjects",
        ["Maths", "Science"]
    )

    if not assigned_subjects:

        assigned_subjects = [
            "Maths",
            "Science"
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
# STUDENTS
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

def get_existing_marks(
    selected_class,
    selected_section,
    selected_subject,
    selected_exam
):

    if not supabase:
        return []

    try:

        response = (
            supabase
            .table("marks")
            .select(
                "sr_no, student_name, class, section, "
                "subject, exam_type, marks_obtained, max_marks, entered_by"
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

        return response.data or []

    except Exception as e:

        st.error(
            f"❌ Existing marks fetch error: {e}"
        )

        return []


# =========================================================
# DELETE MARKS
# =========================================================

def delete_student_marks(
    sr_no,
    selected_class,
    selected_section,
    selected_subject,
    selected_exam
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

        return True

    except Exception as e:

        st.error(
            f"❌ Marks delete error: {e}"
        )

        return False


# =========================================================
# SAVE / UPDATE SINGLE MARK
# =========================================================

def save_single_mark(record):

    if not supabase:
        return False, "Supabase connection unavailable."

    try:

        # -------------------------------------------------
        # Existing record check
        # -------------------------------------------------

        existing = (
            supabase
            .table("marks")
            .select("sr_no")
            .eq(
                "sr_no",
                int(record["sr_no"])
            )
            .eq(
                "class",
                record["class"]
            )
            .eq(
                "section",
                record["section"]
            )
            .eq(
                "subject",
                record["subject"]
            )
            .eq(
                "exam_type",
                record["exam_type"]
            )
            .limit(1)
            .execute()
        )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        if existing.data:

            (
                supabase
                .table("marks")
                .update(record)
                .eq(
                    "sr_no",
                    int(record["sr_no"])
                )
                .eq(
                    "class",
                    record["class"]
                )
                .eq(
                    "section",
                    record["section"]
                )
                .eq(
                    "subject",
                    record["subject"]
                )
                .eq(
                    "exam_type",
                    record["exam_type"]
                )
                .execute()
            )

            return True, "updated"

        # -------------------------------------------------
        # INSERT
        # -------------------------------------------------

        (
            supabase
            .table("marks")
            .insert(record)
            .execute()
        )

        return True, "inserted"

    except Exception as e:

        return False, str(e)


# =========================================================
# EXCEL TEMPLATE
# =========================================================

def create_marks_template():

    columns = [
        "sr_no",
        "student_name",
        "class",
        "section",
        "subject",
        "exam_type",
        "marks_obtained",
        "max_marks"
    ]

    df = pd.DataFrame(
        columns=columns
    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Marks"
        )

    return output.getvalue()


# =========================================================
# EXPORT MARKS
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
        "max_marks",
        "entered_by"
    ]

    export_columns = [
        col
        for col in preferred_columns
        if col in df.columns
    ]

    df = df[export_columns]

    rename_columns = {
        "sr_no": "SR No",
        "student_name": "Student Name",
        "class": "Class",
        "section": "Section",
        "subject": "Subject",
        "exam_type": "Exam Type",
        "marks_obtained": "Marks Obtained",
        "max_marks": "Maximum Marks",
        "entered_by": "Entered By"
    }

    df = df.rename(
        columns=rename_columns
    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Marks"
        )

    return output.getvalue()


# =========================================================
# GRADE
# =========================================================

def calculate_grade(percentage):

    try:

        percentage = float(
            percentage
        )

    except Exception:

        return "-"

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
# RESULT CALCULATION
# =========================================================

def calculate_result(data):

    if not data:
        return None

    df = pd.DataFrame(data)

    if df.empty:
        return None

    df["marks_obtained"] = pd.to_numeric(
        df["marks_obtained"],
        errors="coerce"
    ).fillna(0)

    df["max_marks"] = pd.to_numeric(
        df["max_marks"],
        errors="coerce"
    ).fillna(0)

    total_obtained = float(
        df["marks_obtained"].sum()
    )

    total_max = float(
        df["max_marks"].sum()
    )

    percentage = (
        (total_obtained / total_max) * 100
        if total_max > 0
        else 0
    )

    return {
        "total_obtained": total_obtained,
        "total_max": total_max,
        "percentage": percentage,
        "grade": calculate_grade(
            percentage
        )
    }


# =========================================================
# PERFORMANCE DATA
# =========================================================

def get_performance_data(
    selected_class,
    selected_exam,
    selected_subject="ALL"
):

    if not supabase:
        return []

    try:

        query = (
            supabase
            .table("marks")
            .select(
                "sr_no, student_name, class, section, "
                "subject, exam_type, marks_obtained, max_marks"
            )
            .eq(
                "class",
                selected_class
            )
            .eq(
                "exam_type",
                selected_exam
            )
        )

        if selected_subject != "ALL":

            query = query.eq(
                "subject",
                selected_subject
            )

        response = query.execute()

        return response.data or []

    except Exception as e:

        st.error(
            f"❌ Report fetch error: {e}"
        )

        return []


# =========================================================
# CLASS RESULT SUMMARY
# =========================================================

def build_student_summary(
    marks_data
):

    if not marks_data:
        return pd.DataFrame()

    df = pd.DataFrame(
        marks_data
    )

    required = [
        "sr_no",
        "student_name",
        "marks_obtained",
        "max_marks"
    ]

    for column in required:

        if column not in df.columns:

            return pd.DataFrame()

    df["marks_obtained"] = pd.to_numeric(
        df["marks_obtained"],
        errors="coerce"
    ).fillna(0)

    df["max_marks"] = pd.to_numeric(
        df["max_marks"],
        errors="coerce"
    ).fillna(0)

    grouped = (
        df
        .groupby(
            [
                "sr_no",
                "student_name"
            ],
            as_index=False
        )
        .agg(
            total_marks=(
                "marks_obtained",
                "sum"
            ),
            max_marks=(
                "max_marks",
                "sum"
            )
        )
    )

    grouped["percentage"] = (
        grouped["total_marks"]
        /
        grouped["max_marks"]
        .replace(0, pd.NA)
        * 100
    )

    grouped["percentage"] = (
        pd.to_numeric(
            grouped["percentage"],
            errors="coerce"
        )
        .fillna(0)
        .round(2)
    )

    grouped["grade"] = (
        grouped["percentage"]
        .apply(
            calculate_grade
        )
    )

    grouped = grouped.sort_values(
        by=[
            "percentage",
            "total_marks"
        ],
        ascending=False
    )

    grouped["rank"] = (
        grouped["percentage"]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    return grouped


# =========================================================
# STUDENT RESULT CARD
# =========================================================

def render_student_result_card(
    student_data
):

    if student_data is None:
        return

    total = student_data.get(
        "total_marks",
        0
    )

    maximum = student_data.get(
        "max_marks",
        0
    )

    percentage = student_data.get(
        "percentage",
        0
    )

    grade = student_data.get(
        "grade",
        "-"
    )

    rank = student_data.get(
        "rank",
        "-"
    )

    st.markdown(
        f"""
        <div style="
            border:1px solid #d1d5db;
            border-radius:12px;
            padding:18px;
            margin-top:15px;
            background:#ffffff;
        ">

        <h3 style="margin-top:0;">
        🎓 {student_data.get("student_name", "Student")}
        </h3>

        <p>
        <b>SR No:</b>
        {student_data.get("sr_no", "-")}
        </p>

        <hr>

        <p>
        <b>Total:</b>
        {total:g} / {maximum:g}
        </p>

        <p>
        <b>Percentage:</b>
        {percentage:.2f}%
        </p>

        <p>
        <b>Grade:</b>
        {grade}
        </p>

        <p>
        <b>Rank:</b>
        {rank}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# MARKS ENTRY
# =========================================================

def render_marks_entry(
    all_subjects,
    assigned_classes,
    assigned_subjects,
    is_teacher
):

    st.subheader(
        "✏️ Enter / Edit Marks"
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

            selected_class = st.selectbox(
                "Select Class",
                assigned_classes,
                key="ex_cls"
            )

        else:

            selected_class = st.selectbox(
                "Select Class",
                CLASSES,
                key="ex_cls"
            )

    with c2:

        selected_sec = st.selectbox(
            "Select Section",
            SECTIONS,
            key="ex_sec"
        )

    with c3:

        if (
            is_teacher
            and "ALL" not in assigned_subjects
        ):

            available_subjects = (
                assigned_subjects
            )

        else:

            available_subjects = (
                all_subjects
            )

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

            col_sub1, col_sub2 = st.columns(
                [3, 1]
            )

            with col_sub1:

                new_sub_input = st.text_input(
                    "Enter New Subject Name",
                    key="new_sub_txt",
                    placeholder=(
                        "e.g. Computer Science"
                    )
                )

            with col_sub2:

                st.write("")

                st.write("")

                add_sub_btn = st.button(
                    "Save Subject",
                    use_container_width=True,
                    key="save_new_subject"
                )

            if add_sub_btn:

                clean_sub = (
                    new_sub_input
                    .strip()
                )

                if not clean_sub:

                    st.warning(
                        "कृपया विषय का नाम लिखें।"
                    )

                elif not supabase:

                    st.error(
                        "❌ Supabase connection नहीं है."
                    )

                else:

                    try:

                        # Duplicate subject check
                        existing = (
                            supabase
                            .table("subjects_master")
                            .select(
                                "subject_name"
                            )
                            .eq(
                                "subject_name",
                                clean_sub
                            )
                            .execute()
                        )

                        if existing.data:

                            st.warning(
                                f"⚠️ Subject "
                                f"'{clean_sub}' "
                                "पहले से मौजूद है."
                            )

                        else:

                            (
                                supabase
                                .table(
                                    "subjects_master"
                                )
                                .insert(
                                    {
                                        "subject_name":
                                            clean_sub
                                    }
                                )
                                .execute()
                            )

                            st.success(
                                f"✅ Subject "
                                f"'{clean_sub}' "
                                "मास्टर लिस्ट में जुड़ गया."
                            )

                            st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Subject जोड़ने में "
                            f"त्रुटि: {e}"
                        )

    st.markdown("---")

    # =====================================================
    # STUDENTS
    # =====================================================

    students = get_students(
        selected_class,
        selected_sec
    )

    if not students:

        st.warning(
            f"⚠️ No students found in "
            f"{selected_class} - "
            f"{selected_sec}."
        )

        return

    # =====================================================
    # EXISTING MARKS
    # =====================================================

    existing_marks = get_existing_marks(
        selected_class,
        selected_sec,
        selected_subject,
        selected_exam
    )

    existing_map = {}

    for mark in existing_marks:

        try:

            existing_map[
                int(mark["sr_no"])
            ] = (
                float(
                    mark.get(
                        "marks_obtained",
                        0
                    ) or 0
                ),
                float(
                    mark.get(
                        "max_marks",
                        100
                    ) or 100
                )
            )

        except Exception:

            continue

    # =====================================================
    # MAX MARKS
    # =====================================================

    previous_max = 100

    if existing_marks:

        try:

            previous_max = int(
                float(
                    existing_marks[0].get(
                        "max_marks",
                        100
                    ) or 100
                )
            )

        except Exception:

            previous_max = 100

    max_marks_input = st.number_input(
        "Maximum Marks for this Test",
        min_value=1,
        max_value=1000,
        value=previous_max,
        step=1,
        key="max_marks_input"
    )

    st.markdown(
        f"""
        **Student Marks List
        ({selected_subject} - {selected_exam})**
        """
    )

    # =====================================================
    # MARKS FORM
    # =====================================================

    with st.form(
        "marks_entry_form"
    ):

        marks_payload = []

        for st_data in students:

            sr = int(
                st_data.get(
                    "sr_no",
                    0
                )
            )

            name = st_data.get(
                "student_name",
                "N/A"
            )

            roll = st_data.get(
                "roll_no",
                0
            )

            previous_marks = (
                existing_map.get(
                    sr,
                    (
                        0.0,
                        float(
                            max_marks_input
                        )
                    )
                )[0]
            )

            mc1, mc2, mc3 = st.columns(
                [1, 3, 2]
            )

            with mc1:

                st.write(
                    f"**Roll #{roll}**"
                )

            with mc2:

                st.write(
                    f"**{name}** "
                    f"(SR: {sr})"
                )

            with mc3:

                obtained_marks = st.number_input(
                    label=f"Marks for {sr}",
                    min_value=0.0,
                    max_value=float(
                        max_marks_input
                    ),
                    value=min(
                        float(
                            previous_marks
                        ),
                        float(
                            max_marks_input
                        )
                    ),
                    step=0.5,
                    key=(
                        f"marks_{sr}_"
                        f"{selected_subject}_"
                        f"{selected_exam}"
                    ),
                    label_visibility="collapsed"
                )

            marks_payload.append(
                {
                    "sr_no":
                        sr,

                    "student_name":
                        name,

                    "class":
                        selected_class,

                    "section":
                        selected_sec,

                    "subject":
                        selected_subject,

                    "exam_type":
                        selected_exam,

                    "marks_obtained":
                        float(
                            obtained_marks
                        ),

                    "max_marks":
                        float(
                            max_marks_input
                        ),

                    "entered_by":
                        st.session_state.get(
                            "user_email",
                            "Teacher"
                        )
                }
            )

        submit_marks = st.form_submit_button(
            "💾 Save / Update All Marks",
            use_container_width=True,
            type="primary"
        )

        if submit_marks:

            success_count = 0
            error_list = []

            for record in marks_payload:

                # -----------------------------------------
                # Validation
                # -----------------------------------------

                obtained = float(
                    record[
                        "marks_obtained"
                    ]
                )

                maximum = float(
                    record[
                        "max_marks"
                    ]
                )

                if obtained < 0:

                    error_list.append(
                        f"SR {record['sr_no']}: "
                        "Marks cannot be negative."
                    )

                    continue

                if obtained > maximum:

                    error_list.append(
                        f"SR {record['sr_no']}: "
                        "Marks maximum से ज्यादा हैं."
                    )

                    continue

                # -----------------------------------------
                # Save / Update
                # -----------------------------------------

                success, message = (
                    save_single_mark(
                        record
                    )
                )

                if success:

                    success_count += 1

                else:

                    error_list.append(
                        f"SR {record['sr_no']}: "
                        f"{message}"
                    )

            if success_count:

                st.success(
                    f"✅ {success_count} "
                    "students के marks "
                    "save/update हो गए."
                )

            if error_list:

                with st.expander(
                    "⚠️ Save Details"
                ):

                    for error in error_list:

                        st.write(
                            f"- {error}"
                        )

    # =====================================================
    # EXISTING MARKS MANAGEMENT
    # =====================================================

    refreshed_marks = get_existing_marks(
        selected_class,
        selected_sec,
        selected_subject,
        selected_exam
    )

    if refreshed_marks:

        st.markdown("---")

        st.subheader(
            "🗑️ Saved Marks Management"
        )

        marks_df = pd.DataFrame(
            refreshed_marks
        )

        display_columns = [
            "sr_no",
            "student_name",
            "marks_obtained",
            "max_marks"
        ]

        display_columns = [
            column
            for column in display_columns
            if column in marks_df.columns
        ]

        st.dataframe(
            marks_df[
                display_columns
            ],
            use_container_width=True,
            hide_index=True
        )

        student_options = {
            f"{row.get('student_name', 'N/A')} "
            f"(SR: {row.get('sr_no')})":
                int(row.get("sr_no"))
            for row in refreshed_marks
        }

        selected_delete_label = st.selectbox(
            "Select Student for Delete",
            list(
                student_options.keys()
            ),
            key="marks_delete_student"
        )

        selected_delete_sr = (
            student_options[
                selected_delete_label
            ]
        )

        if st.button(
            "🗑️ Delete Selected Student Marks",
            use_container_width=True,
            key="delete_marks_record"
        ):

            if delete_student_marks(
                selected_delete_sr,
                selected_class,
                selected_sec,
                selected_subject,
                selected_exam
            ):

                st.success(
                    "✅ Student marks deleted successfully."
                )

                st.rerun()


# =========================================================
# EXCEL IMPORT
# =========================================================

def render_marks_excel_tools(
    assigned_classes,
    assigned_subjects,
    is_teacher
):

    st.markdown("---")

    st.subheader(
        "📥📤 Excel Marks Tools"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.download_button(
            "📄 Download Marks Template",
            data=create_marks_template(),
            file_name="marks_import_template.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
            key="marks_template_download"
        )

    with c2:

        uploaded_marks_file = st.file_uploader(
            "📥 Import Marks Excel",
            type=["xlsx"],
            key="marks_excel_upload"
        )

    # =====================================================
    # EXPORT
    # =====================================================

    with c3:

        export_class = st.selectbox(
            "Export Class",
            (
                assigned_classes
                if (
                    is_teacher
                    and "ALL" not in assigned_classes
                )
                else CLASSES
            ),
            key="marks_export_class"
        )

        if supabase:

            try:

                export_data = (
                    supabase
                    .table("marks")
                    .select("*")
                    .eq(
                        "class",
                        export_class
                    )
                    .execute()
                )

                if export_data.data:

                    st.download_button(
                        "📤 Export Marks",
                        data=create_marks_excel(
                            export_data.data
                        ),
                        file_name=(
                            f"{export_class}"
                            "_marks.xlsx"
                        ),
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                        use_container_width=True,
                        key="marks_export_download"
                    )

                else:

                    st.caption(
                        "No marks available."
                    )

            except Exception as e:

                st.caption(
                    f"Export error: {e}"
                )

    # =====================================================
    # IMPORT
    # =====================================================

    if uploaded_marks_file is None:
        return

    try:

        import_df = pd.read_excel(
            uploaded_marks_file
        )

        required_columns = [
            "sr_no",
            "student_name",
            "class",
            "section",
            "subject",
            "exam_type",
            "marks_obtained",
            "max_marks"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in import_df.columns
        ]

        if missing_columns:

            st.error(
                "❌ Missing columns: "
                +
                ", ".join(
                    missing_columns
                )
            )

            return

        st.success(
            f"✅ Excel loaded successfully — "
            f"{len(import_df)} rows found."
        )

        st.dataframe(
            import_df,
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "🚀 Import Marks into Supabase",
            type="primary",
            use_container_width=True,
            key="import_marks_to_supabase"
        ):

            success_count = 0
            error_list = []

            for index, row in import_df.iterrows():

                try:

                    sr_no = int(
                        row["sr_no"]
                    )

                    marks_obtained = float(
                        row["marks_obtained"]
                    )

                    max_marks = float(
                        row["max_marks"]
                    )

                    if marks_obtained < 0:

                        raise ValueError(
                            "Marks cannot be negative."
                        )

                    if max_marks <= 0:

                        raise ValueError(
                            "Maximum marks must be greater than 0."
                        )

                    if marks_obtained > max_marks:

                        raise ValueError(
                            "Marks cannot exceed maximum marks."
                        )

                    record = {

                        "sr_no":
                            sr_no,

                        "student_name":
                            str(
                                row[
                                    "student_name"
                                ]
                            ).strip(),

                        "class":
                            str(
                                row["class"]
                            ).strip(),

                        "section":
                            str(
                                row["section"]
                            ).strip(),

                        "subject":
                            str(
                                row["subject"]
                            ).strip(),

                        "exam_type":
                            str(
                                row["exam_type"]
                            ).strip(),

                        "marks_obtained":
                            marks_obtained,

                        "max_marks":
                            max_marks,

                        "entered_by":
                            st.session_state.get(
                                "user_email",
                                "Excel Import"
                            )
                    }

                    success, message = (
                        save_single_mark(
                            record
                        )
                    )

                    if success:

                        success_count += 1

                    else:

                        error_list.append(
                            f"Row {index + 2}: "
                            f"{message}"
                        )

                except Exception as e:

                    error_list.append(
                        f"Row {index + 2}: {e}"
                    )

            if success_count:

                st.success(
                    f"✅ {success_count} marks "
                    "records imported/updated."
                )

            if error_list:

                with st.expander(
                    "⚠️ Import Details"
                ):

                    for error in error_list:

                        st.write(
                            f"- {error}"
                        )

    except Exception as e:

        st.error(
            f"❌ Excel file पढ़ने में error: {e}"
        )


# =========================================================
# PERFORMANCE REPORT
# =========================================================

def render_performance_report(
    all_subjects,
    assigned_classes,
    assigned_subjects,
    is_teacher
):

    st.subheader(
        "📊 Class Performance & Report Card"
    )

    rc1, rc2, rc3 = st.columns(3)

    with rc1:

        rep_classes = (
            assigned_classes
            if (
                is_teacher
                and "ALL" not in assigned_classes
            )
            else CLASSES
        )

        rep_class = st.selectbox(
            "Select Class",
            rep_classes,
            key="rep_ex_cls"
        )

    with rc2:

        rep_exam = st.selectbox(
            "Select Exam",
            EXAM_TYPES,
            key="rep_ex_type"
        )

    with rc3:

        rep_subject_list = (
            ["ALL"]
            +
            (
                assigned_subjects
                if (
                    is_teacher
                    and "ALL" not in assigned_subjects
                )
                else all_subjects
            )
        )

        rep_subject = st.selectbox(
            "Select Subject Filter",
            rep_subject_list,
            key="rep_ex_sub"
        )

    # =====================================================
    # GET DATA
    # =====================================================

    marks_data = get_performance_data(
        rep_class,
        rep_exam,
        rep_subject
    )

    if not marks_data:

        st.warning(
            "चुनी गई Class और Exam के लिए "
            "कोई marks data उपलब्ध नहीं है."
        )

        return

    mdf = pd.DataFrame(
        marks_data
    )

    # =====================================================
    # RAW MARKS
    # =====================================================

    st.markdown(
        "### 📋 Marks Data"
    )

    raw_columns = [
        "sr_no",
        "student_name",
        "subject",
        "marks_obtained",
        "max_marks"
    ]

    raw_columns = [
        column
        for column in raw_columns
        if column in mdf.columns
    ]

    st.dataframe(
        mdf[raw_columns],
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    summary_df = build_student_summary(
        marks_data
    )

    if summary_df.empty:
        return

    st.markdown("---")

    st.markdown(
        "### 🏆 Student Performance Summary"
    )

    summary_display = summary_df.rename(
        columns={
            "sr_no": "SR No",
            "student_name": "Student Name",
            "total_marks": "Total Marks",
            "max_marks": "Maximum Marks",
            "percentage": "Percentage",
            "grade": "Grade",
            "rank": "Rank"
        }
    )

    st.dataframe(
        summary_display,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # CLASS ANALYTICS
    # =====================================================

    total_students = len(
        summary_df
    )

    average_percentage = float(
        summary_df[
            "percentage"
        ].mean()
    )

    highest_percentage = float(
        summary_df[
            "percentage"
        ].max()
    )

    passed_students = int(
        (
            summary_df[
                "percentage"
            ] >= 40
        ).sum()
    )

    a1, a2, a3, a4 = st.columns(4)

    with a1:

        st.metric(
            "👨‍🎓 Students",
            total_students
        )

    with a2:

        st.metric(
            "📊 Average %",
            f"{average_percentage:.2f}%"
        )

    with a3:

        st.metric(
            "🏆 Highest %",
            f"{highest_percentage:.2f}%"
        )

    with a4:

        st.metric(
            "✅ Passed",
            passed_students
        )

    # =====================================================
    # STUDENT RESULT VIEW
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 🎓 Student Result"
    )

    student_options = {
        f"{row['student_name']} "
        f"(SR: {row['sr_no']})":
            int(row["sr_no"])
        for _, row
        in summary_df.iterrows()
    }

    selected_student_label = st.selectbox(
        "Select Student",
        list(
            student_options.keys()
        ),
        key="report_student_select"
    )

    selected_student_sr = (
        student_options[
            selected_student_label
        ]
    )

    selected_rows = summary_df[
        summary_df["sr_no"]
        == selected_student_sr
    ]

    if not selected_rows.empty:

        student_result = (
            selected_rows.iloc[0]
            .to_dict()
        )

        render_student_result_card(
            student_result
        )

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    report_export = summary_df.rename(
        columns={
            "sr_no": "SR No",
            "student_name": "Student Name",
            "total_marks": "Total Marks",
            "max_marks": "Maximum Marks",
            "percentage": "Percentage",
            "grade": "Grade",
            "rank": "Rank"
        }
    )

    report_csv = report_export.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        "📥 Download Result CSV",
        data=report_csv,
        file_name=(
            f"{rep_class}_"
            f"{rep_exam}_result.csv"
        ),
        mime="text/csv",
        use_container_width=True,
        key="download_result_csv"
    )


# =========================================================
# MAIN EXAM MODULE
# =========================================================

def render_exams_module():

    st.markdown(
        "## 📝 Exam Management & Marks Entry"
    )

    # =====================================================
    # SUPABASE CHECK
    # =====================================================

    if not supabase:

        st.error(
            "❌ Supabase connection उपलब्ध नहीं है."
        )

        return

    # =====================================================
    # SUBJECTS
    # =====================================================

    all_subjects = get_master_subjects()

    # =====================================================
    # PERMISSIONS
    # =====================================================

    (
        user_role,
        assigned_classes,
        assigned_subjects,
        is_teacher
    ) = get_user_permissions()

    # =====================================================
    # TEACHER INFO
    # =====================================================

    if is_teacher:

        st.info(
            f"🔒 **Teacher Access:** "
            f"आपके पास "
            f"**{', '.join(assigned_classes)}** "
            f"क्लासेस और "
            f"**{', '.join(assigned_subjects)}** "
            f"सब्जेक्ट(स) के marks manage करने की अनुमति है."
        )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "✏️ Enter / Edit Marks",
            "📊 Class Performance & Report Card",
            "📥📤 Excel Tools"
        ]
    )

    # =====================================================
    # TAB 1
    # =====================================================

    with tab1:

        render_marks_entry(
            all_subjects,
            assigned_classes,
            assigned_subjects,
            is_teacher
        )

    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        render_performance_report(
            all_subjects,
            assigned_classes,
            assigned_subjects,
            is_teacher
        )

    # =====================================================
    # TAB 3
    # =====================================================

    with tab3:

        render_marks_excel_tools(
            assigned_classes,
            assigned_subjects,
            is_teacher
        )
