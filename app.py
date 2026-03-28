import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from io import BytesIO

from src.pdf_parser import extract_pdf_tables
from src.charts import create_chart
from src.export_utils import export_buttons

# ===== CONFIG =====
st.set_page_config(page_title="DA Dashboard", layout="wide")

# ===== LOAD CSS =====
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ===== LANGUAGE =====
lang = st.sidebar.selectbox(
    "Language",
    ["English", "Tiếng Việt"]
)

TEXT = {
    "title": {
        "English": "PDF Data Dashboard",
        "Tiếng Việt": "Phân tích dữ liệu từ PDF"
    },
    "upload": {
        "English": "Upload PDF",
        "Tiếng Việt": "Tải file PDF"
    },
    "analysis": {
        "English": "Data Analysis",
        "Tiếng Việt": "Phân tích dữ liệu"
    },
    "boxplot": {
        "English": "Boxplot",
        "Tiếng Việt": "Biểu đồ Boxplot"
    },
    "about": {
        "English": "About",
        "Tiếng Việt": "Giới thiệu"
    },
    "download": {
        "English": "Download",
        "Tiếng Việt": "Tải xuống"
    },
    "prompt": {
        "English": "Enter your request",
        "Tiếng Việt": "Nhập yêu cầu"
    }
}

# ===== SIDEBAR =====
st.sidebar.title("📊 Dashboard")

uploaded_file = st.sidebar.file_uploader(
    TEXT["upload"][lang],
    type=["pdf"],
    accept_multiple_files=True
)

# ===== MAIN =====
st.title(TEXT["title"][lang])

# ===== NO FILE =====
if not uploaded_file:
    st.info("Upload PDF to start")
    st.stop()

# ===== PROCESS PDF =====
pdf_files = [BytesIO(f.getvalue()) for f in uploaded_file]
df = extract_pdf_tables(pdf_files)

if df is None:
    st.error("No table found in PDF")
    st.stop()

# ===== TABS =====
tab1, tab2, tab3 = st.tabs([
    TEXT["analysis"][lang],
    TEXT["boxplot"][lang],
    TEXT["about"][lang]
])

with tab1:
    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)
    st.divider()

    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f"### {TEXT['download'][lang]}")
        base_name = datetime.now().strftime("data_%Y%m%d")
        export_buttons(df, base_name)

    st.markdown("### 📊 Interactive Analysis")

    analysis_option = st.selectbox(
        "Choose analysis",
        [
            "Class performance overview",
            "Score distribution (pass vs fail)",
            "Top performing students",
            "Students at risk",
            "Score relationship (scatter plot)"
        ]
    )

    if analysis_option == "Class performance overview":
        avg_score = df["Final"].mean()
        pass_rate = (df["Final"] >= 5).mean() * 100

        col1, col2 = st.columns(2)
        col1.metric("Average Score", round(avg_score, 2))
        col2.metric("Pass Rate (%)", round(pass_rate, 1))

    elif analysis_option == "Score distribution (pass vs fail)":
        df['Status'] = df['Final'].apply(lambda x: 'Đạt (≥5)' if x >= 5 else 'Chưa đạt (<5)')
        
        fig = px.histogram(
            df,
            x="Final",
            color="Status",
            nbins=20,
            marginal="rug",
            color_discrete_map={'Đạt (≥5)': '#10b981', 'Chưa đạt (<5)': '#ef4444'},
            title="📊 Phân phối điểm số",
            labels={"Final": "Điểm tổng kết", "count": "Số lượng sinh viên"},
            opacity=0.8
        )
        
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Điểm tổng kết",
            yaxis_title="Số lượng sinh viên",
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)", range=[0, 10.5]),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            legend=dict(
                title="",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.5)"
            ),
            hoverlabel=dict(bgcolor="#1e293b", font_size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Điểm trung bình", f"{df['Final'].mean():.2f}")
        with col2:
            st.metric("Điểm cao nhất", f"{df['Final'].max():.2f}")
        with col3:
            st.metric("Điểm thấp nhất", f"{df['Final'].min():.2f}")

    elif analysis_option == "Top performing students":
        mode = st.selectbox("Chọn nhóm", ["Top 10", "Bottom 10"])
        
        if mode == "Top 10":
            data = df.sort_values("Final", ascending=False).head(10)
            st.success(f"🏆 Top 10 sinh viên có điểm cao nhất")
        else:
            data = df.sort_values("Final", ascending=True).head(10)
            st.warning(f"⚠️ Bottom 10 sinh viên có điểm thấp nhất")
        
        st.dataframe(data.iloc[:, 1:], use_container_width=True)

    elif analysis_option == "Students at risk":
        risk = df[df["Final"] < 5]
        st.warning(f"{len(risk)} students at risk")
        st.dataframe(risk.iloc[:, 1:])

    elif analysis_option == "Score relationship (scatter plot)":
        col_x = st.selectbox("Trục X", ["CC", "GK", "TL"])
        col_y = st.selectbox("Trục Y", ["CK", "Final"])
        
        corr = df[col_x].corr(df[col_y])
        
        fig = px.scatter(
            df,
            x=col_x,
            y=col_y,
            color="Final",
            color_continuous_scale="viridis",
            hover_name=df.columns[2],
            trendline="ols",
            trendline_color_override="#f97316",
            title=f"{col_x} vs {col_y} | Hệ số tương quan: {corr:.2f}",
            labels={col_x: col_x, col_y: col_y, "Final": "Điểm TB"}
        )
        
        fig.update_traces(
            marker=dict(
                size=10,
                opacity=0.7,
                line=dict(width=1, color="white")
            ),
            selector=dict(mode='markers')
        )
        
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=col_x,
                gridcolor="rgba(255,255,255,0.1)",
                zeroline=False,
                range=[0, 10.5]
            ),
            yaxis=dict(
                title=col_y,
                gridcolor="rgba(255,255,255,0.1)",
                zeroline=False,
                range=[0, 10.5]
            ),
            hoverlabel=dict(bgcolor="#1e293b", font_size=12),
            coloraxis_colorbar=dict(
                title="Điểm TB",
                title_font=dict(color="white"),
                tickfont=dict(color="white")
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        if corr > 0.7:
            st.success(f"✅ Tương quan rất mạnh giữa {col_x} và {col_y}")
        elif corr > 0.4:
            st.info(f"📈 Tương quan trung bình giữa {col_x} và {col_y}")
        else:
            st.warning(f"⚠️ Tương quan yếu giữa {col_x} và {col_y}")
    

with tab2:
    st.subheader("Boxplot Analysis")

    col_x = st.selectbox("X (Category)", df.columns)
    col_y = st.selectbox("Y (Value)", df.columns)

    if col_x and col_y:
        create_chart(f"boxplot {col_x} {col_y}", df)


with tab3:
    st.header("About")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)

    with col2:
        st.write("""
        ### Your Name

        Project:
        - Convert PDF → Data
        - Interactive charts
        - Data analysis dashboard

        Teacher: Your Teacher Name
        """)