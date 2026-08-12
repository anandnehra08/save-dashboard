import datetime
import pandas as pd
import streamlit as st
from database.supabase import supabase

def render_accounts_module():
    st.markdown("### 💼 Accounts Cash Book & Ledger")
    
    with st.form("cash_book_form"):
        c1, c2 = st.columns(2)
        with c1:
            voucher_no = f"VOU-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.text_input("Voucher Number", value=voucher_no, disabled=True)
            tx_type = st.selectbox("Transaction Type", ["Credit (Income)", "Debit (Expense)"])
            category = st.selectbox("Category", ["Fee Collection", "Salary Payment", "Utility Bill", "Maintenance", "Miscellaneous"])
        with c2:
            amount = st.number_input("Amount (₹)", min_value=1.0, step=500.0)
            payment_mode = st.selectbox("Payment Mode", ["Cash", "UPI", "Bank Transfer", "Cheque"])
            recorded_by = st.text_input("Recorded By", st.session_state.get("role", "Admin"))
        
        description = st.text_area("Description", "Transaction details...")
        
        if st.form_submit_button("💾 Save Voucher"):
            clean_type = "Credit" if "Credit" in tx_type else "Debit"
            record = {
                "voucher_no": voucher_no,
                "transaction_date": str(datetime.date.today()),
                "transaction_type": clean_type,
                "category": category,
                "amount": amount,
                "payment_mode": payment_mode,
                "description": description,
                "recorded_by": recorded_by
            }
            try:
                if supabase:
                    supabase.table("cash_book").insert(record).execute()
                    st.success("Voucher recorded!")
            except Exception as e:
                st.error(f"Error saving voucher: {e}")

    if supabase:
        res = supabase.table("cash_book").select("*").order("created_at", desc=True).execute()
        if res.data:
            st.markdown("---")
            st.subheader("Recent Cash Book Entries")
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
