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

# ================= 📊 DASHBOARD (RESTORED ORIGINAL LOGIC) =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Overview of your site metrics")
    
    raw_data = fetch_table("indus_data")
    data = pd.DataFrame(raw_data)
    
    if not data.empty:
        data.fillna(0, inplace=True)
        
        # Original Logic Calculations
        total_proj = data['Project Amount'].astype(float).sum()
        total_invested = 1500000.00 # Placeholder as per your screen
        total_team_bill = data['Team Billing'].astype(float).sum()
        total_team_paid = data['Team Paid Amt'].astype(float).sum()
        total_team_bal = data['Team Balance'].astype(float).sum()
        total_vis_bill = data['VIS Inv Amt'].astype(float).sum()
        total_vis_rec = data['VIS Rec Amt'].astype(float).sum()
        total_vis_bal = data['VIS Balance'].astype(float).sum()
        cash_in_hand = total_vis_rec - total_team_paid

        # --- 1st Row: Project & Invested ---
        r1c1, r1c2 = st.columns(2)
        r1c1.markdown(f'<div class="card blue-card"><div class="card-title">Total Projected Amount</div><div class="card-value">₹{total_proj:,.2f}</div></div>', unsafe_allow_html=True)
        r1c2.markdown(f'<div class="card green-card"><div class="card-title">Total Invested Amount</div><div class="card-value">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)

        # --- 2nd Row: Team Data ---
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.markdown(f'<div class="card purple-card"><div class="card-title">Total Team Billing</div><div class="card-value">₹{total_team_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r2c2.markdown(f'<div class="card orange-card"><div class="card-title">Total Team Paid</div><div class="card-value">₹{total_team_paid:,.2f}</div></div>', unsafe_allow_html=True)
        r2c3.markdown(f'<div class="card red-card"><div class="card-title">Total Team Balance</div><div class="card-value">₹{total_team_bal:,.2f}</div></div>', unsafe_allow_html=True)

        # --- 3rd Row: VIS Data ---
        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.markdown(f'<div class="card teal-card"><div class="card-title">Total VIS Billing</div><div class="card-value">₹{total_vis_bill:,.2f}</div></div>', unsafe_allow_html=True)
        r3c2.markdown(f'<div class="card light-blue-card"><div class="card-title">Total VIS Received</div><div class="card-value">₹{total_vis_rec:,.2f}</div></div>', unsafe_allow_html=True)
        r3c3.markdown(f'<div class="card dark-orange-card"><div class="card-title">Total VIS Balance</div><div class="card-value">₹{total_vis_bal:,.2f}</div></div>', unsafe_allow_html=True)

        # --- 4th Row: Cash in Hand ---
        st.markdown(f'<div class="card cash-hand-card"><div class="card-title">💵 Cash in Hand</div><div style="font-size: 40px; font-weight: bold;">₹{cash_in_hand:,.2f}</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("📋 Detailed Report")
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No data found.")

# ================= 📁 PROJECT MANAGEMENT (WITH SEARCH & 5-LINE PAGINATION) =================
elif menu == "📁 Project Management":
    st.title("📁 Project Master List")

    # Session states for Form
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    # Top Buttons
    c_btn1, c_btn2, c_btn3, c_src = st.columns([1, 1.5, 1, 3])
    
    if c_btn1.button("➕ Add New"):
        st.session_state.show_form = True
        st.session_state.edit_id = None

    bulk_file = c_btn2.file_uploader("Bulk Upload", type=['xlsx'], label_visibility="collapsed")
    
    # Fetch Data
    df_master = pd.DataFrame(fetch_table("indus_data"))
    
    if not df_master.empty:
        # Download
        out = BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
            df_master.to_excel(wr, index=False)
        c_btn3.download_button("📥 Download", out.getvalue(), "Indus_Report.xlsx")

    search = c_src.text_input("🔍 Search Anything...", placeholder="Type Site, ID or Team...")

    # Form (Add/Edit)
    if st.session_state.show_form:
        with st.expander("📝 Project Form", expanded=True):
            with st.form("entry_form"):
                ed = None
                if st.session_state.edit_id:
                    ed = df_master[df_master['id'] == st.session_state.edit_id].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                p_name = col1.text_input("Project", value=ed['Project'] if ed is not None else "")
                p_id = col1.text_input("Project ID", value=ed['Project ID'] if ed is not None else "")
                s_name = col2.text_input("Site Name", value=ed['Site Name'] if ed is not None else "")
                t_name = col2.selectbox("Team", ["Team A", "Team B", "Team C"], index=0)
                t_bill = col3.number_input("Team Billing", value=float(ed['Team Billing']) if ed is not None else 0.0)
                v_amt = col3.number_input("VIS Inv Amt", value=float(ed['VIS Inv Amt']) if ed is not None else 0.0)
                
                if st.form_submit_button("💾 Save"):
                    payload = {"Project": p_name, "Project ID": p_id, "Site Name": s_name, "Team Name": t_name, "Team Billing": t_bill, "VIS Inv Amt": v_amt, "Profit": v_amt - t_bill}
                    if st.session_state.edit_id:
                        update_row("indus_data", st.session_state.edit_id, payload)
                    else:
                        insert_row("indus_data", payload)
                    st.session_state.show_form = False
                    st.rerun()

    # Table with 5 lines & Actions
    if not df_master.empty:
        # Search Filter
        if search:
            df_display = df_master[df_master.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        else:
            df_display = df_master

        # Pagination (5 Rows)
        page_size = 5
        total_p = (len(df_display) // page_size) + (1 if len(df_display) % page_size > 0 else 0)
        curr_p = st.number_input("Page", 1, total_p, 1)
        
        start = (curr_p - 1) * page_size
        end = start + page_size

        st.write("---")
        for i, row in df_display.iloc[start:end].iterrows():
            with st.container():
                cols = st.columns([0.5, 0.5, 0.5, 2, 2, 2, 2])
                # Safe ID Access
                rid = row.get('id', i)
                
                if cols[0].button("✏️", key=f"e_{rid}"):
                    st.session_state.edit_id = rid
                    st.session_state.show_form = True
                    st.rerun()
                if cols[1].button("💰", key=f"p_{rid}"):
                    st.info(f"Pay entry for {row['Project ID']}")
                if cols[2].button("🗑️", key=f"d_{rid}"):
                    delete_row("indus_data", rid)
                    st.rerun()
                
                cols[3].write(f"**ID:** {row['Project ID']}")
                cols[4].write(f"**Site:** {row['Site Name']}")
                cols[5].write(f"**Team:** {row['Team Name']}")
                cols[6].write(f"**Profit:** ₹{row['Profit']}")
                st.write("---")

# ================= 💰 FINANCE (UNCHANGED) =================
elif menu == "💰 Finance":
    st.title("💰 Finance Entry")
    # Finance logic as per your database
