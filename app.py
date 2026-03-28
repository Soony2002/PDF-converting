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

    # DOWNLOAD + CONTROL
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

    numeric_cols = df.select_dtypes(include='number').columns
    df["Average"] = df[numeric_cols].mean(axis=1)

    if analysis_option == "Class performance overview":

        avg_score = df["Average"].mean()
        pass_rate = (df["Average"] >= 5).mean() * 100

        col1, col2 = st.columns(2)

        col1.metric("Average Score", round(avg_score, 2))
        col2.metric("Pass Rate (%)", round(pass_rate, 1))
    elif analysis_option == "Score distribution (pass vs fail)":

        fig = px.histogram(
            df,
            x="Average",
            nbins=10,
            title="Score Distribution",
            color_discrete_sequence=["#6366f1"]
        )

        fig.update_layout(
            template="plotly_dark",
            bargap=0.1
        )

        st.plotly_chart(fig, use_container_width=True)
    elif analysis_option == "Top performing students":

        mode = st.selectbox(
            "Select group",
            ["Top 10", "Bottom 10"]
        )

        if mode == "Top 10":
            data = df.sort_values("Average", ascending=False).head(10)
            title = "🏆 Top 10 Students"
        else:
            data = df.sort_values("Average", ascending=True).head(10)
            title = "⚠️ Bottom 10 Students"

        fig = px.bar(
            data,
            x="Average",
            y=data.columns[1],
            orientation='h',
            color="Average",
            text="Average",
            title=title,
            color_continuous_scale="viridis"
        )

        fig.update_traces(
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Score: %{x:.2f}<extra></extra>"
        )

        fig.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_title="Average Score",
            yaxis_title="Student",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=50, r=50, t=50, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)
    elif analysis_option == "Students at risk":

        risk = df[df["Average"] < 5]

        st.warning(f"{len(risk)} students at risk")

        st.dataframe(risk)
    elif analysis_option == "Score relationship (scatter plot)":

        st.markdown("### 📈 Score Relationship Analysis")

        col_x = st.selectbox("X axis", ["CC", "GK", "TL"])
        col_y = st.selectbox("Y axis", ["CK", "Final"])

        fig = px.scatter(
            df,
            x=col_x,
            y=col_y,
            hover_name=df.columns[1],
        )

        # 🎯 STYLE CHUYÊN NGHIỆP
        fig.update_traces(
            marker=dict(
                size=8,
                color="#6366f1",     # 1 màu clean
                opacity=0.6,
                line=dict(width=0)   # bỏ viền
            ),
            hovertemplate=
            "<b>%{hovertext}</b><br>" +
            f"{col_x}: %{{x}}<br>" +
            f"{col_y}: %{{y}}<extra></extra>"
        )

        fig.update_layout(
            height=500,
            title=f"{col_x} vs {col_y}",
            title_x=0.5,

            # ❌ bỏ nền xám xấu
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",

            # ❌ bỏ legend
            showlegend=False,

            # 🎯 grid nhẹ
            xaxis=dict(
                title=col_x,
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False
            ),
            yaxis=dict(
                title=col_y,
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False
            ),
        )

        st.plotly_chart(fig, use_container_width=True)
    

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