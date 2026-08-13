from datetime import datetime
import random
import pandas as pd
import streamlit as st
from database import supabase
from utils.pdf_generator import generate_fee_receipt_pdf

def render_fees_module():
    st.markdown("## 💰 Fee Management & PDF Receipt Generator")
    
    tab1, tab2, tab3 = st.tabs([
        "💳 Collect Fee & Receipt", 
        "📋 Payment History Ledger", 
        "📊 Fee Collection Analytics"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: COLLECT FEE
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Record New Payment")
        
        search_sr = st.number_input("Enter Student SR Number to fetch details", min_value=1, step=1, key="fee_sr_search")
        
        if search_sr and supabase:
            student_res = supabase.table("students").select("*").eq("sr_no", search_sr).execute()
            student_data = student_res.data or []
            
            if not student_data:
                st.warning(f"⚠️ No student found with SR Number: {search_sr}")
            else:
                st_info = student_data[0]
                st.success(f"👤 **Student Found:** {st_info['student_name']} | Class: {st_info['class']} ({st_info['section']}) | Father: {st_info.get('father_name', 'N/A')}")
                
                # Payment Form
                with st.form("fee_payment_form"):
                    rc1, rc2 = st.columns(2)
                    
                    # Generate Unique Receipt Number
                    receipt_no = f"REC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                    
                    with rc1:
                        st.text_input("Receipt Number", value=receipt_no, disabled=True)
                        payment_date = st.date_input("Payment Date", value=datetime.today())
                        total_due = st.number_input("Total Fee Due (₹)", min_value=0.0, step=500.0, value=25000.0)
                        
                    with rc2:
                        amount_paid = st.number_input("Amount Paid Now (₹)*", min_value=1.0, step=500.0, value=5000.0)
                        discount = st.number_input("Discount / Concession (₹)", min_value=0.0, step=100.0, value=0.0)
                        payment_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Net Banking", "Cheque", "Card"])
                        
                    remarks = st.text_input("Remarks / Note (e.g. Q1 Fee Paid)")
                    
                    submit_payment = st.form_submit_button("💾 Save Payment & Generate PDF Receipt")
                    
                    if submit_payment:
                        payload = {
                            "receipt_no": receipt_no,
                            "payment_date": str(payment_date),
                            "sr_no": int(search_sr),
                            "student_name": st_info["student_name"],
                            "class": st_info["class"],
                            "section": st_info["section"],
                            "total_due": float(total_due),
                            "amount_paid": float(amount_paid),
                            "discount": float(discount),
                            "payment_mode": payment_mode,
                            "remarks": remarks.strip()
                        }
                        
                        try:
                            # Save record to Supabase
                            supabase.table("fee_payments").insert(payload).execute()
                            st.success(f"✅ Fee Payment of ₹{amount_paid} recorded under Receipt **{receipt_no}**!")
                            
                            # Generate PDF Bytes
                            pdf_data = generate_fee_receipt_pdf(payload)
                            
                            # Provide Download Button
                            st.download_button(
                                label="📄 Download Fee Receipt (PDF)",
                                data=pdf_data,
                                file_name=f"Fee_Receipt_{receipt_no}.pdf",
                                mime="application/pdf"
                            )
                        except Exception as e:
                            st.error(f"❌ Failed to save payment: {e}")

    # -------------------------------------------------------------
    # TAB 2: PAYMENT HISTORY LEDGER
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Transaction History")
        if supabase:
            res = supabase.table("fee_payments").select("*").order("created_at", desc=True).execute()
            data = res.data or []
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No transaction history available.")

    # -------------------------------------------------------------
    # TAB 3: FEE ANALYTICS
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Summary Metrics")
        if supabase:
            res = supabase.table("fee_payments").select("amount_paid, discount").execute()
            data = res.data or []
            if data:
                total_collected = sum(item["amount_paid"] for item in data)
                total_discount = sum(item["discount"] for item in data)
                
                m1, m2 = st.columns(2)
                m1.metric("Total Fee Collected", f"₹ {total_collected:,.2f}")
                m2.metric("Total Discount Given", f"₹ {total_discount:,.2f}")
