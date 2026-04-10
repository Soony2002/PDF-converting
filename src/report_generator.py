from fpdf import FPDF
import datetime
import pandas as pd
import os

def generate_pdf_report(df, lang="EN", metadata=None):
    from src.locales import t
    pdf = FPDF()
    
    font_dir = os.path.dirname(__file__)
    pdf.add_font("Roboto", "", os.path.join(font_dir, "Roboto-Regular.ttf"))
    pdf.add_font("Roboto", "B", os.path.join(font_dir, "Roboto-Bold.ttf"))
    
    pdf.add_page()
    
    # ================= 1. HEADER (2 Cột giống bản gốc) =================
    pdf.set_font("Roboto", "", 10)
    pdf.cell(95, 6, "NGÂN HÀNG NHÀ NƯỚC VIỆT NAM", align="C")
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(95, 6, "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", ln=True, align="C")
    
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(95, 6, "TRƯỜNG ĐẠI HỌC NGÂN HÀNG TP.HCM", align="C")
    pdf.cell(95, 6, "Độc lập - Tự do - Hạnh phúc", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Roboto", "B", 14)
    pdf.cell(0, 10, "BẢNG ĐIỂM HỌC PHẦN", ln=True, align="C")
    pdf.ln(2)

    # Đổ metadata đã bóc tách từ 1 dict
    pdf.set_font("Roboto", "", 10)
    if isinstance(metadata, dict) and 'he' in metadata:
        # Hàng 1
        pdf.cell(20, 6, "Hệ:", align="L")
        pdf.set_font("Roboto", "B", 10)
        pdf.cell(75, 6, metadata.get("he", ""), align="L")
        
        pdf.set_font("Roboto", "", 10)
        pdf.cell(30, 6, "Môn học:", align="L")
        pdf.set_font("Roboto", "B", 10)
        pdf.cell(65, 6, metadata.get("mon", ""), ln=True, align="L")
        
        # Hàng 2
        pdf.set_font("Roboto", "", 10)
        pdf.cell(20, 6, "Năm học:", align="L")
        pdf.set_font("Roboto", "B", 10)
        pdf.cell(75, 6, metadata.get("nam", ""), align="L")
        
        pdf.set_font("Roboto", "", 10)
        pdf.cell(30, 6, "Mã học phần:", align="L")
        pdf.set_font("Roboto", "B", 10)
        pdf.cell(65, 6, metadata.get("ma_hp", ""), ln=True, align="L")
        
        # Hàng 3
        pdf.set_font("Roboto", "", 10)
        pdf.cell(20, 6, "Học kỳ:", align="L")
        pdf.set_font("Roboto", "B", 10)
        pdf.cell(75, 6, metadata.get("ky", ""), align="L")
        
        pdf.set_font("Roboto", "", 10)
        pdf.cell(30, 6, "Ngày, giờ thi:", align="L")
        pdf.set_font("Roboto", "B", 10)
        pdf.cell(65, 6, metadata.get("ngay", ""), ln=True, align="L")

    pdf.ln(10)

    # ================= 2. THỐNG KÊ & ĐÁNH GIÁ =================
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "I. THỐNG KÊ & ĐÁNH GIÁ", ln=True)
    pdf.set_font("Roboto", "", 11)

    col_final = "Điểm tổng hợp" if "Điểm tổng hợp" in df.columns else "Final"
    avg_score = df[col_final].mean()
    pass_rate = (df[col_final] >= 5).mean() * 100
    total = len(df)
    
    pdf.cell(0, 6, f"- Tổng số sinh viên: {total}", ln=True)
    pdf.cell(0, 6, f"- Điểm trung bình chung (Hệ 10): {avg_score:.2f}", ln=True)
    
    grades_count = df['Grade'].value_counts()
    
    def print_grade_stat(label, match_label):
        count = grades_count.get(match_label, 0)
        pct = (count / total) * 100 if total > 0 else 0
        pdf.cell(0, 6, f"+ {label}: {count} sinh viên ({pct:.1f}%)", ln=True)
        
    print_grade_stat("Xuất sắc", "Xuất sắc" if lang == "VI" else "Excellent")
    print_grade_stat("Giỏi", "Giỏi" if lang == "VI" else "Good")
    print_grade_stat("Khá", "Khá" if lang == "VI" else "Fair")
    print_grade_stat("Trung bình", "Trung bình" if lang == "VI" else "Average")
    print_grade_stat("Yếu", "Yếu/Kém" if lang == "VI" else "Fail")
    
    pdf.ln(4)
    pdf.set_font("Roboto", "B", 11)
    pdf.cell(0, 6, "Nhận xét chuyên môn:", ln=True)
    pdf.set_font("Roboto", "", 11)
    mode_grade = grades_count.idxmax() if not grades_count.empty else "N/A"
    
    # Generate realistic insight
    if pass_rate >= 95:
        q_text = "RẤT TỐT"
        analysis = f"Đa số sinh viên có nền tảng vững vàng, đặc biệt dải điểm phân bố tập trung nhiều nhất ở ngưỡng '{mode_grade}'. Tỷ lệ đạt tuyệt đối cho thấy đề thi bao quát tốt và phương pháp đào tạo hiện tại đang phát huy tối đa hiệu quả. Đề xuất: Tiếp tục duy trì giáo trình và cách tinh giản kiến thức này."
    elif pass_rate >= 80:
        q_text = "KHÁ/TỐT"
        analysis = f"Mức độ tiếp thu bài của sinh viên khá đồng đều, phần lớn sinh viên nằm ở mức '{mode_grade}'. Dù vậy, vẫn có nhóm nhỏ rải rác dưới trung bình. Đề xuất: Khuyến khích các lớp ôn tập dạng nhóm để kéo phổ điểm của nhóm sinh viên yếu lên mức an toàn."
    elif pass_rate >= 60:
        q_text = "TRUNG BÌNH"
        analysis = f"Chất lượng đầu ra có sự phân hóa rất mạnh. Nhóm sinh viên đạt mức '{mode_grade}' chiếm tỷ trọng cao nhưng đi kèm một số lượng không nhỏ học viên ở mức dưới trung bình. Đề xuất: Giảng viên cần rà soát lại khối kiến thức cốt lõi (Core concepts) nhằm bổ sung thêm bài tập ứng dụng dễ hiểu hơn."
    else:
        q_text = "ĐÁNG BÁO ĐỘNG"
        analysis = f"Tồn tại rủi ro cực kỳ lớn do tỷ lệ trượt môn cao. Phần lớn sinh viên (chủ yếu là {mode_grade}) chưa vượt qua được yêu cầu đánh giá năng lực cơ bản. Kiến nghị: Tổ chức báo cáo phân tích rủi ro hệ thống với bộ môn và xem xét lại cấu trúc đề kiểm tra/đề cương môn học ngay lập tức để tìm nguyên nhân."

    comment = f"Đánh giá chung: {q_text} ({pass_rate:.1f}% Đạt).\nNhận xét chi tiết: {analysis}"
    pdf.multi_cell(0, 6, comment)
    
    pdf.ln(8)

    # ================= 3. DANH SÁCH ĐIỂM CHI TIẾT =================
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "II. DANH SÁCH ĐIỂM CHI TIẾT", ln=True)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Roboto", "B", 10)
    
    pdf.cell(12, 8, "STT", border=1, fill=True, align="C")
    pdf.cell(30, 8, "MSSV", border=1, fill=True, align="C")
    pdf.cell(60, 8, "Họ và Tên", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Lớp", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Điểm TK", border=1, fill=True, align="C")
    pdf.cell(33, 8, "Xếp loại", border=1, fill=True, align="C", ln=True)
    
    pdf.set_font("Roboto", "", 10)
    
    for idx, (orig_index, row) in enumerate(df.iterrows(), start=1):
        if pdf.get_y() > 270:
            pdf.add_page()
            
        stt = str(idx)
        mssv = str(row.get('MSSV', ''))
        name = str(row.get('Name', ''))[:30]
        cls = str(row.get('Class', '')).split('_')[-1]
        final = f"{float(row.get(col_final, 0)):.1f}" if pd.notna(row.get(col_final)) else ""
        grade = str(row.get('Grade', ''))
        
        pdf.cell(12, 8, stt, border=1, align="C")
        pdf.cell(30, 8, mssv, border=1, align="C")
        pdf.cell(60, 8, name, border=1)
        pdf.cell(30, 8, cls, border=1, align="C")
        pdf.cell(25, 8, final, border=1, align="C")
        pdf.cell(33, 8, grade, border=1, align="C", ln=True)

    pdf.ln(10)
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 5, t("signature_date", lang), ln=True, align="R")
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(0, 5, "NGƯỜI LẬP BẢNG", ln=True, align="R")
    pdf.set_font("Roboto", "", 9)
    pdf.cell(0, 5, "(Ký và ghi rõ họ tên)", ln=True, align="R")
    pdf.ln(20)

    # IMPORTANT: Use dest='S' for older fpdf or just output() for fpdf2
    # To be safest, let's return it as a byte string explicitly
    return pdf.output(dest='S')

