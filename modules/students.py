import pandas as pd
import streamlit as st
from database.supabase import supabase


# =========================================================
# CONSTANTS
# =========================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["All", "A", "B", "C", "D"]


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
        st.error(f"❌ Error fetching students: {e}")
        return None


# =========================================================
# STUDENT DIRECTORY
# =========================================================

def render_students_module():

    st.markdown("## 👨‍🎓 Student Admission & Master Directory")

    tab1, tab2, tab3 = st.tabs([
        "📝 New Admission",
        "📋 Live Student Directory",
        "🔍 Search & Manage"
    ])

    # =====================================================
    # TAB 1 — NEW ADMISSION
    # =====================================================

    with tab1:

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

                else:

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

                    if supabase:

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

    # =====================================================
    # TAB 2 — LIVE DIRECTORY
    # =====================================================

    with tab2:

        st.subheader(
            "📋 Live Student Directory"
        )

        # -------------------------------------------------
        # Refresh button
        # -------------------------------------------------

        refresh_col, count_col = st.columns([1, 4])

        with refresh_col:

            refresh_clicked = st.button(
                "🔄 Refresh Data",
                use_container_width=True,
                key="refresh_student_directory"
            )

        # Load fresh data
        students = load_students()

        if students is not None:

            # -------------------------------------------------
            # Convert to DataFrame
            # -------------------------------------------------

            if students:

                df = pd.DataFrame(students)

                # -------------------------------------------------
                # TOP FILTERS
                # -------------------------------------------------

                st.markdown("### 🔎 Search & Filter")

                f1, f2, f3 = st.columns([2, 1, 1])

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

                # -------------------------------------------------
                # SEARCH FILTER
                # -------------------------------------------------

                filtered_df = df.copy()

                if search_text.strip():

                    search_value = search_text.strip().lower()

                    searchable_columns = [
                        "student_name",
                        "sr_no",
                        "roll_no",
                        "mobile"
                    ]

                    mask = pd.Series(
                        False,
                        index=filtered_df.index
                    )

                    for column in searchable_columns:

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
                # CLASS FILTER
                # -------------------------------------------------

                if class_filter != "All":

                    if "class" in filtered_df.columns:

                        filtered_df = filtered_df[
                            filtered_df["class"]
                            == class_filter
                        ]

                # -------------------------------------------------
                # SECTION FILTER
                # -------------------------------------------------

                if section_filter != "All":

                    if "section" in filtered_df.columns:

                        filtered_df = filtered_df[
                            filtered_df["section"]
                            == section_filter
                        ]

                # -------------------------------------------------
                # COUNT
                # -------------------------------------------------

                with count_col:

                    st.metric(
                        "👨‍🎓 Students Found",
                        len(filtered_df)
                    )

                # -------------------------------------------------
                # DISPLAY COLUMNS
                # -------------------------------------------------

                rename_cols = {
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
                    "drop_point": "Drop Point"
                }

                display_df = filtered_df.rename(
                    columns=rename_cols
                )

                display_cols = [
                    col
                    for col in rename_cols.values()
                    if col in display_df.columns
                ]

                if len(display_df) > 0:

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
                    "📭 No students found in the database."
                )

    # =====================================================
    # TAB 3 — SEARCH & MANAGE
    # =====================================================

    with tab3:

        st.subheader(
            "🔍 Search & Edit Student"
        )

        students = load_students()

        if students:

            df = pd.DataFrame(students)

            # -------------------------------------------------
            # Search
            # -------------------------------------------------

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

                result = df[
                    df["sr_no"].astype(int)
                    == int(search_sr)
                ]

                if not result.empty:

                    st.session_state[
                        "searched_student"
                    ] = result.iloc[0].to_dict()

                else:

                    st.warning(
                        "Student not found."
                    )

                    st.session_state.pop(
                        "searched_student",
                        None
                    )

            # -------------------------------------------------
            # Student Edit
            # -------------------------------------------------

            student = st.session_state.get(
                "searched_student"
            )

            if student:

                st.markdown("---")

                st.markdown(
                    f"### ✏️ Edit Student: "
                    f"**{student.get('student_name', 'N/A')}**"
                )

                with st.form(
                    key="edit_student_form"
                ):

                    e1, e2 = st.columns(2)

                    with e1:

                        edit_sr = st.number_input(
                            "SR Number",
                            value=int(
                                student.get("sr_no", 1)
                            ),
                            min_value=1
                        )

                        edit_name = st.text_input(
                            "Student Name",
                            value=str(
                                student.get(
                                    "student_name",
                                    ""
                                )
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
                                CLASSES.index(current_class)
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

                    with e2:

                        edit_roll = st.number_input(
                            "Roll Number",
                            value=int(
                                student.get(
                                    "roll_no",
                                    1
                                ) or 1
                            ),
                            min_value=1
                        )

                        current_gender = student.get(
                            "gender",
                            "Male"
                        )

                        gender_options = [
                            "Male",
                            "Female",
                            "Other"
                        ]

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

                        current_section = student.get(
                            "section",
                            "A"
                        )

                        section_options = [
                            "A",
                            "B",
                            "C",
                            "D"
                        ]

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

                    update_student = st.form_submit_button(
                        "💾 Update Student Record",
                        use_container_width=True
                    )

                    if update_student:

                        if not edit_name.strip():

                            st.error(
                                "Student name is required."
                            )

                        elif supabase:

                            try:

                                update_data = {
                                    "sr_no": int(edit_sr),
                                    "student_name": edit_name.strip(),
                                    "father_name": edit_father.strip(),
                                    "mother_name": edit_mother.strip(),
                                    "class": edit_class,
                                    "section": edit_section,
                                    "roll_no": int(edit_roll),
                                    "gender": edit_gender,
                                    "mobile": edit_mobile.strip(),
                                    "bus_route": edit_bus.strip(),
                                    "drop_point": edit_drop.strip(),
                                    "aadhaar": edit_aadhaar.strip()
                                }

                                original_sr = int(
                                    student["sr_no"]
                                )

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

                                st.success(
                                    "✅ Student record updated successfully!"
                                )

                                st.session_state[
                                    "searched_student"
                                ] = update_data

                            except Exception as e:

                                st.error(
                                    f"❌ Update failed: {e}"
                                )

        else:

            st.info(
                "📭 No students available."
            )
