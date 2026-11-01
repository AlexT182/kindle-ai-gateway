# Kindle AI Gateway

Gateway OpenAI-compatible dành cho Kindle chạy KOReader + KOAssistant. `alex-agent` có thể tự chọn các công cụ chỉ-đọc (web, thời tiết, Wikipedia, crypto và Kindle Vault), nhưng bị giới hạn số bước và không được chạy shell hay tự ý ghi dữ liệu.

## Cấu hình bắt buộc

Yêu cầu Python 3.11 trở lên. Sao chép `.env.example` thành `.env` và đặt các biến sau:

| Biến | Mục đích |
|---|---|
| `DEEPSEEK_API_KEY` | Khóa API của nhà cung cấp AI |
| `AUTH_TOKEN` | Token máy ngẫu nhiên, tối thiểu 32 ký tự; nhập token này vào KOAssistant |
| `ADMIN_PASSWORD` | Mật khẩu riêng để đăng nhập `/admin`, tối thiểu 12 ký tự |
| `SESSION_SECRET` | Khóa ký cookie ngẫu nhiên và độc lập, tối thiểu 32 ký tự |

Không dùng cùng một giá trị cho ba secret. Không truyền secret trên URL. Ứng dụng sẽ từ chối khởi động nếu cấu hình yếu hoặc còn giá trị mặc định cũ.

Có thể tạo hai giá trị ngẫu nhiên bằng Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Chạy lệnh hai lần: một lần cho `AUTH_TOKEN`, một lần cho `SESSION_SECRET`.

## Chạy và kiểm thử

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Hoặc dùng Docker Compose:

```bash
docker compose up --build -d
```

Compose gắn volume `kindle_ai_data` vào `/data`, chạy container bằng user không phải root, bật read-only root filesystem và bỏ Linux capabilities.
Image production dùng `requirements.lock` để khóa cả dependency trực tiếp và bắc cầu; cập nhật lock cùng lúc khi nâng dependency.

## Cấu hình KOAssistant

- Base URL: `https://kindle.alphatech.ai.vn/v1`
- API Key: giá trị `AUTH_TOKEN` (không phải mật khẩu admin)
- Model: `alex-agent`
- Language: Vietnamese

Gateway chấp nhận `Authorization: Bearer`, `X-API-Key` hoặc `api-key` header để tương thích client. Token trong query string bị từ chối.

## Triển khai Dokploy

1. Cấu hình bốn biến bắt buộc trong Environment của Dokploy; không commit `.env`.
2. Gắn persistent volume vào `/data` trước lần deploy đầu tiên.
3. Trỏ domain HTTPS vào port container `8000`.
4. Deploy rồi kiểm tra `/health` trả `200`.
5. Xác nhận `/v1/models` trả `401` khi không có token và `200` khi có Bearer token đúng.
6. Cập nhật token mới trong KOAssistant sau khi production đã khỏe.

Có thể chạy smoke test chỉ-đọc sau mỗi lần deploy:

```powershell
$env:BASE_URL = "https://kindle.alphatech.ai.vn"
$env:AUTH_TOKEN = "<machine token>"
python scripts/smoke_production.py
```

Script kiểm tra health, trang đăng nhập, API auth, bảo vệ graph và CORS; không gọi model AI và không ghi dữ liệu.

Endpoint `/health` cũng kiểm tra khả năng truy cập SQLite Vault; nếu volume hoặc database lỗi, endpoint trả `503` thay vì báo healthy giả.

Trong Dashboard, nút **Tải backup Vault** tạo một ZIP nhất quán gồm SQLite snapshot, ghi chú Markdown và cấu hình trong `/data`. Backup yêu cầu đăng nhập admin và CSRF token; archive tạm được xóa ngay sau khi gửi xong.

Gateway tắt access-log thô của Uvicorn và phát log vận hành dạng tối giản gồm request ID, method, path, status và latency. Query string, token, header và nội dung request không được ghi vào log.

`ALLOWED_ORIGINS` mặc định rỗng vì Kindle/native client không cần CORS. Chỉ thêm các origin HTTPS cụ thể nếu có frontend web khác domain; không dùng `*`.

## Lưu ý dữ liệu và lịch sử Git

Thư mục `data/` là dữ liệu runtime và đã bị loại khỏi Git. Việc xóa các file cũ khỏi commit mới không xóa chúng khỏi lịch sử repository; nếu dữ liệu từng công khai là nhạy cảm, cần rotate secret trước rồi thực hiện một đợt rewrite history riêng có sao lưu và phê duyệt.
