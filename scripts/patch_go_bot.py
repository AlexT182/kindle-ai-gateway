"""Patch go.koplugin to add difficulty settings and strategic Go AI heuristics."""

from pathlib import Path

go_dir = Path("E:/koreader/plugins/go.koplugin")
screen_path = go_dir / "screen.lua"
board_path = go_dir / "board.lua"

# ----------------- 1. Patch screen.lua -----------------
screen_content = screen_path.read_text(encoding="utf-8")

diff_methods = """
function GoScreen:getDifficulty()
    return self.plugin:getSetting("difficulty", "medium")
end

function GoScreen:getDifficultyButtonText()
    local diff = self:getDifficulty()
    local labels = {
        easy = _("Bot: Beginner"),
        medium = _("Bot: Medium"),
        hard = _("Bot: Advanced"),
    }
    return labels[diff] or _("Bot: Medium")
end

function GoScreen:cycleDifficulty()
    local current = self:getDifficulty()
    local next_diff = {
        easy = "medium",
        medium = "hard",
        hard = "easy",
    }
    local new_val = next_diff[current] or "medium"
    self.plugin:saveSetting("difficulty", new_val)
    local msg = {
        easy = _("Bot level: Beginner"),
        medium = _("Bot level: Medium (strategic)"),
        hard = _("Bot level: Advanced (tactical)"),
    }
    self:updateStatus(msg[new_val] or new_val)
end
"""

if "function GoScreen:getDifficulty()" not in screen_content:
    target_anchor = "function GoScreen:buildLayout()"
    assert target_anchor in screen_content, "target_anchor not found in screen.lua"
    screen_content = screen_content.replace(target_anchor, diff_methods + "\n" + target_anchor, 1)

    old_menu = """            { text = self:getOpponentButtonText(), callback = function() self:toggleOpponent() end },
            { text = _("Pass"),         callback = function() self:onPass() end },"""

    new_menu = """            { text = self:getOpponentButtonText(), callback = function() self:toggleOpponent() end },
            { text = self:getDifficultyButtonText(), callback = function() self:cycleDifficulty() end },
            { text = _("Pass"),         callback = function() self:onPass() end },"""

    assert old_menu in screen_content, "old_menu not found in screen.lua"
    screen_content = screen_content.replace(old_menu, new_menu, 1)

    old_ai_call = "local mv = board:getAIMove()"
    new_ai_call = "local mv = board:getAIMove(self:getDifficulty())"
    assert old_ai_call in screen_content, "old_ai_call not found in screen.lua"
    screen_content = screen_content.replace(old_ai_call, new_ai_call, 1)

    screen_path.write_text(screen_content, encoding="utf-8")
    print("screen.lua patched successfully.")
else:
    print("screen.lua already patched.")

# ----------------- 2. Patch board.lua -----------------
board_content = board_path.read_text(encoding="utf-8")

# Helper to count stones
count_helper = """
function GoBoard:_countStones()
    local count = 0
    local n = self.n
    for r = 1, n do
        for c = 1, n do
            if self.grid[r][c] ~= EMPTY then count = count + 1 end
        end
    end
    return count
end
"""

