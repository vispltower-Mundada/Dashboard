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

# ================= 📁 PROJECT MANAGEMENT (TRUE HORIZONTAL TABLE) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Management Portal")

    # Session states
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # --- TOOLBAR (Add, Upload, Download, Search) ---
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    with t1:
        if st.button("➕ Add New", use_container_width=True, type="primary"):
            st.session_state.show_form = True
            st.session_state.edit_id = None
            st.rerun()
    with t2:
        bulk = st.file_uploader("Bulk Upload", type=['xlsx'], label_visibility="collapsed")
    
    df_m = pd.DataFrame(fetch_table("indus_data"))
    
    with t3:
        if not df_m.empty:
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df_m.to_excel(wr, index=False)
            st.download_button("📥 Download Excel", out.getvalue(), "Vision_Master.xlsx", use_container_width=True)
    with t4:
        search = st.text_input("", placeholder="🔍 Search anything...", label_visibility="collapsed")

    # --- CSS FOR REAL HORIZONTAL SCROLL ---
    st.markdown("""
        <style>
        .table-wrapper {
            width: 100%;
            overflow-x: auto; /* This enables the horizontal scroll */
            border: 1px solid #e6e9ef;
            border-radius: 10px;
        }
        .modern-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 2800px; /* Forces the table to stay wide */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .modern-table th {
            background-color: #1E60D5;
            color: white;
            padding: 15px;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .modern-table td {
            padding: 12px;
            border-bottom: 1px solid #f0f2f6;
            font-size: 14px;
            color: #31333F;
        }
        .modern-table tr:hover { background-color: #f8f9fb; }
        .btn-link {
            text-decoration: none;
            color: #1E60D5;
            font-weight: bold;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- TABLE LOGIC ---
    if not df_m.empty:
        # Search filter
        df_f = df_m[df_m.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df_m
        
        # Pagination
        pg_size = 5
        tot_pgs = max(1, (len(df_f) // pg_size) + (1 if len(df_f) % pg_size > 0 else 0))
        curr_pg = st.number_input("Page", 1, tot_pgs, 1)

        # Start Table HTML
        html_table = f"""
        <div class="table-wrapper">
            <table class="modern-table">
                <tr>
                    <th>Actions</th>
                    <th>Project ID</th>
                    <th>Project</th>
                    <th>Site ID</th>
                    <th>Site Name</th>
                    <th>Cluster</th>
                    <th>PO Number</th>
                    <th>Projected Amt</th>
                    <th>Team Name</th>
                    <th>Status</th>
                    <th>Team Billing</th>
                    <th>Team Paid</th>
                    <th>Team Balance</th>
                    <th>VIS Inv No</th>
                    <th>VIS Inv Date</th>
                    <th>VIS Bill Amt</th>
                    <th>VIS Rec Amt</th>
                    <th>VIS Balance</th>
                </tr>
        """

        # Fill Table Rows
        for i, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            rid = row.get('id', i)
            html_table += f"""
                <tr>
                    <td>
                        <a href="?edit={rid}">✏️</a> | 
                        <a href="?pay={rid}">💰</a> | 
                        <a href="?del={rid}">🗑️</a>
                    </td>
                    <td><b>{row.get('Project ID','-')}</b></td>
                    <td>{row.get('Project','-')}</td>
                    <td>{row.get('Site ID','-')}</td>
                    <td>{row.get('Site Name','-')}</td>
                    <td>{row.get('Cluster','-')}</td>
                    <td>{row.get('PO Number','-')}</td>
                    <td>₹{row.get('Projected Amount',0):,.2f}</td>
                    <td>{row.get('Team Name','-')}</td>
                    <td>{row.get('Site Status','-')}</td>
                    <td>₹{row.get('Team Billing',0):,.2f}</td>
                    <td>₹{row.get('Team paid Amount',0):,.2f}</td>
                    <td style="color:red; font-weight:bold;">₹{row.get('Team Balance',0):,.2f}</td>
                    <td>{row.get('VIS Invoice No.','-')}</td>
                    <td>{row.get('VIS Invoice Date','-')}</td>
                    <td>₹{row.get('VIS Bill Amount',0):,.2f}</td>
                    <td>₹{row.get('VIS Received Amt',0):,.2f}</td>
                    <td style="color:orange; font-weight:bold;">₹{row.get('VIS Balance',0):,.2f}</td>
                </tr>
            """
        
        html_table += "</table></div>"
        st.markdown(html_table, unsafe_allow_html=True)

        # --- FOOTER ACTIONS ---
        # Since HTML links inside Markdown can't trigger Python functions easily, 
        # we keep a small button set here for the actual logic.
        st.write("---")
        action_col = st.columns([2, 2, 2, 4])
        target_id = action_col[0].selectbox("Select ID to Edit/Delete", df_f['Project ID'].iloc[(curr_pg-1)*pg_size : curr_pg*pg_size])
        
        if action_col[1].button("✏️ Edit Selected"):
            target_row = df_f[df_f['Project ID'] == target_id].iloc[0]
            st.session_state.edit_id = target_row['id']
            st.session_state.show_form = True
            st.rerun()
            
        if action_col[2].button("🗑️ Delete Selected"):
            target_row = df_f[df_f['Project ID'] == target_id].iloc[0]
            delete_row("indus_data", target_row['id'])
            st.rerun()

    else:
        st.info("No data available. Click 'Add New' to start.")
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
