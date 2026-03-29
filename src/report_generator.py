from fpdf import FPDF
import datetime

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "OFFICIAL GRADE ANALYSIS REPORT", ln=True, align="C")
    
    pdf.set_font("Arial", "I", 10)
    date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    pdf.cell(0, 10, f"Generated on: {date_str}", ln=True, align="C")
    pdf.ln(10)

    # 1. Statistics
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    
    avg_score = df["Final"].mean()
    pass_rate = (df["Final"] >= 5).mean() * 100
    total = len(df)
    
    summary_text = (f"This report covers {total} students across {df['Class'].nunique()} classes. "
                    f"The overall average score is {avg_score:.2f}/10. "
                    f"The passing rate is {pass_rate:.1f}%.")
    pdf.multi_cell(0, 8, summary_text)
    pdf.ln(5)

    # 2. Class Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Breakdown by File/Class", ln=True)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(80, 10, "Class Name", border=1, fill=True)
    pdf.cell(50, 10, "Avg Score", border=1, fill=True)
    pdf.cell(50, 10, "Pass Rate", border=1, fill=True, ln=True)
    
    pdf.set_font("Arial", "", 10)
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