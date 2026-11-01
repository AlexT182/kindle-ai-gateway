import re

# 1. Patch boardgames.koplugin/main.lua with Vietnamese rules
boardgames_path = r"E:\koreader\plugins\boardgames.koplugin\main.lua"
with open(boardgames_path, "r", encoding="utf-8") as f:
    bg_content = f.read()

new_rules_block = '''    local rules = {
        [CHECKERS] = {
            "CỜ ĐAM (CHECKERS):",
            "• Di chuyển chéo trên các ô màu tối.",
            "• Nhảy qua đầu quân địch để ăn quân. Ăn liên hoàn nếu còn lượt.",
            "• Tiến sang hàng cuối cùng của đối thủ để phong Vua (King).",
            "• Vua có quyền đi và nhảy chéo cả tiến lẫn lùi tự do.",
        },
        [CHESS] = {
            "CỜ VUA (CHESS):",
            "• Bảo vệ Vua của bạn và tấn công Vua đối phương.",
            "• Chiếu bí (Checkmate) để giành chiến thắng. Hòa nếu hết nước đi hợp lệ.",
            "• Chạm vào quân cờ -> Chạm vào ô đích được đánh dấu để di chuyển.",
            "• Hỗ trợ Nhập thành (Castling), Bắt tốt qua đường (En passant) và Phong cấp.",
        },
        [CONNECT4] = {
            "BỐN QUÂN THẲNG HÀNG (CONNECT 4):",
            "• Chạm vào cột bất kỳ để thả quân cờ xuống đáy.",
            "• Người đầu tiên nối được 4 quân liên tiếp sẽ chiến thắng.",
            "• Các hàng 4 quân có thể theo chiều ngang, dọc hoặc đường chéo.",
        },
        [TICTACTOE] = {
            "CỜ CA-RÔ 3x3 (TIC TAC TOE):",
            "• Chạm vào một ô trống bất kỳ để đặt dấu X hoặc O.",
            "• Người đầu tiên nối được 3 ô liên tiếp sẽ chiến thắng.",
            "• Nếu đầy bàn cờ mà không ai nối được 3 ô thì ván cờ hòa.",
        },
        [MINESWEEPER] = {
            "DÒ MÌN (MINESWEEPER):",
            "• Bàn cờ 9x9 với 10 quả mìn ẩn giấu.",
            "• Mở các ô an toàn và tránh chạm vào mìn. Nước đầu tiên luôn an toàn.",
            "• Số trên ô hiển thị số lượng mìn xung quanh ô đó.",
            "• Bấm nút Flag ở đáy để chuyển chế độ Cắm cờ đánh dấu vị trí có mìn.",
        },
        [BATTLESHIP] = {
            "THỦY CHIẾN BẮN TÀU (BATTLESHIP):",
            "• Bàn cờ 10x10 với 5 chiến hạm: 5 ô, 4 ô, 3 ô, 3 ô, 2 ô.",
            "• Giai đoạn 1: Bấm [Random Fleet] để máy xếp tàu tự động, hoặc bấm [Rotate] rồi chạm để đặt tàu thủ công.",
            "• Giai đoạn 2 (Bắn tàu): Chạm [Enemy Waters] để nã pháo vào vùng biển địch.",
            "• Ký hiệu 'X' là BẮN TRÚNG, 'o' là BẮN TRƯỢT xuống nước.",
            "• Chạm [Your Fleet] để xem hạm đội của mình. Bắn chìm hết tàu địch để thắng!",
        },
    }'''

bg_pattern = r'    local rules = \{[\s\S]*?\[BATTLESHIP\] = \{[\s\S]*?\},[\s\S]*?\}'
bg_content = re.sub(bg_pattern, new_rules_block, bg_content, count=1)

with open(boardgames_path, "w", encoding="utf-8") as f:
    f.write(bg_content)
print("Updated boardgames rules successfully!")

# 2. Patch go.koplugin/screen.lua with Vietnamese rules
go_path = r"E:\koreader\plugins\go.koplugin\screen.lua"
with open(go_path, "r", encoding="utf-8") as f:
    go_content = f.read()

new_go_rules = '''local GAME_RULES_EN = _([[
CỜ VÂY (GO / WEIQI) — LUẬT CHƠI CƠ BẢN

1. Quy tắc đặt quân:
• Đen đi trước, Trắng đi sau. Quân cờ đặt vào các giao điểm của lưới bàn cờ.
• Trắng được cộng 6.5 điểm (Komi) để bù đắp lợi thế đi trước của Đen.

2. Luật Khí và Bắt quân:
• Các giao điểm trống kề cạnh quân cờ gọi là "Khí".
• Khi một nhóm quân bị đối phương chặn hết toàn bộ Khí, nhóm quân đó sẽ bị bắt và nhấc ra khỏi bàn cờ.
• Không được tự sát (đi vào ô không có khí), trừ khi nước đó bắt chết quân đối phương.

3. Luật Ko (Tranh chấp):
• Không được lập tức bắt lại quân vừa ăn nếu nước đi đó lặp lại hoàn toàn thế cờ của nước trước.

4. Tính điểm và Kết thúc:
• Ván cờ kết thúc khi cả hai bên liên tiếp bấm "Pass".
• Bên nào kiểm soát được nhiều đất (giao điểm trống được vây kín) và quân bắt được nhiều hơn sẽ chiến thắng.
]])'''

go_pattern = r'local GAME_RULES_EN = _\(\[\[[\s\S]*?\]\]\)'
go_content = re.sub(go_pattern, new_go_rules, go_content, count=1)

with open(go_path, "w", encoding="utf-8") as f:
    f.write(go_content)
print("Updated Go rules successfully!")
