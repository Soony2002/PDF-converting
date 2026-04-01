from fpdf import FPDF
import datetime

import os

def generate_pdf_report(df, lang="EN"):
    from src.locales import t
    pdf = FPDF()
    
    font_dir = os.path.dirname(__file__)
    pdf.add_font("Roboto", "", os.path.join(font_dir, "Roboto-Regular.ttf"))
    pdf.add_font("Roboto", "B", os.path.join(font_dir, "Roboto-Bold.ttf"))
    
    pdf.add_page()
    
    # Header
    pdf.set_font("Roboto", "B", 16)
    pdf.cell(0, 10, t("pdf_header", lang), ln=True, align="C")
    
    pdf.set_font("Roboto", "", 10)
    date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    pdf.cell(0, 10, f"{t('pdf_generated_on', lang)}: {date_str}", ln=True, align="C")
    pdf.ln(10)

    # 1. Statistics
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 10, t("pdf_exec_summary", lang), ln=True)
    pdf.set_font("Roboto", "", 11)

    
    avg_score = df["Final"].mean()
    pass_rate = (df["Final"] >= 5).mean() * 100
    total = len(df)
    
    summary_text = t("pdf_summary_text", lang).format(total=total, classes=df['Class'].nunique(), avg=avg_score, pass_rate=pass_rate)
    pdf.multi_cell(0, 8, summary_text)
    pdf.ln(5)

    # 2. Class Table
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 10, t("pdf_class_table", lang), ln=True)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(80, 10, t("pdf_col_class", lang), border=1, fill=True)
    pdf.cell(50, 10, t("pdf_col_avg", lang), border=1, fill=True)
    pdf.cell(50, 10, t("pdf_col_pass", lang), border=1, fill=True, ln=True)
    
    pdf.set_font("Roboto", "", 10)
    summary = df.groupby("Class")["Final"].agg(['mean', lambda x: (x >= 5).mean() * 100]).reset_index()
    
    for _, row in summary.iterrows():
        pdf.cell(80, 10, str(row['Class'])[:35], border=1)
        pdf.cell(50, 10, f"{row['mean']:.2f}", border=1)
        # Fix for column indexing
        p_rate = row.iloc[2] 
        pdf.cell(50, 10, f"{p_rate:.1f}%", border=1, ln=True)

    # IMPORTANT: Use dest='S' for older fpdf or just output() for fpdf2
    # To be safest, let's return it as a byte string explicitly
    return pdf.output(dest='S')