"""Generate user guide files for Kindle Paperwhite 4 in E:/documents/Books."""

import html
import zipfile
from pathlib import Path

target_dir = Path("E:/documents/Books")
target_dir.mkdir(parents=True, exist_ok=True)

md_content = """# SỔ TAY TOÀN TẬP HƯỚNG DẪN SỬ DỤNG KINDLE PAPERWHITE 4
## Trạm Tri Thức AI, Kho Truyện Tranh Cloud, Từ Điển Offline & Hệ Sinh Thái E-ink

---

## 1. TỔNG QUAN HỆ THỐNG ĐÃ NÂNG CẤP

Chiếc Kindle Paperwhite 4 của bạn đã được tối ưu hóa toàn diện thành một thiết bị đọc sách và nghiên cứu thông minh:
- **Phần cứng**: Màn hình 6-inch E-ink Carta 300 DPI chống chói lóa mắt, đèn nền dịu nhẹ điều chỉnh linh hoạt hai tông màu sáng/ấm.
- **Hệ thống đọc sách chính**: **KOReader v2026.07.2** — đọc PDF, EPUB, MOBI, CBZ siêu nhanh, cắt lề thông minh, dàn trang mượt mà, tiết kiệm pin tối đa.
- **Trợ lý AI & Kho tri thức**: **KOAssistant** kết nối trực tiếp với Kindle AI Gateway (`kindle.alphatech.ai.vn`) chạy mô hình alex-agent, DeepSeek, SQLite Vault, tìm kiếm Web thời gian thực và Bộ nhớ cá nhân thông minh.
- **Kho Truyện Tranh & Sách Cloud (Google Drive Integration)**: Kết nối kho truyện gần 800 tập / hơn 50 bộ truyện tranh PDF kinh điển qua chuẩn quốc tế OPDS 1.2 và Web Reader E-ink, tải theo nhu cầu (On-Demand) không lo đầy bộ nhớ trong.
- **Bộ từ điển Anh - Việt Thích Học Offline**: Hàng trăm ngàn mục từ dịch nghĩa tiếng Việt sắc nét, tra cứu tức thì khi chạm vào từ mà không cần Wi-Fi.
- **Bộ công cụ giải trí & rèn luyện tư duy 7-trong-1**:
  + Game Cờ Vây (Go / Weiqi) tích hợp AlphaGo Cloud AI 9-Đẳng.
  + Game Cờ Thú (Animal Chess / Jungle) chuẩn E-ink với chế độ "Linh Thú Thức Tỉnh", Voi & Chó bơi lội, đòn đánh "Cá Sấu Lên Bờ".
  + Bộ 6 Board Games kinh điển (Cờ vua, Cờ đam, Connect 4, Tic Tac Toe, Dò mìn, Thủy chiến).
  + Ứng dụng phác thảo tư duy & Wireframe (Ink Away).
- **Hệ thống truyền file không dây (Wireless Sync)**: SSH/SFTP Server, Calibre Wireless, KOReader Sync (KOSync).

---

## 2. TRỢ LÝ AI KOASSISTANT: TRA CỨU WEB, TÓM TẮT & HỎI ĐÁP THỜI GIAN THỰC

### CÁCH 1: Bộ 9 Nút Tác Vụ 1-Chạm Khi Đang Đọc Sách (Khuyên dùng — Không cần gõ phím)

Bàn phím ảo trên màn hình E-ink gõ tương đối chậm, vì vậy hệ thống đã trang bị sẵn **9 nút tác vụ 1-chạm** cực kỳ tiện lợi:
1. Khi đang đọc một cuốn sách, dùng ngón tay bôi đen (highlight) một cụm từ, đoạn văn hoặc câu hỏi bạn thắc mắc.
2. Thanh công cụ màu trắng hiện lên -> Chạm vào biểu tượng **KOAssistant** (hình robot hoặc hội thoại).
3. Chạm vào 1 trong 9 tác vụ chuyên sâu:
   - **[Tra cứu Web (#search)]**: Tự động mang từ vừa bôi đen tìm kiếm trên Google/Web và tóm lược thông tin thời sự mới nhất kèm nguồn tin.
   - **[Tra Wikipedia (#wiki)]**: Tra nhanh Bách khoa toàn thư Wikipedia tiếng Việt.
   - **[Tóm tắt cốt lõi]**: AI tự động đúc kết 3 luận điểm quan trọng nhất của đoạn trích bằng gạch đầu dòng ngắn gọn.
   - **[Giải thích sâu & Ví dụ]**: Giải thích cặn kẽ bản chất khái niệm và lấy 1 ví dụ thực tế minh họa sinh động theo đúng bối cảnh cuốn sách bạn đang đọc.
   - **[Phản biện & Góc nhìn]**: Đóng vai chuyên gia phản biện, đưa ra 2 góc nhìn đa chiều và 1 câu hỏi đào sâu tư duy.
   - **[Bài học thực hành]**: Rút ra 1-2 hành động cụ thể có thể áp dụng ngay vào công việc và đời sống.
   - **[Lưu Vault (#note)]**: Lưu tự động đoạn trích vào kho tri thức cá nhân trên Server đám mây (có gắn kèm tên sách).
   - **[Lưu Việc (#todo)]**: Biến ý tưởng trong trang sách thành 1 việc cần làm (task) lưu vào kho việc.
   - **[Tổng quan sách]**: Chạm khi không bôi đen từ nào để AI tóm lược toàn cảnh cuốn sách bạn đang mở (chủ đề, bối cảnh, 3 giá trị nổi bật).

---

### CÁCH 2: Gõ Lệnh Trực Tiếp Trong Ô Chat Của KOAssistant

1. Bôi đen văn bản hoặc mở khung chat của KOAssistant.
2. Chạm vào ô nhập liệu ở đáy (`Type your message...`): Bàn phím ảo sẽ trượt lên.
3. Gõ câu hỏi hoặc các lệnh nhanh:
   - `#search <nội dung>`: Tìm kiếm web thời gian thực (ví dụ: `#search giá vàng hôm nay tại Việt Nam`, `#search tổng thống Mỹ mới nhất`).
   - `#wiki <nội dung>`: Tra cứu bách khoa toàn thư.
   - Nhấn **Send** (hoặc Enter) để nhận câu trả lời súc tích tối ưu cho màn hình E-ink.

---

### CÁCH 3: Mở Khung Chat Tự Do (General Chat) Khi Không Đọc Sách

1. Chạm mép trên cùng màn hình để hiện menu chính của KOReader.
2. Chọn tab **Công cụ (Tools)** (biểu tượng cờ lê / bánh răng).
3. Chọn mục **KOAssistant** -> Chọn **General Chat / Action**.
4. Hộp thoại mở ra để bạn trò chuyện, hỏi đáp tự do với AI như ChatGPT trên màn hình E-ink.

---

## 3. BỘ NHỚ VÀ QUẢN LÝ GHI CHÚ CÁ NHÂN VỚI AI

Trong ô chat của KOAssistant, bạn có thể dạy AI hiểu thói quen của bạn và quản lý ghi chú:
- `#remember [chủ đề] <nội dung>`: Dạy AI ghi nhớ ngữ cảnh và phong cách của bạn (Ví dụ: `#remember [chuyên môn] Tôi là lập trình viên backend, hãy giải thích bằng tư duy logic và code minh họa`).
- `#memory`: Xem 10 điều ghi nhớ gần nhất AI đang lưu về bạn.
- `#note [tiêu đề] <nội dung>`: Lưu nhanh một ghi chú, ý tưởng vào kho SQLite Vault đám mây.
- `#todo <công việc>`: Thêm một công việc cần làm vào danh sách việc.
- `#help`: Xem danh sách tất cả các lệnh hỗ trợ trực tiếp trên màn hình.

---

## 4. KHO TRUYỆN TRANH & SÁCH CLOUD TỪ GOOGLE DRIVE (OPDS & WEB READER)

Bộ nhớ trong của Kindle chỉ có vài GB. Toàn bộ kho truyện tranh gần 800 tập / hơn 50 bộ truyện kinh điển (*Bác Sĩ Quái Dị*, *7 Seeds*, *07-Ghost*, *Ouran High School*, *1-00 AM*, *Siêu Nhân May Mắn*, *Ashita No Joe*, *Bad Luck*, *Basara*, *BEASTARS*, *Biệt Đội Lính Cứu Hỏa*, v.v.) được lưu trên Google Drive. Bạn có thể duyệt và tải về đọc từng tập theo nhu cầu (On-Demand), đọc xong xóa đi để giải phóng bộ nhớ mà không bao giờ mất file gốc.

### CÁCH 1: Duyệt thư viện OPDS trong KOReader (Khuyên dùng — Đọc sướng nhất)

1. Bật Wi-Fi trên máy Kindle.
2. Trong KOReader, chạm mép trên màn hình để mở menu.
3. Chạm vào biểu tượng **Kính lúp / Tủ sách** (Search & Library) ở góc trên bên trái.
4. Chọn **"OPDS catalog" (Thư viện OPDS)**.
5. Chọn **"Add catalog" (Thêm thư viện mới)**:
   - Tên thư viện: `Kindle Cloud Manga`
   - Địa chỉ URL: `https://kindle.alphatech.ai.vn/opds`
6. Bấm **Lưu (Save)**.
7. Mở `Kindle Cloud Manga` -> Chọn `📁 Danh Mục Các Bộ Truyện` -> Chọn bộ truyện yêu thích -> Chạm vào tập muốn đọc để tải về máy và mở đọc ngay tức thì!

---

### CÁCH 2: Dùng Trình duyệt Web tích hợp của Kindle (Web Browser)

1. Bật Wi-Fi trên Kindle.
2. Từ màn hình chính của Kindle, chạm vào nút Menu ba chấm ở góc trên bên phải -> Chọn **Web Browser (Trình duyệt thử nghiệm)**.
3. Nhập địa chỉ: `https://kindle.alphatech.ai.vn/library`
4. Giao diện E-ink đen trắng sắc nét hiện ra: Chọn bộ truyện và bấm nút **[Tải Về Đọc]** ở tập mong muốn.

---

### CÁCH 3: Quản lý kho sách trên máy tính / điện thoại (Gateway Webapp)

- Truy cập trang quản trị: `https://kindle.alphatech.ai.vn/admin/library`
- Bấm nút **"Đồng Bộ Danh Mục Ngay" (Scan Google Drive)** khi có thêm truyện mới vào Drive để hệ thống tự động quét ngầm.
- Theo dõi dung lượng bộ nhớ đệm (SSD Cache) trên máy chủ Gateway.

---

## 5. TRA CỨU TỪ ĐIỂN ANH - VIỆT OFFLINE & KHO TỪ VỰNG (VOCABULARY BUILDER)

Chiếc Kindle đã được tích hợp bộ từ điển **Anh - Việt Thích Học Offline (19MB)** với hàng trăm ngàn từ:

### Cách tra từ điển khi đọc sách tiếng Anh:
1. Khi đang đọc một cuốn sách tiếng Anh, chạm ngón tay vào từ bạn chưa biết nghĩa.
2. Bảng tra từ điển sẽ lập tức bật lên hiển thị: phiên âm quốc tế IPA, từ loại (danh từ, động từ...), các tầng nghĩa tiếng Việt chi tiết và ví dụ ngữ cảnh.
3. Toàn bộ hoạt động **hoàn toàn offline**, không cần bật Wi-Fi, tốc độ tra tức thì chỉ 0.1 giây.

### Kho từ vựng (Vocabulary Builder):
- Mỗi khi bạn tra một từ mới trong lúc đọc sách, hệ thống sẽ tự động lưu từ đó vào danh sách từ vựng.
- Để ôn tập từ vựng: Chạm mép trên màn hình -> Tab **Công cụ (Tools)** -> Chọn **Vocabulary Builder** để lật các thẻ flashcard ôn lại nghĩa của các từ đã tra.

---

## 6. HƯỚNG DẪN CHI TIẾT BỘ 7 GAME E-INK & CÁCH CHƠI

Hệ thống có 7 game được thiết kế riêng cho màn hình mực điện tử E-ink (không giật lag, độ tương phản tuyệt đối):

### Nhóm 1: Game Cờ Vây (Go / Weiqi) — TÍCH HỢP ALPHAGO CLOUD AI!
- Cách mở: Menu Công cụ (Tools) -> Chọn [Go].
- Chế độ đối thủ (Menu 3 gạch ở góc trên bên trái):
  + **Đối thủ: Cloud AI 🌐 (AlphaGo)**: Kết nối Siêu AI AlphaGo qua Gateway. AI phân tích chiến thuật, dự đoán tỷ lệ thắng % và gợi ý nước đi chuẩn kỳ thủ chuyên nghiệp.
  + **Đối thủ: Bot Máy 🤖 (Offline)**: 3 cấp độ (Beginner / Medium / Advanced) đánh offline không cần mạng.
  + **Đối thủ: 2 Người 👥 (Chuyền tay)**: Chơi cùng bạn bè trên cùng máy Kindle.
- Bàn cờ: Hỗ trợ bàn 9x9, 13x13, 19x19.

### Nhóm 2: Game Cờ Thú (Animal Chess / Jungle) — LINH THÚ THỨC TỈNH
- Cách mở: Menu Công cụ (Tools) -> Chọn [Cờ Thú (Jungle Game)].
- Quân cờ vẽ bằng Icon Linh Thú nghệ thuật sắc nét 300 DPI.
- Cấp bậc: (8) Voi > (7) Sư Tử > (6) Hổ > (5) Báo > (4) Chó > (3) Sói > (2) Mèo > (1) Chuột.
- Đặc quyền đặc sắc:
  + Chuột (1) ăn được Voi (8). Voi không ăn được Chuột.
  + **Sông nước & Đòn đánh "Cá Sấu Lên Bờ"**: Chuột (1), Chó (4) và Voi (8) đều có thể bơi lội dưới sông. Thú dưới nước có thể lao từ dưới nước lên cạn để bắt thú đối phương!
  + Sư Tử (7), Hổ (6) và Báo (5) có thể nhảy bay qua sông nếu không có thú bơi cản đường.
  + Phân biệt địa hình: Sông có gợn sóng đôi `~ ~ ~`; Bẫy nền trắng tinh có 4 góc ngắm `┌ ┐ └ ┘`.
- Tùy chọn [Luật: Thức Tỉnh ✨]: Sói đi cạnh đồng minh được +1 cấp; Báo phi nhanh 2 ô cạn; Mèo 9 mạng né đòn; Thú diệt 2 quân được Thăng cấp tỏa hào quang.

### Nhóm 3: Gói Board Games 6-trong-1
- Cách mở: Menu Công cụ (Tools) -> Chọn [Board Games].
- Chạm nút **[Settings]** -> **[Choose Game]** để chọn 1 trong 6 trò chơi:
  1. **Thủy Chiến (Battleship)**: Bố trí hạm đội 5 tàu (có nút *Random Fleet* tự xếp trong 1 giây) và nã pháo bắn chìm tàu địch.
  2. **Dò Mìn (Minesweeper)**: Bàn cờ 9x9, chạm mở ô và nút [Flag] cắm cờ đánh dấu mìn.
  3. **Cờ Vua (Chess)**: Hỗ trợ đánh với máy hoặc 2 người, đầy đủ luật nhập thành, bắt tốt qua đường, phong cấp.
  4. **Cờ Đam (Checkers)**: Nhảy chéo ăn quân, phong Vua khi sang hàng cuối.
  5. **Connect 4**: Thả quân nối 4 chấm liên tiếp để thắng.
  6. **Tic Tac Toe**: Cờ ca-rô 3x3 giải trí nhanh.

---

## 7. PHÁC THẢO SƠ ĐỒ TƯ DUY & WIREFRAME (INK AWAY)

- Cách mở: Menu Công cụ (Tools) -> **Ink Away** (hoặc vuốt từ mép phải màn hình lên).
- Vẽ hình khối (Chữ nhật, Tròn, Mũi tên), chèn chữ Text box để tạo sơ đồ tư duy hoặc phác thảo giao diện wireframe.
- Xuất file ảnh PNG làm hình nền khóa màn hình (Sleep screen) hoặc xuất file gửi về máy tính.

---

## 8. TRUYỀN FILE SÁCH & ĐỒNG BỘ KHÔNG DÂY QUA WI-FI (KHÔNG CẦN CÁP USB)

Bạn không cần phải cắm cáp USB vào máy tính mỗi khi muốn chép sách:

### 1. Truyền file qua SSH / SFTP (Khuyên dùng):
- Bật Wi-Fi trên Kindle.
- Trong KOReader, chạm mép trên màn hình -> Tab **Công cụ (Tools)** -> Chọn **SSH Server** -> Bật ON.
- Màn hình sẽ hiện địa chỉ IP (ví dụ: `192.168.1.50`) và cổng (mặc định: `2222`).
- Trên máy tính, mở phần mềm WinSCP, FileZilla hoặc File Explorer gõ `sftp://192.168.1.50:2222`: Bạn có thể kéo thả sách trực tiếp từ PC vào thư mục `documents/Books` trên Kindle với tốc độ Wi-Fi siêu nhanh.

### 2. Kết nối Calibre không dây (Calibre Wireless):
- Bật Calibre trên máy tính -> Menu Kết nối -> Khởi chạy Content Server.
- Trên KOReader: Menu Kính lúp/Tủ sách -> Chọn **Calibre** -> Kết nối để gửi sách từ Calibre sang Kindle qua Wi-Fi.

### 3. Đồng bộ trang đọc dở (KOReader Sync - KOSync):
- Menu Kính lúp/Tủ sách -> Chọn **KOReader Sync**.
- Đăng ký một tài khoản miễn phí: Khi đọc dở một cuốn sách trên Kindle, bạn mở KOReader trên điện thoại Android/iOS sẽ tự động nhảy đến đúng trang sách đó!

---

## 9. ĐỒNG BỘ GHI CHÚ VỀ MÁY TÍNH (OBSIDIAN / NOTION)

Mọi ghi chú bạn lưu bằng `#note` trên Kindle đều nằm an toàn trên server SQLite Vault.
- Khi ngồi vào bàn làm việc, mở Terminal trên máy tính và chạy:
  `python scripts/sync_vault_notes.py`
- Toàn bộ ghi chú đọc sách ban đêm sẽ tự động được kéo về thư mục `vault_notes` trên PC dưới dạng Markdown hoàn chỉnh, có phân loại theo từng cuốn sách và liên kết 2 chiều (backlinks).

---

## 10. CÁC PHÍM TẮT, CỬ CHỈ & THAO TÁC CẦN NHỚ TRÊN KOREADER

- **Chỉnh đèn nền cực nhanh**:
  + Vuốt ngón tay lên/xuống ở **mép viền trái màn hình**: Tăng/giảm độ sáng đèn.
  + Vuốt ngón tay lên/xuống ở **mép viền phải màn hình**: Tăng/giảm nhiệt độ màu (ấm / trắng).
- **Đánh dấu trang (Bookmark)**: Chạm nhanh 1 cái vào góc trên cùng bên phải trang sách.
- **Mở Mục lục & Tiến độ đọc**: Chạm nhẹ vào mép dưới cùng màn hình.
- **Xem Thống kê đọc sách**: Tab Công cụ (Tools) -> Reading Statistics để xem biểu đồ số giờ đọc, tốc độ đọc và số trang đã đọc trong ngày/tuần.
- **Thoát về giao diện Kindle gốc**:
  + Chạm mép trên màn hình -> Tab **Cài đặt / Nguồn** (biểu tượng bánh răng hoặc nút nguồn ở góc phải) -> Chọn **Exit** -> Chọn **Exit to Kindle OS**.
- **Mở lại KOReader từ Kindle gốc**:
  + Ở màn hình chính Kindle (Home), bấm vào cuốn sách có tên **KOReader** (hoặc mở menu KUAL -> KOReader).
- **Mẹo tiết kiệm pin**: Nên tắt Wi-Fi khi đọc sách thông thường; chỉ bật Wi-Fi khi cần hỏi AI KOAssistant, duyệt kho truyện Cloud hoặc đồng bộ ghi chú.

---

Chúc bạn có những trải nghiệm đọc sách, nghiên cứu và giải trí tuyệt vời nhất trên chiếc Kindle Paperwhite 4!
"""

