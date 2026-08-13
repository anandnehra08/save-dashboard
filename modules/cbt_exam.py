import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from supabase import create_client

def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
# -----------------------------------------------------------
# HELPER FUNCTIONS (DB OPS)
# -----------------------------------------------------------
def fetch_all_tests():
    supabase = get_supabase_client()
    try:
        res = supabase.table("cbt_tests").select("*").eq("is_active", True).order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Error fetching tests: {e}")
        return []

def fetch_test_questions(test_id):
    supabase = get_supabase_client()
    try:
        res = supabase.table("cbt_questions").select("*").eq("test_id", test_id).order("id", desc=False).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Error fetching questions: {e}")
        return []

def save_test_attempt(test_id, sr_no, student_name, score, correct, wrong, unattempted, responses):
    supabase = get_supabase_client()
    try:
        data = {
            "test_id": test_id,
            "sr_no": int(sr_no),
            "student_name": student_name,
            "score": score,
            "correct_count": correct,
            "wrong_count": wrong,
            "unattempted_count": unattempted,
            "responses": responses,
            "submitted_at": datetime.now().isoformat()
        }
        supabase.table("cbt_attempts").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Failed to submit test: {e}")
        return False

# -----------------------------------------------------------
# MAIN CBT MODULE ROUTER
# -----------------------------------------------------------
def render_cbt_module():
    st.markdown("""
        <style>
            .nta-header { background-color: #003366; color: white; padding: 12px 20px; border-radius: 6px; }
            .q-box { background-color: #f8f9fa; border: 1px solid #e0e0e0; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
            .eng-text { font-size: 16px; font-weight: 500; color: #1a1a1a; margin-bottom: 5px; }
            .hin-text { font-size: 15px; font-weight: 400; color: #2c3e50; font-family: 'Mukta', sans-serif; background-color: #f1f5f9; padding: 8px; border-radius: 4px; }
            .pal-btn { width: 42px; height: 42px; border-radius: 4px; border: 1px solid #ccc; font-weight: bold; margin: 3px; display: inline-block; }
            .stat-badge { font-weight: bold; padding: 4px 8px; border-radius: 4px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='nta-header'><h2>🎯 NTA Style Online CBT Test Portal (Bilingual)</h2></div>", unsafe_allow_html=True)
    st.write("")

    # Tab System
    tab_exam, tab_result, tab_admin = st.tabs([
        "📝 Attempt Online Exam", 
        "📊 Instant Result & Analysis", 
        "⚙️ NTA Paper Importer / Admin"
    ])

    with tab_exam:
        render_exam_portal()

    with tab_result:
        render_results_tab()

    with tab_admin:
        render_paper_importer()

# -----------------------------------------------------------
# 1. EXAM PORTAL (Bilingual, Timer, NTA Controls)
# -----------------------------------------------------------
def render_exam_portal():
    tests = fetch_all_tests()
    if not tests:
        st.warning("Currently no active NTA Tests available. Please import a test from Admin Panel.")
        return

    test_dict = {f"{t['title']} (ID: {t['id']})": t for t in tests}
    selected_test_label = st.selectbox("📌 Select Test / परीक्षा चुनें:", list(test_dict.keys()))
    selected_test = test_dict[selected_test_label]

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        sr_no = st.number_input("Enter Student Roll No / Sr No:", min_value=1, value=101)
    with c2:
        student_name = st.text_input("Student Name:", value="Candidate")
    with c3:
        lang_pref = st.radio("Language / भाषा:", ["Both (English & हिंदी)", "English Only", "हिंदी केवल"], horizontal=True)

    if st.button("🚀 Start NTA Test Now", type="primary", use_container_width=True):
        st.session_state['active_cbt_id'] = selected_test['id']
        st.session_state['cbt_student_sr'] = sr_no
        st.session_state['cbt_student_name'] = student_name
        st.session_state['cbt_lang'] = lang_pref
        st.session_state['cbt_start_time'] = time.time()
        st.session_state['cbt_duration'] = selected_test['duration_minutes'] * 60
        st.session_state['cbt_user_answers'] = {}
        st.session_state['cbt_review_status'] = {}
        st.session_state['cbt_current_q_idx'] = 0
        st.rerun()

    # If Test is Running
    if st.session_state.get('active_cbt_id') == selected_test['id']:
        questions = fetch_test_questions(selected_test['id'])
        if not questions:
            st.error("No questions found for this test!")
            return

        total_q = len(questions)
        curr_idx = st.session_state.get('cbt_current_q_idx', 0)
        curr_q = questions[curr_idx]

        # Timer Calculation
        elapsed = time.time() - st.session_state['cbt_start_time']
        remaining = max(0, int(st.session_state['cbt_duration'] - elapsed))
        mins, secs = divmod(remaining, 60)
        hrs, mins = divmod(mins, 60)

        # Header with Timer
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.subheader(f"📋 {selected_test['title']} | Subject: {curr_q.get('subject', 'General')}")
        with t_col2:
            st.error(f"⏱️ Time Remaining: **{hrs:02d}:{mins:02d}:{secs:02d}**")

        if remaining <= 0:
            st.warning("⚠️ Time Over! Submitting test automatically...")
            submit_exam_logic(selected_test, questions)
            return

        st.markdown("---")
        
        # Grid: Main Question Area vs Side Palette
        q_col, pal_col = st.columns([3, 1])

        with q_col:
            st.markdown(f"#### Question {curr_idx + 1} of {total_q}")
            
            # Display Question Text (Bilingual support)
            q_text = curr_q['question_text']
            # If bilingual text contains || delimiter (Eng || Hindi)
            if "||" in q_text:
                q_eng, q_hin = q_text.split("||", 1)
            else:
                q_eng, q_hin = q_text, ""

            show_eng = "English" in st.session_state['cbt_lang'] or "Both" in st.session_state['cbt_lang']
            show_hin = "हिंदी" in st.session_state['cbt_lang'] or "Both" in st.session_state['cbt_lang']

            st.markdown("<div class='q-box'>", unsafe_allow_html=True)
            if show_eng and q_eng.strip():
                st.markdown(f"<div class='eng-text'><b>[ENG]</b> {q_eng.strip()}</div>", unsafe_allow_html=True)
            if show_hin and q_hin.strip():
                st.markdown(f"<div class='hin-text'><b>[HIN]</b> {q_hin.strip()}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Options Selection
            saved_ans = st.session_state['cbt_user_answers'].get(curr_q['id'], None)
            
          # पुराने रेडियो बटन वाले कोड को बदलकर यह लिखें:
opts = {
    "A": f"(a) {curr_q['option_a']}",
    "B": f"(b) {curr_q['option_b']}",
    "C": f"(c) {curr_q['option_c']}",
    "D": f"(d) {curr_q['option_d']}"
}

            opt_choices = ["None / Unattempted"] + [f"{k}) {v}" for k, v in opts.items()]
            default_index = 0
            if saved_ans in opts:
                default_index = list(opts.keys()).index(saved_ans) + 1

            selected_opt = st.radio(
                "Select your Answer:", 
                opt_choices, 
                index=default_index, 
                key=f"q_radio_{curr_q['id']}"
            )

            # Update Session State Answer
            if selected_opt != "None / Unattempted":
                st.session_state['cbt_user_answers'][curr_q['id']] = selected_opt[0]
            else:
                st.session_state['cbt_user_answers'].pop(curr_q['id'], None)

            # Bottom Action Controls
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                if st.button("⬅️ Previous", disabled=(curr_idx == 0)):
                    st.session_state['cbt_current_q_idx'] -= 1
                    st.rerun()
            with b2:
                if st.button("Next ➡️", disabled=(curr_idx == total_q - 1)):
                    st.session_state['cbt_current_q_idx'] += 1
                    st.rerun()
            with b3:
                if st.button("📌 Mark for Review"):
                    st.session_state['cbt_review_status'][curr_q['id']] = True
                    if curr_idx < total_q - 1:
                        st.session_state['cbt_current_q_idx'] += 1
                    st.rerun()
            with b4:
                if st.button("🧹 Clear Response"):
                    st.session_state['cbt_user_answers'].pop(curr_q['id'], None)
                    st.session_state['cbt_review_status'].pop(curr_q['id'], None)
                    st.rerun()

        # NTA Right Palette
        with pal_col:
            st.markdown("### 🟢 Question Palette")
            st.markdown("""
            <small>
            🟢 Answered | 🔴 Not Answered | 🟣 Review | ⚪ Not Visited
            </small>
            """, unsafe_allow_html=True)
            st.write("")

            # Render Palette Buttons
            cols = st.columns(4)
            for idx, q in enumerate(questions):
                q_id = q['id']
                is_ans = q_id in st.session_state['cbt_user_answers']
                is_rev = st.session_state['cbt_review_status'].get(q_id, False)

                badge_color = "#e0e0e0" # Grey
                txt_color = "black"
                if is_rev:
                    badge_color = "#8e44ad" # Purple
                    txt_color = "white"
                elif is_ans:
                    badge_color = "#27ae60" # Green
                    txt_color = "white"
                elif idx == curr_idx:
                    badge_color = "#e74c3c" # Red
                    txt_color = "white"

                with cols[idx % 4]:
                    if st.button(f"{idx+1}", key=f"pal_{q_id}"):
                        st.session_state['cbt_current_q_idx'] = idx
                        st.rerun()

            st.markdown("---")
            if st.button("🚩 Submit Test Final", type="primary", use_container_width=True):
                submit_exam_logic(selected_test, questions)

# -----------------------------------------------------------
# SUBMIT EXAM LOGIC & CALCULATION
# -----------------------------------------------------------
def submit_exam_logic(test_info, questions):
    user_answers = st.session_state.get('cbt_user_answers', {})
    
    correct, wrong, unattempted = 0, 0, 0
    score = 0

    for q in questions:
        q_id = q['id']
        correct_opt = str(q['correct_option']).strip().upper()
        user_opt = user_answers.get(q_id, None)

        if not user_opt:
            unattempted += 1
        elif user_opt == correct_opt:
            correct += 1
            score += 4  # NEET Scheme +4
        else:
            wrong += 1
            score -= 1  # NEET Scheme -1

    sr_no = st.session_state.get('cbt_student_sr', 101)
    name = st.session_state.get('cbt_student_name', 'Student')

    success = save_test_attempt(test_info['id'], sr_no, name, score, correct, wrong, unattempted, user_answers)

    if success:
        st.success("🎉 Test Submitted Successfully!")
        # Clear Exam Session
        st.session_state.pop('active_cbt_id', None)
        st.session_state['last_score_card'] = {
            "title": test_info['title'],
            "name": name,
            "score": score,
            "max_score": len(questions) * 4,
            "correct": correct,
            "wrong": wrong,
            "unattempted": unattempted
        }
        st.rerun()

# -----------------------------------------------------------
# 2. RESULT & ANALYSIS TAB
# -----------------------------------------------------------
def render_results_tab():
    if 'last_score_card' in st.session_state:
        card = st.session_state['last_score_card']
        st.balloons()
        st.subheader(f"🏆 Scorecard: {card['name']} - {card['title']}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Marks Scored", f"{card['score']} / {card['max_score']}")
        m2.metric("Correct ✅", card['correct'])
        m3.metric("Wrong ❌", card['wrong'])
        m4.metric("Unattempted ⚪", card['unattempted'])

        accuracy = round((card['correct'] / (card['correct'] + card['wrong'])) * 100, 2) if (card['correct'] + card['wrong']) > 0 else 0
        st.info(f"🎯 **Accuracy Rate:** {accuracy}%")
        st.markdown("---")

    # Leaderboard / Attempts List
    st.subheader("📋 Recent Test Submissions Leaderboard")
    supabase = get_supabase_client()
    try:
        attempts = supabase.table("cbt_attempts").select("*").order("submitted_at", desc=True).limit(20).execute().data
        if attempts:
            df = pd.DataFrame(attempts)
            df_display = df[['sr_no', 'student_name', 'score', 'correct_count', 'wrong_count', 'submitted_at']]
            df_display.columns = ['Roll No', 'Student Name', 'Marks', 'Correct', 'Wrong', 'Submitted Time']
            st.dataframe(df_display, use_container_width=True)
        else:
            st.write("No attempts recorded yet.")
    except Exception as e:
        st.error(f"Error loading leaderboard: {e}")

# -----------------------------------------------------------
# 3. NTA PAPER IMPORTER / ADMIN PANEL
# -----------------------------------------------------------
def render_paper_importer():
    st.subheader("➕ NTA Bilingual Question Bank Importer")
    st.write("यहाँ आप सीधे NTA NEET के नए पेपर (हिंदी + इंग्लिश) बल्क में इम्पोर्ट कर सकते हैं।")

    with st.form("create_test_form"):
        test_title = st.text_input("Test Title / Exam Name:", value="NEET 2027 Full Mock Test 01")
        target_class = st.selectbox("Target Class:", ["Class 11", "Class 12", "NEET Dropper"])
        duration = st.number_input("Duration (Minutes):", value=180)
        
        submitted_test = st.form_submit_button("Create New Test Container")
        if submitted_test and test_title:
            supabase = get_supabase_client()
            res = supabase.table("cbt_tests").insert({
                "title": test_title,
                "target_class": target_class,
                "duration_minutes": duration,
                "total_marks": 720
            }).execute()
            st.success(f"Created Test: '{test_title}'! Now add questions below.")
            st.rerun()

    st.markdown("---")
    st.subheader("📥 Add Questions (JSON / Bilingual Format)")
    
    tests = fetch_all_tests()
    if not tests:
        st.info("First create a test above.")
        return

    test_dict = {f"{t['title']} (ID: {t['id']})": t['id'] for t in tests}
    selected_t_id = st.selectbox("Choose Test to Add Questions:", list(test_dict.keys()))
    t_id = test_dict[selected_t_id]

    # Quick Template
    sample_json = [
        {
            "subject": "Physics",
            "question_text": "What is the unit of Force? || बल का मात्रक क्या है?",
            "option_a": "Joule || जूल",
            "option_b": "Newton || न्यूटन",
            "option_c": "Watt || वाट",
            "option_d": "Pascal || पास्कल",
            "correct_option": "B",
            "explanation": "Newton is the SI unit of Force. || बल का SI मात्रक न्यूटन है।"
        }
    ]

    json_input = st.text_area("Paste JSON Data (English + Hindi separated by '||'):", value=json.dumps(sample_json, indent=2, ensure_ascii=False), height=250)

    if st.button("🚀 Upload Questions to Database", type="primary"):
        try:
            q_list = json.loads(json_input)
            supabase = get_supabase_client()

            for item in q_list:
                item['test_id'] = t_id
                supabase.table("cbt_questions").insert(item).execute()

            st.success(f"✅ Successfully added {len(q_list)} Questions to Test ID {t_id}!")
        except Exception as e:
            st.error(f"Invalid JSON Format! Error: {e}")
