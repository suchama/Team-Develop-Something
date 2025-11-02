# logic_shogi.py
"""
将棋のゲームロジック
"""

from typing import Dict, List, Tuple, Optional
from board import Board
from gamestate import GameState

def game_start() -> Dict:
    """
    将棋の初期局面を返す
    """
    b = Board()        # 初期配置は Board.__init__ に実装されている想定
    gs = GameState()
    gs.current_turn = 1  # 先手から開始
    return {
        "board": b.grid,
        "tegoma": {1: {}, 2: {}},              # 両者持ち駒は空
        "remaining_time": {1: 300, 2: 300},    # 秒数は適宜変更
        "current_turn": gs.current_turn,
    }


def get_valid_moves(board: List[List[int]], tegoma: Dict[int, Dict[int, int]],
                    player: int, place: str, pos: List[int]) -> List[List[int]]:
    """
    1回目のクリックで呼ばれる。
    - place: "board" or "tegoma"
    - pos: [x, y]
    """
    b = Board()
    b.grid = [row[:] for row in board]  # deepcopy

    if place == "board":
        x, y = pos
        return b.get_valid_moves(x, y, player)  # Board 側に合法手取得関数がある想定
    elif place == "tegoma":
        piece = pos[0]  # pos[0] を駒コードとみなす
        # 打てるマスを返す関数を Board に実装済みなら呼び出す
        return b.get_drop_positions(piece, player, tegoma[player])
    return []


def handle_player_move(board: List[List[int]], tegoma: Dict[int, Dict[int, int]], player: int,
                       selected_place: str, selected_pos: List[int], to_pos: List[int]) -> Dict:
    """
    2回目のクリックで呼ばれる。
    移動 or 打ちを反映し、盤面と持ち駒を更新。
    """
    b = Board()
    b.grid = [row[:] for row in board]  # deepcopy
    gs = GameState()
    gs.current_turn = player

    outcome = {
        "winner": None,
        "nari_check": False,
        "board_grid": None,
        "tegoma": tegoma,
    }

    if selected_place == "board":
        x0, y0 = selected_pos
        x1, y1 = to_pos
        piece = b.grid[y0][x0]

        # 取り駒処理
        captured = b.grid[y1][x1]
        if captured != 0:
            base = b.unpromote(captured) % 10  # 成駒なら素に戻す
            tegoma[player][base] = tegoma[player].get(base, 0) + 1

        # 移動
        b.grid[y1][x1] = piece
        b.grid[y0][x0] = 0

        # 成り判定（仮: Board.should_promote がある前提）
        if b.should_promote(piece, y0, y1, player):
            outcome["nari_check"] = True

    elif selected_place == "tegoma":
        # 打ち駒
        piece = selected_pos[0]
        x1, y1 = to_pos
        b.grid[y1][x1] = piece if player == 1 else piece + 10
        tegoma[player][piece] -= 1
        if tegoma[player][piece] == 0:
            del tegoma[player][piece]

    # 勝敗判定
    gs.check_winner()
    outcome["winner"] = gs.winner
    outcome["board_grid"] = b.grid
    outcome["tegoma"] = tegoma
    return outcome


def handle_nari(board: List[List[int]], player: int,
                from_pos: List[int], to_pos: List[int]) -> Dict:
    """
    成り選択が行われたとき呼ばれる。
    """
    b = Board()
    b.grid = [row[:] for row in board]
    x1, y1 = to_pos
    b.grid[y1][x1] = b.promote(b.grid[y1][x1])
    return {
        "board_grid": b.grid,
        "current_turn": player
    }


def handle_ai_move(game_state_dict: Dict, current_turn: int) -> Dict:
    """
    将棋AIの手を適用する（ダミー版）。
    とりあえずランダムで合法手を1つ選ぶなど。
    """
    b = Board()
    b.grid = [row[:] for row in game_state_dict["board"]]
    turn = int(current_turn)

    # TODO: 本格的な将棋AIがあればここで呼ぶ
    valid_all = []
    for y in range(9):
        for x in range(9):
            if b.is_own(b.grid[y][x], turn):
                moves = b.get_valid_moves(x, y, turn)
                for (mx, my) in moves:
                    valid_all.append(((x, y), (mx, my)))

    if not valid_all:
        # パス相当（本来は将棋にはない）
        return {
            "board_grid": b.grid,
            "current_turn": turn,
            "winner": None,
            "tegoma": game_state_dict["tegoma"]
        }

    # とりあえずランダムで1手選ぶ
    import random
    (x0, y0), (x1, y1) = random.choice(valid_all)
    piece = b.grid[y0][x0]
    b.grid[y1][x1] = piece
    b.grid[y0][x0] = 0

    gs = GameState()
    gs.current_turn = turn
    gs.swich_turn()

    return {
        "board_grid": b.grid,
        "current_turn": gs.current_turn,
        "winner": None,
        "tegoma": game_state_dict["tegoma"]
    }
