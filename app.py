import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Material Management Pro", layout="wide")

# ตกแต่ง UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .btn-delete { background-color: #ff4b4b !important; color: white !important; }
    .total-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border: 1px solid #dee2e6; }
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

# 3. หน่วยความจำ (Session State)
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ระบบจัดการวัสดุก่อสร้าง")

try:
    df = load_data()
    if df is not None:
        # ส่วนหัวโครงการ
        with st.container():
            col_p1, col_p2 = st.columns(2)
            project_name = col_p1.text_input("🏢 ชื่อโครงการ:", value="โครงการใหม่")
            calc_date = datetime.now().strftime("%d/%m/%Y")
            col_p2.text_input("📅 วันที่คำนวณ:", value=calc_date, disabled=True)

        st.divider()

        # ส่วนการเพิ่มรายการ
        st.subheader("➕ เพิ่มรายการงาน")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        quantity = col_in2.number_input("ปริมาณงาน:", min_value=0.1, value=1.0, step=0.1)
        
        if col_in3.button("➕ เพิ่มรายการ"):
            selected_row = df[df[0] == selected_work].iloc[0]
            materials = {
                "หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10
            }
            # เพิ่มข้อมูลแยกตามประเภทงาน
            st.session_state.calc_history.append({
                "id": len(st.session_state.calc_history), # ID สำหรับอ้างอิงตอนลบ
                "ประเภทงาน": selected_work,
                "ปริมาณงาน": quantity,
                "รายละเอียดวัสดุ": {m: float(selected_row[idx]) * quantity for m, idx in materials.items() if float(selected_row[idx]) > 0}
            })
            st.rerun()

        # 4. แสดงรายการที่เพิ่มไปแล้ว (พร้อมปุ่มลบรายรายการ)
        if st.session_state.calc_history:
            st.subheader("📝 รายการที่บันทึกไว้")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} ({item['ปริมาณงาน']} หน่วย)"):
                    # แสดงวัสดุข้างใน
                    for mat, val in item['รายละเอียดวัสดุ'].items():
                        st.write(f"- {mat}: **{val:,.2f}**")
                    
                    # ปุ่มลบรายการนี้
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            st.divider()

            # 5. ส่วนตรวจสอบยอดรวม (Summary Table)
            st.subheader("📊 ตรวจสอบยอดรวมวัสดุทั้งหมด")
            
            # ยุบรวมข้อมูลเพื่อสรุปผล
            final_totals = {}
            for item in st.session_state.calc_history:
                for mat, val in item['รายละเอียดวัสดุ'].items():
                    final_totals[mat] = final_totals.get(mat, 0) + val
            
            # แสดงผลแบบ Card สรุปยอด
            sum_col = st.columns(len(final_totals))
            for idx, (mat, val) in enumerate(final_totals.items()):
                sum_col[idx].metric(label=mat, value=f"{val:,.2f}")

            # ตารางสำหรับตรวจสอบความถูกต้องก่อน Export
            st.write("---")
            total_df = pd.DataFrame(list(final_totals.items()), columns=['รายการวัสดุ', 'จำนวนรวมสุทธิ'])
            st.table(total_df)

            # 6. Export และ Clear
            st.subheader("📤 ดำเนินการ")
            col_ex1, col_ex2 = st.columns(2)
            
            # สร้างไฟล์ CSV
            export_data = []
            for item in st.session_state.calc_history:
                for mat, val in item['รายละเอียดวัสดุ'].items():
                    export_data.append({
                        "โครงการ": project_name,
                        "วันที่": calc_date,
                        "ประเภทงาน": item['ประเภทงาน'],
                        "ปริมาณงาน": item['ปริมาณงาน'],
                        "วัสดุ": mat,
                        "จำนวน": val
                    })
            
            if export_data:
                csv = pd.DataFrame(export_data).to_csv(index=False).encode('utf-8-sig')
                col_ex1.download_button(
                    label="📥 ดาวน์โหลดไฟล์สรุป",
                    data=csv,
                    file_name=f'สรุปวัสดุ_{project_name}.csv',
                    mime='text/csv'
                )
            
            if col_ex2.button("🗑️ ล้างข้อมูลทั้งหมด"):
                st.session_state.calc_history = []
                st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ เทสตาราง.csv")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
