import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from io import BytesIO

from src.pdf_parser import extract_pdf_tables
from src.charts import create_chart
from src.export_utils import export_buttons
from src.report_generator import generate_pdf_report
from src.locales import t


# --- HELPER FUNCTION FOR REPORT ---
def render_report_section(df, unique_id, lang="EN"):
    st.markdown("---")
    st.markdown(f"### {t('export_title', lang)}")
    
    try:
        report_data = generate_pdf_report(df, lang)
        
        # If the report comes back as a bytearray, convert to bytes.
        # If it's a string, encode to bytes.
        if isinstance(report_data, bytearray):
            report_data = bytes(report_data)
        elif isinstance(report_data, str):
            report_data = report_data.encode('latin-1')
            
        st.download_button(
            label=t("download_pdf_btn", lang),
            data=report_data, 
            file_name="Grade_Analysis_Report.pdf",
            mime="application/pdf",
            key=f"report_btn_{unique_id}" # Using the unique_id passed to the function
        )
    except Exception as e:
        st.error(f"{t('error_gen_pdf', lang)} {e}")


# ===== CONFIG =====
st.set_page_config(page_title="DA Dashboard", layout="wide")

# Determine language early
if "lang" not in st.session_state:
    st.session_state.lang = "VI"

# ===== SIDEBAR (Define lang first) =====
st.sidebar.markdown("<img src='https://hub.edu.vn/static/_admin/images/logologin.png' class='sidebar-logo' />", unsafe_allow_html=True)

lang_choice = st.sidebar.selectbox("Language / Ngôn ngữ", ["English", "Tiếng Việt"], index=1 if st.session_state.lang == "VI" else 0)
lang = "VI" if lang_choice == "Tiếng Việt" else "EN"
st.session_state.lang = lang

st.sidebar.markdown(f"""
<div class="system-status">
    <span></span> {t("sys_status", lang)}
</div>
<div style="color: #64748b; font-size: 0.75rem; margin-top: 0.5rem; padding-left: 1rem;">
    {t("sys_version", lang)}
</div>
""", unsafe_allow_html=True)


# ===== LOAD CSS =====
def load_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ===== INSIGHT SYSTEM =====
def generate_insights(df, lang, col=None, col_x=None, col_y=None):
    insights = []

    if col:
        mean = df[col].mean()
        median = df[col].median()
        std = df[col].std()
        skew = df[col].skew()
        min_val = df[col].min()
        max_val = df[col].max()

        if lang == "VI":
            insights.append(f"Điểm trung bình: {mean:.2f}, trung vị: {median:.2f}")
        else:
            insights.append(f"Average: {mean:.2f}, Median: {median:.2f}")

        if std > 2:
            insights.append(t("insight_spread", lang))
        else:
            insights.append(t("insight_focused", lang))

        if skew > 0.5:
            insights.append(t("insight_skew_right", lang))
        elif skew < -0.5:
            insights.append(t("insight_skew_left", lang))

        if max_val >= 9:
            insights.append(t("insight_high_score", lang))
        if min_val < 3:
            insights.append(t("insight_low_score", lang))

    if col_x and col_y:
        corr = df[col_x].corr(df[col_y])
        if lang == "VI":
            insights.append(f"Tương quan giữa {col_x} và {col_y}: {corr:.2f}")
        else:
            insights.append(f"Correlation between {col_x} and {col_y}: {corr:.2f}")

        if corr > 0.7:
            insights.append(t("corr_strong", lang))
        elif corr > 0.4:
            insights.append(t("corr_medium", lang))
        else:
            insights.append(t("corr_weak", lang))

    return insights

def render_report(insights, lang, extra_text=None):
    st.markdown(f"<div class='sub-title' style='margin-bottom: 0.5rem;'>{t('report_title', lang)}</div>", unsafe_allow_html=True)
    for i in insights:
        st.info(f"**{i}**", icon="💡")

    if extra_text:
        st.success(f"**{extra_text}**", icon="🎯")


# ===== MAIN =====
st.markdown(f'<div class="main-title">{t("main_title", lang)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{t("main_subtitle", lang)}</div>', unsafe_allow_html=True)

