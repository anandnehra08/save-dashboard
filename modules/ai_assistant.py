import streamlit as st
from datetime import datetime


def clear_chat():
    st.session_state["erp_chat_messages"] = []


def get_erp_response(user_message):
    """
    फिलहाल basic ERP Assistant.
    अगले चरण में इसे Supabase के live data से connect करेंगे.
    """

    msg = user_message.lower().strip()

    if any(word in msg for word in ["student", "students", "विद्यार्थी", "छात्र"]):
        return (
            "👨‍🎓 **Student Management**\n\n"
            "आप Student Directory में students की जानकारी देख सकते हैं, "
            "नए students add कर सकते हैं और student records manage कर सकते हैं।"
        )

    if any(word in msg for word in ["fee", "fees", "फीस", "फीस"]):
        return (
            "💳 **Fees & Accounting**\n\n"
            "Accounting & Fees module में fee collection, dues और receipts "
            "manage किए जा सकते हैं।"
        )

    if any(word in msg for word in ["attendance", "उपस्थिति", "हाजिरी"]):
        return (
            "📅 **Attendance**\n\n"
            "Attendance Register से students की daily attendance manage की जा सकती है।"
        )

    if any(word in msg for word in ["exam", "exams", "marks", "result", "परीक्षा", "परिणाम"]):
        return (
            "📝 **Exam & Marks**\n\n"
            "Exam & Marks module से examinations, marks और results manage किए जा सकते हैं।"
        )

    if any(word in msg for word in ["teacher", "staff", "teacher", "शिक्षक", "स्टाफ"]):
        return (
            "👑 **Staff Management**\n\n"
            "Staff & Access Control module में teachers/staff और उनके access roles "
            "manage किए जा सकते हैं।"
        )

    if any(word in msg for word in ["hello", "hi", "hey", "नमस्ते", "हेलो"]):
        return (
            "👋 नमस्ते! मैं **Campus ERP Assistant** हूँ।\n\n"
            "आप मुझसे Student, Attendance, Fees, Exams और Staff "
            "से संबंधित सवाल पूछ सकते हैं।"
        )

    return (
        "🤖 मैं आपके Campus ERP में आपकी मदद करने के लिए तैयार हूँ।\n\n"
        "आप इनमें से कुछ पूछ सकते हैं:\n\n"
        "• 👨‍🎓 Students की जानकारी\n"
        "• 📅 Attendance\n"
        "• 💳 Fees\n"
        "• 📝 Exams & Results\n"
        "• 👑 Staff Management\n\n"
        "अगले upgrade में मैं Supabase के **live data** से जवाब देना सीखूँगा।"
    )


def render_ai_assistant():

    # -----------------------------
    # Session State
    # -----------------------------
    if "erp_chat_messages" not in st.session_state:
        st.session_state["erp_chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Welcome to Campus ERP AI Assistant**\n\n"
                    "मैं आपके ERP को manage करने में मदद कर सकता हूँ। "
                    "नीचे अपना सवाल लिखें।"
                ),
                "time": datetime.now().strftime("%H:%M")
            }
        ]

    # -----------------------------
    # Header
    # -----------------------------
    st.title("🤖 Campus ERP AI Assistant")
    st.caption("Smart assistant for Campus ERP Pro")

    st.markdown("---")

    # -----------------------------
    # Quick Questions
    # -----------------------------
    st.subheader("⚡ Quick Questions")

    q1, q2, q3, q4, q5 = st.columns(5)

    if q1.button(
        "👨‍🎓 Students",
        use_container_width=True,
        key="chat_quick_students"
    ):
        st.session_state["erp_pending_question"] = (
            "Student management के बारे में बताओ"
        )
        st.rerun()

    if q2.button(
        "📅 Attendance",
        use_container_width=True,
        key="chat_quick_attendance"
    ):
        st.session_state["erp_pending_question"] = (
            "Attendance कैसे manage करें?"
        )
        st.rerun()

    if q3.button(
        "💳 Fees",
        use_container_width=True,
        key="chat_quick_fees"
    ):
        st.session_state["erp_pending_question"] = (
            "Fees management के बारे में बताओ"
        )
        st.rerun()

    if q4.button(
        "📝 Exams",
        use_container_width=True,
        key="chat_quick_exams"
    ):
        st.session_state["erp_pending_question"] = (
            "Exam और marks management के बारे में बताओ"
        )
        st.rerun()

    if q5.button(
        "👑 Staff",
        use_container_width=True,
        key="chat_quick_staff"
    ):
        st.session_state["erp_pending_question"] = (
            "Staff management के बारे में बताओ"
        )
        st.rerun()

    st.markdown("---")

    # -----------------------------
    # Chat History
    # -----------------------------
    chat_container = st.container()

    with chat_container:

        for message in st.session_state["erp_chat_messages"]:

            role = message["role"]

            with st.chat_message(role):

                st.markdown(message["content"])

                if message.get("time"):
                    st.caption(message["time"])

    # -----------------------------
    # Pending Quick Question
    # -----------------------------
    pending_question = st.session_state.pop(
        "erp_pending_question",
        None
    )

    if pending_question:

        st.session_state["erp_chat_messages"].append(
            {
                "role": "user",
                "content": pending_question,
                "time": datetime.now().strftime("%H:%M")
            }
        )

        answer = get_erp_response(pending_question)

        st.session_state["erp_chat_messages"].append(
            {
                "role": "assistant",
                "content": answer,
                "time": datetime.now().strftime("%H:%M")
            }
        )

        st.rerun()

    # -----------------------------
    # Chat Input
    # -----------------------------
    user_prompt = st.chat_input(
        "Campus ERP के बारे में अपना सवाल लिखें..."
    )

    if user_prompt:

        # User message
        st.session_state["erp_chat_messages"].append(
            {
                "role": "user",
                "content": user_prompt,
                "time": datetime.now().strftime("%H:%M")
            }
        )

        # Assistant response
        answer = get_erp_response(user_prompt)

        st.session_state["erp_chat_messages"].append(
            {
                "role": "assistant",
                "content": answer,
                "time": datetime.now().strftime("%H:%M")
            }
        )

        st.rerun()

    # -----------------------------
    # Sidebar Chat Controls
    # -----------------------------
    with st.sidebar:

        st.markdown("---")
        st.subheader("🤖 AI Assistant")

        if st.button(
            "🗑️ Clear Chat History",
            use_container_width=True,
            key="clear_erp_chat"
        ):
            clear_chat()
            st.rerun()

        st.caption(
            f"Messages: {len(st.session_state['erp_chat_messages'])}"
        )
