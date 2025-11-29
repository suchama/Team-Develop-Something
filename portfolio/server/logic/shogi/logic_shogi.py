# logic_shogi.py
"""
将棋ロジック
Board と GameState を利用して、サーバー(app.py)から呼び出される関数群を提供
"""

from typing import Dict, List
from .board import Board
from .gamestate import GameState
from .utils import _can_drop_on_rank, _error_out
import torch
import torch.nn.functional as F
import numpy as np
from .architecture import ShogiCNN
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
    簡易学習版どすえ
    
    """
    b = Board()
    b.grid = [row[:] for row in gamestate_dict["board"]]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # モデル読み込み
    import os

    # logic_shogi.py があるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "params", "best_shogi_cnn_model_2.pth")
    print("MODEL_PATH =", MODEL_PATH)

    shogi_ai_model = ShogiCNN().to(device)
    shogi_ai_model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    shogi_ai_model.eval()

    hands = {
        1: dict(gamestate_dict["tegoma"][1]),
        2: dict(gamestate_dict["tegoma"][2]),
    }

    player = current_turn
    winner = None

    board_tensor = board_to_tensor(b.grid, player).to(device)

    with torch.no_grad():
        logits = shogi_ai_model(board_tensor)[0]      # shape [6561]
        probs = F.softmax(logits, dim=0).cpu().numpy()

    #  全合法手を収集 
    moves = []
    for y in range(9):
        for x in range(9):
            if b.is_own(b.grid[y][x], player):
                for nx, ny in b.get_valid_moves(x, y, player):
                    from_id = 9*y + x
                    to_id   = 9*nx + nx
                    move_id = 81*from_id + to_id
                    moves.append((move_id, (x, y, nx, ny)))

    if not moves:
        return {
            "board_grid": b.grid,
            "current_turn": player,
            "winner": None,
            "tegoma": hands,
        }

    #  手の選択
    move_scores = [(probs[mid], move) for mid, move in moves]
    move_scores.sort(reverse=True, key=lambda x: x[0])
    _, (x0, y0, x1, y1) = move_scores[0]

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

    # これ消すな。AIだけはこっちでターンを管理
    next_turn = player % 2 + 1

    return {
        "board_grid": b.grid,
        "current_turn": next_turn,
        "winner": winner,
        "tegoma": hands,
    }


def board_to_tensor(board_grid, current_turn):
    import numpy as np
    tensor = np.zeros((40, 9, 9), dtype=np.float32)

    for y in range(9):
        for x in range(9):
            piece = board_grid[y][x]

            if piece == 0:
                continue

            # --- 安全な駒番号チェック ---
            if 1 <= piece <= 20:          # 先手
                idx = piece - 1
            elif 21 <= piece <= 40:       # 後手
                idx = piece - 13
            else:
                # 範囲外の番号は無視（エラー回避）
                # 例: 99, -1, 50 など
                continue

            idx = max(0, min(idx, 39))
            tensor[idx, y, x] = 1.0

    tensor[-1, :, :] = 1.0 if current_turn == 1 else 0.0

    return torch.tensor(tensor, dtype=torch.float32).unsqueeze(0)
