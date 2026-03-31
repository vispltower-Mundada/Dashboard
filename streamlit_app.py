import streamlit as st
import pandas as pd
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://gmqjnokfatlevpmijcby.supabase.co"
SUPABASE_KEY = "sb_publishable_Vb9b93LMMhipMEgLiRsrNw_fmZH5OFS"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Vision Dashboard", layout="wide")

# Custom CSS for Modern Dashboard Cards (As per your screenshot)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    .card {
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .blue-card { background-color: #1E60D5; }
    .green-card { background-color: #00B65E; }
    .purple-card { background-color: #9C27B0; }
    .orange-card { background-color: #FF6D00; }
    .red-card { background-color: #D32F2F; }
    .teal-card { background-color: #009688; }
    .light-blue-card { background-color: #00ACC1; }
    .dark-orange-card { background-color: #EF6C00; }
    .cash-hand-card { background-color: #7E57C2; height: 150px !important; }
    
    .card-title { font-size: 14px; opacity: 0.9; margin-bottom: 5px; }
    .card-value { font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def fetch_table(table_name):
    return supabase.table(table_name).select("*").execute().data

# ================= UI MENU =================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "📁 Add Project", "💰 Finance"])

# ================= DASHBOARD (UPDATED SEQUENCE) =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Overview of your site metrics")
    
    # Fetch Data
    raw_data = fetch_table("indus_data")
    data = pd.DataFrame(raw_data)
    
    if not data.empty:
        data.fillna(0, inplace=True)
        
        # --- CALCULATION LOGIC ---
        total_proj = data['Project Amount'].sum()
        total_invested = 1500000.00 # Placeholder (Aap apne logic se badal sakte hain)
        
        # Team Metrics
        total_team_bill = data['Team Billing'].sum()
        total_team_paid = data['Team Paid Amt'].sum()
        total_team_bal = data['Team Balance'].sum()
        
        # VIS Metrics
        total_vis_bill = data['VIS Inv Amt'].sum()
        total_vis_rec = data['VIS Rec Amt'].sum()
        total_vis_bal = data['VIS Balance'].sum()
        
        # Cash in Hand Logic (Example: Received - Paid)
        cash_in_hand = total_vis_rec - total_team_paid

        # --- ROW 1: Project & Invested ---
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            st.markdown(f'<div class="card blue-card"><div class="card-title">Total Projected Amount</div><div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        with r1_col2:
            st.markdown(f'<div class="card green-card"><div class="card-title">Total Invested Amount</div><div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)

        st.write("") # Spacing

        # --- ROW 2: Team Data (3 Columns) ---
        r2_col1, r2_col2, r2_col3 = st.columns(3)
        with r2_col1:
            st.markdown(f'<div class="card purple-card"><div class="card-title">Total Team Billing</div><div class="card-value">₹{total_team_bill:,.2f}</div></div>', unsafe_allow_html=True)
        with r2_col2:
            st.markdown(f'<div class="card orange-card"><div class="card-title">Total Team Paid</div><div class="card-value">₹{total_team_paid:,.2f}</div></div>', unsafe_allow_html=True)
        with r2_col3:
            st.markdown(f'<div class="card red-card"><div class="card-title">Total Team Balance</div><div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)

        st.write("") # Spacing

        # --- ROW 3: VIS Data (3 Columns) ---
        r3_col1, r3_col2, r3_col3 = st.columns(3)
        with r3_col1:
            st.markdown(f'<div class="card teal-card"><div class="card-title">Total VIS Billing</div><div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)
        with r3_col2:
            st.markdown(f'<div class="card light-blue-card"><div class="card-title">Total VIS Received</div><div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        with r3_col3:
            st.markdown(f'<div class="card dark-orange-card"><div class="card-title">Total VIS Balance</div><div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)

        st.write("") # Spacing

        # --- ROW 4: Cash in Hand (Full Width) ---
        st.markdown(f'<div class="card cash-hand-card"><div class="card-title">💵 Cash in Hand</div><div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)

        # Detailed Table Below
        st.write("---")
        st.subheader("📋 Project Detailed Report")
        st.dataframe(data, use_container_width=True)

    else:
        st.info("No data found in indus_data table.")

# ================= BAaki Logic (Finance & Add Project) Same Rakhein =================
