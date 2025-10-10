#logic_shogi
"""
将棋ロジック
Board と GameState を利用して、サーバー(app.py)から呼び出される関数群を提供
"""

from typing import Dict, List, Tuple
from board import Board
from gamestate import GameState
from utils import _can_drop_on_rank, _error_out
import random


def game_start() -> Dict:
    """
    初期盤面を返す
    """
    b = Board()
    gs = GameState()
    gs.current_turn = 1
    gs.board = b
    gs.hands = {1: {}, 2: {}}
    return {
        "board": b.grid,
        "tegoma": gs.hands,
        "remaining_time": {1: 300, 2: 300},
        "current_turn": gs.current_turn
    }

def get_valid_moves(board: List[List[int]], 
                    tegoma: Dict[int, Dict[int, int]],
                    player: int, 
                    place:str,
                    pos: List[int]
                    ) -> List[List[int]]:
    """
    クリック1回目の手の取得
    """
    b = Board()
    b.grid = [row[:] for row in board]
    
    if place == "board":
        x, y = pos
        return b.get_valid_moves(x, y, player)
    
    elif place == "tegoma":
        piece = pos[0]
        moves = []
        for y in range(9):
            for x in range(9):
                if b.grid[y][x] != 0:   # 0だと駒なし
                    continue
                if piece == 8 and b.is_double_pawn(x, player):  #二歩
                    continue
                if not _can_drop_on_rank(piece, y, player):     #行き場なし
                    continue
                moves.append([x, y])
        return moves
    return []


def handle_player_move(board: List[List[int]], 
                       tegoma: Dict[int, Dict[int,int]],
                       player: int, 
                       selected_place: str,             # プレイヤーが押した場所
                       selected_pos: List[int], 
                       to_pos: List[int]) -> Dict:
    """
    クリック２回目の処理
    """
    b = Board()
    b.grid = [row[:] for row in board]

    gs = GameState()
    gs.current_turn = player
    gs.hands = {1: dict(tegoma[1]), 2: dict(tegoma[2])}
    gs.board = b

    nari_check = False

    if selected_place == "board":
        x0, y0 = selected_pos
        x1, y1 = to_pos
        piece  = b.grid[y0][x0]
        
        captured = b.grid[y1][x1]
        if captured != 0 and b.is_enemy(captured, player):
            base = b.unpromote(captured) % 10
            gs. hands[player][base] = gs.hands[player].get(base, 0) + 1

        b.grid[y1][x1] = piece
        b.grid[y0][x0] = 0

        # 成り判定
        if b.should_promote(piece, y0, y1, player):
            nari_check = True
    
    elif selected_place == "tegoma":
        piece = selected_pos[0]
        x1,y1 = to_pos
        if b.grid[y1][x1] != 0:
            return _error_out(b, gs, "そのマスには置けません。")
        
        # 二歩・行き場なし
        if piece == 8 and b.is_double_pawn(x1, player):
            return _error_out(b, gs, "二歩です。")
        if not _can_drop_on_rank(piece, y1, player):
            return _error_out(b, gs, "打てない段です。")
        
        if player == 1:
            place_code = piece
        else: 
            place_code = piece + 10
        b.grid[y1][x1] = place_code
        gs.hands[player][piece] -= 1
        if gs.hands[player][piece] == 0:
            del gs.hands[player][piece]

    # 勝敗判定
    gs.check_winner()
    if gs.winner is None:
        gs.switch_turn()
    
    return {
        "winner": gs.winner,
        "nari_check": nari_check,
        "board_grid": b.grid,
        "tegoma": gs.hands
    }

def handle_nari(board: List[List[int]],
                player: int,
                from_pos: List[int],
                to_pos: List[int],
                ) -> Dict:
    """
    成りの処理
    """
    b = Board()
    b.grid = [row[:] for row in board]
    x1, y1 = to_pos
    b.grid[y1][x1] = b.promote(b.grid[y1][x1])
    return{
        "board_grid": b.grid,
        "current_turn": player
    }
 
def handle_ai_move(gamestate_dict: Dict,
                    current_turn: int,
                    ) -> Dict:
    """
    AIの手（ランダムな合法手）
    """
    b = Board()
    b.grid = [row[:] for row in gamestate_dict["board"]]
    turn = current_turn

    moves = []
    for y in range(9):
        for x in range(9):
            if b.is_own(b.grid[y][x], turn):
                for (nx,ny) in b.get_valid_moves(x, y, turn):   # nx,nyはnextの手
                    moves.append(((x,y),(nx,ny)))

    if not moves:
        return {
            "board_grid": b.grid,
            "current_turn": turn,
            "winner": None,
            "tegoma": gamestate_dict["tegoma"]
        }

    (x0,y0),(x1,y1) = random.choice(moves)
    piece = b.grid[y0][x0]
    b.grid[y1][x1] = piece
    b.grid[y0][x0] = 0

    gs = GameState()
    gs.current_turn = turn
    gs.board = b
    gs.hands = gamestate_dict["tegoma"]
    gs.check_winner()
    if gs.winner is None:
        gs.switch_turn()

    return {
        "board_grid": b.grid,
        "current_turn": gs.current_turn,
        "winner": gs.winner,
        "tegoma": gs.hands
    }
