import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บให้เหมาะกับมือถือ
st.set_page_config(page_title="เครื่องคิดเลขวัสดุ", layout="centered")

# ปรับสไตล์ปุ่มและฟอนต์
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

st.title("🏗️ คำนวณปริมาณวัสดุ")

@st.cache_data
def load_data():
    file_name = "เทสตาราง.xlsx - data ห้ามลบ ห้ามทำชีทนี้.csv"
    
    # ลองโหลดด้วยรหัสภาษาไทย (TIS-620 หรือ CP874)
    try:
        # พยายามอ่านด้วย TIS-620 ก่อน
        df = pd.read_csv(file_name, skiprows=2, header=None, encoding='tis-620')
    except:
        # ถ้าไม่ได้ ให้ลอง CP874 (รหัสภาษาไทยของ Windows)
        df = pd.read_csv(file_name, skiprows=2, header=None, encoding='cp874')
    
    return df

try:
    df = load_data()
    
    # ดึงรายชื่อประเภทงาน (คอลัมน์แรก)
    work_list = df[0].dropna().unique().tolist()
    selected_work = st.selectbox("📌 เลือกประเภทงาน:", work_list)

    # ช่องกรอกปริมาณงาน
    quantity = st.number_input("🔢 ระบุปริมาณงาน (หน่วย):", min_value=0.0, step=1.0)

    if quantity > 0:
        st.divider()
        st.subheader("📋 รายการวัสดุที่ต้องใช้")
        
        # ค้นหาแถวข้อมูลที่ตรงกับงานที่เลือก
        selected_row = df[df[0] == selected_work].iloc[0]
        
        # กำหนดชื่อวัสดุและตำแหน่งคอลัมน์ "อัตรา" (อิงจากไฟล์ของคุณ)
        # index 2=หินใหญ่, 4=หินย่อย, 6=ทรายหยาบ, 8=ปูน, 10=หินคลุก
        materials = {
            "หินใหญ่ (ลบ.ม.)": 2,
            "หินย่อย (ลบ.ม.)": 4,
            "ทรายหยาบ (ลบ.ม.)": 6,
            "ปูนซีเมนต์ (ถุง)": 8,
            "หินคลุก (ลบ.ม.)": 10
        }

        for name, idx in materials.items():
            rate = selected_row[idx]
            try:
                rate_val = float(rate)
                if rate_val > 0:
                    total = quantity * rate_val
                    st.markdown(f"""
                        <div class="material-card">
                            <div style="color: gray; font-size: 12px;">{name}</div>
                            <div style="font-size: 22px; font-weight: bold; color: #ff4b4b;">{total:,.2f}</div>
                            <div style="font-size: 12px; color: #666;">ใช้อัตรา: {rate_val} ต่อหน่วยงาน</div>
                        </div>
                    """, unsafe_allow_html=True)
            except:
                continue

except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลได้: {e}")
    st.info("ตารางคำนวณ.xlsx")
