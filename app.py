import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าจอสำหรับ Mobile First
st.set_page_config(page_title="เครื่องคิดเลขวัสดุ", layout="centered")

# ตกแต่ง CSS ให้ดูง่ายบนมือถือ
st.markdown("""
    <style>
    .stNumberInput input { font-size: 20px !important; }
    .material-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #007bff; margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ โปรแกรมคำนวณวัสดุ")

# 2. ฟังก์ชันโหลดข้อมูลที่รองรับภาษาไทยและโครงสร้างที่ซับซ้อน
@st.cache_data
def load_data():
    file_name = "ตารางคำนวณ.xlsx - data ห้ามลบ ห้ามทำชีทนี้.csv"
    # รายชื่อรหัสภาษาไทยที่ต้องทดสอบ
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
        # ดึงรายชื่อประเภทงาน (คอลัมน์แรก)
        work_list = df[0].dropna().unique().tolist()
        selected_work = st.selectbox("📌 เลือกประเภทงานก่อสร้าง:", work_list)

        # ช่องกรอกปริมาณงาน
        quantity = st.number_input("🔢 ระบุปริมาณงาน (หน่วย):", min_value=0.0, value=1.0, step
