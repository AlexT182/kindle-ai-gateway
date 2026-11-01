# Changelog

Tất cả thay đổi đáng chú ý của dự án được ghi lại tại đây.

## [Unreleased]

### Added

- Script đồng bộ ghi chú Vault từ Gateway về thư mục Markdown trên PC (`scripts/sync_vault_notes.py`) hỗ trợ định dạng Obsidian và cập nhật gia tăng (incremental).
- Bộ kiểm thử hồi quy cho đồng bộ ghi chú (`tests/test_sync_vault_notes.py`), nâng tổng số test suite lên 47/47 passed.
- Cấu hình các thao tác nhanh 1-chạm (Quick Context Actions) cho KOAssistant trên Kindle (`custom_actions.lua`) gồm tra cứu Web thời gian thực `#search`, Wikipedia `#wiki`, tóm tắt, giải thích sâu và lưu Vault.
- Tích hợp game Cờ Vây (`go.koplugin`) hỗ trợ bàn 9x9, 13x13, 19x19 và bot AI cho KOReader.
- Script tự động sinh sổ tay hướng dẫn sử dụng đa định dạng (`scripts/create_kindle_guide.py` tạo `.epub`, `.md`, `.txt`) lưu trực tiếp vào `E:\documents\Books`.

### Fixed

- Sửa lỗi crash văng KOReader trong `boardgames.koplugin`: gán mặc định màu nền `Blitbuffer.COLOR_WHITE` cho `button.lua` và `buttontable.lua` để tránh ngoại lệ nil khi bấm `Settings` hoặc `Close`.

### Documentation

- Thêm kế hoạch tổng thể nâng cấp Kindle Paperwhite 4 (`docs/KINDLE_UPGRADE_MASTER_PLAN.md`) gồm 3 trụ cột: Game E-ink, Vẽ/Mindmap và Trạm tri thức AI 2 chiều.
- Cập nhật biên bản phiên làm việc ngày 2026-11-01 (`docs/sessions/SESSION-2026-11-01.md`) ghi nhận toàn bộ quá trình triển khai thực tế trên ổ `E:\`, xác nhận production 2.1.6, sửa lỗi game và hướng dẫn tra cứu web.

## [2.1.7] - 2026-11-01

### Added

- Endpoint AlphaGo Cloud AI `/api/v1/games/go/move` hỗ trợ tính toán nước cờ kỳ thủ chuyên nghiệp 9-Đẳng, trả về tọa độ, tỷ lệ thắng % và lời bình luận chiến thuật.
- Game Cờ Thú Native mới (`animalchess.koplugin`) chuẩn E-ink 300 DPI với bàn cờ 7x9, 8 loài thú, sông nước, bẫy, hang, bot AI Minimax Alpha-Beta 3 cấp độ và chế độ nâng cao "Linh Thú Thức Tỉnh".
- Tích hợp cửa sổ hướng dẫn luật chơi tiếng Việt trực tiếp trong game cho toàn bộ 8 trò chơi trên Kindle (`animalchess`, `go`, và 6 game trong `boardgames`).
- Chế độ chọn đối thủ minh bạch trong game Cờ Vây (`[Bot Offline]`, `[Cloud AI 🌐 Cần Internet]`, `[2 Người]`) với cơ chế thông báo và tự động dự phòng khi mất kết nối Wi-Fi.

### Fixed

- Patch toàn bộ các nút luật chơi trong `boardgames.koplugin` và `go.koplugin` để hiển thị giải thích chi tiết bằng tiếng Việt thay vì tiếng Anh.

## [2.1.6] - 2026-11-01

### Added

- Lệnh `#remember [chủ đề] <nội dung>` để người dùng chủ động lưu sở thích, mục tiêu hoặc bối cảnh cá nhân.
- Lệnh `#memory` để xem tối đa 10 mục ghi nhớ gần nhất ngay trên Kindle.

### Security

- Chỉ ghi bộ nhớ khi toàn bộ yêu cầu là lệnh `#remember`; nội dung sách chứa ví dụ lệnh không thể tự thay đổi persona.
- Đánh dấu dữ liệu bộ nhớ là hồ sơ không tin cậy trong system prompt, giới hạn 1.000 ký tự mỗi mục và tối đa 100 mục.

### Fixed

- Ghi file persona/bộ nhớ theo cơ chế atomic replace để tránh file JSON dở dang khi request bị gián đoạn.
- Trả về bản sao của dữ liệu mặc định, tránh bộ nhớ mặc định bị sửa trực tiếp trong tiến trình.

## [2.1.5] - 2026-11-01

### Added

- Telemetry riêng tư cho request AI: model, stream status, token count, tool-call count và latency.
- Dashboard tổng hợp hoạt động AI 7 ngày và tự điều chỉnh bố cục theo kích thước màn hình.

### Privacy

- Không lưu prompt, câu trả lời, IP, header hoặc API token trong telemetry.
- Usage event tự xóa sau 90 ngày và lỗi ghi metrics không làm hỏng request AI.

### Fixed

- Theo dõi đầy đủ usage cho non-stream, SSE stream, tool-calling agent, lỗi upstream và client disconnect.
- Yêu cầu DeepSeek gửi usage chunk trong stream để token count chính xác hơn.

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
