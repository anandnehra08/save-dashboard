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
