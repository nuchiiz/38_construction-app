import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Material Calculator Pro", layout="centered")

st.markdown("""
    <style>
    .stNumberInput input { font-size: 20px !important; }
    .material-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #28a745; margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ โปรแกรมคำนวณวัสดุ")

# 2. ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    file_name = "เทสตาราง.csv" # ตรวจสอบให้แน่ใจว่าบน GitHub ชื่อไฟล์นี้
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except:
            continue
    return None

try:
    df = load_data()
    if df is not None:
        # --- ส่วนข้อมูลโครงการ ---
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("🏢 ชื่อโครงการ:", value="โครงการก่อสร้างทั่วไป")
        with col2:
            calc_date = datetime.now().strftime("%d/%m/%Y")
            st.text_input("📅 วันที่คำนวณ:", value=calc_date, disabled=True)

        work_list = df[0].dropna().unique().tolist()
        selected_work = st.selectbox("📌 เลือกประเภทงาน:", work_list)
        quantity = st.number_input("🔢 ระบุปริมาณงาน (หน่วย):", min_value=0.0, value=1.0, step=0.5)

        if quantity > 0:
            st.divider()
            st.subheader(f"📊 รายการสำหรับ {quantity} หน่วย")
            
            selected_row = df[df[0] == selected_work].iloc[0]
            materials = {
                "หินใหญ่ (ลบ.ม.)": 2, "หินย่อย (ลบ.ม.)": 4, "ทรายหยาบ (ลบ.ม.)": 6,
                "ปูนซีเมนต์ (ถุง)": 8, "หินคลุก (ลบ.ม.)": 10
            }

            # เตรียมข้อมูลสำหรับ Export
            export_list = []
            
            for name, idx in materials.items():
                try:
                    rate = float(selected_row[idx])
                    if rate > 0:
                        total = quantity * rate
                        st.markdown(f"""
                            <div class="material-card">
                                <div style="color: gray; font-size: 14px;">{name}</div>
                                <div style="font-size: 24px; font-weight: bold; color: #28a745;">{total:,.2f}</div>
                                <div style="font-size: 12px;">อัตรา: {rate}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        # เก็บข้อมูลเข้า List สำหรับทำไฟล์สรุป
                        export_list.append({
                            "โครงการ": project_name,
                            "วันที่": calc_date,
                            "ประเภทงาน": selected_work,
                            "ปริมาณงาน": quantity,
                            "รายการวัสดุ": name,
                            "อัตราส่วน": rate,
                            "รวมวัสดุที่ใช้": total
                        })
                except:
                    continue

            # --- ส่วนปุ่ม Export ---
            if export_list:
                st.divider()
                export_df = pd.DataFrame(export_list)
                csv = export_df.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์สรุปโครงการ (Excel/CSV)",
                    data=csv,
                    file_name=f'สรุปวัสดุ_{project_name}_{calc_date}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
    else:
        st.error("❌ ไม่พบไฟล์ข้อมูล")

except Exception as e:
    st.error(f"⚠️ ข้อผิดพลาด: {e}")
