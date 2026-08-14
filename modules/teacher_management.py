import streamlit as st
import bcrypt
from database.supabase import supabase

CLASSES = [f"Class {i}" for i in range(1, 13)]
SECTIONS = ["A", "B", "C", "D"]

def hash_password(password: str) -> str:
    """Plain password को सुरक्षित Bcrypt Hash में बदलेगा"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def get_master_subjects():
    default_subjects = ["Maths", "Science", "English", "Hindi", "Physics", "Chemistry", "Social Studies"]
    if supabase:
        try:
            res = supabase.table("subjects_master").select("subject_name").execute()
            if res.data:
                return [item["subject_name"] for item in res.data]
        except Exception:
            pass
    return default_subjects

def render_teacher_management_module():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ **Access Denied:** केवल Principal/Admin ही शिक्षकों के एक्सेस को मैनेज कर सकते हैं।")
        return

    st.title("👑 Staff & Access Control Management")
    st.caption("Principal Control Panel: शिक्षकों को multiple classes और subjects का एक्सेस दें।")

    master_subjects = get_master_subjects()

    tab_add, tab_view = st.tabs(["➕ Add/Assign New Teacher", "📋 Manage Active Teachers"])

    # -------------------------------------------------------------
    # TAB 1: ADD NEW TEACHER & SET MULTIPLE CLASS PERMISSIONS
    # -------------------------------------------------------------
    with tab_add:
        st.subheader("Assign Access to Teacher")
        
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("Teacher Name", placeholder="e.g. Ramesh Kumar")
            t_email = st.text_input("Teacher Email ID", placeholder="e.g. ramesh@school.com")
            t_phone = st.text_input("Phone Number", placeholder="e.g. 9876543211")
            t_pass = st.text_input("Assign Password for Teacher", type="password", value="teacher123")

        with col2:
            t_role = st.selectbox(
                "Assign Role", 
                ["class_teacher", "subject_teacher"], 
                format_func=lambda x: "Class Teacher (Incharge of 1 Class)" if x == "class_teacher" else "Subject Teacher (Multiple Classes & Subjects)"
            )
            
            # 💡 Class Teacher के लिए Single Class और Subject Teacher के लिए MULTIPLE CLASSES
            if t_role == "class_teacher":
                assigned_classes = [st.selectbox("Assigned Incharge Class", CLASSES)]
                assigned_sec = st.selectbox("Assigned Section", SECTIONS)
                assigned_subs = ["ALL"]
                st.info("💡 **Class Teacher** उस क्लास की सभी गतिविधियों का इनचार्ज होगा।")
            else:
                # 🎯 Multiple Class Access Option for Subject Teacher
                assigned_classes = st.multiselect(
                    "Select Classes (Multiple allowed)", 
                    CLASSES, 
                    default=["Class 9", "Class 10"],
                    help="सब्जेक्ट टीचर जिन-जिन क्लासेस में पढ़ाते हैं उन सभी को चुनें।"
                )
                assigned_sec = "ALL"  # All sections or controlled in marks entry
                assigned_subs = st.multiselect("Assigned Subjects", master_subjects, default=[master_subjects[0]] if master_subjects else [])

        if st.button("➕ Create Teacher & Grant Access", type="primary", use_container_width=True):
            clean_email = t_email.strip().lower()
            if t_name.strip() and clean_email and t_pass and assigned_classes and supabase:
                try:
                    # 🔒 Password Hashing (Bcrypt) Applied Here
                    hashed_pass = hash_password(t_pass.strip())

                    payload = {
                        "name": t_name.strip(),
                        "email": clean_email,
                        "phone": t_phone.strip(),
                        "password": hashed_pass, # Hashed password inserted into Database
                        "role": t_role,
                        "assigned_class": assigned_classes[0], # Backward compatibility
                        "assigned_classes": assigned_classes,  # 🎯 Multiple classes array
                        "assigned_section": assigned_sec,
                        "assigned_subjects": assigned_subs
                    }
                    supabase.table("users").insert(payload).execute()
                    st.success(f"✅ **{t_name}** को **{', '.join(assigned_classes)}** का सुरक्षित एक्सेस दे दिया गया है!")
                    st.rerun()
                except Exception as err:
                    st.error(f"❌ Teacher जोड़ने में एरर: {err}")
            else:
                st.warning("कृपया नाम, ईमेल और कम से कम एक क्लास ज़रूर चुनें।")

    # -------------------------------------------------------------
    # TAB 2: VIEW & DELETE TEACHERS
    # -------------------------------------------------------------
    with tab_view:
        st.subheader("All Registered Staff & Permissions")
        if supabase:
            try:
                res = supabase.table("users").select("id, name, email, phone, role, assigned_class, assigned_classes, assigned_section, assigned_subjects").execute()
                teachers = res.data or []

                if teachers:
                    for t in teachers:
                        with st.expander(f"👤 {t['name']} ({t['role'].upper()}) - {t['email']}"):
                            c_a, c_b, c_c = st.columns([2, 2, 1])
                            
                            # Show assigned classes list
                            classes_list = t.get('assigned_classes') or [t.get('assigned_class', 'N/A')]
                            c_a.write(f"**Classes Allowed:** {', '.join(classes_list)}")
                            c_b.write(f"**Subjects:** {', '.join(t.get('assigned_subjects', []))}")
                            
                            if t['role'] != 'admin':
                                if c_c.button("🗑️ Revoke Access", key=f"del_{t['id']}"):
                                    supabase.table("users").delete().eq("id", t['id']).execute()
                                    st.success(f"Access revoked for {t['name']}")
                                    st.rerun()
                else:
                    st.info("अभी कोई शिक्षक पंजीकृत नहीं है।")
            except Exception as e:
                st.error(f"Fetch Error: {e}")
