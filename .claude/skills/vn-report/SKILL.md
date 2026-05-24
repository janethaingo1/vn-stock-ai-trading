# vn-report — Báo cáo Đầu tư HTML

Tạo báo cáo đầu tư HTML đầy đủ cho một mã CK VN.
Kết hợp dữ liệu từ vn-analyze và xuất file HTML có thể mở trên trình duyệt.

## Trigger

`/vn-report <SYMBOL>` hoặc "tạo báo cáo", "xuất report", "báo cáo đầu tư"

## Workflow

1. Chạy toàn bộ phân tích như `/vn-analyze` để thu thập dữ liệu
2. Chụp screenshot chart qua TradingView MCP
3. Tạo file HTML standalone (nhúng tất cả CSS/JS inline)
4. Lưu vào `~/vn-stock-ai-trading/reports/<SYMBOL>-<ngày>.html`

## Cấu trúc báo cáo HTML

- **Header**: Logo, tên công ty, mã CK, ngày tạo báo cáo
- **Trade Score gauge**: Biểu đồ gauge 0-100 dùng CSS
- **Tóm tắt điều hành**: 3-5 bullet points chính
- **Phần kỹ thuật**: Screenshot chart + nhận xét
- **Phần cơ bản**: Bảng chỉ số tài chính key metrics
- **Phần thị trường**: Context VN-Index + ngành
- **Luận điểm đầu tư**: Bull/Bear case
- **Kế hoạch giao dịch**: Vùng mua, cắt lỗ, mục tiêu
- **Disclaimer**: Cảnh báo không phải lời khuyên tài chính

## Output

File: `reports/VCB-2026-05-19.html`

Màu sắc theo Trade Score:
- 80-100: Xanh lá (#27ae60)
- 65-79: Xanh dương (#2980b9)
- 50-64: Vàng (#f39c12)
- 35-49: Cam (#e67e22)
- 0-34: Đỏ (#c0392b)
