import pandas as pd
import pdfplumber
import re
import streamlit as st

@st.cache_data
def extract_pdf_tables(uploaded_files):

    tables = []
    header = None
    first_page_text = ""

    for i, file in enumerate(uploaded_files):
        # Extract filename without .pdf extension
        file_name = file.name.split('.pdf')[0]

        with pdfplumber.open(file) as pdf:
            if i == 0 and not first_page_text:
                first_page_text = pdf.pages[0].extract_text()

            for page in pdf.pages:

                table = page.extract_table()

                if table:

                    df = pd.DataFrame(table)

                    df[2] = df[2].fillna('') + ' ' + df[3].fillna('')
                    df = df.drop(columns=[3])

                    if header is None:

                        header = df.iloc[0].fillna('') + " " + df.iloc[1].fillna('')
                        header = header.str.strip()

                        df.columns = header
                        df = df[2:]

                    else:
                        df.columns = header

                    df = df.iloc[:, :9]

                    df.columns = [
                        "STT","MSSV","Name","Admin_Class",
                        "CC","GK","TL","CK","Final"
                    ]
                    
                    # Set the analytical 'Class' to the filename instead of the inner class
                    df["Class"] = file_name

                    tables.append(df)

    if tables:
        df = pd.concat(tables, ignore_index=True)
        
        df = df[~df["MSSV"].astype(str).str.contains("Mã số", na=False)]
        df = df[df["MSSV"].notna()]
        
        df = df.reset_index(drop=True)

        score_cols = ["CC","GK","TL","CK","Final"]

        for col in score_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        metadata = {
            "he": "", "mon": "", "nam": "", "ma_hp": "", "ky": "", "ngay": ""
        }
        
        if first_page_text:
            lines = first_page_text.split('\n')
            for line in lines:
                # Tránh parse lầm vào bảng điểm
                if "STT" in line or "Mã số" in line or "Điểm thành phần" in line:
                    break
                
                # Trích xuất Header metadata bằng Regex khôn ngoan
                if "Hệ:" in line:
                    m = re.search(r'Hệ:\s*(.*?)\s*Môn', line)
                    if m: metadata['he'] = m.group(1).strip()
                    m = re.search(r'Môn học:\s*(.*)', line)
                    if m: metadata['mon'] = m.group(1).strip()
                elif "Năm học:" in line:
                    m = re.search(r'Năm học:\s*(.*?)\s*Mã', line)
                    if m: metadata['nam'] = m.group(1).strip()
                    m = re.search(r'Mã học phần:\s*(.*)', line)
                    if m: metadata['ma_hp'] = m.group(1).strip()
                elif "Học kỳ:" in line:
                    m = re.search(r'Học kỳ:\s*(.*?)\s*Ngày', line)
                    if m: metadata['ky'] = m.group(1).strip()
                    m = re.search(r'Ngày.*thi:\s*(.*)', line)
                    if m: metadata['ngay'] = m.group(1).strip()

            if len(uploaded_files) > 1:
                metadata['ngay'] = "Nhiều ca thi (chọn 1 lớp cụ thể)"
                metadata['ma_hp'] = re.sub(r'([A-Za-z0-9]+_[0-9]+_[0-9]+)_[A-Za-z0-9]+', r'\1', metadata.get('ma_hp', ''))

        return df, metadata

    return None