# ===== MAIN APP & LANDING PAGE =====

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if not st.session_state.uploaded_file:
    # ---------------------------------------------
    # Welcome Landing Page (Empty State)
    # ---------------------------------------------
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 0.5rem; font-size: 2.5rem;'>{t('landing_title', lang)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #94a3b8; max-width: 600px; margin: 0 auto 3rem auto; font-size: 1.1rem;'>{t('landing_subtitle', lang)}</p>", unsafe_allow_html=True)
    
    # 3-Column Feature Cards
    fc1, fc2, fc3 = st.columns(3)
    
    with fc1:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">{t("feat_1_title", lang)}</div>
            <div class="feature-desc">{t("feat_1_desc", lang)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with fc2:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">{t("feat_2_title", lang)}</div>
            <div class="feature-desc">{t("feat_2_desc", lang)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with fc3:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">{t("feat_3_title", lang)}</div>
            <div class="feature-desc">{t("feat_3_desc", lang)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.info("👇 " + t("upload_pdf", lang))
    uploaded_file = st.file_uploader(
        "",
        type=["pdf"],
        accept_multiple_files=True
    )
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.rerun()
    else:
        st.stop()

# ===== DASHBOARD RENDER =====
uploaded_file = st.session_state.uploaded_file
st.title("📊 PDF Data Dashboard")
if st.button("Clear Data"):
    st.session_state.uploaded_file = None
    st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ===== PROCESS PDF =====
with st.spinner(t("processing_pdf", lang)):
    df = extract_pdf_tables(uploaded_file)

if df is None:
    st.error(t("no_table_error", lang))
    st.stop()


# ===== TABS =====
tab1, tab2, tab3 = st.tabs([
    t("tab1", lang),
    t("tab2", lang),
    t("tab3", lang)
])

# ================= TAB 1 =================
with tab1:

    # ===== DATA CLEANING SUMMARY =====
    clean_html = f"""
    <div class='card'>
    <h3>{t("data_clean_title", lang)}</h3>
    <p>- {t("rows", lang)}: {len(df)}</p>
    <p>- {t("cols", lang)}: {df.shape[1]}</p>
    <p>- {t("missing", lang)}: {df.isna().sum().sum()}</p>
    </div>
    """

    st.markdown(clean_html, unsafe_allow_html=True)

    st.subheader(t("data_preview", lang))
    st.dataframe(df, use_container_width=True)

    st.divider()

    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f"### {t('download_title', lang)}")
        base_name = datetime.now().strftime("data_%Y%m%d")
        export_buttons(df, base_name)

    st.markdown(f"<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>{t('interactive_analysis', lang)}</h3>", unsafe_allow_html=True)

    options_map = {
        t("opt_overview", lang): "Class performance overview",
        t("opt_dist", lang): "Score distribution",
        t("opt_top", lang): "Top performing students",
        t("opt_risk", lang): "Students at risk",
        t("opt_rel", lang): "Score relationship"
    }

    selected_label = st.radio(
        t("analysis_view", lang),
        list(options_map.keys()),
        horizontal=True,
        label_visibility="collapsed"
    )
    analysis_option = options_map[selected_label]
    
    st.write("") # spacing
    # ===== CLASS OVERVIEW =====
    if analysis_option == "Class performance overview":
        avg_score = df["Final"].mean()
        pass_rate = (df["Final"] >= 5).mean() * 100
        total = len(df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(t("metric_avg", lang), f"{avg_score:.2f}")

        with col2:
            st.metric(t("metric_pass", lang), f"{pass_rate:.1f}%")

        with col3:
            st.metric(t("metric_total", lang), f"{total}")


    # ===== DISTRIBUTION =====
    elif analysis_option == "Score distribution":
        df['Status'] = df['Final'].apply(
            lambda x: t("status_pass", lang) if x >= 5 else t("status_fail", lang)
        )

        fig = px.histogram(
            df,
            x="Final",
            color="Status",
            nbins=20,
            opacity=0.8
        )
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", family="Inter"),
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===== REPORT =====
        insights = generate_insights(df, lang, col="Final")
        render_report(insights, lang, t("insight_dist", lang))

    # ===== TOP STUDENTS =====
    elif analysis_option == "Top performing students":
        mode = st.selectbox(t("select_group", lang), ["Top 10", "Bottom 10"])

        if mode == "Top 10":
            data = df.sort_values("Final", ascending=False).head(10)
            st.success(t("top_10_title", lang))
        else:
            data = df.sort_values("Final", ascending=True).head(10)
            st.warning(t("bot_10_title", lang))

        st.dataframe(data.iloc[:, 1:], use_container_width=True)

        insights = [
            t("insight_top_1", lang),
            t("insight_top_2", lang)
        ]

        render_report(insights, lang)

    # ===== AT RISK =====
    elif analysis_option == "Students at risk":
        risk = df[df["Final"] < 5]

        st.warning(f"{len(risk)} {t('risk_title', lang)}")
        st.dataframe(risk.iloc[:, 1:])

        insights = [
            f"{len(risk)} {t('risk_title', lang)}",
            t("insight_risk_1", lang)
        ]

        render_report(insights, lang)

    # ===== SCATTER =====
    elif analysis_option == "Score relationship":
        col_x = st.selectbox(t("axis_x", lang), ["CC", "GK", "TL"])
        col_y = st.selectbox(t("axis_y", lang), ["CK", "Final"])

        corr = df[col_x].corr(df[col_y])

        fig = px.scatter(
            df,
            x=col_x,
            y=col_y,
            color="Final",
            trendline="ols",
            title=f"{col_x} vs {col_y} | Corr: {corr:.2f}"
        )
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", family="Inter"),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===== REPORT =====
        insights = generate_insights(df, lang, col_x=col_x, col_y=col_y)
        render_report(insights, lang)
        
    render_report_section(df, "tab1", lang)


# ================= TAB 2 =================
with tab2:
    st.markdown(f"<h3 style='margin-bottom: 1rem;'>{t('boxplot_title', lang)}</h3>", unsafe_allow_html=True)
    
    with st.expander(t("boxplot_help_title", lang) + " 👈", expanded=False):
        st.markdown(t("boxplot_help_text", lang))

    bp_options = {
        t("boxplot_opt_class", lang): "class_compare",
        t("boxplot_opt_comp", lang): "comp_compare"
    }

    bp_choice_label = st.radio(
        t("boxplot_objective", lang),
        list(bp_options.keys()),
        horizontal=True
    )
    bp_choice = bp_options[bp_choice_label]

    if bp_choice == "class_compare":
        if "Class" in df.columns and "Final" in df.columns:
            fig = px.box(
                df, 
                x="Class", 
                y="Final", 
                color="Class",
                title="Phân bố Điểm Tổng Kết theo Lớp" if lang == "VI" else "Final Score Distribution by Class"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", family="Inter"),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Insights logic
            insights = []
            stats = df.groupby("Class")["Final"].describe()
            
            # Calculate IQR
            iqrs = stats['75%'] - stats['25%']
            medians = stats['50%']
            
            min_iqr_cls = iqrs.idxmin()
            max_iqr_cls = iqrs.idxmax()
            best_median_cls = medians.idxmax()
            
            insights.append(t("insight_bp_iqr_min", lang).format(cls=min_iqr_cls, iqr=iqrs[min_iqr_cls]))
            insights.append(t("insight_bp_iqr_max", lang).format(cls=max_iqr_cls, iqr=iqrs[max_iqr_cls]))
            insights.append(t("insight_bp_median", lang).format(cls=best_median_cls))
            
            # Count low outliers overall (e.g. Final < 3)
            low_outliers = len(df[df["Final"] < 3])
            if low_outliers > 0:
                insights.append(t("insight_bp_outliers", lang).format(count=low_outliers))
            
            render_report(insights, lang)
        else:
            st.warning("Data lacks 'Class' or 'Final' columns.")

    elif bp_choice == "comp_compare":
        # Check which components exist
        comp_cols = [c for c in ["CC", "GK", "TL", "CK"] if c in df.columns]
        if comp_cols:
            df_melted = df.melt(value_vars=comp_cols, var_name="Component", value_name="Score")
            fig = px.box(
                df_melted, 
                x="Component", 
                y="Score", 
                color="Component",
                title="So sánh các Thành phần Điểm" if lang == "VI" else "Component Scores Comparison"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", family="Inter"),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Insights
            insights = []
            stats = df[comp_cols].describe().T
            hardest_comp = stats['50%'].idxmin()
            
            insights.append(t("insight_bp_comp_hard", lang).format(col=hardest_comp))
            
            render_report(insights, lang)
        else:
            st.warning("Data does not contain component scores (CC, GK, TL, CK).")
    
# ================= TAB 3 =================
with tab3:
    st.header(t("about_title", lang))

    st.write(t("about_text", lang))