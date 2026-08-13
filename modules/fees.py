import datetime
import pandas as pd
import streamlit as st
from database.supabase import supabase

def render_fees_module():
    st.markdown("### 💰 Fee Management & Collections")
    
    tab1, tab2 = st.tabs(["💳 Collect Fee", "📊 Fee History"])
    
    with tab1:
        with st.form("fee_form"):
            c1, c2 = st.columns(2)
            with c1:
                sr_no = st.number_input("Student SR Number", min_value=1, step=1)
                amount = st.number_input("Fee Amount Paid (₹)", min_value=1.0, step=100.0)
            with c2:
                payment_mode = st.selectbox("Payment Mode", ["Cash", "UPI", "Bank Transfer", "Cheque"])
                remarks = st.text_input("Remarks / Fee Month", "Monthly Fee")
            
            if st.form_submit_button("💾 Process Payment"):
                record = {
                    "sr_no": sr_no,
                    "amount": amount,
                    "payment_mode": payment_mode,
                    "payment_date": str(datetime.date.today()),
                    "remarks": remarks
                }
                try:
                    if supabase:
                        supabase.table("fees").insert(record).execute()
                        st.success(f"Fee of ₹{amount} collected for SR No: {sr_no}")
                except Exception as e:
                    st.error(f"Error saving fee record: {e}")

    with tab2:
        if supabase:
            try:
                res = supabase.table("fees").select("*").execute()
                if res.data:
                    st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                else:
                    st.info("No fee transactions recorded yet.")
            except Exception as e:
                st.warning("Fees table is ready, but no data exists yet or RLS policy needs update.")
                import pandas as pd
import streamlit as st
import urllib.parse
from database.supabase import supabase

def render_fees_module():
    st.markdown("## 💳 Accounting & Fee Management")
    
    tab1, tab2, tab3 = st.tabs([
        "💰 Fee Collection & Receipt", 
        "📊 Fee Ledger & Accounting", 
        "📲 WhatsApp & SMS Portal"
    ])

    # -------------------------------------------------------------
    # TAB 1: FEE COLLECTION & WHATSAPP RECEIPT
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Collect Student Fee")
        
        c1, c2 = st.columns(2)
        with c1:
            sr_no = st.number_input("Enter Student SR Number*", min_value=1, step=1, key="fee_sr_in")
        
        student_data = None
        if sr_no and supabase:
            try:
                res = supabase.table("students").select("*").eq("sr_no", sr_no).execute()
                if res.data:
                    student_data = res.data[0]
                    st.success(f"👤 **Student Found:** {student_data['student_name']} | Class: {student_data['class']} ({student_data['section']})")
                else:
                    st.warning("⚠️ Student SR No not found.")
            except Exception as e:
                st.error(f"Error fetching student: {e}")

        if student_data:
            with st.form("fee_payment_form"):
                f1, f2 = st.columns(2)
                with f1:
                    amount_paid = st.number_input("Amount Paid (₹)*", min_value=1.0, step=100.0)
                    discount = st.number_input("Discount (₹)", min_value=0.0, step=50.0)
                with f2:
                    payment_mode = st.selectbox("Payment Mode", ["Cash", "UPI", "Bank Transfer", "Cheque"])
                    receipt_no = st.text_input("Receipt No*", value=f"REC-{sr_no}-101")
                
                remarks = st.text_input("Remarks / Note (e.g., Apr-Jun Term Fee)")
                
                submit_fee = st.form_submit_button("💾 Save Payment & Generate Receipt")
                
                if submit_fee:
                    payload = {
                        "sr_no": int(sr_no),
                        "amount_paid": float(amount_paid),
                        "discount": float(discount),
                        "payment_mode": payment_mode,
                        "receipt_no": receipt_no.strip(),
                        "remarks": remarks.strip()
                    }
                    if supabase:
                        try:
                            supabase.table("fee_transactions").insert(payload).execute()
                            st.success(f"✅ Payment of ₹{amount_paid} recorded successfully for {student_data['student_name']}!")
                            
                            # Auto Direct WhatsApp Alert Link
                            mobile = student_data.get("mobile", "")
                            if mobile:
                                msg = f"Dear Parent, received ₹{amount_paid} fee for {student_data['student_name']} (SR: {sr_no}). Receipt No: {receipt_no}. Thank you! - Campus School"
                                encoded_msg = urllib.parse.quote(msg)
                                wa_link = f"https://wa.me/91{mobile}?text={encoded_msg}"
                                st.markdown(f"👉 [📲 Click Here to Send WhatsApp Receipt to Parent]({wa_link})")
                        except Exception as ex:
                            st.error(f"Error saving fee: {ex}")

    # -------------------------------------------------------------
    # TAB 2: ACCOUNTING & TRANSACTION LEDGER
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Accounting Summary & Fee Transactions")
        if supabase:
            try:
                tx_res = supabase.table("fee_transactions").select("*").execute()
                if tx_res.data:
                    df = pd.DataFrame(tx_res.data)
                    
                    # Metrics / Summary
                    total_collected = df['amount_paid'].sum()
                    total_discount = df['discount'].sum()
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Fee Collected", f"₹{total_collected:,.2f}")
                    m2.metric("Total Discounts Given", f"₹{total_discount:,.2f}")
                    m3.metric("Total Transactions", len(df))
                    
                    st.markdown("---")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No fee transactions recorded yet.")
            except Exception as e:
                st.error(f"Error fetching ledger: {e}")

    # -------------------------------------------------------------
    # TAB 3: WHATSAPP & SMS DIRECT PORTAL
    # -------------------------------------------------------------
    with tab3:
        st.subheader("📢 Quick WhatsApp & SMS Broadcast")
        st.info("यहाँ से आप किसी भी अभिभावक को तुरंत सीधा WhatsApp मैसेज भेज सकते हैं।")
        
        phone_num = st.text_input("Parent Mobile Number (10 digit)", placeholder="9876543210")
        custom_msg = st.text_area("Message Text", "Dear Parent, please pay the pending school fees at the earliest. Thank you!")
        
        if st.button("💬 Send WhatsApp Message"):
            if phone_num and custom_msg:
                encoded = urllib.parse.quote(custom_msg)
                wa_url = f"https://wa.me/91{phone_num}?text={encoded}"
                st.markdown(f"👉 [Click here to Open WhatsApp & Send Message]({wa_url})")
            else:
                st.warning("Please enter mobile number and message.")
