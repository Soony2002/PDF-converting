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
def render_report_section(df, unique_id, lang="EN", metadata=None):
    st.markdown("---")
    st.markdown(f"### {t('export_title', lang)}")
    
    try:
        report_data = generate_pdf_report(df, lang, metadata)
        
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

# ===== MAIN CONTENT =====
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
    result = extract_pdf_tables(uploaded_file)

if result is None:
    st.error(t("no_table_error", lang))
    st.stop()

if isinstance(result, tuple):
    df, metadata = result
else:
    df = result
    metadata = {}

def classify_grade(score):
    if pd.isna(score): return t("grade_fail", lang)
    if score >= 9: return t("grade_excel", lang)
    elif score >= 8: return t("grade_good", lang)
    elif score >= 6.5: return t("grade_fair", lang)
    elif score >= 5: return t("grade_avg", lang)
    else: return t("grade_fail", lang)

df["Grade"] = df["Final"].apply(classify_grade)

# Build Sidebar Filters
st.sidebar.markdown(f"<div class='sub-title' style='margin-top: 2rem;'>{t('filter_title', lang)}</div>", unsafe_allow_html=True)

min_score = float(df['Final'].min(skipna=True)) if not df['Final'].isna().all() else 0.0
max_score = float(df['Final'].max(skipna=True)) if not df['Final'].isna().all() else 10.0
min_score, max_score = min(0.0, min_score), max(10.0, max_score)

score_range = st.sidebar.slider(t("filter_score", lang), 0.0, 10.0, (0.0, 10.0), 0.1)

unique_grades = sorted(df['Grade'].dropna().unique())
selected_grades = st.sidebar.multiselect(t("filter_grade", lang), unique_grades, default=[])

unique_classes = sorted(df['Class'].dropna().unique())
selected_classes = st.sidebar.multiselect(t("filter_class", lang), unique_classes, default=[])

if not selected_grades or not selected_classes:
    st.info("👈 Vui lòng tick chọn ít nhất 1 Lớp và 1 Xếp loại trên thanh công cụ để xem dữ liệu." if lang=="VI" else "👈 Please select at least 1 Class and 1 Grade from the sidebar.")
    st.stop()

# Apply Filter
df = df[
    (df['Final'].isna() | ((df['Final'] >= score_range[0]) & (df['Final'] <= score_range[1]))) & 
    (df['Grade'].isin(selected_grades)) & 
    (df['Class'].isin(selected_classes))
]