# 1. Write Markdown file
with open(target_dir / "HUONG_DAN_SU_DUNG_KINDLE.md", "w", encoding="utf-8") as f:
    f.write(md_content)

# 2. Write Plain Text file
with open(target_dir / "HUONG_DAN_SU_DUNG_KINDLE.txt", "w", encoding="utf-8") as f:
    f.write(md_content)

# 3. Create EPUB file
epub_path = target_dir / "HUONG_DAN_SU_DUNG_KINDLE.epub"
with zipfile.ZipFile(epub_path, "w") as zf:
    zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
    zf.writestr("META-INF/container.xml", container_xml, compress_type=zipfile.ZIP_DEFLATED)

    paragraphs = []
    for line in md_content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            paragraphs.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            paragraphs.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            paragraphs.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("#### "):
            paragraphs.append(f"<h4>{html.escape(line[5:])}</h4>")
        elif line.startswith("- "):
            paragraphs.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("+ "):
            paragraphs.append(f"<li>{html.escape(line[2:])}</li>")
        elif line == "---":
            paragraphs.append("<hr/>")
        else:
            paragraphs.append(f"<p>{html.escape(line)}</p>")

    body_html = "\n".join(paragraphs)
    xhtml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="vi">
<head>
  <title>Hướng Dẫn Sử Dụng Kindle Toàn Tập</title>
  <style>
    body {{ font-family: serif; margin: 4%; line-height: 1.5; }}
    h1 {{ text-align: center; font-size: 1.5em; margin-bottom: 0.5em; }}
    h2 {{ font-size: 1.25em; margin-top: 1.2em; border-bottom: 1px solid #444; padding-bottom: 4px; }}
    h3 {{ font-size: 1.1em; margin-top: 1em; color: #222; }}
    h4 {{ font-size: 1.0em; margin-top: 0.8em; font-style: italic; }}
    li {{ margin-bottom: 0.4em; }}
    p {{ text-indent: 1em; margin: 0.4em 0; }}
    hr {{ border: none; border-top: 1px dashed #777; margin: 1em 0; }}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""
    zf.writestr("OEBPS/guide.xhtml", xhtml_content, compress_type=zipfile.ZIP_DEFLATED)

    content_opf = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookID">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Sổ Tay Toàn Tập Hướng Dẫn Sử Dụng Kindle</dc:title>
    <dc:creator>Antigravity</dc:creator>
    <dc:language>vi</dc:language>
    <dc:identifier id="BookID">urn:uuid:kindle-guide-2026-11-03-v4-full</dc:identifier>
  </metadata>
  <manifest>
    <item id="guide" href="guide.xhtml" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="guide"/>
  </spine>
</package>"""
    zf.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)

    toc_ncx = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:kindle-guide-2026-11-03-v4-full"/>
  </head>
  <docTitle><text>Sổ Tay Toàn Tập Hướng Dẫn Sử Dụng Kindle</text></docTitle>
  <navMap>
    <navPoint id="navPoint-1" playOrder="1">
      <navLabel><text>Bắt Đầu</text></navLabel>
      <content src="guide.xhtml"/>
    </navPoint>
  </navMap>
</ncx>"""
    zf.writestr("OEBPS/toc.ncx", toc_ncx, compress_type=zipfile.ZIP_DEFLATED)

print(f"SUCCESS: Generated detailed guide files in {target_dir}")
