import streamlit as st
import pandas as pd
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://gmqjnokfatlevpmijcby.supabase.co"
SUPABASE_KEY = "sb_publishable_Vb9b93LMMhipMEgLiRsrNw_fmZH5OFS"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Vision Dashboard", layout="wide")

# ================= FUNCTIONS =================
def fetch_table(table_name):
    return supabase.table(table_name).select("*").execute().data

def insert_row(table_name, data):
    return supabase.table(table_name).insert(data).execute()

def update_indus(row_id, data):
    return supabase.table("indus_data").update(data).eq("id", row_id).execute()

# ================= UI MENU =================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "📁 Add Project", "💰 Finance"])

# ================= DASHBOARD =================
if menu == "📊 Dashboard":
    st.title("Vision Dashboard Summary")
    data = pd.DataFrame(fetch_table("indus_data"))

    if not data.empty:
        # Filling NaN to avoid errors in calculation
        data.fillna(0, inplace=True)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Project Amt", f"₹{data['Project Amount'].sum():,.0f}")
        col2.metric("Team Billing", f"₹{data['Team Billing'].sum():,.0f}")
        col3.metric("VIS Inv Amt", f"₹{data['VIS Inv Amt'].sum():,.0f}")
        col4.metric("Total Profit", f"₹{data['Profit'].sum():,.0f}")

        st.dataframe(data, use_container_width=True)

# ================= ADD PROJECT =================
elif menu == "📁 Add Project":
    st.title("Project Data Entry")
    
    with st.form("project_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            proj = st.text_input("Project")
            proj_id = st.text_input("Project ID")
            site_id = st.text_input("Site ID")
            site_name = st.text_input("Site Name")
            cluster = st.text_input("Cluster")
            po_no = st.text_input("PO Number")
            
        with c2:
            team_name = st.selectbox("Team Name", ["Team A", "Team B", "Team C", "Team D"])
            site_status = st.selectbox("Site Status", ["Pending", "In Progress", "Completed"])
            proj_amt = st.number_input("Project Amount", value=0.0)
            team_bill = st.number_input("Team Billing", value=0.0)
            team_paid = st.number_input("Team Paid Amt", value=0.0)
            
        with c3:
            vis_inv_no = st.text_input("VIS Inv Number")
            vis_inv_date = st.date_input("VIS Inv Date")
            vis_inv_status = st.selectbox("VIS Inv Status", ["Pending", "Submitted", "Paid"])
            vis_inv_amt = st.number_input("VIS Inv Amt", value=0.0)
            vis_rec_amt = st.number_input("VIS Rec Amt", value=0.0)

        if st.form_submit_button("Save Project Data"):
            # Internal Logic Calculations
            team_bal = team_bill - team_paid
            vis_bal = vis_inv_amt - vis_rec_amt
            profit = vis_inv_amt - team_bill
            
            payload = {
                "Project": proj, "Project ID": proj_id, "Site ID": site_id,
                "Site Name": site_name, "Cluster": cluster, "PO Number": po_no,
                "Project Amount": proj_amt, "Team Name": team_name, "Site Status": site_status,
                "Team Billing": team_bill, "Team Paid Amt": team_paid, "Team Balance": team_bal,
                "VIS Inv Number": vis_inv_no, "VIS Inv Date": str(vis_inv_date),
                "VIS Inv Status": vis_inv_status, "VIS Inv Amt": vis_inv_amt,
                "VIS Rec Amt": vis_rec_amt, "VIS Balance": vis_bal, "Profit": profit
            }
            insert_row("indus_data", payload)
            st.success("Project added successfully!")

# ================= FINANCE =================
elif menu == "💰 Finance":
    st.title("Finance Payment Entry")
    
    indus_data = pd.DataFrame(fetch_table("indus_data"))
    
    if not indus_data.empty:
        # Dropdown for Project ID
        project_ids = indus_data["Project ID"].unique().tolist()
        selected_pid = st.selectbox("Select Project ID", project_ids)
        
        # Auto-fetch related details
        details = indus_data[indus_data["Project ID"] == selected_pid].iloc[0]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**Team Name:** {details['Team Name']}")
            # Showing Team Balance in RED
            st.markdown(f"### Team Balance: <span style='color:red'>₹{details['Team Balance']}</span>", unsafe_allow_html=True)
        
        with col_b:
            pay_date = st.date_input("Payment Date")
            inword = st.number_input("Inword (Cash In)", value=0.0)
            outword = st.number_input("Outword (Cash Out)", value=0.0)
            
        if st.button("Submit Finance Entry"):
            fin_payload = {
                "Payment Date": str(pay_date),
                "Project ID": selected_pid,
                "Team Name": details["Team Name"],
                "Inword": inword,
                "Outword": outword
            }
            insert_row("finance", fin_payload)
            st.success("Finance entry saved!")
    else:
        st.warning("No projects found. Please add a project first.")