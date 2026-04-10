import streamlit as st
from io import BytesIO


def export_buttons(df, base_name):

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Download CSV",
        csv,
        f"{base_name}.csv",
        "text/csv"
    )

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)

    st.download_button(
        "Download XLSX",
        excel_buffer.getvalue(),
        f"{base_name}.xlsx"
    )