new_ai_move = """
function GoBoard:getAIMove(difficulty)
    difficulty = difficulty or "medium"
    if self.status ~= "playing" then return nil end
    local n = self.n
    local color = (self.turn == "black") and BLACK or WHITE
    local opp   = (color == BLACK) and WHITE or BLACK
    local total_stones = self:_countStones()
    local is_opening = (total_stones < math.floor(n * 1.5))

    local best, best_score = nil, -999999
    for r = 1, n do
        for c = 1, n do
            if self.grid[r][c] == EMPTY and not self:_isOwnEye(r, c, color)
               and self:isLegalMove(r, c, color) then
                local captured, liberties = self:_simulate(r, c, color)
                local score = 0

                -- 1. Captures
                if captured > 0 then
                    score = score + captured * 20
                end

                -- 2. Rescue own group in atari
                local own_atari = self:_adjacentGroupLiberties(r, c, color)
                if own_atari == 1 and liberties > 1 then
                    score = score + 18
                end

                -- 3. Threaten opponent group into atari
                local opp_lib = self:_adjacentGroupLiberties(r, c, opp)
                if opp_lib == 2 and liberties >= 2 then
                    score = score + 10
                end

                -- 4. Avoid self-atari
                if liberties == 1 and captured == 0 then
                    score = score - 35
                elseif liberties == 2 then
                    score = score - 4
                else
                    score = score + math.min(liberties, 4) * 2
                end

                -- 5. Positional Go Principles
                local dist_edge = math.min(r, c, n - r + 1, n - c + 1)

                if difficulty == "hard" or difficulty == "medium" then
                    -- Line 1 (Line of death) is severely penalized in opening/midgame
                    if dist_edge == 1 then
                        score = score - (is_opening and 16 or 6)
                    elseif dist_edge == 2 then
                        score = score - (is_opening and 8 or 2)
                    elseif dist_edge == 3 then
                        -- Line 3 (Territory line) - golden for securing corners & territory
                        score = score + (is_opening and 14 or 6)
                    elseif dist_edge == 4 then
                        -- Line 4 (Influence line) - great for expanding influence
                        score = score + (is_opening and 12 or 5)
                    else
                        score = score + (is_opening and 2 or 5)
                    end

                    -- Opening corner & star point priority
                    if is_opening then
                        local star_coord = (n == 9) and 3 or 4
                        local is_corner_star = (r == star_coord or r == n - star_coord + 1)
                                            and (c == star_coord or c == n - star_coord + 1)
                        local is_komoku = ((r == star_coord and (c == star_coord - 1 or c == star_coord + 1))
                                        or (r == n - star_coord + 1 and (c == star_coord - 1 or c == star_coord + 1)))
                        if is_corner_star then
                            score = score + 18
                        elseif is_komoku then
                            score = score + 14
                        end

                        -- Penalize early pointless contact play
                        local contact_count = 0
                        for _, d in ipairs(DIRS4) do
                            local nr, nc = r + d[1], c + d[2]
                            if inBounds(nr, nc, n) and self.grid[nr][nc] == opp then
                                contact_count = contact_count + 1
                            end
                        end
                        if contact_count > 0 and captured == 0 then
                            score = score - 8
                        end
                    else
                        -- Middle/endgame: reward connecting with friendly stones
                        for _, d in ipairs(DIRS4) do
                            local nr, nc = r + d[1], c + d[2]
                            if inBounds(nr, nc, n) and self.grid[nr][nc] == color then
                                score = score + 3
                            end
                        end
                    end
                else
                    -- "easy" mode: random jitter
                    if dist_edge == 1 then score = score - 5 end
                    score = score + math.random(-4, 4)
                end

                if difficulty == "hard" then
                    -- Bonus for diagonal connections (Kosumi) and knight's moves (Keima)
                    for dr = -2, 2 do
                        for dc = -2, 2 do
                            if math.abs(dr) + math.abs(dc) == 2 or (math.abs(dr) == 1 and math.abs(dc) == 2) then
                                local nr, nc = r + dr, c + dc
                                if inBounds(nr, nc, n) and self.grid[nr][nc] == color then
                                    score = score + 4
                                end
                            end
                        end
                    end
                end

                if score > best_score then
                    best_score = score
                    best = { r = r, c = c }
                end
            end
        end
    end

    if best_score and best_score <= -25 then return nil end
    return best
end
"""

if "function GoBoard:_countStones()" not in board_content:
    # Find getAIMove to replace
    import re
    pattern = r"function GoBoard:getAIMove\(\)[\s\S]*?return best\s*end"
    assert re.search(pattern, board_content), "getAIMove pattern not found in board.lua"
    board_content = re.sub(pattern, count_helper.strip() + "\n\n" + new_ai_move.strip(), board_content, count=1)
    board_path.write_text(board_content, encoding="utf-8")
    print("board.lua patched successfully.")
else:
    print("board.lua already patched.")
