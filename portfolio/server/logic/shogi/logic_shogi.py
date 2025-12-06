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


def game_start() -> Dict:
    """
    初期盤面を返す
    """
    b = Board()
    gs = GameState()

    return {
        "board": b.grid,
        "tegoma": gs.hands,
        "remaining_time": {1: 300, 2: 300},
        "current_turn": gs.current_turn,
    }


def get_valid_moves(board: List[List[int]], 
                    tegoma: Dict[int, Dict[int, int]],
                    player: int, 
                    place:str,
                    pos: List[int]
                    ) -> List[List[int]]:
    """
    1回目クリック時の処理
    画面のどこかを選択する。有効な場所をクリックしていたら、そこを返す。
    """
    b = Board()
    b.grid = [row[:] for row in board]

    #  盤面の駒を選んだ場合 
    if place == "board":
        x, y = pos
        return b.get_valid_moves(x, y, player)

    #  手駒を選んだ場合 
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


def handle_player_move(board: List[List[int]], 
                       tegoma: Dict[int, Dict[int,int]],
                       player: int, 
                       selected_place: str,             # プレイヤーが押した場所
                       selected_pos: List[int], 
                       to_pos: List[int]) -> Dict:
    """
    2回目クリック時の処理
    1回目で選択したものをどうするかの処理
    ・移動のみ
    ・駒捕り
    ・成り
    """
    b = Board()
    b.grid = [row[:] for row in board]
    hands = {1: dict(tegoma[1]), 2: dict(tegoma[2])}

    print(f"player : {player}")
    print(f"hands : {hands}")
    print(f"tegoma : {tegoma}")
    nari_check = False
    winner = None

    print(f"-------selected pos ----------: {selected_pos}")

    #  盤面の駒を動かす 
    if selected_place == "board":
        x0, y0 = selected_pos
        x1, y1 = to_pos
        piece = b.grid[y0][x0]
        to_piece = b.grid[y1][x1]

        # 勝敗判定
        if to_piece % 10 == 1:
            winner = player

        # 敵駒を取る場合
        if to_piece != 0 and b.is_enemy(to_piece, player):
            koma_type = b.unpromote(to_piece) % 10
            hands[player][koma_type] = hands[player].get(koma_type, 0) + 1

        # 盤面に反映
        b.grid[y1][x1] = piece
        b.grid[y0][x0] = 0

        # 成り判定
        if b.should_promote(piece, y0, y1, player):
            nari_check = True

    #  手駒を置く
    elif selected_place == "tegoma":
        piece = selected_pos[0]      # selected_pos はint
        x1,y1 = to_pos

        # 駒の配置
        if player == 1:    
            b.grid[y1][x1] = piece
        else:
            b.grid[y1][x1] = piece + 10

        # 手駒を減らす
        print(f"player2 : {player}")
        print(f"piece2 : {piece}")

        hands[player][piece] -= 1
        if hands[player][piece] == 0:
            del hands[player][piece]

    return {
        "winner": winner,
        "nari_check": nari_check,
        "board_grid": b.grid,
        "tegoma": hands,
    }


def handle_nari(board, player, to_pos):
    """
    成りの処理
    """
    b = Board()
    b.grid = [row[:] for row in board]

    x1, y1 = to_pos
    b.grid[y1][x1] = b.promote(b.grid[y1][x1])

    return {
        "board_grid": b.grid,
        "current_turn": player,
    }


def handle_ai_move(gamestate_dict, current_turn):
    """
    AIの手
    """
    b = Board()
    b.grid = [row[:] for row in gamestate_dict["board"]]

    hands = {
        1: dict(gamestate_dict["tegoma"][1]),
        2: dict(gamestate_dict["tegoma"][2]),
    }

    player = current_turn
    winner = None

    #  全合法手を収集 
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

    #  ランダムに手を選ぶ 
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
