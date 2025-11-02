#盤面データ、手番、持ち駒、駒の配置、勝敗情報の管理
import random
from board import Board

class GameState:
    def __init__(self):
        # 現在のターン（1:自分, 2:相手）をランダムで決定
        self.current_turn = random.choice([1, 2])
        # 勝者情報（None:未定, 1:自分, 2:相手）
        self.winner = None
        # 各プレイヤーの持ち駒（駒コードとその数の辞書）
        self.hands = {
            1: {},  # 自分
            2: {}   # 相手
        }
        # 盤面の状態を管理するBoardインスタンス
        self.board = Board()

    # 手番を交代する
    def switch_turn(self):
        self.current_turn = 1 if self.current_turn == 2 else 2

    # 勝敗を判定（相手の玉が存在しない、または詰みなら勝利）
    def check_winner(self):
        enemy_turn = 2 if self.current_turn == 1 else 1
        self.board.update_all_valid_moves(enemy_turn)
        enemy_king_code = 11 if self.current_turn == 1 else 1
        found = False
        for row in self.board.grid:
            if enemy_king_code in row:
                found = True
                break
        if not found:
            self.winner = self.current_turn
            return

        # 詰みチェック
        if self.board.is_checkmate(self.current_turn):
            self.winner = self.current_turn

    # 降参したときの処理（相手の勝ち）
    def surrender(self):
        self.winner = 2 if self.current_turn == 1 else 1

    # ゲーム終了かどうかを判定（勝者が決まっていれば終了）
    def is_game_over(self):
        return self.winner is not None