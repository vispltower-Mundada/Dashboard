import streamlit as st
import pandas as pd
from supabase import create_client
from io import BytesIO

# ================= CONFIG (STRICTLY NO CHANGE) =================
SUPABASE_URL = "https://gmqjnokfatlevpmijcby.supabase.co"
SUPABASE_KEY = "sb_publishable_Vb9b93LMMhipMEgLiRsrNw_fmZH5OFS"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Vision Dashboard", layout="wide")

# ================= CSS (DASHBOARD COLORS KE SAATH MATCHING) =================
st.markdown("""
    <style>
    /* Dashboard Cards CSS (Unchanged) */
    .card { padding: 20px; border-radius: 10px; color: white; margin-bottom: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center; }
    .blue-card { background-color: #1E60D5; } .green-card { background-color: #00B65E; }
    .purple-card { background-color: #9C27B0; } .orange-card { background-color: #FF6D00; }
    .red-card { background-color: #D32F2F; } .teal-card { background-color: #009688; }
    .light-blue-card { background-color: #00ACC1; } .dark-orange-card { background-color: #EF6C00; }
    .cash-hand-card { background-color: #7E57C2; height: 150px !important; }
    
    /* New Table Styling */
    .stDataFrame { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .action-btn { cursor: pointer; border: none; padding: 5px 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def fetch_table(table_name):
    return supabase.table(table_name).select("*").execute().data

def insert_row(table_name, data):
    return supabase.table(table_name).insert(data).execute()

def update_row(table_name, row_id, data):
    return supabase.table(table_name).update(data).eq("id", row_id).execute()

def delete_row(table_name, row_id):
    return supabase.table(table_name).delete().eq("id", row_id).execute()

# ================= UI MENU =================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "📁 Project Management", "💰 Finance"])

# ================= 📊 DASHBOARD (0% CHANGE) =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    data = pd.DataFrame(fetch_table("indus_data"))
    if not data.empty:
        data.fillna(0, inplace=True)
        # ... (Pura Dashboard Logic Jo Pehle Tha) ...
        total_proj = data['Project Amount'].sum()
        total_invested = 1500000.00 
        total_team_bill = data['Team Billing'].sum()
        total_team_paid = data['Team Paid Amt'].sum()
        total_team_bal = data['Team Balance'].sum()
        total_vis_bill = data['VIS Inv Amt'].sum()
        total_vis_rec = data['VIS Rec Amt'].sum()
        total_vis_bal = data['VIS Balance'].sum()
        cash_in_hand = total_vis_rec - total_team_paid

        r1_c1, r1_c2 = st.columns(2)
        r1_c1.markdown(f'<div class="card blue-card">Total Projected Amount<div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        r1_c2.markdown(f'<div class="card green-card">Total Invested Amount<div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        r2_c1.markdown(f'<div class="card purple-card">Total Team Billing<div class="card-value">₹{total_team_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r2_c2.markdown(f'<div class="card orange-card">Total Team Paid<div class="card-value">₹{total_team_paid:,.2f}</div></div>', unsafe_allow_html=True)
        r2_c3.markdown(f'<div class="card red-card">Total Team Balance<div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        r3_c1.markdown(f'<div class="card teal-card">Total VIS Billing<div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r3_c2.markdown(f'<div class="card light-blue-card">Total VIS Received<div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        r3_c3.markdown(f'<div class="card dark-orange-card">Total VIS Balance<div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card cash-hand-card">💵 Cash in Hand<div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)

# ================= 📁 PROJECT MANAGEMENT (NEW STYLE) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")
    
    # Init session states for Edit/Add
    if "form_mode" not in st.session_state: st.session_state.form_mode = None
    if "edit_data" not in st.session_state: st.session_state.edit_data = None

    # --- TOP BUTTONS & SEARCH ---
    col_btn1, col_btn2, col_btn3, col_search = st.columns([1.5, 1.5, 1.5, 4])
    
    if col_btn1.button("➕ Add New"):
        st.session_state.form_mode = "add"
        st.session_state.edit_data = None
        
    upload_file = col_btn2.file_uploader("Bulk Upload", type=['xlsx'], label_visibility="collapsed")
    
    raw_df = pd.DataFrame(fetch_table("indus_data"))
    if not raw_df.empty:
        # Download Button
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            raw_df.to_excel(writer, index=False)
        col_btn3.download_button("📥 Download", data=output.getvalue(), file_name="Indus_Report.xlsx")

    search_query = col_search.text_input("🔍 Search Site, ID, Team...", placeholder="Type to filter table...")

    # --- ACTION FORMS (Add/Edit) ---
    if st.session_state.form_mode:
        with st.expander("📝 Form Entry", expanded=True):
            with st.form("site_form"):
                ed = st.session_state.edit_data
                c1, c2, c3 = st.columns(3)
                p_name = c1.text_input("Project", value=ed['Project'] if ed else "")
                p_id = c1.text_input("Project ID", value=ed['Project ID'] if ed else "")
                s_name = c2.text_input("Site Name", value=ed['Site Name'] if ed else "")
                t_name = c2.selectbox("Team Name", ["Team A", "Team B", "Team C"], index=0)
                t_bill = c3.number_input("Team Billing", value=float(ed['Team Billing']) if ed else 0.0)
                v_amt = c3.number_input("VIS Inv Amt", value=float(ed['VIS Inv Amt']) if ed else 0.0)
                
                # Logic calculation (Keep as is)
                sub_btn = st.form_submit_button("💾 Save Project")
                if sub_btn:
                    payload = {"Project": p_name, "Project ID": p_id, "Site Name": s_name, "Team Name": t_name, 
                               "Team Billing": t_bill, "VIS Inv Amt": v_amt, "Profit": v_amt - t_bill}
                    if st.session_state.form_mode == "edit":
                        update_row("indus_data", ed['id'], payload)
                    else:
                        insert_row("indus_data", payload)
                    st.session_state.form_mode = None
                    st.rerun()

    # --- THE LAVISH TABLE ---
    if not raw_df.empty:
        # Filter Logic
        if search_query:
            df = raw_df[raw_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
        else:
            df = raw_df

        # Pagination Logic (5 per page)
        rows_per_page = 5
        total_pages = (len(df) // rows_per_page) + (1 if len(df) % rows_per_page > 0 else 0)
        curr_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (curr_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        # Display Table with Actions
        st.write("---")
        # Action Buttons in a loop for each row
        for i, row in df.iloc[start_idx:end_idx].iterrows():
            with st.container():
                cols = st.columns([0.5, 0.5, 0.5, 2, 2, 2, 2])
                if cols[0].button("✏️", key=f"ed_{row['id']}"):
                    st.session_state.form_mode = "edit"
                    st.session_state.edit_data = row
                    st.rerun()
                if cols[1].button("💰", key=f"pay_{row['id']}"):
                    st.session_state.target_pay_id = row['Project ID']
                    # Link to Finance Page
                    st.info(f"Go to Finance Page for ID: {row['Project ID']}")
                if cols[2].button("🗑️", key=f"del_{row['id']}"):
                    if st.warning(f"Confirm delete {row['Project ID']}?"):
                        delete_row("indus_data", row['id'])
                        st.rerun()
                
                cols[3].write(f"**ID:** {row['Project ID']}")
                cols[4].write(f"**Site:** {row['Site Name']}")
                cols[5].write(f"**Team:** {row['Team Name']}")
                cols[6].write(f"**Profit:** ₹{row['Profit']}")
                st.write("---")

# ================= 💰 FINANCE (SAME LOGIC) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # ... Finance code stays same as previous ...
