import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Material Calculator", layout="centered")

# ตกแต่ง UI ให้เหมาะกับมือถือ
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

st.title("🏗️ คำนวณวัสดุก่อสร้าง")

# 2. ฟังก์ชันโหลดข้อมูล (อ้างอิงชื่อไฟล์สั้นๆ ว่า เทสตาราง.csv)
@st.cache_data
def load_data():
    file_name = "เทสตาราง.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            # ข้าม 2 แถวแรกที่เป็นหัวตารางซ้อนกัน
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except:
            continue
    return None

try:
    df = load_data()
    
    if df is not None:
        # รายชื่อประเภทงาน (คอลัมน์แรก)
        work_list = df[0].dropna().unique().tolist()
        selected_work = st.selectbox("📌 เลือกประเภทงาน:", work_list)

        # ช่องกรอกปริมาณ
        quantity = st.number_input("🔢 ระบุปริมาณงาน (หน่วย):", min_value=0.0, value=1.0, step=0.5)

        if quantity > 0:
            st.divider()
            st.subheader(f"📊 สรุปรายการสำหรับ {quantity} หน่วย")
            
            # ค้นหาแถวที่ตรงกับงานที่เลือก
            selected_row = df[df[0] == selected_work].iloc[0]
            
            # จับคู่คอลัมน์ "อัตรา" (หินใหญ่=2, หินย่อย=4, ทราย=6, ปูน=8, หินคลุก=10)
            materials = {
                "หินใหญ่ (ลบ.ม.)": 2,
                "หินย่อย (ลบ.ม.)": 4,
                "ทรายหยาบ (ลบ.ม.)": 6,
                "ปูนซีเมนต์ (ถุง)": 8,
                "หินคลุก (ลบ.ม.)": 10
            }

            for name, idx in materials.items():
                try:
                    # ตรวจสอบว่าตำแหน่งคอลัมน์มีอยู่จริง
                    if idx < len(selected_row):
                        rate = float(selected_row[idx])
                        if rate > 0:
                            total = quantity * rate
                            st.markdown(f"""
                                <div class="material-card">
                                    <div style="color: gray; font-size: 14px;">{name}</div>
                                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">{total:,.2f}</div>
                                    <div style="font-size: 12px; color: #666;">ใช้อัตรา: {rate}</div>
                                </div>
                            """, unsafe_allow_html=True)
                except:
                    continue
    else:
        # แสดงข้อความเตือนหากหาไฟล์ไม่เจอ
        st.error("❌ ไม่พบไฟล์ เทสตาราง.csv บน GitHub กรุณาเช็กชื่อไฟล์อีกครั้ง")
        st.info("คำแนะนำ: เปลี่ยนชื่อไฟล์บน GitHub ให้เป็น เทสตาราง.csv")

except Exception as e:
    st.error(f"⚠️ ตรวจพบข้อผิดพลาด: {e}")

