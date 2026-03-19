import streamlit as st
from datetime import datetime

from src.pdf_parser import extract_pdf_tables
from src.charts import create_chart
from src.export_utils import export_buttons

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# TITLE
st.markdown(
'<div class="main-title">Mô phỏng phổ điểm và kiến nghị giáo viên</div>',
unsafe_allow_html=True
)

# DESCRIPTION
st.markdown(
'<div class="sub-title">Upload file PDF bảng điểm và tạo biểu đồ phân tích</div>',
unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Tải file PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    df = extract_pdf_tables(uploaded_files)

    if df is not None:
        
        base_name = datetime.now().strftime("merged_%Y-%m-%d_%H-%M-%S")

        export_buttons(df, base_name)

        st.dataframe(df)

        st.markdown("### Ví dụ prompt")

        st.markdown("""
            • phân bố điểm tổng  
            • trung bình theo lớp  
            • top sinh viên
            """)

        prompt = st.text_input(
            "Nhập yêu cầu phân tích",
            placeholder="Ví dụ: phân bố điểm"
        )

        if prompt:
            create_chart(prompt, df)