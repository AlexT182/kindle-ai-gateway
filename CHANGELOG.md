# Changelog

Tất cả thay đổi đáng chú ý của dự án được ghi lại tại đây.

## [2.1.4] - 2026-11-01

### Changed

- Backup lớn dùng vùng `.tmp` trên persistent volume thay vì tmpfs 64 MB và tự dọn thư mục backup cũ.
- Tác vụ tạo archive chạy trong threadpool để không chặn event loop phục vụ Kindle.
- Thay Uvicorn access log thô bằng log request đã lược bỏ query string, header và body.

### Security

- Bỏ cấu hình tin cậy mọi forwarded IP; proxy header chỉ được chấp nhận theo allowlist mặc định của Uvicorn.
- Ngăn token cũ trong query string vô tình xuất hiện trong access log.

## [2.1.3] - 2026-11-01

### Added

- Nút tải backup Vault trong Dashboard; archive dùng SQLite online backup và kèm Markdown/configuration.
- Security headers, HSTS và request ID cho mọi response.
- Dashboard hiển thị model mặc định và phiên bản gateway thực tế.

### Security

- Chỉ cho phép `#note` và `#todo` ghi dữ liệu khi lệnh nằm ở đầu và chiếm toàn bộ yêu cầu, ngăn nội dung sách nhúng lệnh ghi ngoài ý muốn.
- Backup yêu cầu admin session hợp lệ và CSRF token; file tạm được xóa sau khi tải.

## [2.1.2] - 2026-11-01

### Added

- Readiness check kiểm tra SQLite Vault thật thay vì chỉ xác nhận tiến trình web còn sống.
- Kiểm thử hồi quy cho tính toàn vẹn Vault, API path redaction và scheduler idempotency.

### Changed

- Note ID dùng UUID và file Markdown được ghi nguyên tử trước khi commit index.
- Scheduler dùng năm hiện tại, ISO week, chống chạy đồng thời và không tạo digest trùng kỳ.
- SQLite bật foreign keys, WAL, busy timeout và transaction rollback rõ ràng.

### Fixed

- Ngăn hai ghi chú cùng tiêu đề/cùng giây ghi đè index của nhau.
- Xóa ghi chú giờ xóa đồng bộ cả DB index và file Markdown, đồng thời chặn đường dẫn ngoài Vault.
- API Vault không còn trả về đường dẫn file nội bộ của server.

## [2.1.1] - 2026-11-01

### Added

- Smoke-test production chỉ-đọc cho health, API auth, Vault protection và CORS.

### Fixed

- Khôi phục các lệnh `#note`, `#todo`, graph và prompt kỹ năng legacy trong luồng `alex-agent` mới.
- Chuyển web search từ package `duckduckgo-search` đã đổi tên sang `ddgs` hiện hành.

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
