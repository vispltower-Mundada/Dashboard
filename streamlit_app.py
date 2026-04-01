import streamlit as st
import pandas as pd
from supabase import create_client
from io import BytesIO

# ================= CONFIG (STRICT) =================
SUPABASE_URL = "https://gmqjnokfatlevpmijcby.supabase.co"
SUPABASE_KEY = "sb_publishable_Vb9b93LMMhipMEgLiRsrNw_fmZH5OFS"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Vision Dashboard", layout="wide")

# ================= CSS (DASHBOARD COLORS) =================
st.markdown("""
    <style>
    .card { padding: 20px; border-radius: 10px; color: white; margin-bottom: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center; }
    .blue-card { background-color: #1E60D5; } .green-card { background-color: #00B65E; }
    .purple-card { background-color: #9C27B0; } .orange-card { background-color: #FF6D00; }
    .red-card { background-color: #D32F2F; } .teal-card { background-color: #009688; }
    .light-blue-card { background-color: #00ACC1; } .dark-orange-card { background-color: #EF6C00; }
    .cash-hand-card { background-color: #7E57C2; height: 150px !important; margin-top: 10px; }
    .card-title { font-size: 14px; opacity: 0.9; margin-bottom: 5px; }
    .card-value { font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def fetch_table(table_name):
    try:
        res = supabase.table(table_name).select("*").execute()
        return res.data
    except: return []

def insert_row(table_name, data):
    return supabase.table(table_name).insert(data).execute()

def update_row(table_name, row_id, data):
    return supabase.table(table_name).update(data).eq("id", row_id).execute()

def delete_row(table_name, row_id):
    return supabase.table(table_name).delete().eq("id", row_id).execute()

# ================= UI MENU =================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "📁 Project Management", "💰 Finance"])

# ================= 📊 DASHBOARD (STRICT LOGIC & FIXED) =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Overview of your site metrics")
    
    raw_data = fetch_table("indus_data")
    data = pd.DataFrame(raw_data)
    
    # Yahan dhyan dein: 'if' ke niche ki saari lines 4-spaces aage hain
    if not data.empty:
        # 1. Sabse pehle column names ko clean karein (Extra spaces hatane ke liye)
        data.columns = [c.strip() for c in data.columns]
        
        # 2. Numeric columns ko identify karein aur empty cells mein 0 bharein
        numeric_cols = data.select_dtypes(include=['number']).columns
        data[numeric_cols] = data[numeric_cols].fillna(0)
        
        # 3. Baaki columns (Text) ko empty string se bhar dein
        data = data.fillna("") 
        
        # 4. Calculations (Strictly as before)
        total_proj = pd.to_numeric(data['Project Amount'], errors='coerce').sum()
        total_invested = 1500000.00 
        total_team_bill = pd.to_numeric(data['Team Billing'], errors='coerce').sum()
        total_team_paid = pd.to_numeric(data['Team Paid Amt'], errors='coerce').sum()
        total_team_bal = pd.to_numeric(data['Team Balance'], errors='coerce').sum()
        total_vis_bill = pd.to_numeric(data['VIS Inv Amt'], errors='coerce').sum()
        total_vis_rec = pd.to_numeric(data['VIS Rec Amt'], errors='coerce').sum()
        total_vis_bal = pd.to_numeric(data['VIS Balance'], errors='coerce').sum()
        cash_in_hand = total_vis_rec - total_team_paid

        # --- Dashboard Rows (UI logic strictly the same) ---
        r1c1, r1c2 = st.columns(2)
        r1c1.markdown(f'<div class="card blue-card"><div class="card-title">Total Projected Amount</div><div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        r1c2.markdown(f'<div class="card green-card"><div class="card-title">Total Invested Amount</div><div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.markdown(f'<div class="card purple-card"><div class="card-title">Total Team Billing</div><div class="card-value">₹{total_team_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r2c2.markdown(f'<div class="card orange-card"><div class="card-title">Total Team Paid</div><div class="card-value">₹{total_team_paid:,.2f}</div></div>', unsafe_allow_html=True)
        r2c3.markdown(f'<div class="card red-card"><div class="card-title">Total Team Balance</div><div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)

        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.markdown(f'<div class="card teal-card"><div class="card-title">Total VIS Billing</div><div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r3c2.markdown(f'<div class="card light-blue-card"><div class="card-title">Total VIS Received</div><div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        r3c3.markdown(f'<div class="card dark-orange-card"><div class="card-title">Total VIS Balance</div><div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="card cash-hand-card"><div class="card-title">💵 Cash in Hand</div><div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)
    
    else:
        st.info("No data found in the database.")

# ================= 📁 PROJECT MANAGEMENT (FULL 17-COLUMN TABLE) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")

    # Session states for Edit/Add
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # --- CSS FOR LAVISH HORIZONTAL SCROLL & TOOLBAR ---
    st.markdown("""
        <style>
        /* Container for Horizontal Scroll */
        .full-table-wrapper {
            overflow-x: auto;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-top: 20px;
        }
        /* Sticky Headers & Data Formatting */
        .header-row {
            display: flex;
            background-color: #1E60D5;
            color: white;
            font-weight: bold;
            padding: 12px 5px;
            border-radius: 8px 8px 0 0;
            min-width: 2500px; /* Force extreme horizontal scroll for 17 columns */
        }
        .data-row {
            display: flex;
            padding: 10px 5px;
            border-bottom: 1px solid #eee;
            align-items: center;
            min-width: 2500px;
        }
        .cell { padding: 0 10px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; }
        
        /* Column Width Definitions */
        .w-btn { width: 50px; }
        .w-id { width: 180px; }
        .w-text { width: 150px; }
        .w-amt { width: 130px; }
        .w-status { width: 120px; }
        </style>
    """, unsafe_allow_html=True)

    # --- TOP TOOLBAR (LEFT ALIGNED) ---
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    
    with t1:
        if st.button("➕ Add New", use_container_width=True, type="primary"):
            st.session_state.show_form = True
            st.session_state.edit_id = None
            st.rerun()
    with t2:
        bulk_file = st.file_uploader("Bulk Upload", type=['xlsx'], label_visibility="collapsed")
    
    df_master = pd.DataFrame(fetch_table("indus_data"))
    
    with t3:
        if not df_master.empty:
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df_master.to_excel(wr, index=False)
            st.download_button("📥 Download", out.getvalue(), "Vision_Master_Report.xlsx", use_container_width=True)
    with t4:
        search = st.text_input("", placeholder="🔍 Search by Project, ID, Site or Team...", label_visibility="collapsed")

    # --- FORM (ADD / EDIT) ---
    if st.session_state.show_form:
        st.divider()
        with st.form("site_entry_form"):
            st.subheader("📝 Project Entry / Edit")
            ed = None
            if st.session_state.edit_id and not df_master.empty:
                ed_q = df_master[df_master['id'] == st.session_state.edit_id]
                if not ed_q.empty: ed = ed_q.iloc[0]
            
            c1, c2, c3, c4 = st.columns(4)
            # Row 1
            proj_type = c1.selectbox("Project", ["Airtel", "Jio", "VIL", "O&M"], index=0)
            proj_id = c2.text_input("Project ID (Unique)", value=ed['Project ID'] if ed is not None else "")
            site_id = c3.text_input("Site ID", value=ed['Site ID'] if ed is not None else "")
            site_name = c4.text_input("Site Name", value=ed['Site Name'] if ed is not None else "")
            
            # Row 2
            cluster = c1.text_input("Cluster", value=ed['Cluster'] if ed is not None else "")
            po_no = c2.text_input("PO Number", value=ed['PO Number'] if ed is not None else "")
            p_amt = c3.number_input("Projected Amount", value=float(ed['Projected Amount']) if ed is not None else 0.0)
            t_name = c4.selectbox("Team Name", ["Team A", "Team B", "Team C"], index=0)
            
            # Row 3
            s_status = c1.selectbox("Site Status", ["Pending", "Ongoing", "Completed"])
            t_bill = c2.number_input("Team Billing", value=float(ed['Team Billing']) if ed is not None else 0.0)
            t_paid = c3.number_input("Team Paid Amount", value=float(ed['Team paid Amount']) if ed is not None else 0.0)
            v_inv_no = c4.text_input("VIS Invoice No.", value=ed['VIS Invoice No.'] if ed is not None else "")
            
            # Row 4
            v_inv_date = c1.date_input("VIS Invoice Date")
            v_bill_amt = c2.number_input("VIS Bill Amount", value=float(ed['VIS Bill Amount']) if ed is not None else 0.0)
            v_rec_amt = c3.number_input("VIS Received Amt", value=float(ed['VIS Received Amt']) if ed is not None else 0.0)

            if st.form_submit_button("💾 Save to Database"):
                payload = {
                    "Project": proj_type, "Project ID": proj_id, "Site ID": site_id, "Site Name": site_name,
                    "Cluster": cluster, "PO Number": po_no, "Projected Amount": p_amt, "Team Name": t_name,
                    "Site Status": s_status, "Team Billing": t_bill, "Team paid Amount": t_paid,
                    "Team Balance": t_bill - t_paid, "VIS Invoice No.": v_inv_no, "VIS Invoice Date": str(v_inv_date),
                    "VIS Bill Amount": v_bill_amt, "VIS Received Amt": v_rec_amt,
                    "VIS Balance": v_bill_amt - v_rec_amt, "Profit": v_bill_amt - t_bill
                }
                if st.session_state.edit_id:
                    update_row("indus_data", st.session_state.edit_id, payload)
                else:
                    insert_row("indus_data", payload)
                st.session_state.show_form = False
                st.rerun()

    # --- THE 17-COLUMN LAVISH TABLE ---
    if not df_master.empty:
        if search:
            df_display = df_master[df_master.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        else:
            df_display = df_master

        # Pagination (5 Rows)
        p_size = 5
        total_p = max(1, (len(df_display) // p_size) + (1 if len(df_display) % p_size > 0 else 0))
        curr_p = st.number_input("Page", 1, total_p, 1)
        start, end = (curr_p - 1) * p_size, curr_p * p_size

        st.markdown('<div class="full-table-wrapper">', unsafe_allow_html=True)
        
        # Header Row (All 17 logic columns)
        st.markdown(f"""
            <div class="header-row">
                <div class="cell w-btn">Edit</div>
                <div class="cell w-btn">Pay</div>
                <div class="cell w-btn">Del</div>
                <div class="cell w-id">Project ID</div>
                <div class="cell w-text">Project</div>
                <div class="cell w-text">Site ID</div>
                <div class="cell w-text">Site Name</div>
                <div class="cell w-text">Cluster</div>
                <div class="cell w-text">PO Number</div>
                <div class="cell w-amt">Projected Amt</div>
                <div class="cell w-text">Team Name</div>
                <div class="cell w-status">Status</div>
                <div class="cell w-amt">Team Billing</div>
                <div class="cell w-amt">Team Paid</div>
                <div class="cell w-amt">Team Balance</div>
                <div class="cell w-text">VIS Inv No</div>
                <div class="cell w-amt">VIS Bill Amt</div>
                <div class="cell w-amt">VIS Rec Amt</div>
                <div class="cell w-amt">VIS Balance</div>
            </div>
        """, unsafe_allow_html=True)

        for i, row in df_display.iloc[start:end].iterrows():
            rid = row.get('id', i)
            # Action Buttons Layout
            btn_col = st.columns([0.1, 0.1, 0.1, 8])
            if btn_col[0].button("✏️", key=f"e_{rid}"):
                st.session_state.edit_id = rid
                st.session_state.show_form = True
                st.rerun()
            if btn_col[1].button("💰", key=f"p_{rid}"): st.toast("Opening Finance...")
            if btn_col[2].button("🗑️", key=f"d_{rid}"):
                delete_row("indus_data", rid)
                st.rerun()

            # The Data Row
            st.markdown(f"""
                <div class="data-row">
                    <div class="cell w-btn"></div><div class="cell w-btn"></div><div class="cell w-btn"></div>
                    <div class="cell w-id"><b>{row['Project ID']}</b></div>
                    <div class="cell w-text">{row['Project']}</div>
                    <div class="cell w-text">{row['Site ID']}</div>
                    <div class="cell w-text">{row['Site Name']}</div>
                    <div class="cell w-text">{row['Cluster']}</div>
                    <div class="cell w-text">{row['PO Number']}</div>
                    <div class="cell w-amt">₹{row['Projected Amount']}</div>
                    <div class="cell w-text">{row['Team Name']}</div>
                    <div class="cell w-status">{row['Site Status']}</div>
                    <div class="cell w-amt">₹{row['Team Billing']}</div>
                    <div class="cell w-amt">₹{row['Team paid Amount']}</div>
                    <div class="cell w-amt" style="color:red">₹{row['Team Balance']}</div>
                    <div class="cell w-text">{row['VIS Invoice No.']}</div>
                    <div class="cell w-amt">₹{row['VIS Bill Amount']}</div>
                    <div class="cell w-amt">₹{row['VIS Received Amt']}</div>
                    <div class="cell w-amt" style="color:orange">₹{row['VIS Balance']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
