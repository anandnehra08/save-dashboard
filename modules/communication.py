import urllib.parse
import streamlit as st
from database.supabase import supabase

def render_communication_module():
    st.markdown("### 📱 WhatsApp & Broadcast Portal")
    
    st.subheader("Send Direct WhatsApp Message")
    mobile = st.text_input("Mobile Number (e.g. 919876543210):")
    msg = st.text_area("Message:", "Dear Parent, this is an update from School ERP.")
    
    if st.button("📲 Generate WhatsApp Link"):
        if mobile and msg:
            encoded_msg = urllib.parse.quote(msg)
            whatsapp_url = f"https://wa.me/{mobile}?text={encoded_msg}"
            st.markdown(f"[👉 Click Here to Send Message via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
        else:
            st.error("Please enter both mobile number and message.")
