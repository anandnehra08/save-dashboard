import streamlit as st

# -----------------------------------------------------------
# MAIN DASHBOARD PAGE
# -----------------------------------------------------------
def render_main_dashboard():
    # 1. TOP HEADER & BRANDING LOGO
    col_logo, col_title = st.columns([1, 4])
    
    with col_logo:
        # यहाँ अपना स्कूल/संस्थान का लोगो लगा सकते हैं
        st.image("https://via.placeholder.com/150", width=120)  # आप लोकल इमेज पाथ जैसे 'assets/logo.png' भी दे सकते हैं
        
    with col_title:
        st.title("🏫 Campus ERP Pro")
        st.caption("📍 Address: Near Bus Stand, Main Road, City Center - 344032")
        st.markdown("**Contact:** +91 98765 43210 | **Email:** support@campuserp.com")

    st.markdown("---")

    # 2. QUICK STATS (ताकि डैशबोर्ड खाली न लगे)
    st.subheader("📊 School Overview")
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric(label="👨‍🎓 Total Students", value="1,250", delta="+12 this month")
    m2.metric(label="👨‍🏫 Teaching Staff", value="48", delta="Active")
    m3.metric(label="💰 Fee Collection", value="₹ 4.2 Lakhs", delta="85% Paid")
    m4.metric(label="📝 Active CBT Exams", value="3 Live Tests")

    st.markdown("---")

    # 3. QUICK LINKS / FEATURES GRID
    st.subheader("🚀 Quick Actions")
    q1, q2, q3 = st.columns(3)
    
    with q1:
        st.info("🎒 **New Student Admission**\n\nRegister new students and assign classes.")
    with q2:
        st.success("💳 **Collect School Fee**\n\nGenerate fee receipts and manage dues.")
    with q3:
        st.warning("🎯 **Launch CBT Exam**\n\nAssign online test papers and view result.")

    st.write("")
    st.write("")
    st.markdown("---")

    # 4. DEVELOPER FOOTER (Developer Details & Copyright)
    st.markdown("""
        <style>
            .footer {
                background-color: #f1f5f9;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                color: #475569;
                font-size: 14px;
                margin-top: 30px;
                border-top: 2px solid #cbd5e1;
            }
        </style>
        <div class="footer">
            <p>💻 <b>Designed & Developed by:</b> Your Name / Company Name</p>
            <p>📍 <b>Office:</b> IT Park, Tech City, India | 📞 <b>Dev Support:</b> +91 98765 43210</p>
            <p>© 2026 Campus ERP Pro. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

# Main Function Call
if __name__ == "__main__":
    st.set_page_config(page_title="Campus ERP Pro - Dashboard", page_icon="🏫", layout="wide")
    render_main_dashboard()
