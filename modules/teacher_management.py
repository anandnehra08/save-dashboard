import streamlit as st
import bcrypt
from database.supabase import supabase


# ============================================================
# CONSTANTS
# ============================================================

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]

DEFAULT_SUBJECTS = [
    "Maths",
    "Science",
    "English",
    "Hindi",
    "Physics",
    "Chemistry",
    "Social Studies",
]


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:
    """Plain password को सुरक्षित Bcrypt Hash में बदलेगा."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )
    return hashed.decode("utf-8")


# ============================================================
# MASTER SUBJECTS
# ============================================================

def get_master_subjects():
    """
    subjects_master table से subjects लाता है।
    अगर table उपलब्ध नहीं है तो default subjects उपयोग होंगे।
    """

    if supabase:
        try:
            res = (
                supabase
                .table("subjects_master")
                .select("subject_name")
                .execute()
            )

            if res.data:
                subjects = [
                    item["subject_name"]
                    for item in res.data
                    if item.get("subject_name")
                ]

                if subjects:
                    return subjects

        except Exception:
            pass

    return DEFAULT_SUBJECTS


# ============================================================
# SAFE LIST HELPER
# ============================================================

def safe_list(value):
    """
    Supabase से array / None / string आने पर
    हमेशा clean Python list return करेगा।
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, str):
        if not value.strip():
            return []

        return [value]

    return []


# ============================================================
# TEACHER ACCESS DISPLAY
# ============================================================

def get_teacher_classes(teacher):
    classes = safe_list(
        teacher.get("assigned_classes")
    )

    if not classes and teacher.get("assigned_class"):
        classes = [teacher.get("assigned_class")]

    return classes


def get_teacher_subjects(teacher):
    subjects = safe_list(
        teacher.get("assigned_subjects")
    )

    return subjects


def get_teacher_sections(teacher):
    sections = safe_list(
        teacher.get("assigned_sections")
    )

    if not sections:
        old_section = teacher.get("assigned_section")

        if old_section and old_section != "ALL":
            sections = [old_section]

    return sections


# ============================================================
# MAIN MODULE
# ============================================================

