import streamlit as st
import pandas as pd
import time
from database.supabase import supabase

def render_cbt_module():
    st.markdown("## 🎯 NEET 2027 Computer Based Test (CBT) Portal")
    
    role = st.sidebar.radio("CBT Navigation", ["📝 Student Exam Portal", "🛠️ Admin (Add Test & Questions)", "📊 Test Analytics & Ranks"])

    # -----------------------------------------------------------------
    # ADMIN: CREATE TEST & ADD QUESTIONS
    # -----------------------------------------------------------------
    if role == "🛠️ Admin (Add Test & Questions)":
        st.subheader("Manage NEET CBT Tests")
        tab1, tab2 = st.tabs(["➕ Create New Test", "❓ Add Questions"])
        
        with tab1:
            test_title = st.text_input("Test Title", placeholder="e.g. NEET 2027 Full Mock Test - 01")
            col1, col2 = st.columns(2)
            duration = col1.number_input("Duration (Minutes)", value=180, step=15)
            target_cls = col2.selectbox("Target Class", [f"Class {i}" for i in range(11, 13)])
            
            if st.button("🚀 Create Test"):
                if test_title.strip():
                    try:
                        supabase.table("cbt_tests").insert({
                            "title": test_title.strip(),
                            "duration_minutes": duration,
                            "target_class": target_cls
                        }).execute()
                        st.success(f"Test '{test_title}' created successfully!")
                    except Exception as e:
                        st.error(f"Error creating test: {e}")
                else:
                    st.warning("Enter a valid test title.")
                    
        with tab2:
            try:
                tests_res = supabase.table("cbt_tests").select("*").execute()
                tests = tests_res.data or []
                if not tests:
                    st.info("No tests available. Create a test first.")
                else:
                    test_map = {t["title"]: t["id"] for t in tests}
                    selected_test_name = st.selectbox("Select Test", list(test_map.keys()))
                    selected_test_id = test_map[selected_test_name]
                    
                    st.markdown("---")
                    st.write("##### Question Entry Form")
                    q_sub = st.selectbox("Subject", ["Physics", "Chemistry", "Botany", "Zoology"])
                    q_text = st.text_area("Question Text")
                    c1, c2 = st.columns(2)
                    opt_a = c1.text_input("Option A")
                    opt_b = c2.text_input("Option B")
                    opt_c = c1.text_input("Option C")
                    opt_d = c2.text_input("Option D")
                    
                    c_ans = st.selectbox("Correct Option", ["A", "B", "C", "D"])
                    exp = st.text_area("Explanation / Solution (Optional)")
                    
                    if st.button("💾 Save Question"):
                        if q_text and opt_a and opt_b and opt_c and opt_d:
                            supabase.table("cbt_questions").insert({
                                "test_id": selected_test_id,
                                "subject": q_sub,
                                "question_text": q_text,
                                "option_a": opt_a,
                                "option_b": opt_b,
                                "option_c": opt_c,
                                "option_d": opt_d,
                                "correct_option": c_ans,
                                "explanation": exp
                            }).execute()
                            st.success("Question added successfully!")
                        else:
                            st.warning("Please fill all required question fields.")
            except Exception as e:
                st.error(f"Error loading questions manager: {e}")

    # -----------------------------------------------------------------
    # STUDENT: LIVE CBT EXAM
    # -----------------------------------------------------------------
    elif role == "📝 Student Exam Portal":
        st.subheader("Live NEET CBT Examination")
        
        # Test Selection
        tests_res = supabase.table("cbt_tests").select("*").eq("is_active", True).execute()
        tests = tests_res.data or []
        
        if not tests:
            st.warning("Currently no active CBT tests available.")
            return
            
        test_map = {t["title"]: t for t in tests}
        sel_title = st.selectbox("Select Exam", list(test_map.keys()))
        current_test = test_map[sel_title]
        
        student_sr = st.number_input("Enter Your SR Number", min_value=1, step=1)
        student_name = st.text_input("Enter Your Name")
        
        if "cbt_started" not in st.session_state:
            st.session_state.cbt_started = False

        if not st.session_state.cbt_started:
            if st.button("🏁 Start Examination"):
                if student_sr and student_name:
                    # Fetch questions for this test
                    q_res = supabase.table("cbt_questions").select("*").eq("test_id", current_test["id"]).execute()
                    questions = q_res.data or []
                    
                    if not questions:
                        st.error("This test has no questions added yet!")
                    else:
                        st.session_state.cbt_questions = questions
                        st.session_state.cbt_responses = {}
                        st.session_state.cbt_review = set()
                        st.session_state.cbt_current_index = 0
                        st.session_state.cbt_started = True
                        st.session_state.cbt_start_time = time.time()
                        st.rerun()
                else:
                    st.warning("Please enter your SR Number and Name to start.")
        else:
            # Active Test Dashboard (NTA Style)
            questions = st.session_state.cbt_questions
            curr_idx = st.session_state.cbt_current_index
            q_curr = questions[curr_idx]
            
            st.markdown(f"### {current_test['title']} | Subject: **{q_curr['subject']}**")
            
            # Left Column: Question Window | Right Column: Palette
            col_left, col_right = st.columns([3, 1])
            
            with col_left:
                st.markdown(f"#### Question {curr_idx + 1} of {len(questions)}")
                st.info(q_curr["question_text"])
                
                # Options
                opts = {
                    "A": q_curr["option_a"],
                    "B": q_curr["option_b"],
                    "C": q_curr["option_c"],
                    "D": q_curr["option_d"]
                }
                
                prev_ans = st.session_state.cbt_responses.get(q_curr["id"], None)
                
                chosen = st.radio(
                    "Choose Option:", 
                    options=list(opts.keys()), 
                    format_func=lambda x: f"({x}) {opts[x]}",
                    index=list(opts.keys()).index(prev_ans) if prev_ans in opts else None,
                    key=f"q_radio_{curr_idx}"
                )
                
                if chosen:
                    st.session_state.cbt_responses[q_curr["id"]] = chosen
                
                b_col1, b_col2, b_col3 = st.columns(3)
                if b_col1.button("⬅️ Previous") and curr_idx > 0:
                    st.session_state.cbt_current_index -= 1
                    st.rerun()
                if b_col2.button("Save & Next ➡️") and curr_idx < len(questions) - 1:
                    st.session_state.cbt_current_index += 1
                    st.rerun()
                if b_col3.button("🟣 Mark for Review"):
                    st.session_state.cbt_review.add(q_curr["id"])
                    if curr_idx < len(questions) - 1:
                        st.session_state.cbt_current_index += 1
                    st.rerun()
                    
            with col_right:
                st.markdown("##### Question Palette")
                
                # Grid of Palette Buttons
                cols = st.columns(4)
                for idx, q in enumerate(questions):
                    q_id = q["id"]
                    status_emoji = "⚪" # Unvisited/Not Answered
                    if q_id in st.session_state.cbt_responses:
                        status_emoji = "🟢" # Answered
                    if q_id in st.session_state.cbt_review:
                        status_emoji = "🟣" # Review
                        
                    with cols[idx % 4]:
                        if st.button(f"{status_emoji} {idx+1}", key=f"pal_{idx}"):
                            st.session_state.cbt_current_index = idx
                            st.rerun()
                
                st.markdown("---")
                if st.button("🚨 SUBMIT TEST", type="primary"):
                    # Calculate NEET Score (+4 for correct, -1 for wrong)
                    correct = 0
                    wrong = 0
                    unattempted = 0
                    
                    for q in questions:
                        ans = st.session_state.cbt_responses.get(q["id"])
                        if ans is None:
                            unattempted += 1
                        elif ans == q["correct_option"]:
                            correct += 1
                        else:
                            wrong += 1
                            
                    score = (correct * 4) - (wrong * 1)
                    
                    # Save attempt
                    supabase.table("cbt_attempts").insert({
                        "test_id": current_test["id"],
                        "sr_no": student_sr,
                        "student_name": student_name,
                        "score": score,
                        "correct_count": correct,
                        "wrong_count": wrong,
                        "unattempted_count": unattempted,
                        "responses": st.session_state.cbt_responses
                    }).execute()
                    
                    st.session_state.cbt_started = False
                    st.success(f"🎉 Exam Submitted Successfully! Total Score: {score} / {len(questions)*4}")
                    st.metric("Score", score)
                    st.write(f"✅ Correct: {correct} | ❌ Wrong: {wrong} | ⚪ Unattempted: {unattempted}")

    # -----------------------------------------------------------------
    # ANALYTICS & RANKS
    # -----------------------------------------------------------------
    elif role == "📊 Test Analytics & Ranks":
        st.subheader("CBT Results & Leaderboard")
        try:
            attempts_res = supabase.table("cbt_attempts").select("*").order("score", desc=True).execute()
            data = attempts_res.data or []
            if data:
                df = pd.DataFrame(data)
                cols = ["sr_no", "student_name", "score", "correct_count", "wrong_count", "unattempted_count", "submitted_at"]
                display_df = df[[c for c in cols if c in df.columns]]
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No test attempts recorded yet.")
        except Exception as e:
            st.error(f"Error fetching analytics: {e}")
