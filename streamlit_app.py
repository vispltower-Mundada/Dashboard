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

# ================= 📁 PROJECT MANAGEMENT (FULL 17 COLS + SEARCH) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Management Portal")

    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # TOOLBAR (Left Aligned)
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    with t1:
        if st.button("➕ Add New", use_container_width=True, type="primary"):
            st.session_state.show_form = True
            st.session_state.edit_id = None
            st.rerun()
    with t2:
        bulk = st.file_uploader("Bulk", type=['xlsx'], label_visibility="collapsed")
    
    df_m = pd.DataFrame(fetch_table("indus_data"))
    
    with t3:
        if not df_m.empty:
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df_m.to_excel(wr, index=False)
            st.download_button("📥 Download", out.getvalue(), "Vision_Master.xlsx", use_container_width=True)
    with t4:
        search = st.text_input("", placeholder="🔍 Search by ID, Site, Team...", label_visibility="collapsed")

    # FORM
    if st.session_state.show_form:
        st.divider()
        with st.form("master_form"):
            ed = None
            if st.session_state.edit_id and not df_m.empty:
                ed_row = df_m[df_m['id'] == st.session_state.edit_id]
                if not ed_row.empty: ed = ed_row.iloc[0]
            
            st.subheader("📝 Project Details Form")
            c1, c2, c3, c4 = st.columns(4)
            p_type = c1.selectbox("Project", ["Airtel", "Jio", "VIL", "O&M"], index=0)
            p_id = c2.text_input("Project ID", value=ed['Project ID'] if ed is not None else "")
            s_id = c3.text_input("Site ID", value=ed['Site ID'] if ed is not None else "")
            s_name = c4.text_input("Site Name", value=ed['Site Name'] if ed is not None else "")
            
            clstr = c1.text_input("Cluster", value=ed['Cluster'] if ed is not None else "")
            po = c2.text_input("PO Number", value=ed['PO Number'] if ed is not None else "")
            p_amt = c3.number_input("Projected Amount", value=float(ed.get('Projected Amount', 0)) if ed is not None else 0.0)
            t_name = c4.selectbox("Team Name", ["Team A", "Team B", "Team C", "Team D"])
            
            sts = c1.selectbox("Status", ["Pending", "Ongoing", "Completed"])
            t_bill = c2.number_input("Team Billing", value=float(ed.get('Team Billing', 0)) if ed is not None else 0.0)
            t_paid = c3.number_input("Team Paid Amount", value=float(ed.get('Team paid Amount', 0)) if ed is not None else 0.0)
            v_no = c4.text_input("VIS Inv No", value=ed.get('VIS Invoice No.', '') if ed is not None else "")
            
            v_date = c1.date_input("VIS Inv Date")
            v_amt = c2.number_input("VIS Bill Amt", value=float(ed.get('VIS Bill Amount', 0)) if ed is not None else 0.0)
            v_rec = c3.number_input("VIS Rec Amt", value=float(ed.get('VIS Received Amt', 0)) if ed is not None else 0.0)

            if st.form_submit_button("💾 Save Project"):
                payload = {
                    "Project": p_type, "Project ID": p_id, "Site ID": s_id, "Site Name": s_name,
                    "Cluster": clstr, "PO Number": po, "Projected Amount": p_amt, "Team Name": t_name,
                    "Site Status": sts, "Team Billing": t_bill, "Team paid Amount": t_paid,
                    "Team Balance": t_bill - t_paid, "VIS Invoice No.": v_no, "VIS Invoice Date": str(v_date),
                    "VIS Bill Amount": v_amt, "VIS Received Amt": v_rec, "VIS Balance": v_amt - v_rec,
                    "Profit": v_amt - t_bill
                }
                if st.session_state.edit_id:
                    update_row("indus_data", st.session_state.edit_id, payload)
                else:
                    insert_row("indus_data", payload)
                st.session_state.show_form = False
                st.rerun()

    # TABLE
    if not df_m.empty:
        df_f = df_m[df_m.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df_m
        
        # Pagination
        pg_size = 5
        tot_pgs = max(1, (len(df_f) // pg_size) + (1 if len(df_f) % pg_size > 0 else 0))
        curr_pg = st.number_input("Page", 1, tot_pgs, 1) if tot_pgs > 1 else 1
        
        st.markdown('<div class="full-table-wrapper">', unsafe_allow_html=True)
        st.markdown(f"""<div class="header-row">
            <div class="cell w-btn">Edit</div><div class="cell w-btn">Pay</div><div class="cell w-btn">Del</div>
            <div class="cell w-id">Project ID</div><div class="cell w-text">Project</div><div class="cell w-text">Site ID</div>
            <div class="cell w-text">Site Name</div><div class="cell w-text">Cluster</div><div class="cell w-text">PO Number</div>
            <div class="cell w-amt">Projected Amt</div><div class="cell w-text">Team Name</div><div class="cell w-status">Status</div>
            <div class="cell w-amt">Team Billing</div><div class="cell w-amt">Team Paid</div><div class="cell w-amt">Team Balance</div>
            <div class="cell w-text">VIS Inv No</div><div class="cell w-amt">VIS Bill Amt</div><div class="cell w-amt">VIS Rec Amt</div>
            <div class="cell w-amt">VIS Balance</div></div>""", unsafe_allow_html=True)

        for i, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            rid = row.get('id', i)
            b_col = st.columns([0.04, 0.04, 0.04, 0.88])
            if b_col[0].button("✏️", key=f"e_{rid}"):
                st.session_state.edit_id = rid
                st.session_state.show_form = True
                st.rerun()
            if b_col[1].button("💰", key=f"p_{rid}"): st.toast("Redirecting to Finance...")
            if b_col[2].button("🗑️", key=f"d_{rid}"):
                if st.warning("Are you sure?"):
                    delete_row("indus_data", rid)
                    st.rerun()

            st.markdown(f"""<div class="data-row">
                <div class="cell w-btn"></div><div class="cell w-btn"></div><div class="cell w-btn"></div>
                <div class="cell w-id"><b>{row.get('Project ID','-')}</b></div>
                <div class="cell w-text">{row.get('Project','-')}</div>
                <div class="cell w-text">{row.get('Site ID','-')}</div>
                <div class="cell w-text">{row.get('Site Name','-')}</div>
                <div class="cell w-text">{row.get('Cluster','-')}</div>
                <div class="cell w-text">{row.get('PO Number','-')}</div>
                <div class="cell w-amt">₹{row.get('Projected Amount',0)}</div>
                <div class="cell w-text">{row.get('Team Name','-')}</div>
                <div class="cell w-status">{row.get('Site Status','-')}</div>
                <div class="cell w-amt">₹{row.get('Team Billing',0)}</div>
                <div class="cell w-amt">₹{row.get('Team paid Amount',0)}</div>
                <div class="cell w-amt" style="color:red">₹{row.get('Team Balance',0)}</div>
                <div class="cell w-text">{row.get('VIS Invoice No.','-')}</div>
                <div class="cell w-amt">₹{row.get('VIS Bill Amount',0)}</div>
                <div class="cell w-amt">₹{row.get('VIS Received Amt',0)}</div>
                <div class="cell w-amt" style="color:orange">₹{row.get('VIS Balance',0)}</div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
