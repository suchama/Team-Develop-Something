#盤面データ、手番、持ち駒、駒の配置、勝敗情報の管理
import random
from board import Board

class GameState:
    def __init__(self):
        # 現在のターン（1:自分, 2:相手）をランダムで決定
        self.first = random.choice([1, 2])
        self.current_turn = self.first
        # 勝者情報（None:未定, 1:自分, 2:相手）
        self.winner = None
        # 各プレイヤーの持ち駒（駒コードとその数の辞書）
        self.hands = {
            1: {1:1, 2:1, 3:2, 4:2, 5:2, 6:3, 7:2, 8:2, 9:4, 10:2, 11:1, 12:1, 13:2, 14:1},  # 自分
            2: {101:1, 102:1, 103:2, 104:2, 105:2, 106:3, 107:2, 108:2, 109:4, 110:2, 111:1, 112:1, 113:2, 114:1}   # 相手
        }
        # 盤面の状態を管理するBoardインスタンス
        self.board = Board()
        self.game_state = "start" #start(初期配置) or run(対局) or end(ゲーム終了)　多分endは使わない
        self.your_state = "start" #start or run
        self.opps_state = "start" #start or run

    # 手番を交代する
    def switch_turn(self):
        self.current_turn = 1 if self.current_turn == 2 else 2

    # 勝敗を判定（相手の帥が存在しない、または詰みなら勝利）
    def check_winner(self, grid):
        enemy_turn = 2 if self.current_turn == 1 else 1
        self.board.update_all_valid_moves(enemy_turn)
        enemy_king_code = 101 if self.current_turn == 1 else 1
        found = False
        for row in grid[0]:
            for z in row:
                if enemy_king_code in z:
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