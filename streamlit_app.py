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

# ================= 📁 PROJECT MANAGEMENT (MODAL/POP-UP VERSION) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Management Portal")

    # --- 1. POP-UP FOR EDITING ---
    @st.dialog("📝 Edit Project Details", width="large")
    def edit_project_modal(row_data):
        st.write(f"Editing Project ID: **{row_data['Project ID']}**")
        with st.form("edit_form_popup"):
            c1, c2, c3 = st.columns(3)
            p_name = c1.text_input("Project", value=row_data['Project'])
            s_name = c2.text_input("Site Name", value=row_data['Site Name'])
            t_name = c3.selectbox("Team Name", ["Team A", "Team B", "Team C", "Team D"], 
                                  index=["Team A", "Team B", "Team C", "Team D"].index(row_data['Team Name']) if row_data['Team Name'] in ["Team A", "Team B", "Team C", "Team D"] else 0)
            
            t_bill = c1.number_input("Team Billing", value=float(row_data.get('Team Billing', 0)))
            t_paid = c2.number_input("Team Paid Amount", value=float(row_data.get('Team paid Amount', 0)))
            v_amt = c3.number_input("VIS Bill Amount", value=float(row_data.get('VIS Bill Amount', 0)))
            v_rec = c1.number_input("VIS Received Amt", value=float(row_data.get('VIS Received Amt', 0)))

            if st.form_submit_button("✅ Update & Save"):
                updated_payload = {
                    "Project": p_name, "Site Name": s_name, "Team Name": t_name,
                    "Team Billing": t_bill, "Team paid Amount": t_paid, 
                    "Team Balance": t_bill - t_paid, "VIS Bill Amount": v_amt, 
                    "VIS Received Amt": v_rec, "VIS Balance": v_amt - v_rec,
                    "Profit": v_amt - t_bill
                }
                update_row("indus_data", row_data['id'], updated_payload)
                st.success("Data Updated!")
                st.rerun()

    # --- 2. POP-UP FOR DELETE CONFIRMATION ---
    @st.dialog("⚠️ Confirm Delete")
    def delete_confirmation_modal(row_id, project_id):
        st.warning(f"Are you sure you want to delete **{project_id}**? This action cannot be undone.")
        c1, c2 = st.columns(2)
        if c1.button("❌ Yes, Delete", use_container_width=True):
            delete_row("indus_data", row_id)
            st.rerun()
        if c2.button("Cancel", use_container_width=True):
            st.rerun()

    # --- TOP TOOLBAR ---
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
            st.download_button("📥 Download", out.getvalue(), "Vision_Master.xlsx", use_container_width=True)
    with t4:
        search = st.text_input("", placeholder="🔍 Search Site, ID or Team...", label_visibility="collapsed")

    # --- DATA TABLE ---
    if not df_m.empty:
        df_f = df_m[df_m.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df_m
        
        # Table Styling
        st.markdown("""
            <style>
            .scroll-wrapper { width: 100%; overflow-x: auto; border: 1px solid #ddd; border-radius: 10px; }
            table { width: 100%; border-collapse: collapse; min-width: 2500px; }
            th { background-color: #1E60D5; color: white; padding: 12px; text-align: left; }
            td { padding: 12px; border-bottom: 1px solid #eee; font-size: 13px; background: white; }
            </style>
        """, unsafe_allow_html=True)

        # Pagination & Rendering
        pg_size = 5
        tot_pgs = max(1, (len(df_f) // pg_size) + (1 if len(df_f) % pg_size > 0 else 0))
        curr_pg = st.number_input("Page", 1, tot_pgs, 1)

        # Ham Table ke upar buttons nahi de sakte HTML ke andar, 
        # isliye hum table ke har line ke sath Streamlit native buttons use karenge
        st.write("---")
        for i, row in df_f.iloc[(curr_pg-1)*pg_size : curr_pg*pg_size].iterrows():
            cols = st.columns([0.4, 0.4, 0.4, 8])
            
            # Action Buttons (Native Streamlit)
            if cols[0].button("✏️", key=f"edit_{row['id']}"):
                edit_project_modal(row)
                
            if cols[1].button("💰", key=f"pay_{row['id']}"):
                st.info("Finance module coming soon!")
                
            if cols[2].button("🗑️", key=f"del_{row['id']}"):
                delete_confirmation_modal(row['id'], row['Project ID'])
            
            # Row Data Display (One Line)
            cols[3].markdown(f"**{row['Project ID']}** | {row['Site Name']} | Team: {row['Team Name']} | Bal: ₹{row['Team Balance']}")
            st.divider()

    else:
        st.info("No data found.")
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
