import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro", layout="wide")

# ปรับปรุง CSS สำหรับการเปรียบเทียบ
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

    .stMetric {
        padding: 15px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        border: 1px solid #ddd !important;
    }
    
    /* สีพื้นหลังแยกตามประเภท */
    div[data-testid="stMetric"]:nth-child(1) { background-color: #f0f2f6; } 
    div[data-testid="stMetric"]:nth-child(2) { background-color: #e8eaed; } 
    div[data-testid="stMetric"]:nth-child(3) { background-color: #fff4e6; } 
    div[data-testid="stMetric"]:nth-child(4) { background-color: #ebfbee; } 
    div[data-testid="stMetric"]:nth-child(5) { background-color: #e7f5ff; }

    .compare-box {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #333;
        margin-top: 10px;
    }
    .status-ok { color: #28a745; font-weight: bold; }
    .status-over { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "เทสตาราง.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except: continue
    return None

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ระบบคำนวณและเปรียบเทียบวัสดุ")

try:
    df = load_data()
    if df is not None:
        # ส่วนข้อมูลโครงการและแผนงาน
        with st.container():
            col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
            project_name = col_p1.text_input("🏢 ชื่อโครงการ:", value="โครงการใหม่")
            calc_date = datetime.now().strftime("%d/%m/%Y")
            col_p2.text_input("📅 วันที่:", value=calc_date, disabled=True)
            
        # --- ใหม่: ช่องกรอกปริมาณตามแผนเพื่อเปรียบเทียบ ---
        with st.expander("📊 ตั้งค่าปริมาณตามแผน (Planned Quantity)", expanded=False):
            st.info("กรอกปริมาณวัสดุที่ประเมินไว้เบื้องต้นเพื่อใช้เปรียบเทียบ")
            col_plan1, col_plan2, col_plan3, col_plan4, col_plan5 = st.columns(5)
            plan_h1 = col_plan1.number_input("แผน: หินใหญ่", min_value=0.0, step=1.0)
            plan_h2 = col_plan2.number_input("แผน: หินย่อย", min_value=0.0, step=1.0)
            plan_t = col_plan3.number_input("แผน: ทรายหยาบ", min_value=0.0, step=1.0)
            plan_p = col_plan4.number_input("แผน: ปูนซีเมนต์", min_value=0.0, step=1.0)
            plan_hc = col_plan5.number_input("แผน: หินคลุก", min_value=0.0, step=1.0)
            
            planned_values = {
                "หินใหญ่": plan_h1, "หินย่อย": plan_h2, 
                "ทรายหยาบ": plan_t, "ปูนซีเมนต์": plan_p, "หินคลุก": plan_hc
            }

        st.divider()

        # การเพิ่มรายการ
        st.subheader("➕ เพิ่มรายการงาน")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกงาน:", work_list)
        quantity = col_in2.number_input("ปริมาณงานที่ทำจริง:", min_value=0.1, value=1.0, step=0.1)
        
        if col_in3.button("➕ เพิ่มเข้าโครงการ"):
            selected_row = df[df[0] == selected_work].iloc[0]
            m_map = {"หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10}
            temp_details = {}
            for m_name, idx in m_map.items():
                try:
                    if idx < len(selected_row):
                        rate_val = float(selected_row[idx])
                        if rate_val > 0:
                            temp_details[m_name] = rate_val * quantity
                except: continue
            st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": quantity, "รายละเอียด": temp_details})
            st.rerun()

        # แสดงรายการที่บันทึก
        if st.session_state.calc_history:
            st.subheader("📋 รายการบันทึก")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"📌 {item['ประเภทงาน']} ({item['ปริมาณงาน']} หน่วย)"):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.2f}**")
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            # --- สรุปและเปรียบเทียบ ---
            st.divider()
            st.subheader("📊 ตารางเปรียบเทียบ แผน vs คำนวณจริง")
            
            totals = {}
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    # ทำความสะอาดชื่อเพื่อเทียบกับ planned_values
                    clean_name = m_n.split(" ")[0] 
                    totals[clean_name] = totals.get(clean_name, 0) + m_v

            # สร้างตารางเปรียบเทียบ
            comparison_rows = []
            for mat_name, total_val in totals.items():
                plan_val = planned_values.get(mat_name, 0)
                diff = plan_val - total_val
                status = "✅ ภายในแผน" if diff >= 0 else "⚠️ เกินแผนงาน"
                comparison_rows.append({
                    "รายการวัสดุ": mat_name,
                    "ปริมาณตามแผน": f"{plan_val:,.2f}",
                    "คำนวณจริง": f"{total_val:,.2f}",
                    "ส่วนต่าง (คงเหลือ)": f"{diff:,.2f}",
                    "สถานะ": status
                })
            
            if comparison_rows:
                st.table(pd.DataFrame(comparison_rows))

            # แสดง Metric ยอดรวม
            m_cols = st.columns(len(totals))
            for idx, (m_name, m_val) in enumerate(totals.items()):
                m_cols[idx].metric(label=m_name, value=f"{m_val:,.2f}")

            # ส่งออก
            st.divider()
            col_ex1, col_ex2 = st.columns(2)
            if st.session_state.calc_history:
                csv_data = pd.DataFrame(comparison_rows).to_csv(index=False).encode('utf-8-sig')
                col_ex1.download_button("📥 ดาวน์โหลดรายงานเปรียบเทียบ", csv_data, f"Comparison_{project_name}.csv", "text/csv")
            if col_ex2.button("🚫 ล้างข้อมูลโครงการ"):
                st.session_state.calc_history = []
                st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ data.csv")
except Exception as e:
    st.error(f"⚠️ ข้อผิดพลาด: {e}")
