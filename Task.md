# Checklist Công việc Nâng cấp Dashboard

## 1. Giao diện & Thích ứng Theme (Light/Dark Mode)
- `[ ]` Cập nhật `style.css`: Xoá `!important` chặn màu, dùng `@media` hoặc CSS variables để bảo toàn hiệu ứng Kính (Glassmorphism) trên mọi nền.
- `[ ]` Khởi tạo `.streamlit/config.toml` (nếu cần) để đồng bộ theme.

## 2. Nâng cấp Biểu đồ & Bổ sung Analytical Options (Tab 1)
- `[ ]` Xoá đoạn code ép chữ trắng (`font=dict(color="#f8fafc")`) ở mọi hàm vẽ biểu đồ Plotly.
- `[ ]` Sử dụng `theme="streamlit"` để biểu đồ tự động đổi màu.
- `[ ]` Thêm option "Phân loại Học lực" (Grade Classification) để đếm số lượng Xuất sắc, Giỏi, Khá, TB, Yếu (Theo chuẩn thực tế giáo viên cần để báo cáo cuối kì).

## 3. Xây dựng Radar Chart (Tab 3)
- `[ ]` Thêm bộ lọc Dropdown chọn Sinh viên.
- `[ ]` Tạo Dataframe trung bình lớp để đối chiếu với Sinh viên đó.
- `[ ]` Vẽ Radar Chart phân tích các hệ số (Chuyên Cần, Giữa kì, Thảo luận, Cuối kì).
- `[ ]` Lập trình hàm sinh Nhận xét tự động bằng chữ (Cảnh báo nếu dưới trung bình, Khen ngợi nếu vượt trội).

## 4. Parser Tiêu đề & Export PDF Report
- `[ ]` Sửa `src/pdf_parser.py`: Lấy văn bản thô từ trang 1 của PDF để trích xuất Text Header (Tên trường, Hệ, Môn...).
- `[ ]` Bổ sung logic cắt chuỗi thông minh khi có nhiều mã lớp học phần.
- `[ ]` Sửa `src/report_generator.py`: Dùng thư viện FPDF để vẽ lại đoạn Metadata đó chính xác như bản gốc thay vì fix cứng.
