# logic_othello.py 
"""
サーバー(app.py)からのリクエストを処理し、オセロのロジック全体を管理
"""
from typing import Dict, List, Tuple
from board import Board
from gamestate import GameState
from ai import AI


def game_start() -> Dict:
    """
    初期局面を作成して返す。
    出力
        {"board": board_grid, "remaining_time": {1: 300,2: 300}, "current_turn": 1}
    """
    board = Board()                 # Board() 側で初期配置が入る想定
    gs = GameState()
    gs.current_turn = 1             # 先手=黒から開始
    remaining = {1: 300, 2: 300}    # 必要に応じて変更可

    return {
        "board": board.grid,
        "remaining_time": remaining,
        "current_turn": gs.current_turn,
    }


def handle_player_move(current_grid: List[List[int]], player: int, pos: List[int]) -> Dict:
    """
    プレイヤーの1手を処理
    出力:
      置けない: {"status":"error"}
      置けた  : {
        "status":"success",
        "board_grid": board.grid,
        "current_turn": current_turn: 1|2,
        "winner": gs.winner: None|1|2,
        "scores": {"black":black_count, "white":white_count}
      }
    """

    x, y = pos
    board = Board()
    board.grid = [row[:] for row in current_grid]

    gs = GameState()
    gs.current_turn = int(player)

    # 有効手判定
    board.update_valid(gs.current_turn)
    valid_moves = set(board.get_valid(gs.current_turn))

    if (x, y) not in valid_moves:
        b, w = board.count_piece()
        return {
            "status": "error",
            "message": "無効な手です。",
            # app.py は status のみ参照だが、デバッグに便利なのでスコアも同梱
            "scores": {"black": b, "white": w},
        }

    # 反転を含めて着手
    board.reversi(x, y, gs.current_turn)
    gs.pass_reset()  # 打てたので連続パス数リセット（Othello 仕様）

    # 終局 or 交代判定
    board.update_valid(1)
    board.update_valid(2)

    is_game_over = False
    if not board.get_valid(1) and not board.get_valid(2):
        is_game_over = True
    elif board.full_gameover():
        is_game_over = True

    if is_game_over:
        gs.count_winner(board)        # gs.winner を設定
        next_turn = gs.current_turn   # 終局時はそのままでも OK（app 側は winner を見て終了）
    else:
        gs.swich_turn()               # 手番交代（※ swich_turn のスペルは既存に合わせる）
        next_turn = gs.current_turn

    b, w = board.count_piece()
    return {
        "status": "success",
        "board_grid": board.grid,
        "current_turn": next_turn,
        "winner": gs.winner,                      # None / 1 / 2
        "scores": {"black": b, "white": w},
    }


def check_pass(current_grid: list[list[int]], current_turn: int) -> dict:
    """
    今の手番が打てるか？だけを判定して返す。
    出力:
        {"pass": bool}
    """
    board = Board()
    board.grid = [row[:] for row in current_grid]

    board.update_valid(current_turn)
    can_play_now = bool(board.get_valid(current_turn))
    return {"pass": (not can_play_now)}


def handle_ai_move(game_state_dict: dict, current_turn: int) -> dict:
    """
    AI の一手を決定。
    game_state_dict を in-place 更新しつつ outcome も返す。
    """
    b = Board()
    b.grid = [row[:] for row in game_state_dict["board"]]
    turn = int(current_turn)

    # AIの指し手を決定。難易度はhard
    difficulty = game_state_dict.get("ai_difficulty", "hard")
    ai = AI(difficulty=difficulty)
    move_x, move_y = ai.get_move(b, turn)  # None は返らない前提

    # 着手を適用
    b.reversi(move_x, move_y, turn)

    # 終局判定
    b.update_valid(1)
    b.update_valid(2)
    is_over = (not b.get_valid(1) and not b.get_valid(2)) or b.full_gameover()

    gs = GameState()
    winner = None
    if is_over:
        gs.count_winner(b)
        winner = gs.winner
        game_state_dict["winner"] = winner
        next_turn = turn  # 終局なら turn のまま
    else:
        gs.current_turn = turn
        gs.swich_turn()
        next_turn = gs.current_turn

    # スコア
    black, white = b.count_piece()

    game_state_dict["board"] = b.grid
    game_state_dict["current_turn"] = next_turn

    return {
        "board_grid": b.grid,
        "current_turn": next_turn,
        "winner": winner,
        "scores": {"black": black, "white": white},
    }


