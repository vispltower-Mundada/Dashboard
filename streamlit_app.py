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

# ================= 📁 PROJECT MANAGEMENT (FULL HORIZONTAL TABLE) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")

    # Session states
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # --- CSS FOR REAL HORIZONTAL TABLE ---
    st.markdown("""
        <style>
        .main-table-container {
            overflow-x: auto;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            padding: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 1500px; /* Force horizontal scroll */
        }
        th {
            background-color: #1E60D5;
            color: white;
            text-align: left;
            padding: 12px;
            position: sticky;
            top: 0;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-size: 13px;
        }
        tr:hover { background-color: #f1f5f9; }
        .action-btns { display: flex; gap: 5px; }
        .status-pill {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- TOOLBAR ---
    t1, t2, t3, t4 = st.columns([1, 1, 1, 3])
    with t1:
        if st.button("➕ Add New Site", use_container_width=True):
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
            st.download_button("📥 Download All", out.getvalue(), "Project_Report.xlsx", use_container_width=True)
    with t4:
        search = st.text_input("", placeholder="🔍 Search by Project ID, Site Name, or Team...", label_visibility="collapsed")

    # --- FORM (ADD / EDIT) ---
    if st.session_state.show_form:
        with st.expander("📝 Enter Details", expanded=True):
            with st.form("main_entry_form"):
                ed = None
                if st.session_state.edit_id and not df_master.empty:
                    ed_query = df_master[df_master['id'] == st.session_state.edit_id]
                    if not ed_query.empty: ed = ed_query.iloc[0]
                
                c1, c2, c3, c4 = st.columns(4)
                # Group 1
                p_name = c1.text_input("Project Name", value=ed['Project'] if ed is not None else "")
                p_id = c1.text_input("Project ID", value=ed['Project ID'] if ed is not None else "")
                s_id = c1.text_input("Site ID", value=ed['Site ID'] if ed is not None else "")
                # Group 2
                s_name = c2.text_input("Site Name", value=ed['Site Name'] if ed is not None else "")
                cluster = c2.text_input("Cluster", value=ed['Cluster'] if ed is not None else "")
                po_no = c2.text_input("PO Number", value=ed['PO Number'] if ed is not None else "")
                # Group 3
                t_name = c3.selectbox("Team", ["Team A", "Team B", "Team C", "Team D"], index=0)
                s_status = c3.selectbox("Status", ["Pending", "Ongoing", "Completed"])
                p_amt = c3.number_input("Project Amt", value=float(ed['Project Amount']) if ed is not None else 0.0)
                # Group 4
                t_bill = c4.number_input("Team Billing", value=float(ed['Team Billing']) if ed is not None else 0.0)
                v_inv = c4.number_input("VIS Inv Amt", value=float(ed['VIS Inv Amt']) if ed is not None else 0.0)
                v_rec = c4.number_input("VIS Rec Amt", value=float(ed['VIS Rec Amt']) if ed is not None else 0.0)

                if st.form_submit_button("💾 Save Project Data"):
                    payload = {
                        "Project": p_name, "Project ID": p_id, "Site ID": s_id, "Site Name": s_name,
                        "Cluster": cluster, "PO Number": po_no, "Project Amount": p_amt,
                        "Team Name": t_name, "Site Status": s_status, "Team Billing": t_bill,
                        "Team Paid Amt": ed['Team Paid Amt'] if ed is not None else 0.0,
                        "Team Balance": t_bill - (ed['Team Paid Amt'] if ed is not None else 0.0),
                        "VIS Inv Amt": v_inv, "VIS Rec Amt": v_rec, "VIS Balance": v_inv - v_rec,
                        "Profit": v_inv - t_bill
                    }
                    if st.session_state.edit_id:
                        update_row("indus_data", st.session_state.edit_id, payload)
                    else:
                        insert_row("indus_data", payload)
                    st.session_state.show_form = False
                    st.rerun()

    # --- THE PROFESSIONAL TABLE ---
    if not df_master.empty:
        if search:
            df_display = df_master[df_master.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        else:
            df_display = df_master

        # Pagination logic
        p_size = 5
        total_rows = len(df_display)
        if total_rows > 0:
            total_p = (total_rows // p_size) + (1 if total_rows % p_size > 0 else 0)
            curr_p = st.number_input("Page", 1, total_p, 1) if total_p > 1 else 1
            
            start = (curr_p - 1) * p_size
            end = start + p_size

            # Table UI
            st.markdown('<div class="main-table-container"><table>'
                '<tr>'
                '<th>Actions</th><th>Project ID</th><th>Project</th><th>Site Name</th>'
                '<th>Team</th><th>Status</th><th>Team Bill</th><th>Team Bal</th>'
                '<th>VIS Inv</th><th>VIS Rec</th><th>Profit</th>'
                '</tr>', unsafe_allow_html=True)

            for i, row in df_display.iloc[start:end].iterrows():
                rid = row.get('id', i)
                # Buttons logic inside columns for Streamlit compatibility
                col_act = st.columns([0.8, 1, 1.5, 1.5, 1, 1, 1, 1, 1, 1, 1])
                
                # We use standard Streamlit columns for buttons but custom HTML for data
                with st.container():
                    b1, b2, b3, d1, d2, d3, d4, d5, d6, d7, d8 = st.columns([0.15, 0.15, 0.15, 0.5, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5, 0.5])
                    if b1.button("✏️", key=f"e_{rid}"):
                        st.session_state.edit_id = rid
                        st.session_state.show_form = True
                        st.rerun()
                    if b2.button("💰", key=f"p_{rid}"): st.toast("Opening Finance...")
                    if b3.button("🗑️", key=f"d_{rid}"):
                        delete_row("indus_data", rid)
                        st.rerun()
                    
                    d1.write(row['Project ID'])
                    d2.write(row['Project'])
                    d3.write(row['Site Name'])
                    d4.write(row['Team Name'])
                    d5.write(row['Site Status'])
                    d6.write(f"₹{row['Team Billing']}")
                    d7.write(f"₹{row['Team Balance']}")
                    d8.write(f"₹{row['Profit']}")
                    st.markdown("---")
        else:
            st.warning("Search query matches no results.")
    else:
        st.info("No data in table.")
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
