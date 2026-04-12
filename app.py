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

lang_choice = st.sidebar.selectbox(t("lang_select", st.session_state.lang), ["English", "Tiếng Việt"], index=1 if st.session_state.lang == "VI" else 0)
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

# Footer
# Spacer (đẩy xuống đáy)
st.sidebar.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

# Divider
st.sidebar.markdown("---")

st.sidebar.markdown(
f"""
<div style="text-align:center">

👨‍💻 <b>{t("built_by", lang)}</b><br>
<a href="https://github.com/SonnyDuck" target="_blank" style="text-decoration:none; color:white;">
SoonyDuck 🦆
</a>

<img src="https://unpkg.com/simple-icons@v9/icons/github.svg" alt="GitHub"
     style="width:120px;">
<br><br>

<a href="https://github.com/SonnyDuck" target="_blank">
🔗 GitHub
</a> |
<a href="https://github.com/SonnyDuck/PDF-converting" target="_blank">
📂 {t("project", lang)}
</a>

</div>
""",
unsafe_allow_html=True
)

# ===== MAIN CONTENT =====
def load_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


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
    
    st.info(t("upload_prompt", lang))
    uploaded_file = st.file_uploader(
        t("upload_pdf", lang),
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
st.title(t("page_title", lang))
st.markdown(t("page_subtitle", lang), unsafe_allow_html=True)
if st.button(t("clear_data", lang)):
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

# Clean text format (remove newlines from PDF parsing to prevent CSV breakages and bad PDF formating)
for col in df.select_dtypes(include=["object"]):
    df[col] = df[col].astype(str).str.replace(r'\n|\r', ' ', regex=True).str.replace('  ', ' ').str.strip()

COL_CC = "Chuyên cần"
COL_GK = "Giữa kỳ"
COL_TL = "Tiểu luận"
COL_CK = "Cuối kỳ"
COL_FINAL = "Điểm tổng hợp"

# Rename columns immediately
rename_map = {
    "CC": COL_CC,
    "GK": COL_GK,
    "TL": COL_TL,
    "CK": COL_CK,
    "Final": COL_FINAL
}
df.rename(columns=rename_map, inplace=True)


def localize_col_name(col, lang):
    label_map = {
        "MSSV": {"VI": "MSSV", "EN": "Student ID"},
        "Name": {"VI": "Họ và Tên", "EN": "Name"},
        "Class": {"VI": "Lớp", "EN": "Class"},
        COL_CC: {"VI": COL_CC, "EN": "Attendance"},
        COL_GK: {"VI": COL_GK, "EN": "Midterm"},
        COL_TL: {"VI": COL_TL, "EN": "Essay"},
        COL_CK: {"VI": COL_CK, "EN": "Final"},
        COL_FINAL: {"VI": COL_FINAL, "EN": "Final Score"},
        "Grade": {"VI": "Xếp loại", "EN": "Grade"},
        "CK_sim": {"VI": "CK mô phỏng", "EN": "CK Sim"},
        "Final_sim": {"VI": "Điểm tổng hợp mô phỏng", "EN": "Final Sim"}
    }
    return label_map.get(col, {}).get(lang, col)


def localize_df_columns(df_obj, lang):
    return df_obj.rename(columns=lambda c: localize_col_name(c, lang))


def classify_grade(score, lang):
    if pd.isna(score): return "Fail" if lang == "EN" else "Yếu/Kém"
    if score >= 9: return "Excellent" if lang == "EN" else "Xuất sắc"
    elif score >= 8: return "Good" if lang == "EN" else "Giỏi"
    elif score >= 6.5: return "Fair" if lang == "EN" else "Khá"
    elif score >= 5: return "Average" if lang == "EN" else "Trung bình"
    else: return "Fail" if lang == "EN" else "Yếu/Kém"

df["Grade"] = df[COL_FINAL].apply(lambda x: classify_grade(x, lang))

# ===== TABS =====
tab1, tab2, tab3 = st.tabs([
    f"📊 {t('tab1', lang)}",
    f"📈 {t('tab2', lang)}",
    f"🎯 {t('tab3', lang)}"
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
    st.dataframe(localize_df_columns(df, lang), use_container_width=True)

    st.divider()

    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f"### {t('download_title', lang)}")
        base_name = datetime.now().strftime("data_%Y%m%d")
        export_buttons(df, base_name)

# ================= TAB 2 =================
with tab2:
    st.markdown("### 🎛️ Bộ Lọc Dữ Liệu (Filters)" if lang=="VI" else "### 🎛️ Data Filters")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    # We display short class names in the filter, but map them back to global df
    short_to_long_class = {str(x).split('_')[-1]: x for x in df['Class'].dropna().unique()}
    unique_classes_short = sorted(short_to_long_class.keys())
    
    unique_grades = sorted(df['Grade'].dropna().unique())
    min_score = float(df[COL_FINAL].min(skipna=True)) if not df[COL_FINAL].isna().all() else 0.0
    max_score = float(df[COL_FINAL].max(skipna=True)) if not df[COL_FINAL].isna().all() else 10.0
    min_score, max_score = min(0.0, min_score), max(10.0, max_score)
    
    with f_col1:
        selected_classes_short = st.multiselect(t("filter_class", lang), unique_classes_short, default=[])
    with f_col2:
        selected_grades = st.multiselect(t("filter_grade", lang), unique_grades, default=[])
    with f_col3:
        score_range = st.slider(t("filter_score", lang), 0.0, 10.0, (0.0, 10.0), 0.1)
        
    if not selected_classes_short:
        selected_classes_short = unique_classes_short
    if not selected_grades:
        selected_grades = unique_grades

    selected_classes_long = [short_to_long_class[s] for s in selected_classes_short]

    # Filter global df
    df = df[
        (df[COL_FINAL].isna() | ((df[COL_FINAL] >= score_range[0]) & (df[COL_FINAL] <= score_range[1]))) & 
        (df['Grade'].isin(selected_grades)) & 
        (df['Class'].isin(selected_classes_long))
    ]
    
    # Tab 2 visualization uses short class names
    df_tab2 = df.copy()
    if 'Class' in df_tab2.columns:
        df_tab2['Class'] = df_tab2['Class'].apply(lambda x: str(x).split('_')[-1] if pd.notna(x) else x)
    
    if len(df_tab2) == 0:
        st.warning("Không có dữ liệu phù hợp với bộ lọc." if lang == "VI" else "No data matching filters.")
    else:
        st.markdown(f"### {t('sec_kpi', lang)}")
        avg_score = df_tab2[COL_FINAL].mean()
        pass_rate = (df_tab2[COL_FINAL] >= 5).mean() * 100
        total = len(df_tab2)

        def calc_gpa(score):
            if score >= 9.5: return 4.0
            elif score >= 9.0: return 3.7
            elif score >= 8.5: return 3.4
            elif score >= 8.0: return 3.2
            elif score >= 7.5: return 3.0
            elif score >= 7.0: return 2.8
            elif score >= 6.5: return 2.6
            elif score >= 6.0: return 2.4
            elif score >= 5.5: return 2.2
            elif score >= 5.0: return 2.0
            elif score >= 4.5: return 1.8
            elif score >= 4.0: return 1.6
            else: return 0

        gpa_avg = df_tab2[COL_FINAL].apply(calc_gpa).mean()

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric(t("metric_avg", lang), f"{avg_score:.2f}")
        kpi2.metric("GPA trung bình (hệ 4)" if lang == "VI" else "Avg GPA (4.0)", f"{gpa_avg:.2f}")
        kpi3.metric(t("metric_pass", lang), f"{pass_rate:.1f}%")
        kpi4.metric(t("metric_total", lang), f"{total}")
        kpi5.metric(t("metric_excellent", lang), f"{(df_tab2[COL_FINAL] >= 8).sum()}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- TOP 2 CHARTS ---
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("### Phân phối điểm" if lang=="VI" else "### Score Distribution")
            with st.expander("Hướng dẫn đọc biểu đồ" if lang=="VI" else "How to read this chart"):
                st.write("Biểu đồ cột chồng thể hiện phân bố điểm số thành từng phân khúc. Giúp so sánh tỷ trọng khối lượng sinh viên đạt chuẩn ở các lớp." if lang=="VI" else "Stacked bar chart showing grade density explicitly.")
            df_hist = df_tab2.copy()
            df_hist['ScoreRange'] = pd.cut(df_hist[COL_FINAL], bins=[-1, 3.99, 4.99, 6.49, 7.99, 10], labels=["<4", "4-5", "5-6.5", "6.5-8", "8-10"])
            dist_data = df_hist.groupby(["ScoreRange", "Class"]).size().reset_index(name="Count")
            fig_stack = px.bar(
                dist_data,
                x="ScoreRange",
                y="Count",
                color="Class",
                barmode="stack",
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={
                    "ScoreRange": t("label_score_range", lang),
                    "Count": t("label_count", lang),
                    "Class": localize_col_name("Class", lang)
                }
            )
            st.plotly_chart(fig_stack, use_container_width=True)
            if not dist_data.empty:
                total_students = dist_data["Count"].sum()
                bucket_counts = dist_data.groupby("ScoreRange")["Count"].sum()
                top_bucket = bucket_counts.idxmax()
                top_pct = (bucket_counts.max() / total_students * 100)
                low_bucket = bucket_counts[bucket_counts.index.str.contains("<4|4-5")].sum()
                low_pct = (low_bucket / total_students * 100)
                if lang == "VI":
                    insight = f"💡 Phân bố điểm tập trung chủ yếu ở nhóm {top_bucket} ({top_pct:.1f}%). "
                    if low_pct > 20:
                        insight += f"Đáng chú ý, có {low_pct:.1f}% sinh viên ở mức dưới trung bình, cho thấy cần cải thiện chất lượng giảng dạy hoặc hỗ trợ học sinh yếu."
                    else:
                        insight += "Phân bố khá đồng đều, phản ánh chất lượng đào tạo ổn định."
                    st.info(insight, icon="💡")
                else:
                    insight = f"💡 Score distribution is concentrated in {top_bucket} ({top_pct:.1f}%). "
                    if low_pct > 20:
                        insight += f"Notably, {low_pct:.1f}% of students are below average, suggesting need for teaching improvements or student support."
                    else:
                        insight += "Distribution is fairly balanced, indicating consistent educational quality."
                    st.info(insight, icon="💡")

        with col_c2:
            st.markdown("### Phân loại Sinh viên" if lang=="VI" else "### Student Classification")
            with st.expander("Hướng dẫn đọc biểu đồ" if lang=="VI" else "How to read this chart"):
                st.write("Cụm biểu đồ thể hiện sự chênh lệch quy mô học thuật theo danh hiệu từng lớp, cho phép đối chiếu mức độ Giỏi/Khá/TB." if lang=="VI" else "Grouped bars showing comparative competence across classes.")
            grade_class_dist = df_tab2.groupby(['Class', 'Grade']).size().reset_index(name='Count')
            cat_orders = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu/Kém"] if lang == "VI" else ["Excellent", "Good", "Fair", "Average", "Fail"]
            fig_grouped = px.bar(
                grade_class_dist,
                x="Class",
                y="Count",
                color="Grade",
                barmode="group",
                color_discrete_sequence=["#0ea5e9", "#2563eb", "#1e3a8a", "#64748b", "#cbd5e1"],
                category_orders={"Grade": cat_orders},
                labels={
                    "Class": localize_col_name("Class", lang),
                    "Count": t("label_count", lang),
                    "Grade": localize_col_name("Grade", lang)
                }
            )
            st.plotly_chart(fig_grouped, use_container_width=True)
            if not grade_class_dist.empty:
                total_students = grade_class_dist["Count"].sum()
                grade_counts = grade_class_dist.groupby("Grade")["Count"].sum()
                top_grade = grade_counts.idxmax()
                top_pct = (grade_counts.max() / total_students * 100)
                fail_pct = grade_counts.get("Yếu/Kém" if lang == "VI" else "Fail", 0) / total_students * 100
                excellent_pct = grade_counts.get("Xuất sắc" if lang == "VI" else "Excellent", 0) / total_students * 100
                if lang == "VI":
                    insight = f"💡 Học lực chủ yếu tập trung ở '{top_grade}' ({top_pct:.1f}%). "
                    if fail_pct > 15:
                        insight += f"Tỷ lệ rớt môn cao ({fail_pct:.1f}%), cần xem xét lại phương pháp giảng dạy hoặc đề thi."
                    elif excellent_pct > 20:
                        insight += f"Chất lượng đào tạo xuất sắc với {excellent_pct:.1f}% sinh viên đạt xuất sắc."
                    else:
                        insight += "Phân bố học lực tương đối cân bằng giữa các lớp."
                    st.info(insight, icon="💡")
                else:
                    insight = f"💡 Academic performance is mainly concentrated in '{top_grade}' ({top_pct:.1f}%). "
                    if fail_pct > 15:
                        insight += f"High failure rate ({fail_pct:.1f}%), suggesting need to review teaching methods or exam difficulty."
                    elif excellent_pct > 20:
                        insight += f"Excellent educational quality with {excellent_pct:.1f}% students achieving excellence."
                    else:
                        insight += "Grade distribution is relatively balanced across classes."
                    st.info(insight, icon="💡")
            
        # --- BOTTOM 2 CHARTS ---
        st.markdown("<br>", unsafe_allow_html=True)
        col_c3, col_c4 = st.columns(2)
        with col_c3:
            st.markdown("### Biểu đồ phân tán (Boxplot)" if lang=="VI" else "### Boxplot")
            with st.expander("Hướng dẫn đọc biểu đồ" if lang=="VI" else "How to read this chart"):
                st.write("Thùng (box) chứa 50% lượng sinh viên phổ biến nhất.\n- **Đường ngang giữa Box**: Điểm trung vị (Median).\n- **Hai biên của Box**: Phân vị thứ 75 (Q3) và 25 (Q1).\n- **Đường gạch trên/dưới (Upper/Lower fence)**: Giới hạn điểm phân bố thông thường.\n- **Các dấu chấm lơ lửng**: Các điểm ngoại lai (Outliers) có điểm số quá cao hoặc quá thấp bất thường." if lang=="VI" else "Boxplot demonstrating standard deviation mapping.")
            fig_box = px.box(
                df_tab2,
                x="Class",
                y=COL_FINAL,
                color="Class",
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={
                    "Class": localize_col_name("Class", lang),
                    COL_FINAL: localize_col_name(COL_FINAL, lang)
                }
            )
            st.plotly_chart(fig_box, use_container_width=True)
            if not df_tab2.empty:
                class_stats = df_tab2.groupby("Class")[COL_FINAL].describe()
                best_class = class_stats["50%"].idxmax()
                worst_class = class_stats["50%"].idxmin()
                total_outliers = 0
                for cls in df_tab2["Class"].unique():
                    cls_data = df_tab2[df_tab2["Class"] == cls][COL_FINAL].dropna()
                    if len(cls_data) > 0:
                        q1 = cls_data.quantile(0.25)
                        q3 = cls_data.quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        outliers = cls_data[(cls_data < lower_bound) | (cls_data > upper_bound)]
                        total_outliers += len(outliers)
                if lang == "VI":
                    insight = f"💡 Lớp {best_class} có điểm trung vị cao nhất, {worst_class} thấp nhất. "
                    if total_outliers > 0:
                        insight += f"Có {total_outliers} điểm ngoại lai, cho thấy sự bất thường trong phân bố điểm số."
                    else:
                        insight += "Không có điểm ngoại lai, phân bố điểm khá đồng đều."
                    st.info(insight, icon="💡")
                else:
                    insight = f"💡 Class {best_class} has the highest median score, {worst_class} the lowest. "
                    if total_outliers > 0:
                        insight += f"There are {total_outliers} outliers, indicating anomalies in score distribution."
                    else:
                        insight += "No outliers detected, score distribution is fairly consistent."
                    st.info(insight, icon="💡")

        with col_c4:
            st.markdown("### Tương quan điểm (Scatter Plot)" if lang=="VI" else "### Component Score Correlation")
            with st.expander("Hướng dẫn đọc biểu đồ" if lang=="VI" else "How to read this chart"):
                st.write("Đánh giá độ tuyến tính: Nếu điểm rải theo đường chéo đứt nét thì hệ số ổn định tốt. Chấm đỏ là những trường hợp có điểm thành phần/cuối kỳ đánh lừa hệ thống. Tự do thay đổi lớp để xem độ phân tán cụ thể ít chồng chéo." if lang=="VI" else "Scatter plot assessing component score relationships vs final outcomes for specific class.")
            comp_cols = [COL_CC, COL_GK, COL_TL, COL_CK]
            available_cols = [c for c in comp_cols if c in df_tab2.columns]
            if available_cols and COL_FINAL in df_tab2.columns:
                sc_col1, sc_col2 = st.columns(2)
                with sc_col1:
                    col_x = st.selectbox(t("chart_scatter_sel", lang), available_cols, index=0, key="scatter_cl_x")
                with sc_col2:
                    cls_list = df_tab2['Class'].dropna().unique().tolist()
                    sc_class = st.selectbox("Chọn lớp:" if lang=="VI" else "Select Class:", cls_list, key="scatter_cl_c")
                
                df_scatter = df_tab2[df_tab2['Class'] == sc_class].copy()
                valid_idx = df_scatter[col_x].notna() & df_scatter[COL_FINAL].notna()
                trendline_dict = {}
                if valid_idx.sum() > 5:
                    import numpy as np
                    x_val = df_scatter.loc[valid_idx, col_x].astype(float)
                    y_val = df_scatter.loc[valid_idx, COL_FINAL].astype(float)
                    try:
                        poly = np.polyfit(x_val, y_val, 1)
                        y_pred = poly[0] * x_val + poly[1]
                        residuals = np.abs(y_val - y_pred)
                        threshold = np.nanpercentile(residuals, 95) if len(residuals) > 0 else 0
                        df_scatter['Outlier'] = False
                        df_scatter.loc[valid_idx, 'Outlier'] = residuals > threshold
                        
                        sort_idx = np.argsort(x_val)
                        trendline_dict = {'x': x_val.iloc[sort_idx], 'y': y_pred.iloc[sort_idx]}
                    except:
                        df_scatter['Outlier'] = False
                else:
                    df_scatter['Outlier'] = False
                
                df_scatter['Type'] = df_scatter['Outlier'].map({True: 'Outlier', False: 'Normal'})
                fig_scatter = px.scatter(
                    df_scatter,
                    x=col_x,
                    y=COL_FINAL,
                    color="Type",
                    color_discrete_map={"Normal": "#3b82f6", "Outlier": "#ef4444"},
                    hover_data=["MSSV", "Name", "Class"],
                    labels={
                        col_x: localize_col_name(col_x, lang),
                        COL_FINAL: localize_col_name(COL_FINAL, lang),
                        "Type": t("label_type", lang),
                        "MSSV": localize_col_name("MSSV", lang),
                        "Name": localize_col_name("Name", lang),
                        "Class": localize_col_name("Class", lang)
                    },
                    opacity=0.8
                )
                fig_scatter.update_traces(marker=dict(size=10, line=dict(width=1, color='White')), selector=dict(mode='markers'))
                if trendline_dict:
                    import plotly.graph_objects as go
                    fig_scatter.add_trace(go.Scatter(x=trendline_dict['x'], y=trendline_dict['y'], mode='lines', name='Trendline' if lang == "EN" else 'Đường xu hướng', line=dict(color='orange', width=3, dash='dash')))
                    
                st.plotly_chart(fig_scatter, use_container_width=True)
                if valid_idx.sum() > 1:
                    correlation = round(x_val.corr(y_val), 2)
                    outlier_count = int(df_scatter['Outlier'].sum())
                    if lang == "VI":
                        insight = f"💡 Mối tương quan giữa {localize_col_name(col_x, lang)} và {localize_col_name(COL_FINAL, lang)} là {correlation}. "
                        if correlation > 0.7:
                            insight += "Mối quan hệ mạnh, điểm thành phần dự đoán tốt điểm cuối kỳ. "
                        elif correlation > 0.3:
                            insight += "Mối quan hệ trung bình, cần cải thiện sự ổn định. "
                        else:
                            insight += "Mối quan hệ yếu, cần chú ý yếu tố khác. "
                        if outlier_count > 0:
                            insight += f"Số ngoại lệ: {outlier_count}, có thể là học sinh xuất sắc hoặc cần hỗ trợ."
                        else:
                            insight += "Không có ngoại lệ đáng kể."
                        st.info(insight, icon="💡")
                    else:
                        insight = f"💡 The correlation between {localize_col_name(col_x, lang)} and {localize_col_name(COL_FINAL, lang)} is {correlation}. "
                        if correlation > 0.7:
                            insight += "Strong relationship, component scores predict final scores well. "
                        elif correlation > 0.3:
                            insight += "Moderate relationship, consistency needs improvement. "
                        else:
                            insight += "Weak relationship, other factors may influence scores. "
                        if outlier_count > 0:
                            insight += f"Outliers: {outlier_count}, possibly exceptional students or those needing support."
                        else:
                            insight += "No significant outliers."
                        st.info(insight, icon="💡")
            else:
                st.warning("Không tìm thấy cột điểm thành phần." if lang=="VI" else "Component score columns missing.")

        st.markdown("---")
        st.markdown("### 🏆 Bảng Sinh Viên Thông Minh" if lang=="VI" else "### 🏆 Smart Student Table")
        
        opt_all = "1. Tất cả sinh viên" if lang == "VI" else "1. All Students"
        opt_try = "2. Có sự đột biến trong học tập (GK <= 6 nhưng CK > 8)" if lang == "VI" else "2. Breakthrough (GK <= 6, CK > 8)"
        opt_cc = "3. Đi học nhưng không hiểu bài (Chuyên cần > 8 nhưng Cuối kỳ < 6)" if lang == "VI" else "3. High attendance, poor final (CC > 8, CK < 6)"
        opt_prob = "4. Thi là vấn đề (Điểm quá trình CC, GK, TL >= 8 nhưng cuối kỳ < 6)" if lang == "VI" else "4. Exam issues (Process >= 8, CK < 6)"
        opt_decline = "5. Suy giảm lực học (GK >= 8 nhưng CK <= 6)" if lang == "VI" else "5. Declining performance (GK >= 8, CK <= 6)"
        opt_fail = "6. Rớt môn (Tổng kết < 4)" if lang == "VI" else "6. Failed (Final < 4)"

        smart_option = st.selectbox("📌 Lọc / Highlight theo tiêu chí:" if lang=="VI" else "📌 Filter Highlight Criteria:", [opt_all, opt_try, opt_cc, opt_prob, opt_decline, opt_fail])
        
        columns_to_show = ["STT", "MSSV", "Name", "Class", COL_FINAL, "Grade"]
        for c in [COL_CC, COL_GK, COL_TL, COL_CK]:
            if c in df_tab2.columns and c not in columns_to_show:
                columns_to_show.insert(-2, c)
                
        df_display = df_tab2.copy()
        existing_cols = [c for c in columns_to_show if c in df_display.columns]
        df_display = df_display[existing_cols]
        
        def highlight_smart_table(row):
            styles = [''] * len(row)
            try:
                fin = float(row[COL_FINAL]) if pd.notna(row[COL_FINAL]) else 0.0
                cc = float(row.get(COL_CC, 0)) if COL_CC in row and pd.notna(row[COL_CC]) else 0.0
                gk = float(row.get(COL_GK, 0)) if COL_GK in row and pd.notna(row[COL_GK]) else 0.0
                ck = float(row.get(COL_CK, 0)) if COL_CK in row and pd.notna(row[COL_CK]) else 0.0
                tl = float(row.get(COL_TL, 0)) if COL_TL in row and pd.notna(row[COL_TL]) else 0.0
                
                bg_color = ""
                
                if smart_option == opt_try:
                    if gk <= 6.0 and ck > 8.0: bg_color = "background-color: #d1fae5; color: #065f46; font-weight: bold;"
                elif smart_option == opt_cc:
                    if cc > 8.0 and ck < 6.0: bg_color = "background-color: #fef08a; color: #854d0e; font-weight: bold;"
                elif smart_option == opt_prob:
                    # Điểm quá trình CC, GK, TL >= 8 (TL optional checks) nhưng cuối kỳ < 6
                    proc_good = cc >= 8.0 and gk >= 8.0 and ('TL' not in row or tl >= 8.0)
                    if proc_good and ck < 6.0: bg_color = "background-color: #fed7aa; color: #9a3412; font-weight: bold;"
                elif smart_option == opt_decline:
                    if gk >= 8.0 and ck <= 6.0: bg_color = "background-color: #fca5a5; color: #991b1b; font-weight: bold;"
                elif smart_option == opt_fail:
                    if fin < 4.0: bg_color = "background-color: #f87171; color: #7f1d1d; font-weight: bold;"
                
                if bg_color:
                    return [bg_color] * len(row)
            except:
                pass
            return styles

        # Float formatting logic to format cleanly
        format_dict = {col: "{:.1f}" for col in df_display.select_dtypes(include=['float64', 'float32']).columns}
        
        df_display_renamed = df_display.rename(columns=lambda c: localize_col_name(c, lang))
        styled_df = df_display_renamed.style.apply(highlight_smart_table, axis=1).format(format_dict)
        st.dataframe(styled_df, use_container_width=True)

# ================= TAB 3 =================
with tab3:
    st.markdown(f"### {t('sim_title', lang)}")
    st.write(t("sim_desc", lang))
    
    # Simulate making CK harder, mapping values down
    sim_drop = st.slider(t("sim_slider", lang), min_value=-5.0, max_value=0.0, value=0.0, step=0.5)
    
    if sim_drop < 0 and COL_CK in df.columns:
        df_sim = df.copy()
        df_sim['CK_sim'] = (df_sim[COL_CK] + sim_drop).clip(0, 10)
        # CK takes 50% ratio generally in formula, meaning 5 point drop equals 2.5 final drop
        df_sim['Final_sim'] = (df_sim[COL_FINAL] + sim_drop * 0.5).clip(0, 10)
        
        old_pass = (df[COL_FINAL] >= 5).mean() * 100
        new_pass = (df_sim['Final_sim'] >= 5).mean() * 100
        
        old_avg = df[COL_FINAL].mean()
        new_avg = df_sim['Final_sim'].mean()
        
        col_s1, col_s2 = st.columns(2)
        col_s1.metric(t("sim_kpi_avg", lang), f"{new_avg:.2f}", f"{(new_avg - old_avg):.2f}")
        col_s2.metric(t("sim_kpi_pass", lang), f"{new_pass:.1f}%", f"{(new_pass - old_pass):.1f}%")
        
        st.warning(f"💡 **Insight**: Nếu đề thi khó hơn và giảm {-sim_drop} điểm CK, tỷ lệ qua môn sẽ sụt xuống còn {new_pass:.1f}% (giảm tận {(old_pass - new_pass):.1f}%)!" if lang=="VI" else f"💡 **Insight**: Pass rate drops by {(old_pass - new_pass):.1f}%!")
        
        # Determine who failed because of this drop
        newly_failed = df_sim[(df_sim[COL_FINAL] >= 5) & (df_sim['Final_sim'] < 5)]
        if not newly_failed.empty:
            st.markdown("#### 🚨 Danh sách sinh viên bị ảnh hưởng (Chuyển từ Đậu -> Rớt)" if lang == "VI" else "#### 🚨 Affected Students (Pass -> Fail)")
            affected_cols = ["MSSV", "Name", "Class", COL_CK, "CK_sim", COL_FINAL, "Final_sim"]
            exist_affected = [c for c in affected_cols if c in newly_failed.columns]
            
            format_sim = {col: "{:.1f}" for col in newly_failed[exist_affected].select_dtypes(include=['float64', 'float32']).columns}
            st.dataframe(localize_df_columns(newly_failed[exist_affected], lang).style.format(format_sim), use_container_width=True)
            
    elif sim_drop == 0:
        st.info("👈 Kéo thanh trượt về bên trái để bắt đầu mô phỏng." if lang=="VI" else "👈 Slide left to simulate.")
        
    st.markdown("---")
    
    st.markdown(t("pdf_export_title", lang))
    st.markdown(t("pdf_export_desc", lang))

    col_e1, _ = st.columns([3, 1])
    with col_e1:
        st.markdown(f"**{t('option_1', lang)}**: {t('btn_export_1', lang)}")
        render_report_section(df, "tab3_opt1", lang, metadata=metadata)
        