def render_teacher_management_module():

    # ========================================================
    # ADMIN SECURITY
    # ========================================================

    if st.session_state.get("user_role") != "admin":

        st.error(
            "⛔ **Access Denied:** "
            "केवल Principal/Admin ही शिक्षकों के access को manage कर सकते हैं।"
        )

        return

    # ========================================================
    # HEADER
    # ========================================================

    st.title("👑 Staff & Access Control Management")

    st.caption(
        "Principal Control Panel: "
        "Teachers को multiple classes, sections और subjects का controlled access दें।"
    )

    # ========================================================
    # SUPABASE CHECK
    # ========================================================

    if not supabase:

        st.error(
            "❌ Supabase connection उपलब्ध नहीं है। "
            "Teacher Management इस्तेमाल करने के लिए database connection आवश्यक है।"
        )

        return

    master_subjects = get_master_subjects()

    # ========================================================
    # TABS
    # ========================================================

    tab_add, tab_manage = st.tabs(
        [
            "➕ Add / Assign New Teacher",
            "📋 Manage Active Teachers",
        ]
    )

    # ========================================================
    # TAB 1
    # ADD / ASSIGN TEACHER
    # ========================================================

    with tab_add:

        st.subheader("👨‍🏫 Assign Access to Teacher")

        st.info(
            "🔐 Teacher का password database में plain text में नहीं, "
            "Bcrypt hash के रूप में save होगा।"
        )

        col1, col2 = st.columns(2)

        # ----------------------------------------------------
        # PERSONAL INFORMATION
        # ----------------------------------------------------

        with col1:

            t_name = st.text_input(
                "Teacher Name *",
                placeholder="e.g. Ramesh Kumar",
                key="new_teacher_name",
            )

            t_email = st.text_input(
                "Teacher Email ID *",
                placeholder="e.g. ramesh@school.com",
                key="new_teacher_email",
            )

            t_phone = st.text_input(
                "Phone Number",
                placeholder="e.g. 9876543211",
                key="new_teacher_phone",
            )

            t_pass = st.text_input(
                "Assign Password *",
                type="password",
                value="teacher123",
                key="new_teacher_password",
            )

        # ----------------------------------------------------
        # ROLE & ACCESS
        # ----------------------------------------------------

        with col2:

            t_role = st.selectbox(
                "Assign Role *",
                [
                    "class_teacher",
                    "subject_teacher",
                ],
                format_func=lambda x: (
                    "Class Teacher (Class Incharge)"
                    if x == "class_teacher"
                    else
                    "Subject Teacher (Multiple Classes)"
                ),
                key="new_teacher_role",
            )

            # =================================================
            # CLASS TEACHER
            # =================================================

            if t_role == "class_teacher":

                assigned_class = st.selectbox(
                    "Assigned Incharge Class *",
                    CLASSES,
                    key="new_class_teacher_class",
                )

                assigned_section = st.selectbox(
                    "Assigned Section *",
                    SECTIONS,
                    key="new_class_teacher_section",
                )

                assigned_classes = [
                    assigned_class
                ]

                assigned_sections = [
                    assigned_section
                ]

                assigned_subjects = [
                    "ALL"
                ]

                st.success(
                    "💡 **Class Teacher Access**\n\n"
                    "यह teacher assigned class की "
                    "student, attendance, exam और marks activities "
                    "manage कर सकेगा।"
                )

            # =================================================
            # SUBJECT TEACHER
            # =================================================

            else:

                assigned_classes = st.multiselect(
                    "Select Classes *",
                    CLASSES,
                    default=[],
                    help=(
                        "Teacher जिन classes में पढ़ाते हैं "
                        "उन सभी classes को चुनें।"
                    ),
                    key="new_subject_teacher_classes",
                )

                assigned_sections = st.multiselect(
                    "Select Sections",
                    SECTIONS,
                    default=[],
                    help=(
                        "कोई section select न करने पर "
                        "selected classes के सभी sections "
                        "को access माना जा सकता है।"
                    ),
                    key="new_subject_teacher_sections",
                )

                assigned_subjects = st.multiselect(
                    "Assigned Subjects *",
                    master_subjects,
                    default=[],
                    help="Teacher को केवल selected subjects का access मिलेगा।",
                    key="new_subject_teacher_subjects",
                )

                st.info(
                    "💡 **Subject Teacher** को केवल assigned "
                    "classes + sections + subjects के अनुसार access दिया जाएगा।"
                )

        # ====================================================
        # PREVIEW
        # ====================================================

        st.markdown("---")
        st.subheader("👁️ Access Preview")

        p1, p2, p3 = st.columns(3)

        with p1:
            st.write("**Classes**")

            if assigned_classes:
                st.write(", ".join(assigned_classes))
            else:
                st.write("—")

        with p2:
            st.write("**Sections**")

            if assigned_sections:
                st.write(", ".join(assigned_sections))
            else:
                st.write("All Sections")

        with p3:
            st.write("**Subjects**")

            if assigned_subjects:
                st.write(", ".join(assigned_subjects))
            else:
                st.write("—")

        st.markdown("---")

        # ====================================================
        # CREATE TEACHER
        # ====================================================

        if st.button(
            "➕ Create Teacher & Grant Access",
            type="primary",
            use_container_width=True,
            key="create_teacher_btn",
        ):

            clean_name = t_name.strip()
            clean_email = t_email.strip().lower()
            clean_phone = t_phone.strip()
            clean_password = t_pass.strip()

            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            if not clean_name:

                st.warning(
                    "⚠️ Teacher Name आवश्यक है।"
                )

                st.stop()

            if not clean_email:

                st.warning(
                    "⚠️ Teacher Email ID आवश्यक है।"
                )

                st.stop()

            if not clean_password:

                st.warning(
                    "⚠️ Password आवश्यक है।"
                )

                st.stop()

            if len(clean_password) < 6:

                st.warning(
                    "⚠️ Password कम से कम 6 characters का रखें।"
                )

                st.stop()

            if not assigned_classes:

                st.warning(
                    "⚠️ कम से कम एक class select करें।"
                )

                st.stop()

            if (
                t_role == "subject_teacher"
                and not assigned_subjects
            ):

                st.warning(
                    "⚠️ Subject Teacher के लिए कम से कम "
                    "एक subject select करें।"
                )

                st.stop()

            # ------------------------------------------------
            # DUPLICATE EMAIL CHECK
            # ------------------------------------------------

            try:

                existing = (
                    supabase
                    .table("users")
                    .select("id,name,email")
                    .eq("email", clean_email)
                    .execute()
                )

                if existing.data:

                    st.error(
                        f"❌ यह Email पहले से registered है: "
                        f"{clean_email}"
                    )

                    st.stop()

            except Exception as err:

                st.error(
                    f"❌ Email verification error: {err}"
                )

                st.stop()

            # ------------------------------------------------
            # PASSWORD HASH
            # ------------------------------------------------

            try:

                hashed_pass = hash_password(
                    clean_password
                )

            except Exception as err:

                st.error(
                    f"❌ Password security error: {err}"
                )

                st.stop()

            # ------------------------------------------------
            # DATABASE PAYLOAD
            # ------------------------------------------------

            payload = {
                "name": clean_name,
                "email": clean_email,
                "phone": clean_phone,
                "password": hashed_pass,

                "role": t_role,

                # Backward compatibility
                "assigned_class": assigned_classes[0],

                # Multiple classes
                "assigned_classes": assigned_classes,

                # Existing field
                "assigned_section": (
                    assigned_sections[0]
                    if len(assigned_sections) == 1
                    else "ALL"
                ),

                # New multiple-section access
                "assigned_sections": assigned_sections,

                # Multiple subjects
                "assigned_subjects": assigned_subjects,
            }

            # ------------------------------------------------
            # INSERT
            # ------------------------------------------------

            try:

                supabase.table(
                    "users"
                ).insert(
                    payload
                ).execute()

                st.success(
                    f"✅ **{clean_name}** successfully created!\n\n"
                    f"Classes: {', '.join(assigned_classes)}"
                )

                st.balloons()

                st.rerun()

            except Exception as err:

                # ------------------------------------------------
                # FALLBACK FOR DATABASE WITHOUT assigned_sections
                # ------------------------------------------------

                error_text = str(err)

                if "assigned_sections" in error_text:

                    fallback_payload = payload.copy()

                    fallback_payload.pop(
                        "assigned_sections",
                        None
                    )

                    try:

                        supabase.table(
                            "users"
                        ).insert(
                            fallback_payload
                        ).execute()

                        st.success(
                            f"✅ **{clean_name}** successfully created!"
                        )

                        st.rerun()

                    except Exception as fallback_error:

                        st.error(
                            "❌ Teacher create error:\n\n"
                            f"{fallback_error}"
                        )

                else:

                    st.error(
                        "❌ Teacher create error:\n\n"
                        f"{err}"
                    )

    # ========================================================
    # TAB 2
    # MANAGE TEACHERS
    # ========================================================

    with tab_manage:

        st.subheader(
            "📋 All Registered Staff & Permissions"
        )

        # ----------------------------------------------------
        # FETCH TEACHERS
        # ----------------------------------------------------

        try:

            res = (
                supabase
                .table("users")
                .select(
                    "id, name, email, phone, role, "
                    "assigned_class, assigned_classes, "
                    "assigned_section, assigned_sections, "
                    "assigned_subjects"
                )
                .execute()
            )

            teachers = res.data or []

        except Exception as err:

            # Fallback query if assigned_sections column
            # does not exist in old database.

            try:

                res = (
                    supabase
                    .table("users")
                    .select(
                        "id, name, email, phone, role, "
                        "assigned_class, assigned_classes, "
                        "assigned_section, assigned_subjects"
                    )
                    .execute()
                )

                teachers = res.data or []

            except Exception as final_error:

                st.error(
                    f"❌ Teacher data fetch error: {final_error}"
                )

                return

        # ----------------------------------------------------
        # NO TEACHERS
        # ----------------------------------------------------

        if not teachers:

            st.info(
                "ℹ️ अभी कोई teacher/staff registered नहीं है।"
            )

            return

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        admin_count = sum(
            1
            for t in teachers
            if t.get("role") == "admin"
        )

        class_teacher_count = sum(
            1
            for t in teachers
            if t.get("role") == "class_teacher"
        )

        subject_teacher_count = sum(
            1
            for t in teachers
            if t.get("role") == "subject_teacher"
        )

        s1, s2, s3, s4 = st.columns(4)

        s1.metric(
            "👥 Total Staff",
            len(teachers)
        )

        s2.metric(
            "👑 Admin",
            admin_count
        )

        s3.metric(
            "🏫 Class Teachers",
            class_teacher_count
        )

        s4.metric(
            "📚 Subject Teachers",
            subject_teacher_count
        )

        st.markdown("---")

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search_text = st.text_input(
            "🔎 Search Teacher",
            placeholder="Name या email से search करें...",
            key="teacher_search",
        )

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        role_filter = st.selectbox(
            "Filter by Role",
            [
                "All",
                "Admin",
                "Class Teacher",
                "Subject Teacher",
            ],
            key="teacher_role_filter",
        )

        filtered_teachers = []

        for teacher in teachers:

            name = (
                teacher.get("name") or ""
            ).lower()

            email = (
                teacher.get("email") or ""
            ).lower()

            role = teacher.get("role")

            # Search
            if search_text:

                query = search_text.lower()

                if (
                    query not in name
                    and query not in email
                ):
                    continue

            # Role
            if role_filter == "Admin":

                if role != "admin":
                    continue

            elif role_filter == "Class Teacher":

                if role != "class_teacher":
                    continue

            elif role_filter == "Subject Teacher":

                if role != "subject_teacher":
                    continue

            filtered_teachers.append(
                teacher
            )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        if not filtered_teachers:

            st.info(
                "🔎 दिए गए filter/search के अनुसार कोई teacher नहीं मिला।"
            )

            return

        # ----------------------------------------------------
        # EACH TEACHER
        # ----------------------------------------------------

        for teacher in filtered_teachers:

            teacher_id = teacher.get("id")

            teacher_name = (
                teacher.get("name")
                or "Unknown Teacher"
            )

            teacher_email = (
                teacher.get("email")
                or "No Email"
            )

            teacher_role = (
                teacher.get("role")
                or "unknown"
            )

            classes_list = get_teacher_classes(
                teacher
            )

            sections_list = get_teacher_sections(
                teacher
            )

            subjects_list = get_teacher_subjects(
                teacher
            )

            # ------------------------------------------------
            # ROLE LABEL
            # ------------------------------------------------

            if teacher_role == "admin":

                role_label = "👑 ADMIN"

            elif teacher_role == "class_teacher":

                role_label = "🏫 CLASS TEACHER"

            elif teacher_role == "subject_teacher":

                role_label = "📚 SUBJECT TEACHER"

            else:

                role_label = teacher_role.upper()

            # ------------------------------------------------
            # EXPANDER
            # ------------------------------------------------

            with st.expander(
                f"👤 {teacher_name}  |  "
                f"{role_label}  |  "
                f"{teacher_email}"
            ):

                # =================================================
                # BASIC DETAILS
                # =================================================

                st.markdown("### 👤 Teacher Information")

                i1, i2, i3 = st.columns(3)

                with i1:

                    st.write(
                        f"**Name:** {teacher_name}"
                    )

                with i2:

                    st.write(
                        f"**Email:** {teacher_email}"
                    )

                with i3:

                    st.write(
                        f"**Phone:** "
                        f"{teacher.get('phone') or '—'}"
                    )

                st.markdown("---")

                # =================================================
                # ACCESS INFORMATION
                # =================================================

                st.markdown(
                    "### 🔐 Current Access"
                )

                a1, a2, a3 = st.columns(3)

                with a1:

                    st.write("**Classes**")

                    if classes_list:
                        st.write(
                            ", ".join(classes_list)
                        )
                    else:
                        st.write("—")

                with a2:

                    st.write("**Sections**")

                    if sections_list:
                        st.write(
                            ", ".join(sections_list)
                        )
                    else:
                        st.write("All Sections")

                with a3:

                    st.write("**Subjects**")

                    if subjects_list:
                        st.write(
                            ", ".join(subjects_list)
                        )
                    else:
                        st.write("—")

                # =================================================
                # ADMIN PROTECTION
                # =================================================

                if teacher_role == "admin":

                    st.info(
                        "👑 Admin account — "
                        "इस account का access यहाँ से revoke नहीं किया जाएगा।"
                    )

                    continue

                # =================================================
                # EDIT ACCESS
                # =================================================

                st.markdown("---")
                st.markdown(
                    "### ✏️ Edit Teacher Access"
                )

                edit_col1, edit_col2 = st.columns(2)

                with edit_col1:

                    edit_role = st.selectbox(
                        "Role",
                        [
                            "class_teacher",
                            "subject_teacher",
                        ],
                        index=(
                            0
                            if teacher_role == "class_teacher"
                            else 1
                        ),
                        format_func=lambda x: (
                            "Class Teacher"
                            if x == "class_teacher"
                            else "Subject Teacher"
                        ),
                        key=f"edit_role_{teacher_id}",
                    )

                with edit_col2:

                    new_phone = st.text_input(
                        "Phone Number",
                        value=teacher.get("phone") or "",
                        key=f"edit_phone_{teacher_id}",
                    )

                # ------------------------------------------------
                # EDIT CLASS TEACHER
                # ------------------------------------------------

                if edit_role == "class_teacher":

                    current_class = (
                        classes_list[0]
                        if classes_list
                        and classes_list[0] in CLASSES
                        else "Class 1"
                    )

                    current_section = (
                        sections_list[0]
                        if sections_list
                        and sections_list[0] in SECTIONS
                        else "A"
                    )

                    ec1, ec2 = st.columns(2)

                    with ec1:

                        edit_class = st.selectbox(
                            "Incharge Class",
                            CLASSES,
                            index=CLASSES.index(
                                current_class
                            ),
                            key=f"edit_class_{teacher_id}",
                        )

                    with ec2:

                        edit_section = st.selectbox(
                            "Section",
                            SECTIONS,
                            index=SECTIONS.index(
                                current_section
                            ),
                            key=f"edit_section_{teacher_id}",
                        )

                    edit_classes = [
                        edit_class
                    ]

                    edit_sections = [
                        edit_section
                    ]

                    edit_subjects = [
                        "ALL"
                    ]

                # ------------------------------------------------
                # EDIT SUBJECT TEACHER
                # ------------------------------------------------

                else:

                    edit_classes = st.multiselect(
                        "Allowed Classes",
                        CLASSES,
                        default=[
                            x
                            for x in classes_list
                            if x in CLASSES
                        ],
                        key=f"edit_classes_{teacher_id}",
                    )

                    edit_sections = st.multiselect(
                        "Allowed Sections",
                        SECTIONS,
                        default=[
                            x
                            for x in sections_list
                            if x in SECTIONS
                        ],
                        key=f"edit_sections_{teacher_id}",
                    )

                    edit_subjects = st.multiselect(
                        "Allowed Subjects",
                        master_subjects,
                        default=[
                            x
                            for x in subjects_list
                            if x in master_subjects
                        ],
                        key=f"edit_subjects_{teacher_id}",
                    )

                # =================================================
                # SAVE ACCESS
                # =================================================

                if st.button(
                    "💾 Save Access Changes",
                    type="primary",
                    key=f"save_access_{teacher_id}",
                    use_container_width=True,
                ):

                    if not edit_classes:

                        st.warning(
                            "⚠️ कम से कम एक class select करें।"
                        )

                        continue

                    if (
                        edit_role == "subject_teacher"
                        and not edit_subjects
                    ):

                        st.warning(
                            "⚠️ Subject Teacher के लिए "
                            "कम से कम एक subject select करें।"
                        )

                        continue

                    update_payload = {
                        "role": edit_role,
                        "phone": new_phone.strip(),

                        # Backward compatibility
                        "assigned_class": edit_classes[0],

                        # Multiple classes
                        "assigned_classes": edit_classes,

                        # Existing section field
                        "assigned_section": (
                            edit_sections[0]
                            if len(edit_sections) == 1
                            else "ALL"
                        ),

                        # Multiple subjects
                        "assigned_subjects": edit_subjects,

                        # New field
                        "assigned_sections": edit_sections,
                    }

                    try:

                        supabase.table(
                            "users"
                        ).update(
                            update_payload
                        ).eq(
                            "id",
                            teacher_id
                        ).execute()

                        st.success(
                            f"✅ {teacher_name} का access successfully updated!"
                        )

                        st.rerun()

                    except Exception as err:

                        # Fallback if assigned_sections
                        # column doesn't exist.

                        if "assigned_sections" in str(err):

                            fallback = update_payload.copy()

                            fallback.pop(
                                "assigned_sections",
                                None
                            )

                            try:

                                supabase.table(
                                    "users"
                                ).update(
                                    fallback
                                ).eq(
                                    "id",
                                    teacher_id
                                ).execute()

                                st.success(
                                    f"✅ {teacher_name} का access updated!"
                                )

                                st.rerun()

                            except Exception as fallback_error:

                                st.error(
                                    f"❌ Update Error: {fallback_error}"
                                )

                        else:

                            st.error(
                                f"❌ Update Error: {err}"
                            )

                # =================================================
                # PASSWORD CHANGE
                # =================================================

                st.markdown("---")

                st.markdown(
                    "### 🔑 Change Teacher Password"
                )

                new_password = st.text_input(
                    "New Password",
                    type="password",
                    key=f"new_password_{teacher_id}",
                )

                if st.button(
                    "🔐 Update Password",
                    key=f"update_password_{teacher_id}",
                ):

                    if not new_password:

                        st.warning(
                            "⚠️ नया password डालें।"
                        )

                    elif len(new_password) < 6:

                        st.warning(
                            "⚠️ Password कम से कम 6 characters का होना चाहिए।"
                        )

                    else:

                        try:

                            new_hash = hash_password(
                                new_password
                            )

                            supabase.table(
                                "users"
                            ).update(
                                {
                                    "password": new_hash
                                }
                            ).eq(
                                "id",
                                teacher_id
                            ).execute()

                            st.success(
                                "✅ Password successfully updated!"
                            )

                        except Exception as err:

                            st.error(
                                f"❌ Password update error: {err}"
                            )

                # =================================================
                # DANGER ZONE
                # =================================================

                st.markdown("---")

                st.markdown(
                    "### ⚠️ Access Control"
                )

                danger1, danger2 = st.columns(2)

                # ------------------------------------------------
                # DEACTIVATE / REVOKE
                # ------------------------------------------------

                with danger1:

                    if st.button(
                        "🗑️ Revoke Access",
                        key=f"delete_teacher_{teacher_id}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            f"confirm_delete_{teacher_id}"
                        ] = True

                # ------------------------------------------------
                # CONFIRM DELETE
                # ------------------------------------------------

                if st.session_state.get(
                    f"confirm_delete_{teacher_id}",
                    False
                ):

                    st.warning(
                        f"⚠️ क्या आप **{teacher_name}** "
                        "का access permanently revoke करना चाहते हैं?"
                    )

                    confirm1, confirm2 = st.columns(2)

                    with confirm1:

                        if st.button(
                            "✅ Yes, Revoke Access",
                            key=f"confirm_yes_{teacher_id}",
                            type="primary",
                        ):

                            try:

                                supabase.table(
                                    "users"
                                ).delete().eq(
                                    "id",
                                    teacher_id
                                ).execute()

                                st.success(
                                    f"✅ {teacher_name} का access revoke कर दिया गया।"
                                )

                                st.session_state[
                                    f"confirm_delete_{teacher_id}"
                                ] = False

                                st.rerun()

                            except Exception as err:

                                st.error(
                                    f"❌ Revoke Error: {err}"
                                )

                    with confirm2:

                        if st.button(
                            "❌ Cancel",
                            key=f"confirm_no_{teacher_id}",
                        ):

                            st.session_state[
                                f"confirm_delete_{teacher_id}"
                            ] = False

                            st.rerun()
