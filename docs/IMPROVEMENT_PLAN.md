# Kế hoạch cải thiện Kindle AI Gateway

Trạng thái: **Chờ phê duyệt**  
Cập nhật: 2026-11-01  
Phạm vi: Kindle chạy KOReader + KOAssistant, gateway tại `kindle.alphatech.ai.vn`, dữ liệu Vault và trang quản trị.

Không hạng mục nào trong tài liệu này được triển khai chỉ vì đã được liệt kê. Mỗi giai đoạn cần được chủ dự án duyệt trước. Không tự động phục hồi dữ liệu, đổi secret hoặc thay đổi production.

## Thứ tự đề xuất

### Giai đoạn 1 — Backup và khôi phục

- Kiểm tra định dạng manifest và tính toàn vẹn SQLite trong file backup.
- Chặn đường dẫn tuyệt đối, `..`, symlink và ZIP có kích thước bất thường.
- Cung cấp chế độ `dry-run` mặc định, không thay đổi dữ liệu.
- Khi thực sự restore, yêu cầu xác nhận rõ ràng và ứng dụng phải được dừng.
- Tạo bản backup dự phòng trước khi ghi đè và hỗ trợ rollback khi lỗi.
- Viết unit/integration tests bằng thư mục tạm; không thử restore trên production.

**Điều kiện hoàn tất:** backup hợp lệ được kiểm tra thành công; archive lỗi bị từ chối; restore thử nghiệm phục hồi đúng DB, Markdown và config; không mất dữ liệu khi mô phỏng lỗi.

### Giai đoạn 2 — Quản lý bộ nhớ cá nhân

- Cho phép xem, sửa và xóa từng mục memory trong Dashboard.
- Thêm lệnh Kindle `#forget` với cú pháp rõ ràng.
- Xóa toàn bộ memory phải có xác nhận hai bước.
- Cho phép xuất/nhập memory bằng định dạng có version.
- Giữ memory là dữ liệu không tin cậy, không phải system instruction.

**Điều kiện hoàn tất:** thao tác có CSRF/auth, ghi nguyên tử, giới hạn kích thước, có kiểm thử chống command injection và thao tác nhầm.

### Giai đoạn 3 — Kiểm soát chi phí và quá tải

- Giới hạn request AI chạy đồng thời.
- Đặt timeout riêng cho DeepSeek và từng công cụ mạng.
- Giới hạn token theo chế độ trả lời.
- Hiển thị request, token, tool calls, độ trễ và lỗi trên Dashboard.
- Không lưu prompt, câu trả lời, IP, header hoặc API token.

**Điều kiện hoàn tất:** quá tải trả lỗi có kiểm soát; client ngắt kết nối giải phóng tài nguyên; telemetry không chứa nội dung nhạy cảm.

### Giai đoạn 4 — Trải nghiệm Kindle/E-ink

- Thêm chế độ trả lời ngắn, tiêu chuẩn và chuyên sâu.
- Chuẩn hóa `#help` và thông báo lỗi cho màn hình E-ink.
- Giảm định dạng phức tạp, emoji và nội dung dài không cần thiết.
- Xử lý rõ trường hợp mất mạng, timeout, token sai và upstream lỗi.
- Kiểm tra thủ công trên Kindle thật; không dùng Playwright hoặc browser automation.

**Điều kiện hoàn tất:** thao tác đọc, chọn đoạn văn, Explain/Summarize và hỏi trực tiếp hoạt động ổn định trên thiết bị thật.

### Giai đoạn 5 — Knowledge Vault

- Cải thiện tìm kiếm tiếng Việt và xếp hạng kết quả.
- Sửa/xóa ghi chú an toàn từ Dashboard.
- Phát hiện ghi chú và liên kết trùng.
- Xuất Markdown/ZIP và kiểm tra nhất quán giữa file với SQLite.

### Giai đoạn 6 — Agent và nguồn dữ liệu

- Phân biệt rõ kiến thức mô hình, dữ liệu Vault và kết quả web.
- Kèm nguồn khi dùng dữ liệu web.
- Duy trì allowlist công cụ, giới hạn vòng lặp và số tool calls.
- Không cho agent chạy shell hoặc MCP tùy ý.
- Bổ sung tổng hợp ghi chú, kế hoạch đọc và ôn tập theo yêu cầu rõ ràng.

### Giai đoạn 7 — Bảo mật và vận hành

- Rate limit riêng cho đăng nhập, API và thao tác ghi.
- Kiểm tra cấu hình/secret khi khởi động.
- Rà soát dependency, Docker image, quyền volume và chính sách log.
- Tài liệu hóa quy trình rotate token/mật khẩu và xử lý sự cố.

### Giai đoạn 8 — Deploy và xác minh production

- Tạo checklist Dokploy và xác nhận persistent volume `/data`.
- Chạy unit test, integration test, compile, dependency audit và production build.
- Chạy smoke test chỉ-đọc sau deploy.
- Xác nhận `/health` trả đúng `version` mới.
- Các bước cần browser thật được ghi là kiểm tra thủ công.

## Thứ tự phê duyệt khuyến nghị

Phê duyệt và thực hiện giai đoạn 1–4 trước. Sau khi kiểm tra trên Kindle thật, đánh giá lại rồi mới duyệt giai đoạn 5–8.

## Ngoài phạm vi nếu chưa có phê duyệt riêng

- Restore hoặc xóa dữ liệu production.
- Đổi API token, mật khẩu admin hoặc session secret.
- Cài phần mềm lên Kindle hoặc cập nhật firmware.
- Thay nhà cung cấp AI hay phát sinh dịch vụ trả phí mới.
- Bật shell, công cụ tùy ý hoặc quyền thực thi từ xa cho agent.
