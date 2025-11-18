# ユーティリティ

from typing import Dict
from board import Board
from gamestate import GameState

def _can_drop_on_rank(piece: int, y: int, turn: int) -> bool:
    """行き所なし打ちを禁止"""
    if turn == 1:
        if piece in (7,8) and y == 0: return False  # 香・歩
        if piece == 6 and y <= 1: return False      # 桂
    else:
        if piece in (7,8) and y == 8: return False
        if piece == 6 and y >= 7: return False
    return True


def _error_out(b: Board, gs: GameState, msg: str) -> Dict:
    return {
        "winner": None,
        "nari_check": False,
        "board_grid": b.grid,
        "tegoma": gs.hands,
        "message": msg
    }
