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

    # IMPORTANT: Use dest='S' for older fpdf or just output() for fpdf2
    # To be safest, let's return it as a byte string explicitly
    return pdf.output(dest='S')