import pandas as pd
import pdfplumber


def extract_pdf_tables(uploaded_files):

    tables = []
    header = None

    for file in uploaded_files:
        # Extract filename without .pdf extension
        file_name = file.name.split('.pdf')[0]

        with pdfplumber.open(file) as pdf:

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

        return df

    return None