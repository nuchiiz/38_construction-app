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
        border-left: 5px solid #ff4b4b; margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ คำนวณวัสดุก่อสร้าง")

# 2. ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    file_name = "ตารางคำนวณ.xlsx"
    # ทดสอบรหัสภาษาไทย
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            # เริ่มอ่านจากแถวที่ 3 (index 2) เพื่อข้ามหัวตารางที่ซ้อนกัน
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
            
            # 3. ส่วนที่เคย Error (ปิดปีกกาและวงเล็บให้ครบถ้วน)
            materials = {
                "หินใหญ่ (ลบ.ม.)": 2,
                "หินย่อย (ลบ.ม.)": 4,
                "ทรายหยาบ (ลบ.ม.)": 6,
                "ปูนซีเมนต์ (ถุง)": 8,
                "หินคลุก (ลบ.ม.)": 10
            }

            # วนลูปแสดงผล
            for name, idx in materials.items():
                try:
                    # ตรวจสอบว่าคอลัมน์มีข้อมูลและเป็นตัวเลข
                    rate = float(selected_row[idx])
                    if rate > 0:
                        total = quantity * rate
                        st.markdown(f"""
                            <div class="material-card">
                                <div style="color: gray; font-size: 14px;">{name}</div>
                                <div style="font-size: 24px; font-weight: bold; color: #ff4b4b;">{total:,.2f}</div>
                                <div style="font-size: 12px;">อัตรา: {rate}</div>
                            </div>
                        """, unsafe_allow_html=True)
                except:
                    continue
    else:
        st.error("❌ ไม่สามารถโหลดไฟล์ข้อมูลได้ กรุณาตรวจสอบชื่อไฟล์ใน GitHub")

except Exception as e:
    st.error(f"⚠️ ตรวจพบข้อผิดพลาด: {e}")
