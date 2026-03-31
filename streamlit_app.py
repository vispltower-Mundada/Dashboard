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

# ================= DASHBOARD (NEW LOOK) =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Overview of your site metrics")
    
    data = pd.DataFrame(fetch_table("indus_data"))
    
    if not data.empty:
        data.fillna(0, inplace=True)
        
        # Calculations (Same Logic)
        total_proj = data['Project Amount'].sum()
        total_invested = 1500000.00 # Placeholder as per your screenshot
        total_billing = data['Team Billing'].sum()
        total_paid = data['Team Paid Amt'].sum()
        total_team_bal = data['Team Balance'].sum()
        total_vis_bill = data['VIS Inv Amt'].sum()
        total_vis_rec = data['VIS Rec Amt'].sum()
        total_vis_bal = data['VIS Balance'].sum()
        cash_in_hand = 1530000.00 # Placeholder for demo

        # Row 1
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="card blue-card"><div class="card-title">Total Projected Amount</div><div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card green-card"><div class="card-title">Total Invested Amount</div><div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card purple-card"><div class="card-title">Total Team Billing</div><div class="card-value">₹{total_billing:,.2f}</div></div>', unsafe_allow_html=True)

        # Row 2
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown(f'<div class="card orange-card"><div class="card-title">Total Team Paid</div><div class="card-value">₹{total_paid:,.2f}</div></div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="card red-card"><div class="card-title">Total Team Balance</div><div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<div class="card teal-card"><div class="card-title">Total VIS Billing</div><div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)

        # Row 3
        c7, c8, c9 = st.columns(3)
        with c7:
            st.markdown(f'<div class="card light-blue-card"><div class="card-title">Total VIS Received</div><div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        with c8:
            st.markdown(f'<div class="card dark-orange-card"><div class="card-title">Total VIS Balance</div><div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)

        # Cash in Hand (Wide Card)
        st.markdown(f'<div class="card cash-hand-card"><div class="card-title">💵 Cash in Hand</div><div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)

        st.subheader("📋 Detailed Report")
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("Data load nahi ho raha hai. Please check Supabase connection.")

# ================= BAaki Logic (Finance & Add Project) Same Rakhein =================
