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

# ================= 📁 PROJECT MANAGEMENT (LAVISH & ERROR-FREE) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")

    # Session states
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # --- TOP TOOLBAR ---
    st.markdown("""
        <style>
        .stButton>button { border-radius: 10px; font-weight: bold; }
        .table-container { overflow-x: auto; white-space: nowrap; padding: 10px; background: #f8f9fa; border-radius: 15px; }
        </style>
    """, unsafe_allow_html=True)

    t1, t2, t3, t4 = st.columns([1, 1, 1, 3])
    
    with t1:
        if st.button("➕ Add New", use_container_width=True):
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
            st.download_button("📥 Download", out.getvalue(), "Indus_Report.xlsx", use_container_width=True)

    with t4:
        search = st.text_input("", placeholder="🔍 Search Site, ID, Team...", label_visibility="collapsed")

    # --- FORM (ADD / EDIT) ---
    if st.session_state.show_form:
        st.write("---")
        with st.form("entry_form"):
            ed = None
            if st.session_state.edit_id and not df_master.empty:
                ed_list = df_master[df_master['id'] == st.session_state.edit_id]
                if not ed_list.empty:
                    ed = ed_list.iloc[0]
            
            st.subheader("📝 Project Details")
            c1, c2, c3 = st.columns(3)
            p_name = c1.text_input("Project", value=ed['Project'] if ed is not None else "")
            p_id = c1.text_input("Project ID", value=ed['Project ID'] if ed is not None else "")
            s_name = c2.text_input("Site Name", value=ed['Site Name'] if ed is not None else "")
            t_name = c2.selectbox("Team", ["Team A", "Team B", "Team C"], index=0)
            t_bill = c3.number_input("Team Billing", value=float(ed['Team Billing']) if ed is not None else 0.0)
            v_inv = c3.number_input("VIS Inv Amt", value=float(ed['VIS Inv Amt']) if ed is not None else 0.0)

            f_c1, f_c2 = st.columns([1, 4])
            if f_c1.form_submit_button("💾 Save"):
                payload = {
                    "Project": p_name, "Project ID": p_id, "Site Name": s_name, 
                    "Team Name": t_name, "Team Billing": t_bill, "VIS Inv Amt": v_inv,
                    "Team Balance": t_bill, "Profit": v_inv - t_bill, "VIS Balance": v_inv
                }
                if st.session_state.edit_id:
                    update_row("indus_data", st.session_state.edit_id, payload)
                else:
                    insert_row("indus_data", payload)
                st.session_state.show_form = False
                st.rerun()
            if f_c2.form_submit_button("❌ Cancel"):
                st.session_state.show_form = False
                st.rerun()

    # --- THE TABLE WITH PAGINATION FIX ---
    if not df_master.empty:
        # Search Filter
        if search:
            df_display = df_master[df_master.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        else:
            df_display = df_master

        # PAGINATION FIX: RangeError prevention
        p_size = 5
        total_rows = len(df_display)
        
        if total_rows > 0:
            total_p = (total_rows // p_size) + (1 if total_rows % p_size > 0 else 0)
            
            # Slider sirf tab dikhega jab 1 se zyada page honge
            if total_p > 1:
                curr_p = st.slider("Select Page", 1, total_p, 1)
            else:
                curr_p = 1
            
            start = (curr_p - 1) * p_size
            end = start + p_size

            st.write("### 📋 Detailed Records")
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            
            for i, row in df_display.iloc[start:end].iterrows():
                rid = row.get('id', i)
                with st.container():
                    b1, b2, b3, d1, d2, d3, d4 = st.columns([0.4, 0.4, 0.4, 1.5, 2, 1.5, 1.5])
                    
                    if b1.button("✏️", key=f"e_{rid}"):
                        st.session_state.edit_id = rid
                        st.session_state.show_form = True
                        st.rerun()
                    
                    if b2.button("💰", key=f"p_{rid}"):
                        st.toast(f"Go to Finance for {row['Project ID']}")
                    
                    if b3.button("🗑️", key=f"d_{rid}"):
                        delete_row("indus_data", rid)
                        st.rerun()

                    d1.markdown(f"**ID:**<br>`{row['Project ID']}`", unsafe_allow_html=True)
                    d2.markdown(f"**Project:**<br>{row['Project']} - {row['Site Name']}", unsafe_allow_html=True)
                    d3.markdown(f"**Team:**<br>{row['Team Name']}", unsafe_allow_html=True)
                    d4.markdown(f"**Profit:**<br>₹{row.get('Profit', 0)}", unsafe_allow_html=True)
                    st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No matching records found for your search.")
    else:
        st.info("Database is empty. Click 'Add New' to start.")
# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
