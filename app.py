import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Material Management Pro", layout="wide")

# ตกแต่ง UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .material-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    file_name = "เทสตาราง.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            # ข้าม 2 แถวแรกที่เป็นหัวตาราง
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except:
            continue
    return None

# 3. เคลียร์ Session เก่าเพื่อป้องกัน Error จากโครงสร้างเดิม
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
            # คอลัมน์ที่เก็บ "อัตรา" คือ index 2, 4, 6, 8
