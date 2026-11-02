import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_go_move_endpoint_opening():
    payload = {
        "size": 9,
        "board": [],
        "turn": "white",
        "difficulty": "pro"
    }
    response = client.post("/api/v1/games/go/move", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "move" in data
    assert "engine" in data
    assert data["move"] is not None
    assert 1 <= data["move"]["r"] <= 9
    assert 1 <= data["move"]["c"] <= 9
    assert "winrate" in data
    assert "commentary" in data


def test_go_move_endpoint_occupied():
    # Occupy (3, 3) 1-indexed -> (2, 2) in 0-indexed
    board = [["black" if (r == 2 and c == 2) else None for c in range(9)] for r in range(9)]
    payload = {
        "size": 9,
        "board": board,
        "turn": "white",
        "difficulty": "pro"
    }
    response = client.post("/api/v1/games/go/move", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["move"] != {"r": 3, "c": 3}


def test_go_move_atari_capture():
    # Surround black stone at (3, 3) on 3 sides: (2, 3), (4, 3), (3, 2). Only (3, 4) remains.
    # White must capture it at (3, 4)!
    board = [[0 for _ in range(9)] for _ in range(9)]
    board[2][2] = 1  # Black at (3, 3)
    board[1][2] = 2  # White at (2, 3)
    board[3][2] = 2  # White at (4, 3)
    board[2][1] = 2  # White at (3, 2)
    payload = {
        "size": 9,
        "board": board,
        "turn": "white",
        "difficulty": "medium"
    }
    response = client.post("/api/v1/games/go/move", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["move"] == {"r": 3, "c": 4}
    assert "Bắt" in data["commentary"]



def test_go_move_endpoint_integer_board():
    # 0 = empty, 1 = black, 2 = white (matches KOReader internal representation)
    board = [[0 for _ in range(9)] for _ in range(9)]
    board[2][2] = 1  # Black stone at (3, 3) 1-indexed
    payload = {
        "size": 9,
        "board": board,
        "turn": "white",
        "difficulty": "pro"
    }
    response = client.post("/api/v1/games/go/move", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["move"] != {"r": 3, "c": 3}


def test_go_move_atari_capture():
    # Surround black stone at (3, 3) on 3 sides: (2, 3), (4, 3), (3, 2). Only (3, 4) remains.
    # White must capture it at (3, 4)!
    board = [[0 for _ in range(9)] for _ in range(9)]
    board[2][2] = 1  # Black at (3, 3)
    board[1][2] = 2  # White at (2, 3)
    board[3][2] = 2  # White at (4, 3)
    board[2][1] = 2  # White at (3, 2)
    payload = {
        "size": 9,
        "board": board,
        "turn": "white",
        "difficulty": "medium"
    }
    response = client.post("/api/v1/games/go/move", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["move"] == {"r": 3, "c": 4}
    assert "Bắt" in data["commentary"]


