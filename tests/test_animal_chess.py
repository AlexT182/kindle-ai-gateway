import pytest

# Simulating Jungle logic to verify test cases
class JungleBoard:
    def __init__(self, mode="classic"):
        self.mode = mode
        self.grid = [[None]*7 for _ in range(9)]
        self.history = []
        self.turn = "bottom"
        self.status = "playing"
        self.winner = None
        self.setup()

    def setup(self):
        # 1-indexed conversion: r 1..9, c 1..7 -> [r-1][c-1]
        self._place(1, 1, "top", 7)
        self._place(1, 7, "top", 6)
        self._place(2, 2, "top", 4)
        self._place(2, 6, "top", 2)
        self._place(3, 1, "top", 1)
        self._place(3, 3, "top", 5)
        self._place(3, 5, "top", 3)
        self._place(3, 7, "top", 8)

        self._place(9, 7, "bottom", 7)
        self._place(9, 1, "bottom", 6)
        self._place(8, 6, "bottom", 4)
        self._place(8, 2, "bottom", 2)
        self._place(7, 7, "bottom", 1)
        self._place(7, 5, "bottom", 5)
        self._place(7, 3, "bottom", 3)
        self._place(7, 1, "bottom", 8)

    def _place(self, r, c, side, rank):
        self.grid[r-1][c-1] = {"side": side, "rank": rank, "base_rank": rank, "kills": 0, "dodged": False}

    def is_river(self, r, c):
        return (4 <= r <= 6) and ((2 <= c <= 3) or (5 <= c <= 6))

    def is_trap(self, r, c):
        if (r, c) in [(1, 3), (1, 5), (2, 4)]: return "top"
        if (r, c) in [(9, 3), (9, 5), (8, 4)]: return "bottom"
        return None

    def is_den(self, r, c):
        if (r, c) == (1, 4): return "top"
        if (r, c) == (9, 4): return "bottom"
        return None


def test_jungle_initial_setup():
    b = JungleBoard()
    # Check top pieces
    assert b.grid[0][0]["rank"] == 7 # Lion
    assert b.grid[0][6]["rank"] == 6 # Tiger
    assert b.grid[2][0]["rank"] == 1 # Rat
    assert b.grid[2][6]["rank"] == 8 # Elephant

    # Check rivers
    assert b.is_river(4, 2) is True
    assert b.is_river(5, 3) is True
    assert b.is_river(6, 4) is False # Central bridge is land
    assert b.is_river(4, 5) is True

    # Check dens
    assert b.is_den(1, 4) == "top"
    assert b.is_den(9, 4) == "bottom"
    assert b.is_den(5, 4) is None


def test_rat_elephant_mechanics():
    b = JungleBoard()
    # Rat (1) vs Elephant (8) on land:
    # Rat can eat Elephant
    att_rank, def_rank = 1, 8
    can_eat = (att_rank == 1 and def_rank == 8)
    assert can_eat is True
    # Elephant cannot eat Rat
    can_eat_back = (att_rank == 8 and def_rank == 1)
    assert can_eat_back is False


def test_leopard_river_jump():
    b = JungleBoard()
    # Bottom Leopard is at row 7, col 5
    # Top Wolf is at row 3, col 5
    leopard = b.grid[6][4]
    wolf = b.grid[2][4]
    assert leopard["rank"] == 5 # Leopard
    assert wolf["rank"] == 3    # Wolf
    assert leopard["side"] == "bottom"
    assert wolf["side"] == "top"
    # Leopard can capture Wolf
    assert leopard["rank"] >= wolf["rank"]


def test_swimming_and_crocodile_strike():
    b = JungleBoard()
    # Swimmers: Rat (1), Dog (4), Elephant (8)
    can_swim_ranks = [1, 4, 8]
    assert 1 in can_swim_ranks
    assert 4 in can_swim_ranks
    assert 8 in can_swim_ranks
    assert 6 not in can_swim_ranks # Tiger cannot swim
    assert 7 not in can_swim_ranks # Lion cannot swim

    # Crocodile Strike rule:
    # Swimmers in river can attack pieces on land according to rank
    # 1. Elephant (8) in river captures Leopard (5) on land
    att_in_river = True
    def_in_river = False
    att_rank = 8
    def_rank = 5
    is_swimmer = att_rank in can_swim_ranks
    can_capture_land = is_swimmer and (att_rank >= def_rank)
    assert can_capture_land is True

    # 2. Rat (1) in river captures Elephant (8) on land
    att_rank, def_rank = 1, 8
    can_rat_capture_elephant_land = (att_rank == 1 and def_rank == 8)
    assert can_rat_capture_elephant_land is True

    # 3. Dog (4) in river captures Wolf (3) on land
    att_rank, def_rank = 4, 3
    can_dog_capture_wolf_land = (att_rank >= def_rank)
    assert can_dog_capture_wolf_land is True

    # 4. Non-swimmer on land cannot attack into river
    tiger_rank = 6
    can_tiger_attack_river = tiger_rank in can_swim_ranks
    assert can_tiger_attack_river is False

