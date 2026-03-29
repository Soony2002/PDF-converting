import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from io import BytesIO

from src.pdf_parser import extract_pdf_tables
from src.charts import create_chart
from src.export_utils import export_buttons
from src.report_generator import generate_pdf_report


# --- HELPER FUNCTION FOR REPORT ---
def render_report_section(df, unique_id):
    st.markdown("---")
    st.markdown("### 📄 Export Official Report")
    
    try:
        report_data = generate_pdf_report(df)
        
        # If the report comes back as a string, encode it to bytes
        if isinstance(report_data, str):
            report_data = report_data.encode('latin-1')
            
        st.download_button(
            label="📥 Download Official PDF Analysis",
            data=report_data, 
            file_name="Grade_Analysis_Report.pdf",
            mime="application/pdf",
            key=f"report_btn_{unique_id}" # Using the unique_id passed to the function
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")

# ===== CONFIG =====
st.set_page_config(page_title="DA Dashboard", layout="wide")

# ===== LOAD CSS =====
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ===== INSIGHT SYSTEM =====
def generate_insights(df, col=None, col_x=None, col_y=None):
    insights = []

    if col:
        mean = df[col].mean()
        median = df[col].median()
        std = df[col].std()
        skew = df[col].skew()
        min_val = df[col].min()
        max_val = df[col].max()

        insights.append(f"Điểm trung bình: {mean:.2f}, trung vị: {median:.2f}")

        if std > 2:
            insights.append("Dữ liệu phân tán rộng → chênh lệch lớn")
        else:
            insights.append("Dữ liệu khá tập trung")

        if skew > 0.5:
            insights.append("Phân phối lệch phải → nhiều điểm thấp")
        elif skew < -0.5:
            insights.append("Phân phối lệch trái → nhiều điểm cao")

        if max_val >= 9:
            insights.append("Có sinh viên đạt điểm rất cao")
        if min_val < 3:
            insights.append("Có nhóm điểm rất thấp cần chú ý")

    if col_x and col_y:
        corr = df[col_x].corr(df[col_y])
        insights.append(f"Tương quan giữa {col_x} và {col_y}: {corr:.2f}")

        if corr > 0.7:
            insights.append("Mối quan hệ rất mạnh")
        elif corr > 0.4:
            insights.append("Mối quan hệ trung bình")
        else:
            insights.append("Mối quan hệ yếu")

    return insights

def render_report(insights, extra_text=None):
    html = "<div class='card'>"
    html += "<h3>📄 Report</h3>"

    for i in insights:
        html += f"<p>👉 {i}</p>"

    if extra_text:
        html += f"<p><b>👉 {extra_text}</b></p>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

# ===== SIDEBAR =====
st.sidebar.title("📊 Dashboard")

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"],
    accept_multiple_files=True
)

# ===== MAIN =====
st.markdown('<h1 class="main-title">📊 PDF Data Dashboard</h1>', unsafe_allow_html=True)

if not uploaded_file:
    st.info("Upload PDF to start")
    st.stop()

# ===== PROCESS PDF =====
with st.spinner("Đang xử lý PDF..."):
    pdf_files = [BytesIO(f.getvalue()) for f in uploaded_file]
    df = extract_pdf_tables(pdf_files)

if df is None:
    st.error("No table found in PDF")
    st.stop()


# ===== TABS =====
tab1, tab2, tab3 = st.tabs([
    "Analysis",
    "Boxplot",
    "About"
])

# ================= TAB 1 =================
with tab1:

    # ===== DATA CLEANING SUMMARY =====
    clean_html = f"""
    <div class='card'>
    <h3>🧹 Data Cleaning Summary</h3>
    <p>- Số dòng: {len(df)}</p>
    <p>- Số cột: {df.shape[1]}</p>
    <p>- Missing: {df.isna().sum().sum()}</p>
    </div>
    """

    st.markdown(clean_html, unsafe_allow_html=True)

    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)

    st.divider()

    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("### Download")
        base_name = datetime.now().strftime("data_%Y%m%d")
        export_buttons(df, base_name)

    st.markdown("### 📊 Interactive Analysis")

    analysis_option = st.selectbox(
        "Choose analysis",
        [
            "Class performance overview",
            "Score distribution",
            "Top performing students",
            "Students at risk",
            "Score relationship"
        ]
    )

    # ===== CLASS OVERVIEW =====
    if analysis_option == "Class performance overview":
        avg_score = df["Final"].mean()
        pass_rate = (df["Final"] >= 5).mean() * 100
        total = len(df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class='card'>
                <h4>Avg Score</h4>
                <h2>{avg_score:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='card'>
                <h4>Pass Rate</h4>
                <h2>{pass_rate:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='card'>
                <h4>Total Students</h4>
                <h2>{total}</h2>
            </div>
            """, unsafe_allow_html=True)

    # ===== DISTRIBUTION =====
    elif analysis_option == "Score distribution":
        st.caption("Biểu đồ phân phối điểm số")

        df['Status'] = df['Final'].apply(
            lambda x: 'Đạt (≥5)' if x >= 5 else 'Chưa đạt (<5)'
        )

        fig = px.histogram(
            df,
            x="Final",
            color="Status",
            nbins=20,
            opacity=0.8
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===== REPORT =====
        insights = generate_insights(df, col="Final")
        render_report(insights, "Phân phối điểm phản ánh mức độ học tập chung")

    # ===== TOP STUDENTS =====
    elif analysis_option == "Top performing students":
        mode = st.selectbox("Chọn nhóm", ["Top 10", "Bottom 10"])

        if mode == "Top 10":
            data = df.sort_values("Final", ascending=False).head(10)
            st.success("🏆 Top 10 sinh viên")
        else:
            data = df.sort_values("Final", ascending=True).head(10)
            st.warning("⚠️ Bottom 10 sinh viên")

        st.dataframe(data.iloc[:, 1:], use_container_width=True)

        insights = [
            "Nhóm sinh viên có kết quả cao nhất",
            "Có thể dùng làm benchmark cho lớp"
        ]

        render_report(insights)

    # ===== AT RISK =====
    elif analysis_option == "Students at risk":
        risk = df[df["Final"] < 5]

        st.warning(f"{len(risk)} students at risk")
        st.dataframe(risk.iloc[:, 1:])

        insights = [
            f"Có {len(risk)} sinh viên thuộc nhóm nguy cơ",
            "Cần hỗ trợ thêm để cải thiện kết quả"
        ]

        render_report(insights)

    # ===== SCATTER =====
    elif analysis_option == "Score relationship":
        col_x = st.selectbox("Trục X", ["CC", "GK", "TL"])
        col_y = st.selectbox("Trục Y", ["CK", "Final"])

        corr = df[col_x].corr(df[col_y])

        fig = px.scatter(
            df,
            x=col_x,
            y=col_y,
            color="Final",
            trendline="ols",
            title=f"{col_x} vs {col_y} | Corr: {corr:.2f}"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===== REPORT =====
        
        insights = generate_insights(df, col_x=col_x, col_y=col_y)
        render_report(insights)
        
    render_report_section(df, "tab1")


# ================= TAB 2 =================
with tab2:
    st.subheader("Boxplot Analysis")

    col_x = st.selectbox("X", df.columns)
    col_y = st.selectbox("Y", df.columns)

    if col_x and col_y:
        create_chart(f"boxplot {col_x} {col_y}", df)

    render_report_section(df, "tab2")
    
# ================= TAB 3 =================
with tab3:
    st.header("About")

    st.write("""
    Project:
    - Convert PDF → Data
    - Interactive charts
    - Data analysis dashboard
    """)