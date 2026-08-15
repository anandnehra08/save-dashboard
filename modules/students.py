import io
import pandas as pd
import streamlit as st
from database.supabase import supabase
import streamlit.components.v1 as components

# =========================================================
# CONSTANTS
# =========================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["All", "A", "B", "C", "D"]

STUDENT_COLUMNS = [
    "sr_no",
    "student_name",
    "father_name",
    "mother_name",
    "class",
    "section",
    "roll_no",
    "gender",
    "mobile",
    "bus_route",
    "drop_point",
    "aadhaar"
]

EXCEL_COLUMN_NAMES = {
    "sr_no": "SR No",
    "student_name": "Student Name",
    "father_name": "Father Name",
    "mother_name": "Mother Name",
    "class": "Class",
    "section": "Section",
    "roll_no": "Roll No",
    "gender": "Gender",
    "mobile": "Mobile",
    "bus_route": "Bus Route",
    "drop_point": "Drop Point",
    "aadhaar": "Aadhaar / ID"
}


# =========================================================
# LOAD STUDENTS
# =========================================================

def load_students():

    if not supabase:
        return None

    try:

        response = (
            supabase
            .table("students")
            .select("*")
            .order("sr_no")
            .execute()
        )

        return response.data or []

    except Exception as e:

        st.error(
            f"❌ Error fetching students: {e}"
        )

        return None


# =========================================================
# EXCEL TEMPLATE
# =========================================================

