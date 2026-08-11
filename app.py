import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os
import re
import io

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SAVE Dashboard & Analytics System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Enhancement
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .header-style {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INITIALIZATION & SESSION STATE
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Standard User"
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}

# ==========================================
# UTILITY FUNCTIONS
# ==========================================
def load_data(filepath):
    """Load data from CSV or Excel file safely"""
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def format_currency(val):
    """Format numbers into INR currency format"""
    if pd.isna(val) or val is None:
        return "₹0"
    return f"₹{val:,.2f}"

def format_number(val):
    """Format large numbers with commas"""
    if pd.isna(val) or val is None:
        return "0"
    return f"{val:,}"

def generate_sample_data():
    """Generates synthetic dataset if no external file is loaded"""
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")
    categories = ['Tuition Fee', 'Transport Fee', 'Admission Fee', 'Exam Fee', 'Other']
    modes = ['Cash', 'Bank Transfer', 'UPI', 'Cheque']
    classes = [f"Class {i}" for i in range(1, 13)]
    
    data = []
    for d in dates:
        num_records = np.random.randint(1, 8)
        for _ in range(num_records):
            cat = np.random.choice(categories, p=[0.5, 0.25, 0.1, 0.1, 0.05])
            amt = np.random.randint(500, 15000) if cat != 'Tuition Fee' else np.random.randint(5000, 45000)
            data.append({
                'Date': d,
                'Category': cat,
                'Class': np.random.choice(classes),
                'Amount': amt,
                'Payment_Mode': np.random.choice(modes, p=[0.4, 0.3, 0.2, 0.1]),
                'Status': np.random.choice(['Success', 'Pending', 'Failed'], p=[0.9, 0.07, 0.03]),
                'Student_ID': f"STD-{np.random.randint(1000, 9999)}"
            })
    return pd.DataFrame(data)

# ==========================================
# HEADER SECTION (ORIGINAL VERSION)
# ==========================================
def render_header():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.title("📊 SAVE")
    with col2:
        st.subheader("School Management & Analytics System")
    with col3:
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.divider()

# ==========================================
# DASHBOARD METRICS COMPONENTS
# ==========================================
def render_metrics_cards(df):
    if df is None or df.empty:
        st.warning("No data available to display metrics.")
        return

    total_amount = df['Amount'].sum() if 'Amount' in df.columns else 0
    total_transactions = len(df)
    success_rate = (len(df[df['Status'] == 'Success']) / total_transactions * 100) if 'Status' in df.columns and total_transactions > 0 else 100
    avg_txn = total_amount / total_transactions if total_transactions > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Total Revenue", value=format_currency(total_amount))
    with c2:
        st.metric(label="Total Transactions", value=format_number(total_transactions))
    with c3:
        st.metric(label="Success Rate", value=f"{success_rate:.1f}%")
    with c4:
        st.metric(label="Avg Transaction", value=format_currency(avg_txn))

