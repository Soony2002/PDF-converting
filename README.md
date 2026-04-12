# PDF Data Dashboard

Một ứng dụng web phân tích dữ liệu bảng điểm từ PDF một cách tự động, với biểu đồ tương tác và báo cáo chuyên nghiệp.

## Tính năng chính

- **📄 Trích xuất dữ liệu PDF**: Tự động đọc và phân tích bảng điểm từ file PDF.
- **📊 Biểu đồ tương tác**: Hiển thị phân bố điểm, so sánh lớp học, phát hiện outliers.
- **🤖 Phân tích tự động**: Tính toán insights như tỷ lệ đạt, điểm trung bình, phân loại học lực.
- **📈 Báo cáo PDF**: Xuất báo cáo chính thức với bảng điểm và nhận xét chuyên môn.
- **🌐 Giao diện đa ngôn ngữ**: Hỗ trợ tiếng Việt và tiếng Anh.
- **📥 Xuất dữ liệu**: Tải xuống CSV hoặc XLSX.

## Công nghệ sử dụng

- **Python 3.12**
- **Streamlit**: Framework UI web
- **Pandas**: Xử lý dữ liệu
- **Plotly**: Biểu đồ tương tác
- **PDFPlumber**: Trích xuất dữ liệu từ PDF
- **FPDF2**: Tạo báo cáo PDF
- **OpenPyXL**: Xuất file Excel

## Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- Git (để clone repo)

### Bước 1: Clone repository
```bash
git clone https://github.com/yourusername/pdf-converting.git
cd pdf-converting
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)
```bash
python -m venv venv
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng
```bash
streamlit run app.py
```

Ứng dụng sẽ mở trong trình duyệt tại `http://localhost:8501`.

## Cách sử dụng

1. **Upload PDF**: Chọn file PDF bảng điểm và tải lên.
2. **Xem dữ liệu**: Kiểm tra dữ liệu đã trích xuất trong tab "Phân Tích Tổng Quan".
3. **Phân tích**: Sử dụng các tab để xem biểu đồ và insights.
4. **Xuất báo cáo**: Tải xuống báo cáo PDF hoặc dữ liệu CSV/XLSX.

## Cấu trúc dự án

```
pdf-converting/
├── app.py                 # File chính của ứng dụng
├── style.css              # CSS tùy chỉnh giao diện
├── requirements.txt       # Dependencies Python
├── .streamlit/
│   └── config.toml        # Cấu hình Streamlit
└── src/
    ├── __init__.py
    ├── pdf_parser.py      # Logic trích xuất PDF
    ├── charts.py          # Tạo biểu đồ
    ├── export_utils.py    # Xuất dữ liệu
    ├── report_generator.py # Tạo báo cáo PDF
    ├── locales.py         # Đa ngôn ngữ
    └── Roboto-Bold.ttf    # Font cho PDF
    └── Roboto-Regular.ttf
```

## Deploy lên web

### Streamlit Cloud
1. Push code lên GitHub
2. Đăng nhập https://share.streamlit.io
3. Chọn repository và file `app.py`



## Đóng góp

Nếu bạn muốn đóng góp:
1. Fork repository
2. Tạo branch mới
3. Commit thay đổi
4. Push và tạo Pull Request

## Giấy phép

MIT License - Xem file LICENSE để biết thêm chi tiết.

## Liên hệ

- GitHub: [SoonyDuck](https://github.com/SonnyDuck)
- Email: sonpo1704@Gmail.com