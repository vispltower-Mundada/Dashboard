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

# ================= 📁 PROJECT MANAGEMENT (FULL PROFESSIONAL PORTAL) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Management Portal")

    # --- 1. POP-UP MODALS (ST.DIALOG) ---
    
    @st.dialog("📝 Edit Site Details", width="large")
    def edit_modal(row_data):
        st.write(f"Editing: **{row_data.get('Project ID', 'N/A')}**")
        with st.form("edit_form_popup", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            # Pre-filled values from row_data
            p_name = c1.text_input("Project Name", value=row_data.get('Project', ''))
            s_name = c2.text_input("Site Name", value=row_data.get('Site Name', ''))
            t_name = c3.selectbox("Team Name", ["Team A", "Team B", "Team C", "Team D"], 
                                  index=0) # Indexing logic can be added here
            
            p_amt = c1.number_input("Projected Amount", value=float(row_data.get('Projected Amount', 0)))
            t_bill = c2.number_input("Team Billing", value=float(row_data.get('Team Billing', 0)))
            t_paid = c3.number_input("Team Paid Amount", value=float(row_data.get('Team paid Amount', 0)))
            
            v_inv = c1.text_input("VIS Invoice No.", value=row_data.get('VIS Invoice No.', ''))
            v_amt = c2.number_input("VIS Bill Amount", value=float(row_data.get('VIS Bill Amount', 0)))
            v_rec = c3.number_input("VIS Received Amt", value=float(row_data.get('VIS Received Amt', 0)))

            if st.form_submit_button("✅ Update & Save Changes"):
                updated_payload = {
                    "Project": p_name, "Site Name": s_name, "Team Name": t_name,
                    "Projected Amount": p_amt, "Team Billing": t_bill, "Team paid Amount": t_paid,
                    "Team Balance": t_bill - t_paid, "VIS Invoice No.": v_inv,
                    "VIS Bill Amount": v_amt, "VIS Received Amt": v_rec,
                    "VIS Balance": v_amt - v_rec, "Profit": v_amt - t_bill
                }
                update_row("indus_data", row_data['id'], updated_payload)
                st.success("Entry Updated Successfully!")
                st.rerun()

    @st.dialog("🗑️ Confirm Deletion")
    def delete_modal(row_id, p_id):
        st.error(f"Are you sure you want to delete Project ID: **{p_id}**?")
        st.write("This action is permanent and cannot be undone.")
        col1, col2 = st.columns(2)
        if col1.button("Yes, Delete", use_container_width=True):
            delete_row("indus_data", row_id)
            st.rerun()
        if col2.button("Cancel", use_container_width=True):
            st.rerun()

    # --- 2. TOP TOOLBAR ---
    t1, t2, t3, t4 = st.columns([1, 1.2, 1, 3])
    with t1:
        if st.button("➕ Add New Site", use_container_width=True, type="primary"):
            st.session_state.show_form = not st.session_state.get('show_form', False)

    df_m = pd.DataFrame(fetch_table("indus_data"))
    
    with t3:
        if not df_m.empty:
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df_m.to_excel(wr, index=False)
            st.download_button("📥 Download Excel", out.getvalue(), "Vision_Master.xlsx", use_container_width=True)
    
    with t4:
        search = st.text_input("", placeholder="🔍 Search ID, Site, Team or Status...", label_visibility="collapsed")

    # --- 3. THE DATA TABLE WITH SCROLLER ---
    if not df_m.empty:
        # Search Filter
        df_f = df_m[df_m.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df_m
        
        # Pagination
        pg_size = 5
        tot_pgs = max(1, (len(df_f) // pg_size) + (1 if len(df_f) % pg_size > 0 else 0))
        curr_pg = st.number_input("Page", 1, tot_pgs, 1)

        # Helper function for Currency/Nan Fix
        def clean_val(val):
            try:
                v = float(val)
                return 0.0 if pd.isna(v) else v
            except:
                return 0.0

        # Build HTML Table Rows
        table_rows = ""
        for _, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            table_rows += f"""
            <tr>
                <td><b>{row.get('Project ID','-')}</b></td>
                <td>{row.get('Project','-')}</td>
                <td>{row.get('Site ID','-')}</td>
                <td>{row.get('Site Name','-')}</td>
                <td>{row.get('Cluster','-')}</td>
                <td>{row.get('PO Number','-')}</td>
                <td>₹{clean_val(row.get('Projected Amount')):,.2f}</td>
                <td>{row.get('Team Name','-')}</td>
                <td>{row.get('Site Status','-')}</td>
                <td>₹{clean_val(row.get('Team Billing')):,.2f}</td>
                <td>₹{clean_val(row.get('Team paid Amount')):,.2f}</td>
                <td style="color:red; font-weight:bold;">₹{clean_val(row.get('Team Balance')):,.2f}</td>
                <td>{row.get('VIS Invoice No.','-')}</td>
                <td>{row.get('VIS Invoice Date','-')}</td>
                <td>₹{clean_val(row.get('VIS Bill Amount')):,.2f}</td>
                <td>₹{clean_val(row.get('VIS Received Amt')):,.2f}</td>
                <td style="color:orange; font-weight:bold;">₹{clean_val(row.get('VIS Balance')):,.2f}</td>
            </tr>
            """

        full_html = f"""
        <html>
        <head>
        <style>
            .container {{ width: 100%; overflow-x: auto; font-family: sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; min-width: 2800px; border: 1px solid #ddd; }}
            th {{ background-color: #1E60D5; color: white; padding: 12px; text-align: left; position: sticky; top: 0; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; font-size: 13px; background: white; }}
            tr:hover {{ background-color: #f1f5f9; }}
        </style>
        </head>
        <body>
            <div class="container">
                <table>
                    <tr>
                        <th>Project ID</th><th>Project</th><th>Site ID</th><th>Site Name</th>
                        <th>Cluster</th><th>PO Number</th><th>Projected Amt</th><th>Team Name</th>
                        <th>Status</th><th>Team Billing</th><th>Team Paid</th><th>Team Bal</th>
                        <th>VIS Inv No</th><th>VIS Inv Date</th><th>VIS Bill Amt</th><th>VIS Rec Amt</th><th>VIS Balance</th>
                    </tr>
                    {table_rows}
                </table>
            </div>
        </body>
        </html>
        """
        import streamlit.components.v1 as components
        components.html(full_html, height=350, scrolling=True)

        # --- 4. ACTION BUTTONS (BELOW TABLE) ---
        st.write("### ⚙️ Line Actions")
        # Creating columns for each action button per visible row
        for i, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            rid = row.get('id', i)
            p_id = row.get('Project ID', 'N/A')
            
            c_act = st.columns([0.5, 0.5, 0.5, 8])
            if c_act[0].button("✏️", key=f"edit_{rid}"):
                edit_modal(row)
            
            if c_act[1].button("💰", key=f"pay_{rid}"):
                st.toast(f"Finance Link for {p_id} coming soon!")
                
            if c_act[2].button("🗑️", key=f"del_{rid}"):
                delete_modal(row['id'], p_id)
            
            c_act[3].write(f"Actions for ID: **{p_id}** | Site: {row.get('Site Name','-')}")
            st.divider()
    else:
        st.info("No data available.")
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
