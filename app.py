import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro", layout="wide")

# ปรับปรุง CSS ให้ตัวหนังสือเด่นและสีพื้นหลังชัดเจน
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

    /* ปรับแต่ง Metric ให้ตัวหนังสือหนาและเด่น */
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #000000 !important; /* ตัวเลขสีดำเข้ม */
    }
    [data-testid="stMetricLabel"] {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #1a1a1a !important;
    }

    /* สีพื้นหลัง Metric แบบ High Contrast */
    div[data-testid="stMetric"]:nth-child(1) { background-color: #D1D5DB; border: 2px solid #9CA3AF; } /* หินใหญ่ - เทาเข้ม */
    div[data-testid="stMetric"]:nth-child(2) { background-color: #9CA3AF; border: 2px solid #4B5563; } /* หินย่อย - เทา */
    div[data-testid="stMetric"]:nth-child(3) { background-color: #FDE68A; border: 2px solid #F59E0B; } /* ทราย - เหลืองเข้ม */
    div[data-testid="stMetric"]:nth-child(4) { background-color: #A7F3D0; border: 2px solid #10B981; } /* ปูน - เขียวเด่น */
    div[data-testid="stMetric"]:nth-child(5) { background-color: #BFDBFE; border: 2px solid #3B82F6; } /* หินคลุก - ฟ้า */

    /* ปรับช่อง Input ให้ตัวหนังสือใหญ่ */
    input { font-size: 20px !important; font-weight: bold !important; }
    
    /* กรอบรายการงาน */
    .stExpander {
        border: 2px solid #1a1a1a !important;
        background-color: #ffffff !important;
        border-radius: 10px !important;
        box-shadow: 3px 3px 0px #000000;
    }
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

st.title("🏗️ ระบบจัดการและเปรียบเทียบวัสดุ (Full Report)")

try:
    df = load_data()
    if df is not None:
        # ส่วนหัวโครงการ
        col_p1, col_p2 = st.columns([3, 1])
        project_name = col_p1.text_input("🏢 ชื่อโครงการ / ไซต์งาน:", value="โครงการใหม่")
        calc_date = datetime.now().strftime("%d/%m/%Y")
        col_p2.text_input("📅 วันที่:", value=calc_date, disabled=True)
            
        # การตั้งค่าแผน
        with st.expander("📊 1. ตั้งค่าปริมาณตามแผน (Planned)", expanded=False):
            col_plan = st.columns(5)
            p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก"]
            planned_values = {}
            for i, name in enumerate(p_names):
                planned_values[name] = col_plan[i].number_input(f"แผน: {name}", min_value=0.0, key=f"p_{i}")

        st.divider()

        # เพิ่มรายการงาน
        st.subheader("➕ 2. เพิ่มรายการงานที่ทำจริง")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        quantity = col_in2.number_input("ปริมาณงานจริง:", min_value=0.1, value=1.0)
        
        if col_in3.button("➕ เพิ่มเข้าโครงการ"):
            selected_row = df[df[0] == selected_work].iloc[0]
            m_map = {"หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10}
            temp_details = {}
            for m_name, idx in m_map.items():
                try:
                    if idx < len(selected_row):
                        rate_val = float(selected_row[idx])
                        if rate_val > 0: temp_details[m_name] = rate_val * quantity
                except: continue
            st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": quantity, "รายละเอียด": temp_details})
            st.rerun()

        # แสดงรายการ
        if st.session_state.calc_history:
            st.subheader("📋 3. รายการบันทึกสะสม")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} | {item['ปริมาณงาน']} หน่วย", expanded=False):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.2f}**")
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            # ส่วนสรุปและเปรียบเทียบ
            st.divider()
            st.subheader("📊 4. สรุปผลและเปรียบเทียบแผน")
            
            totals = {k: 0.0 for k in p_names}
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    # Matching name
                    for p_n in p_names:
                        if p_n in m_n: totals[p_n] += m_v

            # แสดง Metric สีเด่นชัด
            m_cols = st.columns(len(p_names))
            for i, name in enumerate(p_names):
                m_cols[i].metric(label=name, value=f"{totals[name]:,.2f}")

            # ตารางเปรียบเทียบในแอป
            comp_rows = []
            for name in p_names:
                p_val = planned_values[name]
                a_val = totals[name]
                diff = p_val - a_val
                comp_rows.append({
                    "รายการวัสดุ": name,
                    "แผนงาน": p_val,
                    "รวมคำนวณจริง": a_val,
                    "ส่วนต่าง": diff,
                    "สถานะ": "✅ OK" if diff >= 0 else "⚠️ Over"
                })
            st.table(pd.DataFrame(comp_rows))

            # --- ส่วน EXPORT ข้อมูลแบบละเอียดรวมภาพรวม ---
            st.subheader("📤 5. ส่งออกข้อมูล")
            
            # 1. ส่วนรายละเอียด (Detailed)
            export_detailed = []
            for item in st.session_state.calc_history:
                row = {"ประเภทงาน": item['ประเภทงาน'], "ปริมาณงานจริง": item['ปริมาณงาน']}
                # ใส่ค่าวัสดุแต่ละตัว
                for name in p_names:
                    val = 0.0
                    for m_n, m_v in item['รายละเอียด'].items():
                        if name in m_n: val = m_v
                    row[name] = val
                export_detailed.append(row)
            
            df_detailed = pd.DataFrame(export_detailed)
            
            # 2. ส่วนสรุปเปรียบเทียบ (Comparison)
            df_comp = pd.DataFrame(comp_rows)
            
            # รวมไฟล์ CSV (คั่นด้วยบรรทัดว่าง)
            output_text = f"รายงานวัสดุโครงการ: {project_name}\nวันที่คำนวณ: {calc_date}\n\n"
            output_text += "--- รายละเอียดรายรายการ ---\n"
            output_text += df_detailed.to_csv(index=False)
            output_text += "\n--- สรุปยอดรวมและเปรียบเทียบแผน ---\n"
            output_text += df_comp.to_csv(index=False)
            
            col_ex1, col_ex2 = st.columns(2)
            col_ex1.download_button(
                label="📥 ดาวน์โหลดรายงานฉบับสมบูรณ์",
                data=output_text.encode('utf-8-sig'),
                file_name=f'Report_{project_name}_{calc_date}.csv',
                mime='text/csv',
                use_container_width=True
            )
            if col_ex2.button("🚫 ล้างข้อมูลโครงการทั้งหมด"):
                st.session_state.calc_history = []
                st.rerun()

    else:
        st.error("❌ ไม่พบไฟล์ data.csv")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
