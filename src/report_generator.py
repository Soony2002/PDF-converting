from fpdf import FPDF
import datetime

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

    # ================= 2. INSIGHT PHÂN TÍCH =================
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 10, "1. Insight Phân Tích Bảng Điểm", ln=True)
    pdf.set_font("Roboto", "", 11)

    
    avg_score = df["Final"].mean()
    pass_rate = (df["Final"] >= 5).mean() * 100
    total = len(df)
    
    summary_text = t("pdf_summary_text", lang).format(total=total, classes=df['Class'].nunique(), avg=avg_score, pass_rate=pass_rate)
    pdf.multi_cell(0, 8, summary_text)
    pdf.ln(5)

    # ================= 3. BẢNG ĐIỂM (TỔNG HỢP) =================
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 10, "2. Bảng Thống Kê / Điểm", ln=True)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(80, 10, "Lớp Học Phần", border=1, fill=True)
    pdf.cell(50, 10, "Điểm TB Chung", border=1, fill=True)
    pdf.cell(50, 10, "Tỷ lệ đạt (≥5)", border=1, fill=True, ln=True)
    
    pdf.set_font("Roboto", "", 10)
    summary = df.groupby("Class")["Final"].agg(['mean', lambda x: (x >= 5).mean() * 100]).reset_index()
    
    for _, row in summary.iterrows():
        pdf.cell(80, 10, str(row['Class'])[:35], border=1)
        pdf.cell(50, 10, f"{row['mean']:.2f} / 10.0", border=1)
        p_rate = row.iloc[2] 
        pdf.cell(50, 10, f"{p_rate:.1f}%", border=1, ln=True)

    pdf.ln(15)
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 5, t("signature_date", lang), ln=True, align="R")
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(0, 5, t("signature_creator", lang), ln=True, align="R")
    pdf.set_font("Roboto", "", 9)
    pdf.cell(0, 5, t("signature_sign", lang), ln=True, align="R")
    pdf.ln(20)

    # IMPORTANT: Use dest='S' for older fpdf or just output() for fpdf2
    # To be safest, let's return it as a byte string explicitly
    return pdf.output(dest='S')

def generate_visual_pdf_report(df, lang="EN", metadata=None, insights=None):
    if insights is None:
        insights = {}
    from src.locales import t
    pdf = FPDF()
    font_dir = os.path.dirname(__file__)
    pdf.add_font("Roboto", "", os.path.join(font_dir, "Roboto-Regular.ttf"))
    pdf.add_font("Roboto", "B", os.path.join(font_dir, "Roboto-Bold.ttf"))
    
    pdf.add_page()
    pdf.set_font("Roboto", "B", 14)
    tit = "BÁO CÁO PHÂN TÍCH INSIGHTS CHUYÊN SÂU" if lang=="VI" else "ANALYTICAL INSIGHTS REPORT"
    pdf.cell(0, 10, tit, ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "1. Tổng quan Lớp xuất sắc nhất" if lang=="VI" else "1. Top Performing Class", ln=True)
    pdf.set_font("Roboto", "", 11)
    t_1 = f"- Dựa trên phân tích phân bố trung bình, lớp {insights.get('top_class', 'N/A')} đang dẫn đầu bộ dữ liệu hiện tại." if lang=="VI" else f"- Class {insights.get('top_class', 'N/A')} is currently leading the academic metrics."
    pdf.multi_cell(0, 8, t_1)
    
    pdf.ln(5)
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "2. Mức độ tản mát dữ liệu (Độ đồng đều)" if lang=="VI" else "2. Variance Analytics", ln=True)
    pdf.set_font("Roboto", "", 11)
    t_2 = f"- Lớp có điểm số đồng đều nhất (Khoảng cách điểm phần lõi bé nhất) thuộc về {insights.get('least_var', 'N/A')}." if lang=="VI" else f"- Class {insights.get('least_var', 'N/A')} holds the tightest IQR distribution showing consistent performance."
    pdf.multi_cell(0, 8, t_2)
    
    pdf.ln(5)
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "3. Nhận định Rủi ro Khóa Học (Simulation)" if lang=="VI" else "3. Exam Simulation Risk", ln=True)
    pdf.set_font("Roboto", "", 11)
    t_3 = f"- Kịch bản giả định: {insights.get('pass_drop', 'Chưa có dữ liệu.')}" if lang=="VI" else f"- Generated Scenario Risk: {insights.get('pass_drop', 'N/A')}"
    # fpdf does not handle long utf8 characters securely without replacement sometimes but standard Roboto supports VN.
    pdf.multi_cell(0, 8, t_3)
    
    # --- CHART VISUALIZATION INJECTION ---
    import tempfile
    
    pdf.ln(10)
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "II. Trực quan hóa Biểu Đồ (Charts)" if lang=="VI" else "II. Visual Charts", ln=True)
    
    def embed_chart(img_key, title):
        if img_key in insights:
            pdf.ln(5)
            pdf.set_font("Roboto", "B", 10)
            pdf.cell(0, 8, title, ln=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(insights[img_key])
                tmp_path = tmp.name
            pdf.image(tmp_path, w=160)
            os.unlink(tmp_path)

    embed_chart('img_rank', "[Biểu đồ 1] Xếp hạng lớp theo Điểm Tổng Kết" if lang=="VI" else "[Chart 1] Class Ranking")
    embed_chart('img_grouped', "[Biểu đồ 2] Phân loại Học Lực theo Lớp" if lang=="VI" else "[Chart 2] Grade Distribution")
    embed_chart('img_box', "[Biểu đồ 3] Phân tán & Sự Lệch Điểm" if lang=="VI" else "[Chart 3] Score Variance Boxplot")
    
    pdf.ln(10)
    pdf.set_font("Roboto", "", 9)
    t_4 = "Báo cáo này tập trung vào số liệu phân tích chuyên sâu tự động xuất ra từ Dashboard." if lang=="VI" else "This report isolates textual and visual insights directly from the interactive dashboard."
    pdf.multi_cell(0, 6, t_4)
    
    return pdf.output(dest='S')