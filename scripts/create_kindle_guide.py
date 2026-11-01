"""Generate user guide files for Kindle Paperwhite 4 in E:/documents/Books."""

import html
import zipfile
from pathlib import Path

target_dir = Path("E:/documents/Books")
target_dir.mkdir(parents=True, exist_ok=True)

md_content = """# SỔ TAY HƯỚNG DẪN SỬ DỤNG KINDLE PAPERWHITE 4
## Hệ sinh thái Đọc Sách Thông Minh, Game E-ink & Trạm Tri Thức AI

---

## 1. TỔNG QUAN HỆ THỐNG

Chiếc Kindle Paperwhite 4 của bạn đã được nâng cấp toàn diện:
- Phần cứng: Màn hình 6-inch E-ink Carta 300 DPI chống lóa, đèn nền tích hợp.
- Hệ thống đọc sách: KOReader v2026.07.2 — hỗ trợ tùy biến mạnh mẽ, hiển thị đẹp và tiết kiệm pin.
- Trợ lý AI & Kho tri thức: KOAssistant kết nối trực tiếp với Kindle AI Gateway (chạy model alex-agent, DeepSeek, SQLite Vault và Bộ nhớ cá nhân hóa).
- Bộ công cụ mở rộng: Đã cài sẵn gói Game cờ (Board Games) và Ứng dụng phác thảo tư duy (Ink Away).

---

## 2. TRỢ LÝ ĐỌC SÁCH THÔNG MINH 1-CHẠM (KOASSISTANT)

Không cần gõ bàn phím ảo chậm chạp trên màn hình E-ink, bạn chỉ cần chạm và chọn:

### Cách sử dụng:
1. Mở một cuốn sách bất kỳ trong KOReader.
2. Dùng ngón tay bôi đen (highlight) một đoạn văn bản hoặc từ ngữ bạn quan tâm.
3. Trong menu chọn hiện ra, chọn biểu tượng KOAssistant.
4. Các nút tác vụ nhanh định sẵn sẽ xuất hiện ngay trước mắt:
   - Tóm tắt cốt lõi: Trích xuất 3 luận điểm quan trọng nhất của đoạn trích, trình bày súc tích gạch đầu dòng.
   - Giải thích sâu & Ví dụ: Diễn giải khái niệm trừu tượng thành ngôn ngữ gần gũi, kèm 1 ví dụ minh họa thực tế đời sống.
   - Phản biện & Góc nhìn: Chỉ ra các điểm còn thiếu sót, góc nhìn trái chiều và 1 câu hỏi kích thích tư duy phản biện.
   - Bài học thực hành: Rút ra 1-2 hành động cụ thể để áp dụng vào thực tế.
   - Lưu Vault (#note): Tự động đẩy đoạn trích vào kho lưu trữ tri thức cá nhân trên server (kèm tên sách và thời gian).
   - Lưu Việc (#todo): Đưa nội dung vào danh sách việc cần làm.
   - Tổng quan sách (ở menu ngoài): Tóm lược giá trị và bối cảnh toàn bộ cuốn sách.

---

## 3. CÁC LỆNH TƯƠNG TÁC BỘ NHỚ VÀ TRI THỨC VỚI AI

Khi mở giao diện trò chuyện tự do với trợ lý, bạn có thể sử dụng các lệnh đặc biệt:

- #remember [chủ đề] <nội dung>
  Mục đích: Dạy cho AI hiểu bạn hơn.
  Ví dụ: #remember [nghề nghiệp] Tôi là lập trình viên, hãy ưu tiên giải thích các vấn đề bằng tư duy hệ thống và thuật toán.
- #memory
  Mục đích: Hiển thị tối đa 10 mục ghi nhớ gần nhất mà trợ lý đang lưu giữ về bạn.
- #note [tiêu đề] <nội dung>
  Mục đích: Tạo một ghi chú độc lập vào SQLite Vault.
- #todo <nội dung>
  Mục đích: Tạo một đầu việc cần làm.
- #help
  Mục đích: Xem danh sách các cú pháp hỗ trợ trên màn hình Kindle.

---

## 4. GIẢI TRÍ VỚI BỘ GAME E-INK (BOARD GAMES)

Khi cần thư giãn sau những giờ đọc sách tập trung:

- Cách mở:
  1. Chạm vào mép trên cùng màn hình để hiện thanh menu KOReader.
  2. Chọn tab Công cụ (Tools) (biểu tượng bánh răng/cờ lê).
  3. Chọn mục Board Games.
- 6 trò chơi tích hợp sẵn:
  1. Cờ vua (Chess): Chơi với máy hoặc chơi 2 người.
  2. Dò mìn (Minesweeper): Trò chơi logic tính toán cổ điển.
  3. Connect 4: Xếp 4 quân cờ thẳng hàng.
  4. Cờ đam (Checkers): Đơn giản, thư giãn.
  5. Tic Tac Toe (Cờ ca-rô 3x3): Nhanh gọn.
  6. Thủy chiến (Battleship): Bắn tàu theo tọa độ.
- Tối ưu E-ink: Giao diện tương phản đen trắng sắc nét, chỉ làm mới từng ô di chuyển nên không hề bị chớp nháy màn hình.

---

## 5. PHÁC THẢO SƠ ĐỒ TƯ DUY & WIREFRAME (INK AWAY)

Ứng dụng giúp bạn ghi chép, phác thảo ý tưởng bất chợt:

- Cách mở:
  - Cách 1: Vào menu Công cụ (Tools) -> Chọn Ink Away (drawing canvas).
  - Cách 2: Khi ở màn hình duyệt file, dùng ngón tay vuốt từ cạnh phải màn hình lên phía trên.
- Mẹo phác thảo Mindmap & Wireframe đẹp trên màn hình cảm ứng điện dung:
  - Hạn chế viết chữ tự do nét dài bằng tay (dễ bị méo).
  - Sử dụng công cụ Shape (Hình khối chữ nhật/oval) để tạo các nút ý tưởng.
  - Sử dụng công cụ Arrow / Line (Mũi tên/Đường kẻ) để nối các nhánh liên kết.
  - Sử dụng công cụ Text box để gõ chữ in ngay ngắn.
- Xuất file:
  - Hỗ trợ lưu thành sổ tay nhiều trang.
  - Xuất file ảnh PNG làm hình nền chờ (Screensaver) hoặc xuất PDF chuyển sang máy tính.

---

## 6. ĐỒNG BỘ GHI CHÚ VỀ MÁY TÍNH (OBSIDIAN / NOTION)

Mọi ghi chú bạn lưu bằng #note trên Kindle đều nằm an toàn trên máy chủ đám mây.

- Khi về bàn làm việc, mở máy tính và chạy script:
  python scripts/sync_vault_notes.py
- Toàn bộ ghi chú sẽ được kéo về thư mục vault_notes trên máy tính:
  - Tự động định dạng Markdown chuẩn với YAML frontmatter, tags và wikilinks.
  - Tự động gom nhóm vào thư mục con theo tên từng cuốn sách.
  - Mở trực tiếp bằng Obsidian, Logseq, VS Code hoặc import vào Notion.

---

## 7. CÁC PHÍM TẮT & CỬ CHỈ CẦN NHỚ TRÊN KOREADER

- Chỉnh độ sáng đèn nền: Vuốt ngón tay lên/xuống ở mép trái màn hình.
- Chỉnh nhiệt độ màu đèn nền: Vuốt ngón tay lên/xuống ở mép phải màn hình.
- Đánh dấu trang (Bookmark): Chạm nhanh vào góc trên cùng bên phải trang sách.
- Mở mục lục & Tiến độ: Chạm mép dưới cùng màn hình.
- Bật/Tắt Wi-Fi nhanh: Chạm menu trên cùng -> tab Bánh răng -> Cài đặt mạng. Nên tắt Wi-Fi khi đọc thuần túy để pin kéo dài cả tháng!

Chúc bạn có những giờ phút đọc sách, tư duy và sáng tạo tuyệt vời trên chiếc Kindle!
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
        elif line.startswith("- "):
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
    h3 {{ font-size: 1.1em; margin-top: 1em; }}
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
    <dc:identifier id="BookID">urn:uuid:kindle-guide-2026-11-01</dc:identifier>
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
    <meta name="dtb:uid" content="urn:uuid:kindle-guide-2026-11-01"/>
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

print(f"SUCCESS: Generated guide files in {target_dir}")
