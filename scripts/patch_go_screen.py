import re

path = r"E:\koreader\plugins\go.koplugin\screen.lua"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add json and https at top if not present
if 'local https = require("ssl.https")' not in content:
    content = content.replace(
        'local FrameContainer  = require("ui/widget/container/framecontainer")',
        'local https           = require("ssl.https")\n'
        'local http            = require("socket.http")\n'
        'local ltn12           = require("ltn12")\n'
        'local json            = require("json")\n'
        'local InfoMessage     = require("ui/widget/infomessage")\n'
        'local FrameContainer  = require("ui/widget/container/framecontainer")'
    )

new_ai_section = '''-- ---------------------------------------------------------------------------
-- Opponent
--
-- Supports 3 modes:
-- 1. "human"    : Two human players on one device.
-- 2. "ai"       : Local offline heuristic bot (Easy / Medium / Hard).
-- 3. "cloud_ai" : Cloud AI (AlphaGo / KataGo) via kindle-ai-gateway (Requires Internet).
-- ---------------------------------------------------------------------------

local AI_COLOR = "white"
local AI_DELAY = 0.35

function GoScreen:getOpponent()
    return self.plugin:getSetting("opponent", "ai")
end

function GoScreen:isSolo()
    local opp = self:getOpponent()
    return opp == "ai" or opp == "cloud_ai"
end

function GoScreen:getOpponentButtonText()
    local opp = self:getOpponent()
    if opp == "cloud_ai" then
        return _("Đối thủ: Cloud AI 🌐 (AlphaGo)")
    elseif opp == "ai" then
        return _("Đối thủ: Bot Máy 🤖 (Offline)")
    else
        return _("Đối thủ: 2 Người 👥 (Chuyền tay)")
    end
end

function GoScreen:toggleOpponent()
    local current = self:getOpponent()
    local next_opp = "ai"
    if current == "human" then
        next_opp = "ai"
    elseif current == "ai" then
        next_opp = "cloud_ai"
    else
        next_opp = "human"
    end
    self.plugin:saveSetting("opponent", next_opp)
    if next_opp == "cloud_ai" then
        self:updateStatus(_("Chế độ Cloud AI (AlphaGo 🌐). Yêu cầu kết nối Wi-Fi/Internet."))
    elseif next_opp == "ai" then
        self:updateStatus(_("Chế độ Bot Máy (Offline - Không cần mạng)."))
    else
        self:updateStatus(_("Chế độ 2 người chơi chuyền tay trên 1 máy."))
    end
    self:maybeRunAI()
end

function GoScreen:maybeRunAI()
    local board = self.board
    if not self:isSolo() then return end
    if board.status ~= "playing" or board.turn ~= AI_COLOR then return end
    if self.ai_thinking then return end
    self.ai_thinking = true

    local opp_mode = self:getOpponent()

    if opp_mode == "cloud_ai" then
        self:updateStatus(_("AlphaGo Cloud AI đang tính toán nước đi... 🌐"))
        UIManager:scheduleIn(0.2, function()
            local grid = {}
            for r = 1, board.n do
                grid[r] = {}
                for c = 1, board.n do
                    grid[r][c] = board.grid[r][c]
                end
            end
            local payload = json.encode({
                size = board.n,
                board = grid,
                turn = AI_COLOR,
                difficulty = self:getDifficulty(),
            })

            local resp_body = {}
            local res, code, headers = https.request{
                url = "https://kindle.alphatech.ai.vn/api/v1/games/go/move",
                method = "POST",
                headers = {
                    ["Content-Type"] = "application/json",
                    ["Content-Length"] = tostring(#payload),
                },
                source = ltn12.source.string(payload),
                sink = ltn12.sink.table(resp_body),
            }

            self.ai_thinking = false
            if board.status ~= "playing" or board.turn ~= AI_COLOR then return end

            local parsed = nil
            if code == 200 and #resp_body > 0 then
                pcall(function()
                    parsed = json.decode(table.concat(resp_body))
                end)
            end

            if parsed and parsed.move and parsed.move.r and parsed.move.c then
                if board:placeStone(parsed.move.r, parsed.move.c) == "ok" then
                    self.board_widget:refresh()
                    local comment = parsed.commentary or "Nước cờ tối ưu."
                    local winrate = math.floor(parsed.winrate or 50)
                    self:updateStatus(T(_("AlphaGo (%1%%): %2"), winrate, comment))
                    self.plugin:saveState(self:serializeState())
                    return
                end
            elseif parsed and parsed["pass"] then
                board:pass()
                self.board_widget:refresh()
                self:updateStatus(_("AlphaGo Cloud AI chọn Pass."))
                self.plugin:saveState(self:serializeState())
                return
            end

            -- If network/cloud failed, warn and fallback
            UIManager:show(InfoMessage:new{
                text = _("Không thể kết nối Internet tới AlphaGo Cloud AI!\\n(Cần Wi-Fi để gửi thế cờ về Server).\\n\\nĐang chuyển sang nước đi Bot Offline tạm thời."),
                timeout = 4,
            })

            local mv = board:getAIMove(self:getDifficulty())
            if mv and board:placeStone(mv.r, mv.c) == "ok" then
                self.board_widget:refresh()
                self:updateStatus(_("Bot Offline dự phòng đã hạ quân."))
            else
                board:pass()
                self.board_widget:refresh()
                self:updateStatus(_("Bot Offline dự phòng Pass."))
            end
            self.plugin:saveState(self:serializeState())
        end)
    else
        -- Local offline AI
        UIManager:scheduleIn(AI_DELAY, function()
            self.ai_thinking = false
            if board.status ~= "playing" or board.turn ~= AI_COLOR then return end
            local mv = board:getAIMove(self:getDifficulty())
            if mv and board:placeStone(mv.r, mv.c) == "ok" then
                self.board_widget:refresh()
                self:updateStatus()
            else
                board:pass()
                self.board_widget:refresh()
                self:updateStatus(_("Bot máy đã Pass."))
            end
            self.plugin:saveState(self:serializeState())
        end)
    end
end
'''

# Find the opponent block in content and replace it
pattern = r'local AI_COLOR = "white"[\s\S]*?self\.plugin:saveState\(self:serializeState\(\)\)\s*end\)\s*end'
content = re.sub(pattern, new_ai_section, content)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched screen.lua successfully!")
