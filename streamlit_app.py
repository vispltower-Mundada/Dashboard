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

        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.markdown(f'<div class="card teal-card"><div class="card-title">Total VIS Billing</div><div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r3c2.markdown(f'<div class="card light-blue-card"><div class="card-title">Total VIS Received</div><div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        r3c3.markdown(f'<div class="card dark-orange-card"><div class="card-title">Total VIS Balance</div><div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="card cash-hand-card"><div class="card-title">💵 Cash in Hand</div><div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)
    else:
        st.info("No data found in the database.")


# ================= 2. 📁 PROJECT MANAGEMENT (LAVISH TABLE + ORIGINAL FORM) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")

    # --- 1. HANDLE ACTION CLICKS (URL QUERY PARAMS) ---
    if "edit_id" in st.query_params:
        st.session_state.edit_id = int(st.query_params["edit_id"])
        st.session_state.show_form = True
        st.query_params.clear()
        st.query_params["menu"] = "Project"
        st.rerun()

    if "del_id" in st.query_params:
        delete_row("indus_data", int(st.query_params["del_id"]))
        st.query_params.clear()
        st.query_params["menu"] = "Project"
        st.rerun()

    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # --- 2. TOP TOOLBAR ---
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    with t1:
        if st.button("➕ Add New Site", use_container_width=True, type="primary"):
            st.session_state.show_form = not st.session_state.show_form
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
            st.download_button("📥 Download", out.getvalue(), "Vision_Master.xlsx", use_container_width=True)
    with t4:
        search = st.text_input("", placeholder="🔍 Search Site, ID or Team...", label_visibility="collapsed")

    # --- 3. ORIGINAL EDIT/ADD FORM (NO POP-UPS) ---
    if st.session_state.show_form:
        st.divider()
        with st.form("master_entry_form"):
            st.subheader("📝 Project Details Form")
            ed = None
            if st.session_state.edit_id and not df_m.empty:
                ed_row = df_m[df_m['id'] == st.session_state.edit_id]
                if not ed_row.empty: ed = ed_row.iloc[0]
            
            c1, c2, c3, c4 = st.columns(4)
            p_type = c1.selectbox("Project", ["Airtel", "Jio", "VIL", "O&M"], index=0)
            p_id = c2.text_input("Project ID", value=str(ed.get('Project ID', '')) if ed is not None else "")
            s_id = c3.text_input("Site ID", value=str(ed.get('Site ID', '')) if ed is not None else "")
            s_name = c4.text_input("Site Name", value=str(ed.get('Site Name', '')) if ed is not None else "")
            
            clstr = c1.text_input("Cluster", value=str(ed.get('Cluster', '')) if ed is not None else "")
            po = c2.text_input("PO Number", value=str(ed.get('PO Number', '')) if ed is not None else "")
            p_amt = c3.number_input("Projected Amount", value=float(ed.get('Projected Amount', 0)) if ed is not None else 0.0)
            t_name = c4.selectbox("Team Name", ["Team A", "Team B", "Team C", "Team D"])
            
            sts = c1.selectbox("Status", ["Pending", "Ongoing", "Completed"])
            t_bill = c2.number_input("Team Billing", value=float(ed.get('Team Billing', 0)) if ed is not None else 0.0)
            t_paid = c3.number_input("Team Paid Amount", value=float(ed.get('Team paid Amount', 0)) if ed is not None else 0.0)
            v_no = c4.text_input("VIS Inv No", value=str(ed.get('VIS Invoice No.', '')) if ed is not None else "")
            
            v_amt = c1.number_input("VIS Bill Amt", value=float(ed.get('VIS Bill Amount', 0)) if ed is not None else 0.0)
            v_rec = c2.number_input("VIS Rec Amt", value=float(ed.get('VIS Received Amt', 0)) if ed is not None else 0.0)

            if st.form_submit_button("💾 Save Data"):
                payload = {
                    "Project": p_type, "Project ID": p_id, "Site ID": s_id, "Site Name": s_name,
                    "Cluster": clstr, "PO Number": po, "Projected Amount": p_amt, "Team Name": t_name,
                    "Site Status": sts, "Team Billing": t_bill, "Team paid Amount": t_paid,
                    "Team Balance": t_bill - t_paid, "VIS Invoice No.": v_no,
                    "VIS Bill Amount": v_amt, "VIS Received Amt": v_rec, "VIS Balance": v_amt - v_rec,
                    "Profit": v_amt - t_bill
                }
                if st.session_state.edit_id:
                    update_row("indus_data", st.session_state.edit_id, payload)
                else:
                    insert_row("indus_data", payload)
                st.session_state.show_form = False
                st.rerun()

    # --- 4. LAVISH TABLE WITH SCROLLER (NO CODE LEAKS) ---
    if not df_m.empty:
        df_f = df_m[df_m.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df_m
        
        pg_size = 10
        tot_pgs = max(1, (len(df_f) // pg_size) + (1 if len(df_f) % pg_size > 0 else 0))
        curr_pg = st.number_input("Page", 1, tot_pgs, 1)

        def clean_val(val):
            try: return f"₹{float(val):,.2f}" if not pd.isna(val) else "₹0.00"
            except: return "₹0.00"

        html_code = """
        <style>
        .scroll-container { width: 100%; overflow-x: auto; border-radius: 10px; border: 1px solid #ddd; background: white; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .data-table { width: 100%; border-collapse: collapse; min-width: 2800px; font-family: sans-serif; }
        .data-table th { background: #1E60D5; color: white; padding: 12px; text-align: left; position: sticky; top: 0; z-index: 2; font-size: 14px; }
        .data-table td { padding: 12px; border-bottom: 1px solid #eee; font-size: 13px; color: #333; }
        .data-table tr:hover { background: #f8f9fa; }
        .sticky-action { position: sticky; left: 0; background: #f4f6f9 !important; z-index: 1; border-right: 2px solid #ddd !important; text-align: center; }
        .sticky-action-header { position: sticky; left: 0; z-index: 3 !important; background: #1E60D5 !important; border-right: 2px solid #144ba6 !important; text-align: center; }
        .btn-icon { text-decoration: none; font-size: 16px; margin: 0 6px; }
        .status-badge { background: #e3f2fd; color: #1e88e5; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; }
        </style>
        <div class="scroll-container">
            <table class="data-table">
                <tr>
                    <th class="sticky-action-header">Actions</th>
                    <th>Project ID</th><th>Project</th><th>Site ID</th><th>Site Name</th>
                    <th>Cluster</th><th>PO Number</th><th>Projected Amt</th><th>Status</th>
                    <th>Team Billing</th><th>Team Paid</th><th>Team Balance</th>
                    <th>VIS Inv No</th><th>VIS Bill Amt</th><th>VIS Rec Amt</th><th>VIS Balance</th>
                </tr>
        """

        for i, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            db_id = row.get('id') if row.get('id') else row.get('ID', i)
            p_id = row.get('Project ID', 'N/A')
            
            html_code += f"""
                <tr>
                    <td class="sticky-action">
                        <a href="?menu=Project&edit_id={db_id}" target="_parent" class="btn-icon">✏️</a>
                        <a href="?menu=Project&pay_id={p_id}" target="_parent" class="btn-icon">💰</a>
                        <a href="?menu=Project&del_id={db_id}" target="_parent" class="btn-icon">🗑️</a>
                    </td>
                    <td style="font-weight:bold; color:#1E60D5;">{p_id}</td>
                    <td>{row.get('Project','-')}</td>
                    <td>{row.get('Site ID','-')}</td>
                    <td>{row.get('Site Name','-')}</td>
                    <td>{row.get('Cluster','-')}</td>
                    <td>{row.get('PO Number','-')}</td>
                    <td>{clean_val(row.get('Projected Amount'))}</td>
                    <td><span class="status-badge">{row.get('Site Status','-')}</span></td>
                    <td>{clean_val(row.get('Team Billing'))}</td>
                    <td>{clean_val(row.get('Team paid Amount'))}</td>
                    <td style="color:#d32f2f; font-weight:bold;">{clean_val(row.get('Team Balance'))}</td>
                    <td>{row.get('VIS Invoice No.','-')}</td>
                    <td>{clean_val(row.get('VIS Bill Amt'))}</td>
                    <td>{clean_val(row.get('VIS Received Amt'))}</td>
                    <td style="color:#f57c00; font-weight:bold;">{clean_val(row.get('VIS Balance'))}</td>
                </tr>
            """
        
        html_code += "</table></div>"
        
        # Safe HTML rendering
        st.markdown(html_code.replace('\n', ''), unsafe_allow_html=True)

    else:
        st.info("No projects found.")


# ================= 3. 💰 FINANCE =================
elif menu == "💰 Finance":
    st.title("💰 Finance Module")
    st.info("Finance features will be added here soon!")
