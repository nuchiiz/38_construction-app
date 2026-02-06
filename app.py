import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบคำนวณวัสดุ", layout="wide")

# ตกแต่ง UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border: 1px solid #d1d1d1; }
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

# 3. เตรียมหน่วยความจำ
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ระบบจัดการวัสดุ (หลายรายการ)")

try:
    df = load_data()
    if df is not None:
        # ส่วนข้อมูลโครงการ
        col_p1, col_p2 = st.columns(2)
        project_name = col_p1.text_input("🏢 ชื่อโครงการ:", value="โครงการใหม่")
        calc_date = datetime.now().strftime("%d/%m/%Y")
        col_p2.text_input("📅 วันที่:", value=calc_date, disabled=True)

        st.divider()

        # ส่วนการเพิ่มรายการ
        st.subheader("➕ เพิ่มรายการงาน")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        quantity = col_in2.number_input("ปริมาณงาน:", min_value=0.1, value=1.0, step=0.1)
        
        if col_in3.button("➕ เพิ่มเข้าโครงการ"):
            selected_row = df[df[0] == selected_work].iloc[0]
            # แผนผังคอลัมน์อัตรา (2=หินใหญ่, 4=หินย่อย, 6=ทราย, 8=ปูน, 10=หินคลุก)
            m_map = {"หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10}
            
            temp_details = {}
            for m_name, idx in m_map.items():
                try:
                    # ตรวจสอบว่าคอลัมน์มีอยู่จริงและเป็นตัวเลข
                    if idx < len(selected_row):
                        rate_val = float(selected_row[idx])
                        if rate_val > 0:
                            temp_details[m_name] = rate_val * quantity
                except (ValueError, TypeError):
                    continue
            
            # บันทึกข้อมูล
            st.session_state.calc_history.append({
                "ประเภทงาน": selected_work,
                "ปริมาณงาน": quantity,
                "รายละเอียด": temp_details
            })
            st.rerun()

        # 4. รายการที่บันทึกและการลบ
        if st.session_state.calc_history:
            st.divider()
            st.subheader("📝 รายการที่เลือกไว้")
            
            # สร้างสำเนาเพื่อวนลูปตอนลบ
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"รายการที่ {i+1}: {item['ประเภทงาน']} ({item['ปริมาณงาน']} หน่วย)"):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.2f}**")
                    
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            # 5. สรุปยอดรวม (ตรวจสอบยอดรวม)
            st.divider()
            st.subheader("📊 ยอดรวมวัสดุทั้งหมดที่ต้องใช้")
            
            totals = {}
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    totals[m_n] = totals.get(m_n, 0) + m_v
            
            if totals:
                # แสดง Metric สวยๆ
                m_cols = st.columns(len(totals))
                for idx, (m_name, m_val) in enumerate(totals.items()):
                    m_cols[idx].metric(m_name, f"{m_val:,.2f}")
                
                # แสดงตารางสรุป
                st.table(pd.DataFrame(list(totals.items()), columns=['วัสดุ', 'จำนวนรวมสุทธิ']))

            # 6. ส่งออกข้อมูล
            col_ex1, col_ex2 = st.columns(2)
            
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
                col_ex1.download_button("📥 ดาวน์โหลดไฟล์สรุป", csv_data, f"Summary_{project_name}.csv", "text/csv")
            
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
