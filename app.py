import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="คำนวณอัตราปริมาณงานของงานคอนกรีตและหินต่าง ๆ", layout="wide")

# ปรับปรุงฟอนต์และกรอบให้ชัดเจน (CSS)
st.markdown("""
    <style>
    /* ปรับขนาดฟอนต์หัวข้อหลัก */
    h1, h2, h3 { color: #1E1E1E; font-family: 'Sarabun', sans-serif; }
    
    /* กรอบรายการงานที่บันทึกไว้ */
    .stExpander {
        border: 2px solid #28a745 !important;
        border-radius: 10px !important;
        background-color: #F8FFF9 !important;
        margin-bottom: 10px !important;
    }
    
    /* ปรับขนาดตัวเลขใน Metric (ยอดรวม) */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #28a745 !important;
    }
    
    /* ตารางสรุปผล */
    .stTable {
        border: 1px solid #dee2e6;
        border-radius: 10px;
    }
    
    /* ช่องกรอกข้อมูล */
    .stNumberInput input {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    file_name = "เทสตาราง.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except:
            continue
    return None

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ระบบจัดการวัสดุ (ฉบับปรับปรุงใหม่)")

try:
    df = load_data()
    if df is not None:
        # ส่วนข้อมูลโครงการ
        with st.container():
            col_p1, col_p2 = st.columns(2)
            project_name = col_p1.text_input("🏢 ชื่อโครงการ (กรอกเพื่อตั้งชื่อไฟล์):", value="โครงการใหม่")
            calc_date = datetime.now().strftime("%d/%m/%Y")
            col_p2.text_input("📅 วันที่คำนวณ:", value=calc_date, disabled=True)

        st.divider()

        # ส่วนการเพิ่มรายการ
        st.subheader("➕ เพิ่มรายการงานใหม่")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        quantity = col_in2.number_input("ปริมาณงาน (หน่วย):", min_value=0.1, value=1.0, step=0.1)
        
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
                except:
                    continue
            
            st.session_state.calc_history.append({
                "ประเภทงาน": selected_work,
                "ปริมาณงาน": quantity,
                "รายละเอียด": temp_details
            })
            st.rerun()

        # 4. แสดงรายการที่เพิ่มไปแล้ว (ใช้กรอบชัดเจน)
        if st.session_state.calc_history:
            st.divider()
            st.subheader("📋 รายการที่บันทึกไว้ (ตรวจสอบ/ลบ)")
            
            for i, item in enumerate(st.session_state.calc_history):
                # ปรับแต่งกรอบ Expander ด้วย CSS ด้านบนแล้ว
                with st.expander(f"📌 {item['ประเภทงาน']} | จำนวน {item['ปริมาณงาน']} หน่วย", expanded=True):
                    cols_m = st.columns(len(item['รายละเอียด']))
                    for idx, (m_n, m_v) in enumerate(item['รายละเอียด'].items()):
                        cols_m[idx].write(f"**{m_n}**")
                        cols_m[idx].write(f"{m_v:,.2f}")
                    
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            # 5. สรุปยอดรวม (ตัวเลขใหญ่ชัดเจน)
            st.divider()
            st.subheader("📊 ยอดรวมวัสดุสุทธิ (สำหรับสั่งของ)")
            
            totals = {}
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    totals[m_n] = totals.get(m_n, 0) + m_v
            
            if totals:
                # แสดงผลยอดรวมแบบ Card
                m_cols = st.columns(len(totals))
                for idx, (m_name, m_val) in enumerate(totals.items()):
                    with m_cols[idx]:
                        st.metric(label=m_name, value=f"{m_val:,.2f}")
                
                # ตารางสรุปแบบทางการ
                st.table(pd.DataFrame(list(totals.items()), columns=['รายการวัสดุ', 'จำนวนรวมที่ต้องใช้']))

            # 6. ส่งออกและล้างข้อมูล
            st.divider()
            col_ex1, col_ex2 = st.columns(2)
            
            # เตรียมไฟล์ CSV
            export_list = []
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    export_list.append({
                        "โครงการ": project_name,
                        "วันที่": calc_date,
                        "ประเภทงาน": item['ประเภทงาน'],
                        "ปริมาณ": item['ปริมาณงาน'],
                        "วัสดุ": m_n,
                        "จำนวน": m_v
                    })
            
            if export_list:
                csv_data = pd.DataFrame(export_list).to_csv(index=False).encode('utf-8-sig')
                col_ex1.download_button("📥 ดาวน์โหลดไฟล์สรุป (Excel/CSV)", csv_data, f"Summary_{project_name}.csv", "text/csv")
            
            if col_ex2.button("🚫 ล้างข้อมูลทั้งหมด"):
                st.session_state.calc_history = []
                st.rerun()

    else:
        st.error("❌ ไม่พบไฟล์ data.csv บน GitHub")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
    if st.button("🔄 รีเซ็ตแอปพลิเคชัน"):
        st.session_state.calc_history = []
        st.rerun()
