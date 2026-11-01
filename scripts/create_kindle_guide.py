"""Generate user guide files for Kindle Paperwhite 4 in E:/documents/Books."""

import html
import zipfile
from pathlib import Path

target_dir = Path("E:/documents/Books")
target_dir.mkdir(parents=True, exist_ok=True)

md_content = """# SỔ TAY HƯỚNG DẪN SỬ DỤNG KINDLE PAPERWHITE 4
## Trạm Tri Thức AI, Hướng Dẫn Tra Cứu Web & Bộ 7 Game E-ink

---

## 1. TỔNG QUAN HỆ THỐNG

Chiếc Kindle Paperwhite 4 của bạn đã được nâng cấp toàn diện:
- Phần cứng: Màn hình 6-inch E-ink Carta 300 DPI chống lóa, đèn nền tích hợp.
- Hệ thống đọc sách: KOReader v2026.07.2 — hiển thị đẹp, tiết kiệm pin, lật trang nhanh.
- Trợ lý AI & Kho tri thức: KOAssistant kết nối trực tiếp với Kindle AI Gateway (chạy model alex-agent, DeepSeek, SQLite Vault, tìm kiếm Web thời gian thực và Bộ nhớ cá nhân).
- Bộ công cụ giải trí & tư duy:
  + Bộ 6 Board Games kinh điển (Cờ vua, Cờ đam, Connect 4, Tic Tac Toe, Dò mìn, Thủy chiến).
  + Game Cờ vây (Go / Weiqi) hỗ trợ bàn 9x9, 13x13, 19x19 đấu với bot AI.
  + Ứng dụng phác thảo tư duy & Wireframe (Ink Away).

---

## 2. HƯỚNG DẪN CHI TIẾT: GÕ LỆNH #SEARCH Ở ĐÂU VÀ NHƯ THẾ NÀO?

Nhiều bạn thắc mắc: "Làm sao để gõ được lệnh #search trên máy đọc sách? Gõ ở chỗ nào?". Dưới đây là hướng dẫn cụ thể từng bước:

### CÁCH 1: Gõ trực tiếp trong ô Chat của KOAssistant (Bất kỳ lúc nào)

1. Khi đang mở một cuốn sách trong KOReader:
   - Dùng ngón tay chạm và giữ (hoặc quét ngang) để bôi đen (highlight) một từ hoặc một câu bất kỳ trên màn hình.
   - Một thanh công cụ màu trắng hiện lên: Bạn tìm và chạm vào biểu tượng KOAssistant (hình robot hoặc biểu tượng trò chuyện).
2. Khi hộp thoại KOAssistant xuất hiện:
   - Nhìn xuống dưới đáy hộp thoại, bạn sẽ thấy một ô nhập liệu có dòng chữ gợi ý: `Type your message...` (hoặc `Nhập tin nhắn...`).
   - Chạm ngón tay vào ô này: Bàn phím ảo của KOReader sẽ trượt lên từ cạnh dưới màn hình.
3. Gõ lệnh và gửi:
   - Gõ chính xác dấu `#` rồi đến chữ `search` và nội dung câu hỏi.
     Ví dụ: `#search giá vàng hôm nay tại Việt Nam`
     Ví dụ: `#search kết quả bóng đá ngoại hạng Anh mới nhất`
     Ví dụ: `#search ai đang là tổng thống Mỹ`
   - Nhấn nút Send (hoặc Enter) trên bàn phím ảo.
   - Gateway sẽ lập tức điều khiển bot tìm kiếm Google/Web, đọc các bài báo mới nhất và trả về câu trả lời tổng hợp súc tích kèm nguồn tin!

---

### CÁCH 2: Dùng nút 1-Chạm "Tra cứu Web (#search)" (KHÔNG CẦN GÕ PHÍM)

Bàn phím ảo trên màn hình E-ink gõ tương đối chậm. Vì vậy, hệ thống đã trang bị sẵn nút 1-chạm để bạn tra cứu tức thì:

1. Khi đang đọc sách, gặp một nhân vật, sự kiện hoặc khái niệm thời sự chưa rõ:
   - Bôi đen (highlight) cụm từ đó (ví dụ: bôi đen từ "Sam Altman" hoặc "Quantum Computing").
2. Chạm vào biểu tượng KOAssistant trên thanh công cụ.
3. Trong danh sách các nút tác vụ hiện ra, chạm ngay vào:
   - [Tra cứu Web (#search)]: Hệ thống tự động lấy từ vừa bôi đen mang đi tìm kiếm trên Web và tóm lược ngay lập tức!
   - [Tra Wikipedia (#wiki)]: Nếu muốn tra bách khoa toàn thư Wikipedia tiếng Việt.

---

### CÁCH 3: Mở khung Chat Tự Do (General Chat) khi không đọc sách

Nếu bạn đang ở màn hình duyệt file (File Manager) hoặc muốn hỏi đáp độc lập mà không cần mở sách:
1. Chạm vào mép trên cùng màn hình để hiện thanh menu chính của KOReader.
2. Chọn tab Công cụ (Tools) (biểu tượng cờ lê / bánh răng).
3. Chọn mục KOAssistant -> Chọn General Chat / Action.
4. Hộp thoại chat mở ra -> Chạm vào ô nhập tin nhắn ở đáy -> Gõ `#search <nội dung>` và nhấn Gửi.

---

## 3. BỘ NHỚ VÀ QUẢN LÝ GHI CHÚ CÁ NHÂN VỚI AI

Trong cùng ô nhập tin nhắn của KOAssistant, bạn có thể dùng các lệnh sau:

- #remember [chủ đề] <nội dung>
  Mục đích: Dạy AI hiểu bối cảnh và sở thích của bạn để câu trả lời sau này luôn đúng ý.
  Ví dụ: `#remember [chuyên môn] Tôi là lập trình viên backend, hãy giải thích bằng tư duy logic và code minh họa.`
- #memory
  Mục đích: Hiển thị 10 điều ghi nhớ gần nhất mà AI đang lưu giữ về bạn.
- #note [tiêu đề] <nội dung>
  Mục đích: Lưu một ý tưởng hay vào kho ghi chú cá nhân (SQLite Vault).
- #todo <công việc>
  Mục đích: Thêm một việc cần làm vào danh sách task.
- #help
  Mục đích: Xem nhanh danh sách các lệnh trợ giúp ngay trên Kindle.

---

## 4. HƯỚNG DẪN CHI TIẾT BỘ 7 GAME E-INK & CÁCH CHƠI

Hiện tại thiết bị của bạn đã có 7 game được tối ưu riêng cho màn hình mực điện tử E-ink (không giật lag, không chớp nháy):

### Nhóm 1: Game Cờ Vây (Go / Weiqi) — ĐÃ TÍCH HỢP ALPHAGO CLOUD AI!

- Cách mở: Chạm mép trên màn hình -> Tab Công cụ (Tools) -> Chọn mục [Go].
- Cách đổi chế độ đối thủ & Cài đặt bàn cờ:
  Chạm vào biểu tượng Menu 3 gạch ở góc trên cùng bên trái thanh tiêu đề:
  + [Opponent]: Chạm để chuyển đổi 3 chế độ đối thủ:
    * Đối thủ: Bot Máy 🤖 (Offline): Đánh với Bot offline máy tính tích hợp sẵn, không cần Wi-Fi/Internet.
    * Đối thủ: Cloud AI 🌐 (AlphaGo): Kết nối với Siêu trí tuệ nhân tạo AlphaGo qua Gateway. AI tính toán nước cờ kỳ thủ đỉnh cao, hiển thị tỷ lệ thắng % và phân tích chiến thuật (Yêu cầu kết nối Wi-Fi & Internet).
    * Đối thủ: 2 Người 👥 (Chuyền tay): Hai người chơi đổi lượt trên cùng một chiếc Kindle.
  + [Bot: Beginner / Medium / Advanced]: Chạm vào dòng này để đổi 3 mức độ của bot máy offline:
    * Beginner (Tập sự): Máy đi ngẫu nhiên đơn giản, phù hợp làm quen luật cờ.
    * Medium (Tiêu chuẩn): Khai cuộc chiếm góc Hoshi, mở biên đường 3-4, cứu quân và bắt quân atari.
    * Advanced (Nâng cao): Áp dụng chiến thuật cờ vây toàn diện, nối quân Keima/Kosumi, bắt quân sát ván.
  + [Size]: Đổi kích thước bàn cờ (9x9, 13x13, 19x19).
- Cách chơi & Luật cơ bản:
  + Bạn đi quân Đen (đi trước), máy đi quân Trắng (Trắng được 6.5 điểm Komi).
  + Chạm vào các giao điểm trên bàn cờ để đặt quân.
  + Luật khí và bắt quân: Nhóm quân cờ sống nhờ các giao điểm trống liền kề ("khí"). Khi bị đối phương chặn hết khí, quân sẽ bị bắt và nhấc ra khỏi bàn cờ.
  + Mục tiêu: Vây chiếm các vùng đất trống. Bên nào kiểm soát diện tích đất và bắt được nhiều quân hơn sẽ chiến thắng.

---

### Nhóm 2: Game Cờ Thú (Animal Chess / Jungle) — LINH THÚ THỨC TỈNH

- Cách mở: Chạm mép trên màn hình -> Tab Công cụ (Tools) -> Chọn mục [Cờ Thú (Jungle Game)].
- Thiết kế riêng cho Kindle E-ink 300 DPI: Bàn cờ 7 cột x 9 hàng sắc nét, các ô sông nước, hang, bẫy và huy hiệu thú vẽ nổi bật.
- Cấp bậc 8 loài thú (Từ mạnh đến yếu):
  (8) Voi > (7) Sư Tử > (6) Hổ > (5) Báo > (4) Chó > (3) Sói > (2) Mèo > (1) Chuột.
- Quy tắc đặc sắc:
  + Chuột ăn Voi: Chuột (1) là loài duy nhất ăn được Voi (8) trên cạn! Ngược lại Voi không thể ăn Chuột.
  + Sông nước: Chỉ có Chuột được lặn dưới sông. Sư Tử (7) và Hổ (6) có quyền NHẢY QUA SÔNG theo chiều dọc hoặc ngang (nếu không có Chuột bơi cản giữa sông).
  + Ô Bẫy: Quân địch sập vào 3 ô Bẫy quanh hang bạn sẽ bị giảm sức mạnh về 0. Bất kỳ thú nào của bạn cũng có thể lao vào ăn nó!
  + Mục tiêu: Tiến 1 quân vào Hang đối thủ hoặc tiêu diệt toàn bộ quân địch để chiến thắng.
- Tùy chọn Chế độ & Cấp độ:
  + Đấu với Máy (Dễ / Vừa / Khó với thuật toán Minimax Alpha-Beta tính trước 3-4 nước cờ) hoặc 2 Người chuyền tay.
  + Nút [Đi Lại] (Undo) ngay ở thanh điều khiển đáy để rút lại nước cờ nhầm lẫn.
  + Tùy chọn [Luật: Cổ Điển 📜] hoặc [Luật: Thức Tỉnh ✨]:
    * Sói Bầy Đàn: Sói đi cạnh Chó/Báo đồng minh được +1 cấp sức mạnh (ăn được Chó).
    * Báo Lao Nhanh: Báo có thể phi thẳng 2 ô một lượt trên cạn nếu đường thông thoáng.
    * Mèo 9 Mạng: Lần đầu tiên bị ăn, Mèo tự động né đòn nhảy sang ô trống thoát chết.
    * Thăng Cấp: Thú nào ăn được 2 quân địch sẽ được Thăng cấp (+1 sao sức mạnh vĩnh viễn).

---

### Nhóm 3: Gói Board Games 6-trong-1

- Cách mở: Chạm mép trên màn hình -> Tab Công cụ (Tools) -> Chọn mục [Board Games].
- Điều khiển chung: Ở chân màn hình luôn có 4 nút:
  [Settings]      [Undo]      [Draw / Flag]      [Close]
  + Để đổi game: Chạm [Settings] -> [Choose Game] -> Chọn 1 trong 6 game bên dưới.
  + Để đổi độ khó / người chơi: Chạm [Settings] -> Chạm [Mode] (Solo/2 người) hoặc [Bot Level] (Dễ/Vừa/Khó).
  + Để thoát về sách: Chạm [Close] (góc dưới bên phải).

#### 1. Hướng dẫn chi tiết Game Thủy Chiến (Battleship):
Game mô phỏng cuộc chiến hải quân bắn hạ hạm đội đối phương, gồm 2 giai đoạn rõ ràng:
- Giai đoạn 1: Bố trí đội tàu (Setup Phase)
  + Bạn sở hữu 5 chiến hạm có độ dài khác nhau: Tàu sân bay (5 ô), Thiết giáp hạm (4 ô), Tuần dương hạm (3 ô), Tàu ngầm (3 ô), Tàu khu trục (2 ô).
  + Các nút ở thanh điều khiển dưới đáy:
    * [Rotate: H / V]: Đổi chiều xoay tàu (Ngang hoặc Dọc). Sau đó chạm lên ô bàn cờ để đặt tàu.
    * [Random Fleet]: NÚT QUAN TRỌNG NHẤT — Nếu lười xếp tay, hãy bấm nút này để máy tự động xếp ngẫu nhiên 5 tàu vào vị trí tối ưu trong 1 giây!
  + Sau khi đủ 5 tàu, trận chiến khai hỏa!
- Giai đoạn 2: Tác chiến bắn tàu (Battle Phase)
  + Dưới đáy màn hình có 2 nút chuyển đổi góc nhìn:
    * [Enemy Waters] (Vùng biển địch): Mặc định bạn sẽ ở góc nhìn này. Chạm ngón tay vào ô tọa độ bất kỳ để nã pháo!
      - Ký hiệu `X`: Bắn TRÚNG (Hit) vào thân tàu địch! Tiếp tục bắn các ô liền kề để đánh chìm hẳn con tàu.
      - Ký hiệu `o`: Bắn TRƯỢT (Miss) xuống nước.
    * [Your Fleet] (Hạm đội của bạn): Chạm nút này để xem bot đã bắn vào đâu trên đội tàu của mình.
  + Mục tiêu: Bắn chìm toàn bộ 5 tàu của bot trước khi hạm đội của bạn bị xóa sổ!

#### 2. Dò Mìn (Minesweeper):
- Bàn cờ 9x9 với 10 quả mìn ẩn giấu.
- Chạm vào ô để mở. Ô mở ra sẽ hiện số (số lượng mìn xung quanh ô đó).
- Nút [Flag] / [Reveal] ở đáy: Chạm để chuyển đổi giữa chế độ Mở ô và chế độ Cắm cờ đánh dấu ô có mìn.

#### 3. Cờ Vua (Chess):
- Chơi với máy hoặc 2 người.
- Chạm vào quân cờ của bạn -> Các ô nước đi hợp lệ sẽ sáng lên -> Chạm vào ô đích để di chuyển.
- Có hỗ trợ nhập thành (Castling), bắt tốt qua đường (En passant) và phong cấp (Promotion) trong menu Settings.

#### 4. Cờ Đam (Checkers):
- Quân cờ đi chéo trên các ô màu tối. Nhảy qua đầu quân địch để ăn.
- Sang được hàng cuối của đối phương sẽ hóa thành Vua (King) và có thể đi tiến/lùi tự do.

#### 5. Connect 4:
- Chạm vào cột bất kỳ để thả quân cờ xuống. Người đầu tiên nối được 4 quân liên tiếp (ngang, dọc hoặc chéo) sẽ thắng.

#### 6. Tic Tac Toe (Cờ ca-rô 3x3):
- Chạm vào ô trống để đánh dấu X/O. Nối 3 ô thẳng hàng để chiến thắng.

---

## 5. PHÁC THẢO SƠ ĐỒ TƯ DUY & WIREFRAME (INK AWAY)

- Cách mở: Menu Công cụ (Tools) -> Ink Away (hoặc vuốt từ cạnh phải màn hình lên trên).
- Mẹo phác thảo Mindmap:
  + Dùng công cụ Shape (Hình chữ nhật/Oval) để tạo các nhánh ý tưởng.
  + Dùng công cụ Line / Arrow để nối các nhánh.
  + Dùng Text box để chèn chữ in thẳng hàng.
  + Xuất file ảnh PNG làm hình nền chờ (Sleep screen) hoặc xuất PDF gửi về PC.

---

## 6. ĐỒNG BỘ GHI CHÚ VỀ MÁY TÍNH (OBSIDIAN / NOTION)

Mọi ghi chú bạn lưu bằng `#note` trên Kindle đều nằm an toàn trên server đám mây.
- Khi về bàn làm việc, mở máy tính và chạy lệnh:
  `python scripts/sync_vault_notes.py`
- Toàn bộ ghi chú đọc sách ban đêm sẽ tự động được kéo về thư mục `vault_notes` trên máy tính dưới dạng Markdown hoàn chỉnh, có phân loại theo tên sách.

---

## 7. CÁC PHÍM TẮT & CỬ CHỈ CẦN NHỚ TRÊN KOREADER

- Chỉnh độ sáng đèn nền: Vuốt ngón tay lên/xuống ở mép trái màn hình.
- Chỉnh nhiệt độ màu đèn nền: Vuốt ngón tay lên/xuống ở mép phải màn hình.
- Đánh dấu trang (Bookmark): Chạm nhanh vào góc trên cùng bên phải trang sách.
- Mở mục lục & Tiến độ: Chạm mép dưới cùng màn hình.
- Tiết kiệm pin: Nên tắt Wi-Fi khi đọc sách thuần túy; chỉ bật Wi-Fi khi cần tra cứu AI hoặc tải sách.

Chúc bạn có những trải nghiệm đọc sách, học tập và thư giãn đỉnh cao trên chiếc Kindle!
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
  <title>Hướng Dẫn Sử Dụng Kindle</title>
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
    <dc:title>Sổ Tay Hướng Dẫn Sử Dụng Kindle</dc:title>
    <dc:creator>Antigravity</dc:creator>
    <dc:language>vi</dc:language>
    <dc:identifier id="BookID">urn:uuid:kindle-guide-2026-11-01-v2</dc:identifier>
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
    <meta name="dtb:uid" content="urn:uuid:kindle-guide-2026-11-01-v2"/>
  </head>
  <docTitle><text>Sổ Tay Hướng Dẫn Sử Dụng Kindle</text></docTitle>
  <navMap>
    <navPoint id="navPoint-1" playOrder="1">
      <navLabel><text>Bắt Đầu</text></navLabel>
      <content src="guide.xhtml"/>
    </navPoint>
  </navMap>
</ncx>"""
    zf.writestr("OEBPS/toc.ncx", toc_ncx, compress_type=zipfile.ZIP_DEFLATED)

print(f"SUCCESS: Generated detailed guide files in {target_dir}")