def create_excel_template():

    template_df = pd.DataFrame(
        columns=STUDENT_COLUMNS
    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        template_df.to_excel(
            writer,
            index=False,
            sheet_name="Students"
        )

    return output.getvalue()


# =========================================================
# EXPORT EXCEL
# =========================================================

def create_student_excel(data):

    if not data:
        return None

    df = pd.DataFrame(data)

    export_columns = [
        column
        for column in STUDENT_COLUMNS
        if column in df.columns
    ]

    df = df[export_columns]

    df = df.rename(
        columns=EXCEL_COLUMN_NAMES
    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Students"
        )

    return output.getvalue()


# =========================================================
# VALIDATE EXCEL
# =========================================================

def validate_excel_dataframe(df):

    required_columns = [
        "sr_no",
        "student_name",
        "class",
        "section"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        return False, (
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    if df.empty:

        return False, "Excel file खाली है।"

    return True, ""


# =========================================================
# TAB 1 — NEW ADMISSION
# =========================================================

def render_new_admission():

    with st.form(
        key="student_admission_form_v1",
        clear_on_submit=True
    ):

        st.subheader(
            "Student Personal & Academic Details"
        )

        c1, c2 = st.columns(2)

        with c1:

            sr_no = st.number_input(
                "SR Number*",
                min_value=1,
                step=1
            )

            student_name = st.text_input(
                "Student Full Name*"
            )

            father_name = st.text_input(
                "Father's Name"
            )

            mother_name = st.text_input(
                "Mother's Name"
            )

            class_name = st.selectbox(
                "Class*",
                CLASSES
            )

            bus_route = st.text_input(
                "Bus Route (Optional)"
            )

        with c2:

            roll_no = st.number_input(
                "Roll Number",
                min_value=1,
                step=1
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

            section = st.selectbox(
                "Section*",
                ["A", "B", "C", "D"]
            )

            mobile = st.text_input(
                "Contact Mobile Number"
            )

            aadhaar = st.text_input(
                "Aadhaar / ID Reference (Optional)"
            )

            drop_point = st.text_input(
                "Drop Point (Optional)"
            )

        submitted = st.form_submit_button(
            "💾 Save Student Record",
            use_container_width=True
        )

        if submitted:

            if not student_name.strip():

                st.error(
                    "Please enter the student's name."
                )

                return

            if supabase:

                record = {
                    "sr_no": int(sr_no),
                    "student_name": student_name.strip(),
                    "roll_no": int(roll_no),
                    "gender": gender,
                    "class": class_name,
                    "section": section,
                    "father_name": father_name.strip(),
                    "mother_name": mother_name.strip(),
                    "mobile": mobile.strip(),
                    "bus_route": bus_route.strip(),
                    "drop_point": drop_point.strip(),
                    "aadhaar": aadhaar.strip()
                }

                try:

                    supabase.table(
                        "students"
                    ).insert(record).execute()

                    st.success(
                        f"✅ Student **{student_name}** "
                        f"(SR: {sr_no}) created successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Error saving to database: {e}"
                    )


# =========================================================
# TAB 2 — LIVE DIRECTORY
# =========================================================

def render_live_directory():

    st.subheader(
        "📋 Live Student Directory"
    )

    students = load_students()

    if students is None:
        return

    # =====================================================
    # EXCEL TOOLS
    # =====================================================

    st.markdown("### 📥📤 Excel Tools")

    excel_col1, excel_col2, excel_col3 = st.columns(3)

    with excel_col1:

        st.download_button(
            label="📄 Download Excel Template",
            data=create_excel_template(),
            file_name="student_import_template.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
            key="download_student_template"
        )

    with excel_col2:

        uploaded_file = st.file_uploader(
            "📥 Import Students from Excel",
            type=["xlsx"],
            key="student_excel_upload"
        )

    with excel_col3:

        if students:

            excel_data = create_student_excel(
                students
            )

            st.download_button(
                label="📤 Export Students to Excel",
                data=excel_data,
                file_name="student_directory.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
                key="export_students_excel"
            )

        else:

            st.info(
                "No students available for export."
            )

    # =====================================================
    # EXCEL IMPORT
    # =====================================================

    if uploaded_file is not None:

        try:

            import_df = pd.read_excel(
                uploaded_file
            )

            # Convert Excel column names to database names
            reverse_columns = {
                value: key
                for key, value
                in EXCEL_COLUMN_NAMES.items()
            }

            import_df = import_df.rename(
                columns=reverse_columns
            )

            valid, error_message = (
                validate_excel_dataframe(
                    import_df
                )
            )

            if not valid:

                st.error(
                    f"❌ Excel validation failed: "
                    f"{error_message}"
                )

            else:

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
                    "🚀 Import Students into Supabase",
                    type="primary",
                    use_container_width=True,
                    key="import_students_to_supabase"
                ):

                    success_count = 0
                    skipped_count = 0
                    error_list = []

                    for index, row in import_df.iterrows():

                        try:

                            sr_no_value = int(
                                row["sr_no"]
                            )

                            student_name_value = str(
                                row["student_name"]
                            ).strip()

                            if not student_name_value:

                                skipped_count += 1

                                error_list.append(
                                    f"Row {index + 2}: "
                                    "Student name missing"
                                )

                                continue

                            # ---------------------------------
                            # Check duplicate SR No
                            # ---------------------------------

                            existing = (
                                supabase
                                .table("students")
                                .select("sr_no")
                                .eq(
                                    "sr_no",
                                    sr_no_value
                                )
                                .execute()
                            )

                            if existing.data:

                                skipped_count += 1

                                error_list.append(
                                    f"Row {index + 2}: "
                                    f"SR No {sr_no_value} "
                                    "already exists"
                                )

                                continue

                            # ---------------------------------
                            # Prepare record
                            # ---------------------------------

                            def clean_value(column):

                                if column not in row:
                                    return ""

                                value = row[column]

                                if pd.isna(value):
                                    return ""

                                return str(value).strip()

                            record = {
                                "sr_no": sr_no_value,
                                "student_name":
                                    student_name_value,
                                "father_name":
                                    clean_value("father_name"),
                                "mother_name":
                                    clean_value("mother_name"),
                                "class":
                                    clean_value("class"),
                                "section":
                                    clean_value("section"),
                                "roll_no":
                                    int(
                                        row["roll_no"]
                                    )
                                    if (
                                        "roll_no" in row
                                        and not pd.isna(
                                            row["roll_no"]
                                        )
                                    )
                                    else 0,
                                "gender":
                                    clean_value("gender"),
                                "mobile":
                                    clean_value("mobile"),
                                "bus_route":
                                    clean_value("bus_route"),
                                "drop_point":
                                    clean_value("drop_point"),
                                "aadhaar":
                                    clean_value("aadhaar")
                            }

                            supabase.table(
                                "students"
                            ).insert(record).execute()

                            success_count += 1

                        except Exception as e:

                            error_list.append(
                                f"Row {index + 2}: {e}"
                            )

                    # -----------------------------------------
                    # Import Result
                    # -----------------------------------------

                    st.markdown("---")

                    if success_count:

                        st.success(
                            f"✅ {success_count} students "
                            "imported successfully."
                        )

                    if skipped_count:

                        st.warning(
                            f"⚠️ {skipped_count} rows skipped."
                        )

                    if error_list:

                        with st.expander(
                            "⚠️ Import Details"
                        ):

                            for error in error_list:

                                st.write(
                                    f"- {error}"
                                )

                    if success_count:

                        st.rerun()

        except Exception as e:

            st.error(
                f"❌ Excel file पढ़ने में error: {e}"
            )

    # =====================================================
    # FILTERS
    # =====================================================

    if students:

        df = pd.DataFrame(students)

        st.markdown("---")
        st.markdown("### 🔎 Search & Filter")

        f1, f2, f3 = st.columns(
            [2, 1, 1]
        )

        with f1:

            search_text = st.text_input(
                "🔍 Search Student",
                placeholder=(
                    "Name / SR No / Roll No / Mobile"
                ),
                key="student_fast_search"
            )

        with f2:

            class_filter = st.selectbox(
                "📚 Class",
                ["All"] + CLASSES,
                key="student_class_filter"
            )

        with f3:

            section_filter = st.selectbox(
                "📌 Section",
                SECTIONS,
                key="student_section_filter"
            )

        filtered_df = df.copy()

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search_text.strip():

            search_value = (
                search_text
                .strip()
                .lower()
            )

            mask = pd.Series(
                False,
                index=filtered_df.index
            )

            for column in [
                "student_name",
                "sr_no",
                "roll_no",
                "mobile"
            ]:

                if column in filtered_df.columns:

                    mask = (
                        mask
                        |
                        filtered_df[column]
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            search_value,
                            na=False
                        )
                    )

            filtered_df = filtered_df[mask]

        # -------------------------------------------------
        # Class
        # -------------------------------------------------

        if class_filter != "All":

            filtered_df = filtered_df[
                filtered_df["class"]
                == class_filter
            ]

        # -------------------------------------------------
        # Section
        # -------------------------------------------------

        if section_filter != "All":

            filtered_df = filtered_df[
                filtered_df["section"]
                == section_filter
            ]

        # -------------------------------------------------
        # Count
        # -------------------------------------------------

        st.metric(
            "👨‍🎓 Students Found",
            len(filtered_df)
        )

        # -------------------------------------------------
        # Display
        # -------------------------------------------------

        display_df = filtered_df.rename(
            columns=EXCEL_COLUMN_NAMES
        )

        display_cols = [
            "SR No",
            "Student Name",
            "Father Name",
            "Mother Name",
            "Class",
            "Section",
            "Roll No",
            "Gender",
            "Mobile",
            "Bus Route",
            "Drop Point"
        ]

        display_cols = [
            column
            for column in display_cols
            if column in display_df.columns
        ]

        if not filtered_df.empty:

            st.dataframe(
                display_df[display_cols],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "🔍 No student found with these filters."
            )

    else:

        st.info(
            "📭 No students found in database."
        )

def render_student_profile(student):
    st.markdown("---")
    st.markdown(
        f"""
        <div class="student-profile">
            <h2>🎓 Student Profile</h2>
            <h3>{student.get("student_name", "N/A")}</h3>
            <p><b>SR No:</b> {student.get("sr_no", "N/A")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 👤 Personal Details")
        st.write(f"**Student Name:** {student.get('student_name', 'N/A')}")
        st.write(f"**Father Name:** {student.get('father_name', 'N/A')}")
        st.write(f"**Mother Name:** {student.get('mother_name', 'N/A')}")
        st.write(f"**Gender:** {student.get('gender', 'N/A')}")

    with c2:
        st.markdown("### 📚 Academic Details")
        st.write(f"**SR No:** {student.get('sr_no', 'N/A')}")
        st.write(f"**Roll No:** {student.get('roll_no', 'N/A')}")
        st.write(f"**Class:** {student.get('class', 'N/A')}")
        st.write(f"**Section:** {student.get('section', 'N/A')}")

    with c3:
        st.markdown("### 🚌 Contact & Transport")
        st.write(f"**Mobile:** {student.get('mobile') or 'N/A'}")
        st.write(f"**Bus Route:** {student.get('bus_route') or 'N/A'}")
        st.write(f"**Drop Point:** {student.get('drop_point') or 'N/A'}")
        st.write(
            f"**Aadhaar / ID:** "
            f"{'Available' if student.get('aadhaar') else 'Not Available'}"
        )

    st.markdown("---")

    profile_text = f"""
CAMPUS ERP PRO
STUDENT PROFILE

Student Name : {student.get('student_name', 'N/A')}
SR No        : {student.get('sr_no', 'N/A')}
Roll No      : {student.get('roll_no', 'N/A')}
Class        : {student.get('class', 'N/A')}
Section      : {student.get('section', 'N/A')}
Gender       : {student.get('gender', 'N/A')}

Father Name  : {student.get('father_name', 'N/A')}
Mother Name  : {student.get('mother_name', 'N/A')}
Mobile       : {student.get('mobile') or 'N/A'}
Bus Route    : {student.get('bus_route') or 'N/A'}
Drop Point   : {student.get('drop_point') or 'N/A'}
Aadhaar/ID   : {student.get('aadhaar') or 'N/A'}
"""

    st.download_button(
        "📄 Download Student Profile",
        data=profile_text,
        file_name=f"student_{student.get('sr_no', 'record')}.txt",
        mime="text/plain",
        use_container_width=True,
        key=f"download_profile_{student.get('sr_no')}"
    )
def render_print_student_profile(student):

    import streamlit.components.v1 as components

    student_name = str(student.get("student_name") or "N/A")
    sr_no = str(student.get("sr_no") or "N/A")
    father_name = str(student.get("father_name") or "N/A")
    mother_name = str(student.get("mother_name") or "N/A")
    gender = str(student.get("gender") or "N/A")
    roll_no = str(student.get("roll_no") or "N/A")
    class_name = str(student.get("class") or "N/A")
    section = str(student.get("section") or "N/A")
    mobile = str(student.get("mobile") or "N/A")
    bus_route = str(student.get("bus_route") or "N/A")
    drop_point = str(student.get("drop_point") or "N/A")

    aadhaar_status = (
        "Available"
        if student.get("aadhaar")
        else "Not Available"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>

    <meta charset="UTF-8">

    <style>

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        padding: 10px;
        font-family: Arial, sans-serif;
        background: #f3f4f6;
    }}

    .print-profile {{
        width: 100%;
        max-width: 850px;
        margin: auto;
        background: white;
        border: 2px solid #1e3a8a;
        border-radius: 12px;
        padding: 28px;
        color: #111827;
    }}

    .print-title {{
        text-align: center;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 15px;
        margin-bottom: 22px;
    }}

    .print-title h1 {{
        margin: 0;
        color: #1e3a8a;
        font-size: 28px;
    }}

    .print-title p {{
        margin: 6px 0;
        color: #374151;
    }}

    .profile-section {{
        margin-top: 20px;
    }}

    .profile-section h3 {{
        margin: 0;
        background: #eef2ff;
        padding: 9px 12px;
        border-left: 5px solid #1e3a8a;
        color: #1e3a8a;
        font-size: 17px;
    }}

    .profile-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
    }}

    .profile-table td {{
        border: 1px solid #d1d5db;
        padding: 10px;
        font-size: 14px;
    }}

    .profile-label {{
        width: 32%;
        font-weight: bold;
        background: #f9fafb;
    }}

    .signature-area {{
        margin-top: 65px;
    }}

    .signature-table {{
        width: 100%;
    }}

    .signature-table td {{
        text-align: center;
        border: none;
        padding: 10px;
    }}

    .signature-line {{
        height: 55px;
    }}

    .footer {{
        text-align: center;
        margin-top: 20px;
        font-size: 11px;
        color: #6b7280;
    }}

    .print-btn {{
        width: 100%;
        margin-top: 15px;
        padding: 12px;
        border: none;
        border-radius: 8px;
        background: #1e3a8a;
        color: white;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }}

    .print-btn:hover {{
        opacity: 0.9;
    }}

    @media print {{

        body {{
            background: white;
            padding: 0;
        }}

        .print-profile {{
            max-width: none;
            border: 2px solid #1e3a8a;
            border-radius: 0;
            padding: 20px;
        }}

        .print-btn {{
            display: none !important;
        }}

        @page {{
            size: A4;
            margin: 12mm;
        }}

    }}

    </style>

    </head>

    <body>

    <div class="print-profile">

        <div class="print-title">

            <h1>🏫 CAMPUS ERP PRO</h1>

            <p><b>STUDENT PROFILE</b></p>

            <p>Student Academic Record</p>

        </div>


        <div class="profile-section">

            <h3>👤 Personal Details</h3>

            <table class="profile-table">

                <tr>
                    <td class="profile-label">Student Name</td>
                    <td>{student_name}</td>
                </tr>

                <tr>
                    <td class="profile-label">Father's Name</td>
                    <td>{father_name}</td>
                </tr>

                <tr>
                    <td class="profile-label">Mother's Name</td>
                    <td>{mother_name}</td>
                </tr>

                <tr>
                    <td class="profile-label">Gender</td>
                    <td>{gender}</td>
                </tr>

            </table>

        </div>


        <div class="profile-section">

            <h3>📚 Academic Details</h3>

            <table class="profile-table">

                <tr>
                    <td class="profile-label">SR Number</td>
                    <td>{sr_no}</td>
                </tr>

                <tr>
                    <td class="profile-label">Roll Number</td>
                    <td>{roll_no}</td>
                </tr>

                <tr>
                    <td class="profile-label">Class</td>
                    <td>{class_name}</td>
                </tr>

                <tr>
                    <td class="profile-label">Section</td>
                    <td>{section}</td>
                </tr>

            </table>

        </div>


        <div class="profile-section">

            <h3>🚌 Contact & Transport</h3>

            <table class="profile-table">

                <tr>
                    <td class="profile-label">Mobile</td>
                    <td>{mobile}</td>
                </tr>

                <tr>
                    <td class="profile-label">Bus Route</td>
                    <td>{bus_route}</td>
                </tr>

                <tr>
                    <td class="profile-label">Drop Point</td>
                    <td>{drop_point}</td>
                </tr>

                <tr>
                    <td class="profile-label">Aadhaar / ID</td>
                    <td>{aadhaar_status}</td>
                </tr>

            </table>

        </div>


        <div class="signature-area">

            <table class="signature-table">

                <tr>
                    <td>
                        Parent / Guardian Signature
                    </td>

                    <td>
                        Authorized Signature
                    </td>
                </tr>

                <tr>
                    <td class="signature-line"></td>
                    <td class="signature-line"></td>
                </tr>

            </table>

        </div>


        <div class="footer">
            Generated by Campus ERP Pro
        </div>


        <button
            class="print-btn"
            onclick="window.print()"
        >
            🖨️ Print A4 Student Profile
        </button>

    </div>

    </body>
    </html>
    """

    components.html(
        html,
        height=900,
        scrolling=True
    )
    components.html(
        html,
        height=900,
        scrolling=True
    )


# =========================================================
# DUPLICATE CHECK HELPERS
# =========================================================

def check_duplicate_sr(sr_no, exclude_sr=None):

    if not supabase:
        return False

    try:

        response = (
            supabase
            .table("students")
            .select("sr_no")
            .eq("sr_no", int(sr_no))
            .execute()
        )

        if not response.data:
            return False

        for row in response.data:

            existing_sr = int(
                row.get("sr_no")
            )

            if (
                exclude_sr is not None
                and existing_sr == int(exclude_sr)
            ):
                continue

            return True

        return False

    except Exception as e:

        st.error(
            f"❌ Duplicate SR check failed: {e}"
        )

        return False


def check_duplicate_roll(
    roll_no,
    class_name,
    section,
    exclude_sr=None
):

    if not supabase:
        return False

    if not roll_no or int(roll_no) <= 0:
        return False

    try:

        response = (
            supabase
            .table("students")
            .select(
                "sr_no, roll_no, class, section"
            )
            .eq(
                "roll_no",
                int(roll_no)
            )
            .eq(
                "class",
                class_name
            )
            .eq(
                "section",
                section
            )
            .execute()
        )

        if not response.data:
            return False

        for row in response.data:

            existing_sr = int(
                row.get("sr_no")
            )

            if (
                exclude_sr is not None
                and existing_sr == int(exclude_sr)
            ):
                continue

            return True

        return False

    except Exception as e:

        st.error(
            f"❌ Duplicate Roll check failed: {e}"
        )

        return False

# =========================================================
# TAB 3 — SEARCH & MANAGE
# =========================================================

def render_search_manage():

    st.subheader(
        "🔍 Search & Manage Student"
    )

    # =====================================================
    # SEARCH STUDENT
    # =====================================================

    search_sr = st.number_input(
        "Enter SR No",
        min_value=1,
        step=1,
        key="search_sr_input"
    )

    if st.button(
        "🔍 Search Student",
        key="btn_search_student"
    ):

        if not supabase:

            st.error(
                "❌ Supabase connection नहीं है."
            )

            return

        try:

            response = (
                supabase
                .table("students")
                .select("*")
                .eq(
                    "sr_no",
                    int(search_sr)
                )
                .limit(1)
                .execute()
            )

            if response.data:

                st.session_state[
                    "searched_student"
                ] = response.data[0]

                st.session_state[
                    "delete_confirm"
                ] = False

                st.success(
                    "✅ Student found successfully."
                )

            else:

                st.warning(
                    f"⚠️ SR No {search_sr} का student नहीं मिला."
                )

                st.session_state.pop(
                    "searched_student",
                    None
                )

        except Exception as e:

            st.error(
                f"❌ Search error: {e}"
            )

    student = st.session_state.get(
        "searched_student"
    )

    if not student:
        return

    # =====================================================
    # STUDENT PROFILE
    # =====================================================

    render_student_profile(
        student
    )

    # =====================================================
    # PROFESSIONAL A4 PRINT PROFILE
    # =====================================================

    render_print_student_profile(
        student
    )

    st.markdown("---")

    # =====================================================
    # EDIT STUDENT
    # =====================================================

    st.markdown(
        f"### ✏️ Edit Student: "
        f"**{student.get('student_name', 'N/A')}**"
    )

    with st.form(
        key="edit_student_form"
    ):

        c1, c2 = st.columns(2)

        # =================================================
        # LEFT COLUMN
        # =================================================

        with c1:

            original_sr = int(
                student.get(
                    "sr_no",
                    1
                )
            )

            edit_sr = st.number_input(
                "SR Number",
                min_value=1,
                step=1,
                value=original_sr
            )

            edit_name = st.text_input(
                "Student Name",
                value=str(
                    student.get(
                        "student_name",
                        ""
                    ) or ""
                )
            )

            edit_father = st.text_input(
                "Father's Name",
                value=str(
                    student.get(
                        "father_name",
                        ""
                    ) or ""
                )
            )

            edit_mother = st.text_input(
                "Mother's Name",
                value=str(
                    student.get(
                        "mother_name",
                        ""
                    ) or ""
                )
            )

            current_class = student.get(
                "class",
                CLASSES[0]
            )

            edit_class = st.selectbox(
                "Class",
                CLASSES,
                index=(
                    CLASSES.index(
                        current_class
                    )
                    if current_class in CLASSES
                    else 0
                )
            )

            edit_bus = st.text_input(
                "Bus Route",
                value=str(
                    student.get(
                        "bus_route",
                        ""
                    ) or ""
                )
            )

        # =================================================
        # RIGHT COLUMN
        # =================================================

        with c2:

            edit_roll = st.number_input(
                "Roll Number",
                min_value=0,
                step=1,
                value=int(
                    student.get(
                        "roll_no",
                        0
                    ) or 0
                )
            )

            gender_options = [
                "Male",
                "Female",
                "Other"
            ]

            current_gender = student.get(
                "gender",
                "Male"
            )

            edit_gender = st.selectbox(
                "Gender",
                gender_options,
                index=(
                    gender_options.index(
                        current_gender
                    )
                    if current_gender
                    in gender_options
                    else 0
                )
            )

            section_options = [
                "A",
                "B",
                "C",
                "D"
            ]

            current_section = student.get(
                "section",
                "A"
            )

            edit_section = st.selectbox(
                "Section",
                section_options,
                index=(
                    section_options.index(
                        current_section
                    )
                    if current_section
                    in section_options
                    else 0
                )
            )

            edit_mobile = st.text_input(
                "Mobile",
                value=str(
                    student.get(
                        "mobile",
                        ""
                    ) or ""
                )
            )

            edit_aadhaar = st.text_input(
                "Aadhaar / ID Reference",
                value=str(
                    student.get(
                        "aadhaar",
                        ""
                    ) or ""
                )
            )

            edit_drop = st.text_input(
                "Drop Point",
                value=str(
                    student.get(
                        "drop_point",
                        ""
                    ) or ""
                )
            )

        # =================================================
        # UPDATE BUTTON
        # =================================================

        update_student = st.form_submit_button(
            "💾 Update Student Record",
            use_container_width=True,
            type="primary"
        )

        if update_student:

            # ---------------------------------------------
            # NAME VALIDATION
            # ---------------------------------------------

            if not edit_name.strip():

                st.error(
                    "❌ Student name is required."
                )

                return

            if not supabase:

                st.error(
                    "❌ Supabase connection नहीं है."
                )

                return

            # ---------------------------------------------
            # DUPLICATE SR CHECK
            # ---------------------------------------------

            if check_duplicate_sr(
                edit_sr,
                exclude_sr=original_sr
            ):

                st.error(
                    f"❌ SR No {edit_sr} already exists."
                )

                return

            # ---------------------------------------------
            # DUPLICATE ROLL CHECK
            # ---------------------------------------------

            if (
                int(edit_roll) > 0
                and check_duplicate_roll(
                    edit_roll,
                    edit_class,
                    edit_section,
                    exclude_sr=original_sr
                )
            ):

                st.error(
                    f"❌ Roll No {edit_roll} already exists "
                    f"in {edit_class} - Section {edit_section}."
                )

                return

            # ---------------------------------------------
            # UPDATE DATA
            # ---------------------------------------------

            update_data = {

                "sr_no":
                    int(edit_sr),

                "student_name":
                    edit_name.strip(),

                "father_name":
                    edit_father.strip(),

                "mother_name":
                    edit_mother.strip(),

                "class":
                    edit_class,

                "section":
                    edit_section,

                "roll_no":
                    int(edit_roll),

                "gender":
                    edit_gender,

                "mobile":
                    edit_mobile.strip(),

                "bus_route":
                    edit_bus.strip(),

                "drop_point":
                    edit_drop.strip(),

                "aadhaar":
                    edit_aadhaar.strip()
            }

            try:

                # -----------------------------------------
                # UPDATE SUPABASE
                # -----------------------------------------

                (
                    supabase
                    .table("students")
                    .update(update_data)
                    .eq(
                        "sr_no",
                        original_sr
                    )
                    .execute()
                )

                # -----------------------------------------
                # FRESH DATA FROM DATABASE
                # -----------------------------------------

                fresh_response = (
                    supabase
                    .table("students")
                    .select("*")
                    .eq(
                        "sr_no",
                        int(edit_sr)
                    )
                    .limit(1)
                    .execute()
                )

                if fresh_response.data:

                    st.session_state[
                        "searched_student"
                    ] = fresh_response.data[0]

                else:

                    st.session_state[
                        "searched_student"
                    ] = update_data

                st.success(
                    "✅ Student updated successfully!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Update failed: {e}"
                )

    # =====================================================
    # DELETE STUDENT
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 🗑️ Delete Student"
    )

    st.warning(
        f"Student: **{student.get('student_name', 'N/A')}** "
        f"| SR No: **{student.get('sr_no', 'N/A')}**"
    )

    if not st.session_state.get(
        "delete_confirm",
        False
    ):

        if st.button(
            "🗑️ Delete Student",
            key="delete_student_button",
            use_container_width=True
        ):

            st.session_state[
                "delete_confirm"
            ] = True

            st.rerun()

    else:

        st.error(
            "⚠️ यह student record permanently delete होगा।"
        )

        d1, d2 = st.columns(2)

        with d1:

            if st.button(
                "❌ Yes, Delete Permanently",
                key="confirm_delete_student",
                use_container_width=True,
                type="primary"
            ):

                try:

                    delete_sr = int(
                        student.get(
                            "sr_no"
                        )
                    )

                    (
                        supabase
                        .table("students")
                        .delete()
                        .eq(
                            "sr_no",
                            delete_sr
                        )
                        .execute()
                    )

                    st.session_state.pop(
                        "searched_student",
                        None
                    )

                    st.session_state[
                        "delete_confirm"
                    ] = False

                    st.success(
                        f"✅ Student SR No {delete_sr} deleted successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Delete failed: {e}"
                    )

        with d2:

            if st.button(
                "↩️ Cancel",
                key="cancel_delete_student",
                use_container_width=True
            ):

                st.session_state[
                    "delete_confirm"
                ] = False

                st.rerun()

# =========================================================
# MAIN STUDENT MODULE
# =========================================================

def render_students_module():
    st.markdown(
        "## 👨‍🎓 Student Admission & Master Directory"
    )

    tab1, tab2, tab3 = st.tabs([
        "📝 New Admission",
        "📋 Live Student Directory",
        "🔍 Search & Manage"
    ])

    with tab1:

        render_new_admission()

    with tab2:

        render_live_directory()

    with tab3:

        render_search_manage()
