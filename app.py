import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Multi-Material Calc", layout="wide")

# ตกแต่ง UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    .report-table { font-size: 14px; }
    .total-box { background-color: #e9ecef; padding: 15px; border-radius: 10px; margin-top: 10px; }
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

# 3. เตรียมระบบหน่วยความจำ (Session State)
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ระบบคำนวณวัสดุรวมหลายรายการ")

try:
    df = load_data()
    if df is not None:
        # ส่วนข้อมูลโครงการ
        with st.expander("📝 ข้อมูลโครงการ", expanded=True):
            col_p1, col_p2 = st.columns(2)
            project_name = col_p1.text_input("ชื่อโครงการ:", value="โครงการใหม่")
            calc_date = col_p2.text_input("วันที่:", value=datetime.now().strftime("%d/%m/%Y"), disabled=True)

        # ส่วนการเลือกงาน
        st.subheader("➕ เพิ่มรายการงาน")
        col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
        
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_input1.selectbox("ประเภทงาน:", work_list)
        quantity = col_input2.number_input("ปริมาณงาน:", min_value=0.1, value=1.0, step=0.1)
        
        if col_input3.button("➕ เพิ่มเข้าโครงการ"):
            selected_row = df[df[0] == selected_work].iloc[0]
            materials = {
                "หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10
            }
            
            # คำนวณวัสดุทุกตัวในแถวนั้น
            for mat_name, idx in materials.items():
                try:
                    rate = float(selected_row[idx])
                    if rate > 0:
                        total_mat = quantity * rate
                        # บันทึกลงหน่วยความจำ
                        st.session_state.calc_history.append({
                            "ประเภทงาน": selected_work,
                            "ปริมาณงาน": quantity,
                            "รายการวัสดุ": mat_name,
                            "อัตรา": rate,
                            "จำนวนที่ใช้": total_mat
                        })
                except:
                    continue
            st.success(f"เพิ่ม {selected_work} เรียบร้อย!")

        # 4. แสดงผลรายการทั้งหมดที่เพิ่มไปแล้ว
        if st.session_state.calc_history:
            st.divider()
            st.subheader("📊 ตารางสรุปภาพรวมโครงการ")
            
            summary_df = pd.DataFrame(st.session_state.calc_history)
            
            # แสดงตารางแบบสรุปผลรวมวัสดุแยกตามประเภท
            pivot_df = summary_df.groupby("รายการวัสดุ")["จำนวนที่ใช้"].sum().reset_index()
            
            st.write("**รวมวัสดุทั้งหมดที่ต้องสั่ง:**")
            cols = st.columns(len(pivot_df))
            for i, row in pivot_df.iterrows():
                cols[i].metric(label=row['รายการวัสดุ'], value=f"{row['จำนวนที่ใช้']:,.2f}")

            with st.expander("🔍 ดูรายละเอียดแยกตามรายการงาน"):
                st.table(summary_df)

            # ปุ่มล้างข้อมูล
            if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
                st.session_state.calc_history = []
                st.rerun()

            # 5. ปุ่ม Export
            st.subheader("📤 ส่งออกข้อมูล")
            # เพิ่มข้อมูลโครงการลงในไฟล์ด้วย
            export_df = summary_df.copy()
            export_df['ชื่อโครงการ'] = project_name
            export_df['วันที่'] = calc_date
            
            csv = export_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์สรุปโครงการ (.csv)",
                data=csv,
                file_name=f'สรุปวัสดุ_{project_name}.csv',
                mime='text/csv',
                use_container_width=True
            )
    else:
        st.error("❌ ไม่พบไฟล์ข้อมูล เทสตาราง.csv")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
