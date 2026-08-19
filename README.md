# Kindle AI Gateway (Dokploy & KOAssistant)

Gateway trung gian chuẩn hóa OpenAI API cho thiết bị **Amazon Kindle** (chạy **KOReader + KOAssistant**), tích hợp:
- **Tự động Web Search** (DuckDuckGo / Tavily) giúp AI cập nhật dữ liệu thời gian thực.
- **Bộ lọc chuyên dụng cho E-ink**: Tự động loại bỏ Emoji, tối ưu hóa ngắt đoạn, căn chỉnh tiếng Việt cho Kindle Paperwhite.
- **Xác thực bảo mật**: Quản lý bằng Bearer Token bảo vệ API.
- **Hỗ trợ Streaming SSE**: Phản hồi theo thời gian thực cực kỳ mượt mà.

---

## 1. Cài đặt biến môi trường trên Dokploy

Khi tạo ứng dụng trên **Dokploy** (chọn Docker hoặc Git repository), cấu hình các biến môi trường (Environment Variables):

| Tên biến | Bắt buộc | Mô tả |
|---|---|---|
| `DEEPSEEK_API_KEY` | **Có** | API Key lấy từ [platform.deepseek.com](https://platform.deepseek.com) |
| `AUTH_TOKEN` | **Có** | Mã bí mật do bạn tự đặt (dùng để điền vào Kindle) |
| `ENABLE_WEB_SEARCH` | Không | `true` (mặc định bật tự động tìm kiếm web) |
| `TAVILY_API_KEY` | Không | API Key từ Tavily (nếu muốn tăng tốc độ tìm kiếm) |

---

## 2. Cấu hình Domain & SSL trên Dokploy
1. Trong Dokploy, thêm Domain: `kindle.alphatech.ai.vn`.
2. Trỏ port container vào `8000`.
3. Bật tự động cấp phát SSL / HTTPS (Let's Encrypt / Traefik).

---

## 3. Cấu hình trên Kindle (KOReader + KOAssistant)
1. Mở **KOReader** trên Kindle.
2. Mở menu trên cùng → Chọn **Tools (Cờ lê)** → **Trang 2** → **KOAssistant** → **API Keys**.
3. Chọn Provider: **Custom OpenAI Compatible** (hoặc `OpenAI Compatible`).
4. Điền các thông số:
   - **Base URL**: `https://kindle.alphatech.ai.vn/v1`
   - **API Key**: Mã `AUTH_TOKEN` bạn đã đặt ở trên.
   - **Model**: `deepseek-chat` hoặc `alex-agent`.
5. Vào **Settings** → **AI Language Settings** → Chọn **Vietnamese**.

---

## 4. Kiểm tra hoạt động
1. Thử chat một câu hỏi thời sự (ví dụ: *"Tin tức công nghệ mới nhất hôm nay là gì?"*).
2. Server sẽ tự động kích hoạt **Web Search** → gom dữ liệu gửi DeepSeek → làm sạch Emoji → trả kết quả tiếng Việt mượt mà về Kindle!
