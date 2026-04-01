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

# ================= 📁 PROJECT MANAGEMENT (STRICT ERROR-FREE VERSION) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Management Portal")

    # --- 1. POP-UP DIALOGS ---
    @st.dialog("📝 Edit Site Details", width="large")
    def edit_modal(row_data):
        st.write(f"Editing Project ID: **{row_data.get('Project ID', 'N/A')}**")
        with st.form("edit_site_form"):
            c1, c2, c3 = st.columns(3)
            # Safe get use kar rahe hain taaki crash na ho
            p_name = c1.text_input("Project", value=str(row_data.get('Project', '')))
            s_name = c2.text_input("Site Name", value=str(row_data.get('Site Name', '')))
            t_name = c3.selectbox("Team", ["Team A", "Team B", "Team C", "Team D"], index=0)
            
            # Numeric values ko safely float mein convert kar rahe hain
            def to_f(v): 
                try: return float(v) if v and not pd.isna(v) else 0.0
                except: return 0.0

            t_bill = c1.number_input("Team Billing", value=to_f(row_data.get('Team Billing')))
            t_paid = c2.number_input("Team Paid Amount", value=to_f(row_data.get('Team paid Amount')))
            v_amt = c3.number_input("VIS Bill Amount", value=to_f(row_data.get('VIS Bill Amount')))
            
            if st.form_submit_button("✅ Save Changes"):
                # Database Update Logic
                payload = {
                    "Project": p_name, "Site Name": s_name, "Team Name": t_name,
                    "Team Billing": t_bill, "Team paid Amount": t_paid,
                    "Team Balance": t_bill - t_paid, "VIS Bill Amount": v_amt,
                    "Profit": v_amt - t_bill
                }
                # row_id ke liye 'id' ya 'ID' dono check karenge
                actual_id = row_data.get('id') if row_data.get('id') else row_data.get('ID')
                if actual_id:
                    update_row("indus_data", actual_id, payload)
                    st.success("Updated!")
                    st.rerun()
                else:
                    st.error("Error: Record ID not found in database.")

    @st.dialog("🗑️ Confirm Delete")
    def delete_modal(row_id, p_id):
        st.warning(f"Are you sure you want to delete **{p_id}**?")
        if st.button("❌ Yes, Delete Permanently", use_container_width=True):
            delete_row("indus_data", row_id)
            st.rerun()

    # --- 2. TOOLBAR ---
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    with t1:
        if st.button("➕ Add New Site", use_container_width=True, type="primary"):
            st.session_state.show_form = not st.session_state.get('show_form', False)

    # Fetch Data
    raw_res = fetch_table("indus_data")
    df_m = pd.DataFrame(raw_res)

    if not df_m.empty:
        # SEARCH FILTER
        search = t4.text_input("", placeholder="🔍 Search...", label_visibility="collapsed")
        df_f = df_m[df_m.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df_m
        
        # PAGINATION
        pg_size = 5
        tot_pgs = max(1, (len(df_f) // pg_size) + (1 if len(df_f) % pg_size > 0 else 0))
        curr_pg = st.number_input("Page", 1, tot_pgs, 1)

        # TABLE CSS
        st.markdown("""
            <style>
            .scroll-view { width: 100%; overflow-x: auto; border: 1px solid #eee; border-radius: 10px; margin-bottom: 20px; }
            .vision-table { width: 100%; border-collapse: collapse; min-width: 2500px; }
            .vision-table th { background-color: #1E60D5; color: white; padding: 12px; text-align: left; }
            .vision-table td { padding: 12px; border-bottom: 1px solid #f0f0f0; font-size: 13px; background: white; }
            </style>
        """, unsafe_allow_html=True)

        st.write("---")

        # --- DATA ROWS LOOP ---
        for i, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            # KEY FIX: Agar 'id' nahi mila toh index 'i' use karein buttons ke liye
            # Lekin delete/edit ke liye asli ID chahiye, isliye .get use karenge
            db_id = row.get('id') if row.get('id') else row.get('ID', i)
            p_id_display = row.get('Project ID', 'N/A')

            # Buttons Row (Strictly Start of the Line)
            b1, b2, b3, info = st.columns([0.4, 0.4, 0.4, 8])
            
            if b1.button("✏️", key=f"edit_btn_{db_id}_{i}"):
                edit_modal(row)
            
            if b2.button("💰", key=f"pay_btn_{db_id}_{i}"):
                st.toast(f"Finance Link for {p_id_display}")
            
            if b3.button("🗑️", key=f"del_btn_{db_id}_{i}"):
                delete_modal(db_id, p_id_display)
            
            info.markdown(f"**Project ID:** `{p_id_display}` | **Site:** {row.get('Site Name','-')}")

            # Horizontal Scrollable Data
            def fmt(v): 
                try: return f"₹{float(v):,.2f}" if not pd.isna(v) else "₹0.00"
                except: return "₹0.00"

            table_html = f"""
            <div class="scroll-view">
                <table class="vision-table">
                    <tr>
                        <th>Project</th><th>Site ID</th><th>Cluster</th><th>PO Number</th>
                        <th>Projected Amt</th><th>Status</th><th>Team Billing</th>
                        <th>Team Paid</th><th>Team Balance</th><th>VIS Inv No</th>
                        <th>VIS Bill Amt</th><th>VIS Rec Amt</th><th>VIS Balance</th>
                    </tr>
                    <tr>
                        <td>{row.get('Project','-')}</td><td>{row.get('Site ID','-')}</td>
                        <td>{row.get('Cluster','-')}</td><td>{row.get('PO Number','-')}</td>
                        <td>{fmt(row.get('Projected Amount'))}</td><td>{row.get('Site Status','-')}</td>
                        <td>{fmt(row.get('Team Billing'))}</td><td>{fmt(row.get('Team paid Amount'))}</td>
                        <td style="color:red; font-weight:bold;">{fmt(row.get('Team Balance'))}</td>
                        <td>{row.get('VIS Invoice No.','-')}</td><td>{fmt(row.get('VIS Bill Amount'))}</td>
                        <td>{fmt(row.get('VIS Received Amt'))}</td>
                        <td style="color:orange; font-weight:bold;">{fmt(row.get('VIS Balance'))}</td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            
    else:
        st.info("No data found. Click 'Add New' to start.")
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
