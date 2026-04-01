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


# ================= 2. 📁 PROJECT MANAGEMENT =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")

    df_m = pd.DataFrame(fetch_table("indus_data"))

    # --- 1. POP-UP DIALOG FOR ADD/EDIT (3 STEPS FORMAT) ---
    @st.dialog("📝 Project Details Form", width="large")
    def project_form_modal(ed=None):
        existing_pids = df_m['Project ID'].dropna().astype(str).tolist() if not df_m.empty else []
        if ed is not None and str(ed.get('Project ID')) in existing_pids:
            existing_pids.remove(str(ed.get('Project ID')))

        with st.form("master_entry_form"):
            # ---------------- STEP 1: SITE DETAILS ----------------
            st.markdown("### 📍 1. Site Details")
            c1, c2, c3 = st.columns(3)
            p_opts = ["Airtel", "Jio", "VIL", "O&M"]
            p_val = str(ed.get('Project', 'Airtel')) if ed else "Airtel"
            p_type = c1.selectbox("Project", p_opts, index=p_opts.index(p_val) if p_val in p_opts else 0)
            p_id = c2.text_input("Project ID (Must be Unique) *", value=str(ed.get('Project ID', '')) if ed else "")
            s_id = c3.text_input("Site ID", value=str(ed.get('Site ID', '')) if ed else "")
            
            c4, c5, c6 = st.columns(3)
            s_name = c4.text_input("Site Name", value=str(ed.get('Site Name', '')) if ed else "")
            clstr = c5.text_input("Cluster", value=str(ed.get('Cluster', '')) if ed else "")
            po = c6.text_input("PO Number", value=str(ed.get('PO Number', '')) if ed else "")
            
            p_amt = st.number_input("Projected Amount", value=float(ed.get('Projected Amount', 0)) if ed else 0.0)

            # ---------------- STEP 2: TEAM DETAILS ----------------
            st.markdown("### 👥 2. Team Details")
            c7, c8 = st.columns(2)
            t_opts = ["Team A", "Team B", "Team C", "Team D"]
            t_val = str(ed.get('Team Name', 'Team A')) if ed else "Team A"
            t_name = c7.selectbox("Team Name", t_opts, index=t_opts.index(t_val) if t_val in t_opts else 0)
            
            sts_opts = ["Pending", "Ongoing", "Completed", "Done", "Yet to Start"]
            sts_val = str(ed.get('Site Status', 'Pending')) if ed else "Pending"
            sts = c8.selectbox("Site Status", sts_opts, index=sts_opts.index(sts_val) if sts_val in sts_opts else 0)

            c9, c10 = st.columns(2)
            t_bill = c9.number_input("Team Billing", value=float(ed.get('Team Billing', 0)) if ed else 0.0)
            t_paid = c10.number_input("Team Paid Amount", value=float(ed.get('Team paid Amount', 0)) if ed else 0.0)
            st.info(f"**Team Balance (Auto-calculated):** ₹ {t_bill - t_paid:,.2f}")

            # ---------------- STEP 3: VIS BILLING DETAILS ----------------
            st.markdown("### 📄 3. VIS Billing Details")
            c11, c12 = st.columns(2)
            v_no = c11.text_input("VIS Invoice No.", value=str(ed.get('VIS Invoice No.', '')) if ed else "")
            v_date = c12.text_input("VIS Invoice Date", value=str(ed.get('VIS Invoice Date', '')) if ed else "")

            c13, c14 = st.columns(2)
            v_amt = c13.number_input("VIS Bill Amount", value=float(ed.get('VIS Bill Amount', 0)) if ed else 0.0)
            v_rec = c14.number_input("VIS Received Amt", value=float(ed.get('VIS Received Amt', 0)) if ed else 0.0)
            st.info(f"**VIS Balance (Auto-calculated):** ₹ {v_amt - v_rec:,.2f}")

            st.divider()
            if st.form_submit_button("💾 Save Project Data", use_container_width=True):
                if not p_id.strip():
                    st.error("❌ Project ID is required!")
                elif p_id.strip() in existing_pids:
                    st.error(f"❌ Project ID '{p_id}' already exists! Please enter a unique ID.")
                else:
                    payload = {
                        "Project": p_type, "Project ID": p_id.strip(), "Site ID": s_id, "Site Name": s_name,
                        "Cluster": clstr, "PO Number": po, "Projected Amount": p_amt, "Team Name": t_name,
                        "Site Status": sts, "Team Billing": t_bill, "Team paid Amount": t_paid,
                        "Team Balance": t_bill - t_paid, "VIS Invoice No.": v_no, "VIS Invoice Date": v_date,
                        "VIS Bill Amount": v_amt, "VIS Received Amt": v_rec, "VIS Balance": v_amt - v_rec,
                        "Profit": v_amt - t_bill
                    }
                    if ed is not None:
                        update_row("indus_data", ed['id'], payload)
                    else:
                        insert_row("indus_data", payload)
                    st.rerun()

    # --- 2. HANDLE URL PARAMS (TRIGGER POP-UPS) ---
    if "edit_id" in st.query_params:
        rid = int(st.query_params["edit_id"])
        
        # URL clean karein taaki refresh par wapas na khule, par page Project hi rahe
        st.query_params.clear()
        st.query_params["menu"] = "Project"
        
        # Jis line par click kiya hai, uska data dhundh kar form mein pass karein
        ed_row = df_m[df_m['id'] == rid]
        if not ed_row.empty:
            project_form_modal(ed_row.iloc[0]) # Yeh line same 'Add New' jaisa form pre-filled kholegi

    if "del_id" in st.query_params:
        rid = int(st.query_params["del_id"])
        st.query_params.clear()
        st.query_params["menu"] = "Project"
        delete_row("indus_data", rid)
        st.rerun()

    if "pay_id" in st.query_params:
        st.toast(f"Finance module for Project {st.query_params['pay_id']} coming soon!")
        st.query_params.clear()
        st.query_params["menu"] = "Project"

    # --- 3. TOP TOOLBAR ---
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    with t1:
        if st.button("➕ Add New Site", use_container_width=True, type="primary"):
            project_form_modal()
            
    with t2:
        bulk = st.file_uploader("Bulk Upload", type=['xlsx'], label_visibility="collapsed")
    
    with t3:
        if not df_m.empty:
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df_m.to_excel(wr, index=False)
            st.download_button("📥 Download", out.getvalue(), "Vision_Master.xlsx", use_container_width=True)
            
    with t4:
        search = st.text_input("", placeholder="🔍 Search Site, ID or Team...", label_visibility="collapsed")

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
                    <th>VIS Inv No</th><th>VIS Inv Date</th><th>VIS Bill Amt</th><th>VIS Rec Amt</th><th>VIS Balance</th>
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
                    <td>{row.get('VIS Invoice Date','-')}</td>
                    <td>{clean_val(row.get('VIS Bill Amt'))}</td>
                    <td>{clean_val(row.get('VIS Received Amt'))}</td>
                    <td style="color:#f57c00; font-weight:bold;">{clean_val(row.get('VIS Balance'))}</td>
                </tr>
            """
        
        html_code += "</table></div>"
        
        st.markdown(html_code.replace('\n', ''), unsafe_allow_html=True)

    else:
        st.info("No projects found.")


# ================= 3. 💰 FINANCE =================
elif menu == "💰 Finance":
    st.title("💰 Finance Module")
    st.info("Finance features will be added here soon!")
