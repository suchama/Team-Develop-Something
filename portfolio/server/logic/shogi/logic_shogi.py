# logic_shogi.py
"""
将棋ロジック
Board と GameState を利用して、サーバー(app.py)から呼び出される関数群を提供
"""

from typing import Dict, List
from .board import Board
from .gamestate import GameState
from .utils import _can_drop_on_rank, _error_out
import random


# ============================================
#  初期化
# ============================================

def game_start() -> Dict:
    b = Board()
    gs = GameState()

    return {
        "board": b.grid,
        "tegoma": gs.hands,
        "remaining_time": {1: 300, 2: 300},
        "current_turn": gs.current_turn,
    }


# ============================================
# 合法手生成
# ============================================

def get_valid_moves(board, tegoma_player, player, place, pos):
    b = Board()
    b.grid = [row[:] for row in board]

    # --- 盤面の駒を選んだ場合 ---
    if place == "board":
        x, y = pos
        return b.get_valid_moves(x, y, player)

    # --- 手駒を選んだ場合 ---
    elif place == "tegoma":
        piece = pos[0]
        moves = []

        for y in range(9):
            for x in range(9):
                if b.grid[y][x] != 0:
                    continue
                if piece == 8 and b.is_double_pawn(x, player):
                    continue
                if not _can_drop_on_rank(piece, y, player):
                    continue
                moves.append((x, y))

        return moves

    return []


# ============================================
# プレイヤーの手（2回目クリック）
# ============================================

def handle_player_move(board, tegoma, player, selected_place, selected_pos, to_pos) -> Dict:
    b = Board()
    b.grid = [row[:] for row in board]

    # 正しい手駒の参照
    hands = {1: dict(tegoma[1]), 2: dict(tegoma[2])}

    nari_check = False
    winner = None

    # ---------- 盤面の駒を動かす ----------
    if selected_place == "board":
        x0, y0 = selected_pos
        x1, y1 = to_pos
        piece = b.grid[y0][x0]
        to_piece = b.grid[y1][x1]

        # 玉を取ったら勝利
        if to_piece % 10 == 1:
            winner = player

        # 取った駒を手駒に戻す
        if to_piece != 0 and b.is_enemy(to_piece, player):
            koma_type = b.unpromote(to_piece) % 10
            hands[player][koma_type] = hands[player].get(koma_type, 0) + 1

        # 移動反映
        b.grid[y1][x1] = piece
        b.grid[y0][x0] = 0

        # 成り判定
        if b.should_promote(piece, y0, y1, player):
            nari_check = True

    # ---------- 手駒 → 盤面に置く ----------
    elif selected_place == "tegoma":
        piece = selected_pos      # selected_pos はint

        x1, y1 = to_pos

        # 配置
        place_code = piece if player == 1 else piece + 10
        b.grid[y1][x1] = place_code

        # 手駒を減らす
        hands[player][piece] -= 1
        if hands[player][piece] == 0:
            del hands[player][piece]

    # ターン切替（勝ったら交代しない）
    next_turn = player % 2 + 1

    return {
        "winner": winner,
        "nari_check": nari_check,
        "board_grid": b.grid,
        "tegoma": hands,
        "next_turn": next_turn,
    }


# ============================================
# 成り処理
# ============================================

def handle_nari(board, player, to_pos):
    b = Board()
    b.grid = [row[:] for row in board]

    x1, y1 = to_pos
    b.grid[y1][x1] = b.promote(b.grid[y1][x1])

    return {
        "board_grid": b.grid,
        "current_turn": player,
    }


# ============================================
# AI の手
# ============================================

def handle_ai_move(gamestate_dict, current_turn):
    b = Board()
    b.grid = [row[:] for row in gamestate_dict["board"]]

    hands = {
        1: dict(gamestate_dict["tegoma"][1]),
        2: dict(gamestate_dict["tegoma"][2]),
    }

    player = current_turn
    winner = None

    # --- 全合法手を収集 ---
    moves = []
    for y in range(9):
        for x in range(9):
            if b.is_own(b.grid[y][x], player):
                for nx, ny in b.get_valid_moves(x, y, player):
                    moves.append(((x, y), (nx, ny)))

    if not moves:
        return {
            "board_grid": b.grid,
            "current_turn": player,
            "winner": None,
            "tegoma": hands,
        }

    # --- ランダムに手を選ぶ ---
    (x0, y0), (x1, y1) = random.choice(moves)

    piece = b.grid[y0][x0]
    to_piece = b.grid[y1][x1]

    # 玉を取った場合
    if to_piece % 10 == 1:
        winner = player

    # 駒を取る処理
    if to_piece != 0 and b.is_enemy(to_piece, player):
        koma_type = b.unpromote(to_piece) % 10
        hands[player][koma_type] = hands[player].get(koma_type, 0) + 1

    # 反映
    b.grid[y1][x1] = piece
    b.grid[y0][x0] = 0

    next_turn = player % 2 + 1

    return {
        "board_grid": b.grid,
        "current_turn": next_turn,
        "winner": winner,
        "tegoma": hands,
    }
