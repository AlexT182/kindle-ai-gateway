go_path = r"E:\koreader\plugins\go.koplugin\screen.lua"
with open(go_path, "r", encoding="utf-8") as f:
    text = f.read()

bad_str = '''            UIManager:show(InfoMessage:new{
                text = _("Không thể kết nối Internet tới AlphaGo Cloud AI!
(Cần Wi-Fi để gửi thế cờ về Server).

Đang chuyển sang nước đi Bot Offline tạm thời."),
                timeout = 4,
            })'''

good_str = '''            UIManager:show(InfoMessage:new{
                text = _("Không thể kết nối Internet tới AlphaGo Cloud AI!\\n(Cần Wi-Fi để gửi thế cờ về Server).\\n\\nĐang chuyển sang nước đi Bot Offline tạm thời."),
                timeout = 4,
            })'''

if bad_str in text:
    text = text.replace(bad_str, good_str)
else:
    # Normalize newlines
    bad_str_lf = bad_str.replace("\r\n", "\n")
    text_lf = text.replace("\r\n", "\n")
    text_lf = text_lf.replace(bad_str_lf, good_str.replace("\r\n", "\n"))
    text = text_lf

with open(go_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed go.koplugin screen.lua!")
