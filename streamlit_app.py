import streamlit as st
import pandas as pd
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://gmqjnokfatlevpmijcby.supabase.co"
SUPABASE_KEY = "sb_publishable_Vb9b93LMMhipMEgLiRsrNw_fmZH5OFS"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Vision Dashboard", layout="wide")

# Custom CSS for Dashboard Cards (Strictly for UI)
st.markdown("""
    <style>
    .card { padding: 20px; border-radius: 10px; color: white; margin-bottom: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center; }
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

def insert_row(table_name, data):
    return supabase.table(table_name).insert(data).execute()

def delete_row(table_name, row_id):
    return supabase.table(table_name).delete().eq("id", row_id).execute()

# ================= UI MENU =================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "📁 Add Project", "💰 Finance"])

# ================= 📊 DASHBOARD (STRICT LOGIC) =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    raw_data = fetch_table("indus_data")
    data = pd.DataFrame(raw_data)
    
    if not data.empty:
        data.fillna(0, inplace=True)
        # Calculations
        total_proj = data['Project Amount'].sum()
        total_invested = 1500000.00 
        total_team_bill = data['Team Billing'].sum()
        total_team_paid = data['Team Paid Amt'].sum()
        total_team_bal = data['Team Balance'].sum()
        total_vis_bill = data['VIS Inv Amt'].sum()
        total_vis_rec = data['VIS Rec Amt'].sum()
        total_vis_bal = data['VIS Balance'].sum()
        cash_in_hand = total_vis_rec - total_team_paid

        # Layout Rows
        r1_c1, r1_c2 = st.columns(2)
        r1_c1.markdown(f'<div class="card blue-card"><div class="card-title">Total Projected Amount</div><div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        r1_c2.markdown(f'<div class="card green-card"><div class="card-title">Total Invested Amount</div><div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)

        r2_c1, r2_c2, r2_c3 = st.columns(3)
        r2_c1.markdown(f'<div class="card purple-card"><div class="card-title">Total Team Billing</div><div class="card-value">₹{total_team_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r2_c2.markdown(f'<div class="card orange-card"><div class="card-title">Total Team Paid</div><div class="card-value">₹{total_team_paid:,.2f}</div></div>', unsafe_allow_html=True)
        r2_c3.markdown(f'<div class="card red-card"><div class="card-title">Total Team Balance</div><div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)

        r3_c1, r3_c2, r3_c3 = st.columns(3)
        r3_c1.markdown(f'<div class="card teal-card"><div class="card-title">Total VIS Billing</div><div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r3_c2.markdown(f'<div class="card light-blue-card"><div class="card-title">Total VIS Received</div><div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        r3_c3.markdown(f'<div class="card dark-orange-card"><div class="card-title">Total VIS Balance</div><div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="card cash-hand-card"><div class="card-title">💵 Cash in Hand</div><div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)
    else:
        st.info("No data available.")

# ================= 📁 ADD PROJECT (RESTORED) =================
elif menu == "📁 Add Project":
    st.title("📁 Project Management")
    
    # 1. Entry Form
    with st.expander("➕ Add New Site Entry", expanded=True):
        with st.form("site_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p_name = st.text_input("Project Name")
                p_id = st.text_input("Project ID (Unique)")
                s_id = st.text_input("Site ID")
                s_name = st.text_input("Site Name")
                cluster = st.text_input("Cluster")
            with col2:
                po_no = st.text_input("PO Number")
                p_amt = st.number_input("Project Amount", value=0.0)
                t_name = st.selectbox("Team Name", ["Team A", "Team B", "Team C", "Team D"])
                s_status = st.selectbox("Site Status", ["Pending", "Ongoing", "Completed"])
                t_bill = st.number_input("Team Billing", value=0.0)
            with col3:
                t_paid = st.number_input("Team Paid Amt", value=0.0)
                v_inv_no = st.text_input("VIS Inv Number")
                v_inv_amt = st.number_input("VIS Inv Amt", value=0.0)
                v_rec_amt = st.number_input("VIS Rec Amt", value=0.0)
                v_status = st.selectbox("VIS Inv Status", ["Not Submitted", "Submitted", "Paid"])

            if st.form_submit_button("Save Data"):
                # Automatic Logic Calculations
                t_bal = t_bill - t_paid
                v_bal = v_inv_amt - v_rec_amt
                profit = v_inv_amt - t_bill
                
                payload = {
                    "Project": p_name, "Project ID": p_id, "Site ID": s_id, "Site Name": s_name,
                    "Cluster": cluster, "PO Number": po_no, "Project Amount": p_amt,
                    "Team Name": t_name, "Site Status": s_status, "Team Billing": t_bill,
                    "Team Paid Amt": t_paid, "Team Balance": t_bal, "VIS Inv Number": v_inv_no,
                    "VIS Inv Amt": v_inv_amt, "VIS Rec Amt": v_rec_amt, "VIS Balance": v_bal, "Profit": profit,
                    "VIS Inv Status": v_status
                }
                insert_row("indus_data", payload)
                st.success("Project Saved Successfully!")
                st.rerun()

    # 2. Existing Data List (With Delete Option)
    st.subheader("📋 Existing Projects")
    data_list = pd.DataFrame(fetch_table("indus_data"))
    if not data_list.empty:
        for index, row in data_list.iterrows():
            c1, c2 = st.columns([8, 1])
            c1.write(f"**{row['Project']}** | ID: {row['Project ID']} | Site: {row['Site Name']} | Team: {row['Team Name']}")
            if c2.button("🗑️", key=f"del_{row['id']}"):
                delete_row("indus_data", row['id'])
                st.rerun()

# ================= 💰 FINANCE (RESTORED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    indus_df = pd.DataFrame(fetch_table("indus_data"))
    
    if not indus_df.empty:
        p_ids = indus_df["Project ID"].unique().tolist()
        selected_id = st.selectbox("Select Project ID", p_ids)
        
        # Auto-fetch logic
        proj_row = indus_df[indus_df["Project ID"] == selected_id].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Team Assigned:** {proj_row['Team Name']}")
            # Balance in RED as requested before
            st.markdown(f"### Team Balance: <span style='color:red'>₹{proj_row['Team Balance']}</span>", unsafe_allow_html=True)
        
        with col2:
            f_date = st.date_input("Payment Date")
            inw = st.number_input("Inword", value=0.0)
            outw = st.number_input("Outword", value=0.0)
            
        if st.button("Save Finance Entry"):
            fin_payload = {
                "Payment Date": str(f_date), "Project ID": selected_id,
                "Team Name": proj_row['Team Name'], "Inword": inw, "Outword": outw
            }
            insert_row("finance", fin_payload)
            st.success("Finance Data Saved!")
