import streamlit as st

def render_cbt_module():
    st.markdown("### 💻 Online CBT Exam Engine")
    
    st.info("🎯 Sample NEET/Board Practice Test")
    
    q1 = st.radio("Q1. What is the unit of Electric Current?", ["Volt", "Ampere", "Ohm", "Watt"])
    q2 = st.radio("Q2. Which cell organelle is known as the powerhouse of the cell?", ["Nucleus", "Ribosome", "Mitochondria", "Golgi Body"])
    
    if st.button("📝 Submit CBT Exam"):
        score = 0
        if q1 == "Ampere":
            score += 4
        if q2 == "Mitochondria":
            score += 4
            
        st.success(f"🎉 Exam Finished! Your Total Score: {score} / 8")
