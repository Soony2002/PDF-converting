# Nâng cấp Tính năng Dashboard & Report PDF (Giữ nguyên Nhận diện UI)

Mục tiêu cốt lõi: 
1. **Giữ nguyên bản sắc thiết kế hiện tại của bạn**: Không chạy theo lối mòn Power BI. UI sẽ được tinh chỉnh CSS để luôn mượt mà và cá tính ở cả bảng màu ánh sáng (Light Mode) và bóng tối (Dark Mode).
2. **Tab 3**: Cập nhật tính năng biểu đồ Radar Chart đối chiếu cá nhân.
3. **Báo cáo PDF**: Trích xuất chính xác Header gốc (Ngân hàng nhà nước, Tên trường, Mã học phần...). 
  - Nếu upload 1 lớp: Giữ nguyên y đúc mã học phần và lớp (ví dụ: `AMA301_2511_1_D05`).
  - Nếu upload nhiều lớp: Tự động phát hiện và cắt bỏ phần đuôi lớp, chỉ giữ lại mã môn chung (ví dụ: `AMA301_2511_1`).

## User Review Required

> [!IMPORTANT]
> - Giao diện của bạn hiện đang dùng Glassmorphism (Kính mờ) trong `style.css`. Để nó thích ứng được Light Mode, tôi sẽ chuyển các mã màu cứng sang biến CSS trong nền của Streamlit (giúp chuyển từ xuyên thấu tối sang xuyên thấu sáng) mà vẫn giữ đúng linh hồn thiết kế của bạn.

## Proposed Changes

### 1. Thay đổi Giao diện & Thích ứng màu sắc

#### [MODIFY] [app.py](file:///c:/Users/Administrator/Downloads/PDF-converting/app.py)
- **Tính năng Tra cứu Cá nhân (Tab 3)**: Xây dựng Radar chart và logic nhận xét cảnh báo (nhưng vẫn nằm trong khối `st.container()` mang phong cách thiết kế hiện tại của bạn).
- **Thích ứng Biểu đồ (Chart Colors)**: Gỡ bỏ ép màu chữ (`font=dict(color="#f8fafc")`) trên các biểu đồ Plotly. Cài đặt cờ `theme="streamlit"` để biểu đồ tự động đổi màu text khi users đổi Light/Dark mode.

#### [MODIFY] [style.css](file:///c:/Users/Administrator/Downloads/PDF-converting/style.css)
- Giữ nguyên các hiệu ứng (hover scale, hover glow) mà code cũ đang làm rất tốt.
- Xóa bỏ các dòng mã lệnh `!important` ép màu nền đen ở khối `:root`. Thay bằng `@media (prefers-color-scheme: light)` và `@media (prefers-color-scheme: dark)` để duy trì độ "trong suốt" (Glassmorphism) đẹp ở cả phông trắng hoặc đen.

### 2. Nâng cấp PDF Parser và Export

#### [MODIFY] [src/pdf_parser.py](file:///c:/Users/Administrator/Downloads/PDF-converting/src/pdf_parser.py)
- Thêm logic dùng `page.extract_text()` trên trang đầu tiên của file PDF.
- Thu thập Header text, dùng Regex hoặc thao tác xử lý chuỗi (String manipulation) để trích xuất các Metadata chính xác (Hệ, Năm, Học kỳ, Mã học phần, Ngày giờ thi).
- **Xử lý đa file**: 
  - Nếu `len(uploaded_files) > 1`: Phân tích chuỗi Mã học phần (VD: `AMA301_2511_1_D05`), tìm cụm gạch dưới cuối cùng và loại bỏ nó để về dạng gốc `AMA301_2511_1`. Thay thế "Ngày giờ thi" thành *"Nhiều ca thi (chọn 1 lớp cụ thể)"* giống như bản tham khảo.
- Đóng gói chung với Dataframe và trả về cho `app.py`.

#### [MODIFY] [src/report_generator.py](file:///c:/Users/Administrator/Downloads/PDF-converting/src/report_generator.py)
- Nâng cấp `generate_pdf_report(df, metadata, lang)`. 
- Vẽ lại khối Header 2 cột: (Ngân hàng nhà nước... | Cộng hòa...) và vẽ lại Metadata của Môn học ngay phía dưới, trước khi kết xuất bảng thống kê chuyên môn.

## Open Questions

> [!WARNING]
> Mọi yêu cầu của bạn đã được tiếp thu: Thiết kế giữ nguyên chất riêng, tích hợp Radar thông minh, và cơ chế trích xuất Header PDF khôn ngoan cho cả 1 file và nhiều file.
> 
> Bạn bấm đồng ý (hoặc gõ OK) để tôi bắt tay vào viết code thực thi luôn nhé.

## Verification Plan
1. Upload thử 1 file PDF -> Check file Export PDF xem Header đúng tên lớp không.
2. Upload thử 2 file PDF -> Check file Export PDF xem Header có cắt chữ lớp và sửa Ngày giờ thi không.
3. Thay đổi giao diện Streamlit (Settings -> Light) để xem các component Glass UI của bạn biến thành màu sáng trong thẻ.