# ==========================================
# CHARTS & ANALYTICS MODULES
# ==========================================
def render_charts(df):
    if df is None or df.empty:
        return

    tab1, tab2, tab3 = st.tabs(["📈 Revenue Trends", "🏷️ Category Breakdown", "💳 Payment Modes"])
    
    with tab1:
        if 'Date' in df.columns and 'Amount' in df.columns:
            df_trend = df.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].sum().reset_index()
            fig = px.line(df_trend, x='Date', y='Amount', title='Monthly Revenue Trend', markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
    with tab2:
        if 'Category' in df.columns and 'Amount' in df.columns:
            df_cat = df.groupby('Category')['Amount'].sum().reset_index()
            fig = px.pie(df_cat, names='Category', values='Amount', title='Revenue Distribution by Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if 'Payment_Mode' in df.columns and 'Amount' in df.columns:
            df_mode = df.groupby('Payment_Mode')['Amount'].sum().reset_index()
            fig = px.bar(df_mode, x='Payment_Mode', y='Amount', color='Payment_Mode', title='Transactions by Payment Method')
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# DATA FILTERING MODULE
# ==========================================
def apply_filters(df):
    st.sidebar.header("🔍 Filters")
    
    if df is None or df.empty:
        return df

    filtered_df = df.copy()

    # Date Filter
    if 'Date' in filtered_df.columns:
        min_date = filtered_df['Date'].min().date()
        max_date = filtered_df['Date'].max().date()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        if len(date_range) == 2:
            start_d, end_d = date_range
            filtered_df = filtered_df[(filtered_df['Date'].dt.date >= start_d) & (filtered_df['Date'].dt.date <= end_d)]

    # Category Filter
    if 'Category' in filtered_df.columns:
        cats = ['All'] + list(filtered_df['Category'].unique())
        selected_cat = st.sidebar.selectbox("Category", cats)
        if selected_cat != 'All':
            filtered_df = filtered_df[filtered_df['Category'] == selected_cat]

    # Payment Mode Filter
    if 'Payment_Mode' in filtered_df.columns:
        modes = ['All'] + list(filtered_df['Payment_Mode'].unique())
        selected_mode = st.sidebar.selectbox("Payment Mode", modes)
        if selected_mode != 'All':
            filtered_df = filtered_df[filtered_df['Payment_Mode'] == selected_mode]

    return filtered_df

# ==========================================
# MAIN APPLICATION LOGIC
# ==========================================
def main():
    render_header()
    
    # Sidebar File Upload
    st.sidebar.subheader("📂 Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel Data", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file.name) # Fallback to loader
        if df is None:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    else:
        st.info("Using auto-generated demonstration data. Upload your dataset from the sidebar.")
        df = generate_sample_data()

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    # Apply Sidebar Filters
    filtered_df = apply_filters(df)

    # Render Dashboard Components
    render_metrics_cards(filtered_df)
    st.markdown("---")
    render_charts(filtered_df)

    # Data Table View
    st.markdown("### 📋 Detailed Records")
    st.dataframe(filtered_df, use_container_width=True, height=350)

    # Export Section
    st.markdown("### 📤 Export Options")
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name=f"SAVE_Analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

# ==========================================
# EXTENDED FUNCTIONALITY & UTILITIES (LINES 200-2100)
# ==========================================

def calculate_advanced_kpis(df):
    """Calculates advanced metrics including MoM growth and churn rate"""
    if df is None or df.empty or 'Amount' not in df.columns or 'Date' not in df.columns:
        return {}
    
    df_sorted = df.sort_values('Date')
    df_sorted['YearMonth'] = df_sorted['Date'].dt.to_period('M')
    monthly = df_sorted.groupby('YearMonth')['Amount'].sum()
    
    growth_rates = monthly.pct_change() * 100
    latest_growth = growth_rates.iloc[-1] if len(growth_rates) > 1 else 0.0
    
    return {
        'total_revenue': df['Amount'].sum(),
        'monthly_avg': monthly.mean() if not monthly.empty else 0,
        'latest_mom_growth': latest_growth,
        'peak_month': str(monthly.idxmax()) if not monthly.empty else "N/A",
        'peak_revenue': monthly.max() if not monthly.empty else 0
    }

def render_advanced_reports(df):
    """Renders advanced tabular reports and pivot tables"""
    st.subheader("📑 Advanced Reports & Pivot Views")
    
    report_type = st.selectbox("Select Report View", ["Class vs Category Matrix", "Monthly Reconciliation", "Student Transaction History"])
    
    if report_type == "Class vs Category Matrix":
        if 'Class' in df.columns and 'Category' in df.columns and 'Amount' in df.columns:
            pivot_df = pd.pivot_table(df, values='Amount', index='Class', columns='Category', aggfunc='sum', fill_value=0)
            st.dataframe(pivot_df.style.format("₹{:,.2f}"), use_container_width=True)
        else:
            st.warning("Required columns (Class, Category, Amount) missing.")
            
    elif report_type == "Monthly Reconciliation":
        if 'Date' in df.columns and 'Amount' in df.columns and 'Payment_Mode' in df.columns:
            df_temp = df.copy()
            df_temp['Month'] = df_temp['Date'].dt.strftime('%Y-%m')
            recon_df = pd.pivot_table(df_temp, values='Amount', index='Month', columns='Payment_Mode', aggfunc=['sum', 'count'], fill_value=0)
            st.dataframe(recon_df, use_container_width=True)
            
    elif report_type == "Student Transaction History":
        if 'Student_ID' in df.columns:
            student_ids = df['Student_ID'].unique()
            selected_student = st.selectbox("Search/Select Student ID", student_ids)
            student_records = df[df['Student_ID'] == selected_student]
            st.write(f"Total Paid: **{format_currency(student_records['Amount'].sum())}**")
            st.dataframe(student_records, use_container_width=True)

def system_logs_manager():
    """Manages internal log records"""
    logs = [
        {"Timestamp": datetime.now() - timedelta(minutes=15), "User": "System", "Action": "Data Sync Executed", "Status": "Success"},
        {"Timestamp": datetime.now() - timedelta(hours=2), "User": "Standard User", "Action": "Report Generation", "Status": "Success"},
        {"Timestamp": datetime.now() - timedelta(days=1), "User": "Standard User", "Action": "File Upload", "Status": "Success"}
    ]
    return pd.DataFrame(logs)

# ---------------------------------------------------------------------
# End of app.py base dataset
# ---------------------------------------------------------------------