if len(df) == 0:
    st.warning("Không có dữ liệu phù hợp với bộ lọc." if lang == "VI" else "No data matching filters.")
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

    st.markdown(f"### {t('sec_kpi', lang)}")
    avg_score = df["Final"].mean()
    pass_rate = (df["Final"] >= 5).mean() * 100
    total = len(df)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(t("metric_avg", lang), f"{avg_score:.2f}")
    kpi2.metric(t("metric_pass", lang), f"{pass_rate:.1f}%")
    kpi3.metric(t("metric_total", lang), f"{total}")
    kpi4.metric(t("metric_excellent", lang), f"{(df['Final'] >= 8).sum()}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(f"### 1. Xếp hạng lớp theo Điểm Tổng Kết (Trung Bình)" if lang=="VI" else "### 1. Class Ranking by Final Score")
    with st.expander(t("guide_heading", lang)):
        st.write(t("guide_class_rank", lang))
        
    class_avg_df = df.groupby('Class')['Final'].mean().reset_index().sort_values(by='Final', ascending=False)
    # Highlight top class
    top_class = class_avg_df.iloc[0]['Class'] if len(class_avg_df) > 0 else None
    class_avg_df['Color'] = class_avg_df['Class'].apply(lambda x: '#f59e0b' if x == top_class else '#3b82f6')
    
    fig_rank = px.bar(class_avg_df, x='Class', y='Final', text_auto='.2f', color='Color', color_discrete_map="identity")
    fig_rank.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#f8fafc"))
    st.plotly_chart(fig_rank, use_container_width=True)
    
    if len(class_avg_df) > 0:
        st.success(f"💡 **Insight:** Lớp **{top_class}** đang dẫn đầu với điểm trung bình **{class_avg_df.iloc[0]['Final']:.2f}**." if lang=="VI" else f"💡 **Insight:** Class **{top_class}** leads with an average of **{class_avg_df.iloc[0]['Final']:.2f}**.")
    
    st.markdown("---")
    
    st.markdown(f"### 2. Phân loại Học Lực theo Lớp" if lang=="VI" else "### 2. Grade Classification by Class")
    with st.expander(t("guide_heading", lang)):
        st.write(t("guide_class_grade", lang))
        
    grade_class_dist = df.groupby(['Class', 'Grade']).size().reset_index(name='Count')
    fig_grouped = px.bar(
        grade_class_dist, x="Class", y="Count", color="Grade", barmode="group",
        color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b", "#6366f1", "#8b5cf6"]
    )
    fig_grouped.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#f8fafc"))
    st.plotly_chart(fig_grouped, use_container_width=True)
    
    # Calculate group with highest 'Fail' or 'Excellent'
    try:
        excel_class = grade_class_dist[grade_class_dist['Grade'].str.contains('Xuất sắc|Excellent')].sort_values(by='Count', ascending=False).iloc[0]['Class']
        st.info(f"💡 **Insight:** Lớp **{excel_class}** có số lượng sinh viên Xuất sắc nhiều nhất so với các lớp khác." if lang=="VI" else f"💡 **Insight:** Class **{excel_class}** has the most Excellent students.")
    except:
        pass

# ================= TAB 2 =================
with tab2:
    st.markdown("### Phân tích Phân bố & Sự Lệch Điểm" if lang=="VI" else "### Score Variance & Discrepancies")
    
    with st.expander(t("guide_heading", lang)):
        st.write(t("guide_boxplot", lang))
        
    fig_box = px.box(df, x="Class", y="Final", color="Class", title="Boxplot Điểm Tổng Kết theo Lớp" if lang=="VI" else "Final Score Boxplot")
    fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#f8fafc"))
    st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### Đối chiếu Điểm Thành Phần" if lang=="VI" else "### Component Score Comparison")
    with st.expander(t("guide_heading", lang)):
        st.write(t("guide_scatter", lang))
        
    comp_cols = ["CC", "GK", "TL", "CK"]
    available_cols = [c for c in comp_cols if c in df.columns]
    
    if available_cols:
        col_x = st.selectbox(t("chart_scatter_sel", lang), available_cols, index=len(available_cols)-1)
        
        corr_val = df[col_x].corr(df['Final'])
        fig_scatter = px.scatter(
            df, x=col_x, y="Final", color="Class", trendline="ols",
            title=f"{col_x} vs Final (Corr: {corr_val:.2f})" if pd.notna(corr_val) else f"{col_x} vs Final"
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#f8fafc"))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        if pd.notna(corr_val) and corr_val > 0.8:
            st.success(f"💡 **Insight:** Mức độ tương quan rất mạnh ({corr_val:.2f}), chứng tỏ sinh viên được điểm {col_x} cao thường có điểm Final rất tốt." if lang=="VI" else "💡 **Insight:** High correlation found!")
    else:
        st.warning("Không tìm thấy các cột điểm thành phần." if lang=="VI" else "Component score columns missing.")

    st.markdown("---")
    st.markdown(f"### {t('risk_table_title', lang)}")
    
    risk_df = df[df['Final'].isna() | (df['Final'] <= 1.0)]
    
    if len(risk_df) > 0:
        st.error(f"Phát hiện {len(risk_df)} sinh viên vắng thi hoặc có điểm liệt (<= 1.0).", icon="⚠️")
        st.dataframe(risk_df[["STT", "MSSV", "Name", "Class", "Final", "Grade"]], use_container_width=True)
    else:
        st.success(t("risk_empty", lang), icon="✅")

# ================= TAB 3 =================
with tab3:
    st.markdown(f"### {t('sim_title', lang)}")
    st.write(t("sim_desc", lang))
    
    # Simulate making CK harder, mapping values down
    sim_drop = st.slider(t("sim_slider", lang), min_value=-5.0, max_value=0.0, value=0.0, step=0.5)
    
    if sim_drop < 0 and "CK" in df.columns:
        df_sim = df.copy()
        df_sim['CK_sim'] = (df_sim['CK'] + sim_drop).clip(0, 10)
        # CK takes 50% ratio generally in formula, meaning 5 point drop equals 2.5 final drop
        df_sim['Final_sim'] = (df_sim['Final'] + sim_drop * 0.5).clip(0, 10)
        
        old_pass = (df['Final'] >= 5).mean() * 100
        new_pass = (df_sim['Final_sim'] >= 5).mean() * 100
        
        old_avg = df['Final'].mean()
        new_avg = df_sim['Final_sim'].mean()
        
        col_s1, col_s2 = st.columns(2)
        col_s1.metric(t("sim_kpi_avg", lang), f"{new_avg:.2f}", f"{(new_avg - old_avg):.2f}")
        col_s2.metric(t("sim_kpi_pass", lang), f"{new_pass:.1f}%", f"{(new_pass - old_pass):.1f}%")
        
        st.warning(f"💡 **Insight**: Nếu đề thi khó hơn và giảm {-sim_drop} điểm CK, tỷ lệ qua môn sẽ sụt xuống còn {new_pass:.1f}% (giảm tận {(old_pass - new_pass):.1f}%)!" if lang=="VI" else f"💡 **Insight**: Pass rate drops by {(old_pass - new_pass):.1f}%!")
    elif sim_drop == 0:
        st.info("👈 Kéo thanh trượt về bên trái để bắt đầu mô phỏng." if lang=="VI" else "👈 Slide left to simulate.")
        
    st.markdown("---")
    
    st.markdown("### 🖨️ Phân hệ PDF Export" if lang=="VI" else "### 🖨️ PDF Export Module")
    st.markdown("Chọn 1 trong 2 định dạng xuất (Báo cáo Thô / Báo cáo Chuyên Sâu)")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown(f"**Option 1**: {t('btn_export_1', lang)}")
        render_report_section(df, "tab3_opt1", lang, metadata=metadata)
        
    with col_e2:
        st.markdown(f"**Option 2**: {t('btn_export_2', lang)}")
        # We wrap standard PDF export but can mock a visual metadata drop for chart fallback 
        import json
        st.download_button(
            label="Tải xuống PDF Nhận Xét",
            data=json.dumps({"Sim_Drop": sim_drop, "Total": len(df), "Avg": df['Final'].mean(), "Insights": "Generated insights..."}),
            file_name="Visual_Report_Data.json",
            mime="application/json"
        )
        st.caption("*(Xuất biểu đồ ra PDF cần cấu hình `kaleido`. Hệ thống hiện xuất tệp phân tích Insight JSON)*")