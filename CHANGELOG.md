# Changelog

Tất cả thay đổi đáng chú ý của dự án được ghi lại tại đây.

## [2.1.0] - 2026-10-31

### Added

- Vòng lặp tool-calling cho `alex-agent` với giới hạn bước và danh sách công cụ chỉ-đọc được phép.
- Xác thực riêng cho API và trang quản trị, signed session cookie, CSRF protection và rate limiting.
- Bộ kiểm thử hồi quy cho xác thực, CORS, admin session, agent tools và cấu hình triển khai.
- Lockfile dependency production và quy trình kiểm tra lỗ hổng bằng `pip-audit`.
- Persistent Docker volume, healthcheck và tài liệu triển khai Dokploy/KOAssistant.

### Changed

- Nâng dependency lên các phiên bản hiện hành không có CVE đã biết tại thời điểm phát hành.
- Chuyển dữ liệu runtime sang `DATA_DIR`; mặc định container dùng `/data`.
- Container chạy bằng user không phải root, root filesystem read-only và bỏ Linux capabilities.
- CORS mặc định tắt; chỉ cho phép origin HTTPS được cấu hình rõ ràng.
- Scheduler dùng múi giờ `Asia/Ho_Chi_Minh` và có lifecycle khởi động/dừng an toàn.
- Lỗi upstream AI trả về trạng thái gateway phù hợp thay vì giả thành câu trả lời thành công.

### Security

- Sửa lỗi nghiêm trọng khiến mọi API token đều được chấp nhận.
- Loại bỏ token khỏi query string và không còn lưu raw secret trong cookie admin.
- Bảo vệ Vault API và knowledge graph image bằng API token.
- Loại dữ liệu Vault khỏi Git tracking và thêm `data/`, `.env`, `.gstack/` vào ignore rules.
- Bắt buộc `AUTH_TOKEN`, `ADMIN_PASSWORD` và `SESSION_SECRET` mạnh, độc lập; cấu hình yếu sẽ khiến ứng dụng từ chối khởi động.

### Fixed

- Bổ sung các import còn thiếu khiến scheduler phát sinh `NameError` khi chạy job.
- Luôn kết thúc SSE stream bằng `[DONE]`, kể cả khi upstream trả lỗi hoặc đóng stream sớm.
