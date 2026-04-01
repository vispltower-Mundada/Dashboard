import streamlit as st
import pandas as pd
from supabase import create_client
from io import BytesIO

# ================= CONFIG & SUPABASE SETUP =================
st.set_page_config(page_title="Vision Tech Dashboard", layout="wide")

# Replace with your actual Supabase credentials if different
SUPABASE_URL = "https://gmqjnokfatlevpmijcby.supabase.co"
SUPABASE_KEY = "sb_publishable_Vb9b93LMMhipMEgLiRsrNw_fmZH5OFS"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= HELPER FUNCTIONS =================
def fetch_table(table_name):
    try:
        res = supabase.table(table_name).select("*").execute()
        return res.data
    except Exception as e: 
        st.error(f"Error fetching data: {e}")
        return []

def insert_row(table_name, data):
    return supabase.table(table_name).insert(data).execute()

def update_row(table_name, row_id, data):
    return supabase.table(table_name).update(data).eq("id", row_id).execute()

def delete_row(table_name, row_id):
    return supabase.table(table_name).delete().eq("id", row_id).execute()

# ================= MAIN NAVIGATION & URL FIX =================
# Ye URL check karta hai taaki action button click karne par page Dashboard par na bhaage
params = st.query_params
default_idx = 1 if params.get("menu") == "Project" else 0

menu = st.sidebar.radio("Main Menu", ["📊 Dashboard", "📁 Project Management", "💰 Finance"], index=default_idx)

# ================= 1. 📊 DASHBOARD =================
if menu == "📊 Dashboard":
    st.title("📊 Vision Tech Dashboard")
    st.caption("Overview of your site metrics")
    
    raw_data = fetch_table("indus_data")
    data = pd.DataFrame(raw_data)
    
    if not data.empty:
        # Numeric safety
        numeric_cols = data.select_dtypes(include=['number']).columns
        data[numeric_cols] = data[numeric_cols].fillna(0)
        data = data.fillna("") 
        
        # Calculations
        total_proj = pd.to_numeric(data.get('Projected Amount', data.get('Project Amount', 0)), errors='coerce').sum()
        total_invested = 1500000.00 
        total_team_bill = pd.to_numeric(data.get('Team Billing', 0), errors='coerce').sum()
        total_team_paid = pd.to_numeric(data.get('Team paid Amount', data.get('Team Paid Amt', 0)), errors='coerce').sum()
        total_team_bal = pd.to_numeric(data.get('Team Balance', 0), errors='coerce').sum()
        total_vis_bill = pd.to_numeric(data.get('VIS Bill Amount', data.get('VIS Inv Amt', 0)), errors='coerce').sum()
        total_vis_rec = pd.to_numeric(data.get('VIS Received Amt', data.get('VIS Rec Amt', 0)), errors='coerce').sum()
        total_vis_bal = pd.to_numeric(data.get('VIS Balance', 0), errors='coerce').sum()
        cash_in_hand = total_vis_rec - total_team_paid

        # Dashboard CSS
        st.markdown("""
        <style>
        .card { padding: 20px; border-radius: 12px; color: white; margin-bottom: 10px; height: 130px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .blue-card { background-color: #1E60D5; } .green-card { background-color: #00B65E; }
        .purple-card { background-color: #9C27B0; } .orange-card { background-color: #FF6D00; }
        .red-card { background-color: #D32F2F; } .teal-card { background-color: #009688; }
        .light-blue-card { background-color: #00ACC1; } .dark-orange-card { background-color: #EF6C00; }
        .cash-hand-card { background-color: #7E57C2; height: 160px !important; margin-top: 15px; }
        .card-title { font-size: 14px; opacity: 0.9; margin-bottom: 8px; font-weight: 500; }
        .card-value { font-size: 26px; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2)
        r1c1.markdown(f'<div class="card blue-card"><div class="card-title">Total Projected Amount</div><div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        r1c2.markdown(f'<div class="card green-card"><div class="card-title">Total Invested Amount</div><div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.markdown(f'<div class="card purple-card"><div class="card-title">Total Team Billing</div><div class="card-value">₹{total_team_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r2c2.markdown(f'<div class="card orange-card"><div class="card-title">Total Team Paid</div><div class="card-value">₹{total_team_paid:,.2f}</div></div>', unsafe_allow_html=True)
        r2c3.markdown(f'<div class="card red-card"><div class="card-title">Total Team Balance</div><div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)

        r3c1, r3c2,