def generate_visual_pdf_report(df, lang="EN", metadata=None, insights=None):
    if insights is None:
        insights = {}
    from src.locales import t
    pdf = FPDF()
    pdf.set_margins(10, 10, 10)
    font_dir = os.path.dirname(__file__)
    pdf.add_font("Roboto", "", os.path.join(font_dir, "Roboto-Regular.ttf"))
    pdf.add_font("Roboto", "B", os.path.join(font_dir, "Roboto-Bold.ttf"))
    
    pdf.add_page()
    w_page = 190 # 210 - 20
    
    pdf.set_font("Roboto", "B", 14)
    tit = "BÁO CÁO PHÂN TÍCH INSIGHTS CHUYÊN SÂU" if lang=="VI" else "ANALYTICAL INSIGHTS REPORT"
    pdf.cell(w_page, 10, tit, ln=1, align="C")
    pdf.ln(5)
    
    # --- KPI SECTION ---
    if 'kpis' in insights:
        kpis = insights['kpis']
        pdf.set_font("Roboto", "B", 12)
        pdf.cell(w_page, 8, "I. TỔNG QUAN KPIs (Từ Dashboard)" if lang=="VI" else "I. KPIs Overview", ln=1)
        pdf.set_font("Roboto", "", 11)
        
        pdf.set_fill_color(245, 245, 245)
        
        # Total width 190 / 5 = 38
        c_w = 38
        pdf.cell(c_w, 10, "Tổng số sinh viên", border=1, fill=True, align="C")
        pdf.cell(c_w, 10, "Điểm TB Chung", border=1, fill=True, align="C")
        pdf.cell(c_w, 10, "Trung bình GPA", border=1, fill=True, align="C")
        pdf.cell(c_w, 10, "Tỷ lệ Đạt (>=5)", border=1, fill=True, align="C")
        pdf.cell(c_w, 10, "Xuất sắc (>=8)", border=1, fill=True, align="C", ln=1)
        
        pdf.set_font("Roboto", "B", 11)
        pdf.cell(c_w, 10, str(kpis.get('total', '')), border=1, align="C")
        pdf.cell(c_w, 10, f"{kpis.get('avg', 0):.2f}", border=1, align="C")
        pdf.cell(c_w, 10, f"{kpis.get('gpa', 0):.2f}", border=1, align="C")
        pdf.cell(c_w, 10, f"{kpis.get('pass_rate', 0):.1f}%", border=1, align="C")
        pdf.cell(c_w, 10, str(kpis.get('excellent', '')), border=1, align="C", ln=1)
        pdf.ln(6)

    # --- SIMULATION SECTION ---
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(w_page, 8, "II. NHẬN ĐỊNH RỦI RO & INSIGHTS" if lang=="VI" else "II. INSIGHTS & RISK", ln=1)
    pdf.set_font("Roboto", "", 11)
    
    t_1 = f"- Lớp dẫn đầu (Theo điểm TB): {insights.get('top_class', 'N/A')}." if lang=="VI" else f"- Top Class (By Average Score): {insights.get('top_class', 'N/A')}."
    pdf.multi_cell(w_page, 8, t_1)
    
    t_2 = f"- Lớp có điểm số đồng đều nhất (Ít phân tán nhất): {insights.get('least_var', 'N/A')}." if lang=="VI" else f"- Class with lowest variance: {insights.get('least_var', 'N/A')}."
    pdf.multi_cell(w_page, 8, t_2)
    
    t_3 = f"- Kịch bản rủi ro (Mô phỏng): {insights.get('pass_drop', 'Chưa có phân tích mô phỏng.')}" if lang=="VI" else f"- Simulated Scenario Risk: {insights.get('pass_drop', 'N/A')}"
    pdf.multi_cell(w_page, 8, t_3)
    
    # --- CHART VISUALIZATION INJECTION ---
    import tempfile
    
    pdf.ln(10)
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(w_page, 8, "III. TRỰC QUAN HÓA BẢN ĐỒ DỮ LIỆU" if lang=="VI" else "III. DATA VISUALIZATIONS", ln=1)
    
    def embed_chart(img_key, title):
        if img_key in insights:
            if pdf.get_y() > 220:
                pdf.add_page()
            else:
                pdf.ln(5)
            pdf.set_font("Roboto", "B", 10)
            pdf.multi_cell(w_page, 8, title)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(insights[img_key])
                tmp_path = tmp.name
            # Slightly scale the image down so 2 can easily fit on a page
            pdf.image(tmp_path, w=150)
            os.unlink(tmp_path)

    embed_chart('img_stack', "[Biểu đồ 1] Phân phối Tỷ trọng khoảng điểm" if lang=="VI" else "[Chart 1] Score Distribution")
    embed_chart('img_grouped', "[Biểu đồ 2] Phân loại Học lực sinh viên" if lang=="VI" else "[Chart 2] Student Grade Classification")
    embed_chart('img_box', "[Biểu đồ 3] Boxplot Phân tán & Lệch chuẩn" if lang=="VI" else "[Chart 3] Variance & Range Boxplot")
    embed_chart('img_scatter', "[Biểu đồ 4] Scatter - Correlation Điểm Thành Phần" if lang=="VI" else "[Chart 4] Component Correlation Scatter")
    
    pdf.ln(10)
    pdf.set_font("Roboto", "", 9)
    t_4 = "Báo cáo tự động xuất tuyến tính toàn bộ các mảng biểu diễn không gian từ tương tác trên Dashboard." if lang=="VI" else "This is an internal comprehensive auto-generated visual report."
    pdf.multi_cell(w_page, 6, t_4)
    
    return pdf.output(dest='S')