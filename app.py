import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าจอสำหรับมือถือ
st.set_page_config(page_title="Material Calc Pro", layout="centered")

# ตกแต่ง UI
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

# 2. ฟังก์ชันโหลดข้อมูล (รองรับ Encoding ภาษาไทย)
@st.cache_data
def load_data():
    file_name = "ตารางคำนวณ.xlsx - data ห้ามลบ ห้ามทำชีทนี้.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            # ข้ามหัวตาราง 2 แถวแรก
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except:
            continue
    return None

try:
    df = load_data()
    
    if df is not None:
        # ดึงรายชื่อประเภทงาน (คอลัมน์แรก)
        work_list = df[0].dropna().unique().tolist()
        selected_work = st.selectbox("📌 เลือกประเภทงานก่อสร้าง:", work_list)

        # แก้ไขจุดที่ Syntax Error: ปิดวงเล็บให้ถูกต้อง
        quantity = st.number_input("🔢 ระบุปริมาณงาน (หน่วย):", min_value=0.0, value=1.0, step=0.5)

        if quantity > 0:
            st.divider()
            st.subheader(f"📊 สรุปผลลัพธ์ ({quantity} หน่วย)")
            
            # ดึงแถวข้อมูลที่เลือก
            selected_row = df[df[0] == selected_work].iloc[0]
            
            # จับคู่คอลัมน์ "อัตรา" ตามโครงสร้างไฟล์ (หินใหญ่=2, หินย่อย=4, ทราย=6, ปูน=8, หินคลุก=10)
            materials = {
                "หินใหญ่ (ลบ.ม.)": 2,
                "หินย่อย (ลบ.ม.)": 4,
                "ทรายหยาบ (ลบ.ม.)": 6,
                "ปูนซีเมนต์ (ถุง)":
