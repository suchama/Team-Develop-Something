# ユーティリティ

from typing import Dict
from .board import Board
from .gamestate import GameState
#from .architecture import ShogiCNN
#import numpy as np
#import torch
#import torch.nn.functinal as F


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

"""
def board_to_tensor(board_grid, current_turn):
    tensor = np.zeros((40, 9, 9),dtype=np.float32) 

    for y in range(9):
        for x in range(9):
            piece = board_grid[y][x]
            if piece == 0:
                continue
            idx = max(0, min(idx, 39))
            tensor[idx, y, x] = 1.0

    if current_turn == 1:
        tensor[-1, :, :] = 1.0
    else:
        tensor[-1, :, :] = 0.0 

    return torch.tensor(tensor, dtype=torch.float32).unsqueeze(0)
"""