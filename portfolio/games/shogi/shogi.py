# 将棋ゲームの統合クラス
import pygame
from pygame.locals import *
import sys
import time
import random
from board import Board
from gamestate import GameState
from graphics import Graphics
from inputer import Inputer

class Shogi:
    # ①ゲームの初期化：盤面、手駒、手番を初期化
    def __init__(self):
        pygame.init()
        self.board = Board()
        self.gamestate = GameState()
        self.graphics = Graphics()
        self.inputer = Inputer()
        self.current_turn = self.gamestate.current_turn
        self.clock = pygame.time.Clock()
        self.running = True
        remaining_time = 120 # 持ち時間
        self.your_remaining_time = remaining_time
        self.opp_remaining_time = remaining_time
        self.zahyo = None
        self.turn_count = 0

    # ②画面の描画：ウィンドウ生成と初期盤面表示
    def display_update(self):
        self.graphics.draw_board(self.turn_count)
        self.graphics.board_update(self.board.grid, self.gamestate.hands)

    # ③プレイヤーの入力待ち
    def input_player(self):
        if self.current_turn == 1:
            remain_time = self.your_remaining_time
        else:
            remain_time = self.opp_remaining_time

        last_time = time.time()  # 最後に更新した時間

        # ターンの表示＋タイマー初期表示
        self.graphics.timer_update(self.current_turn, remain_time)

        while True:
            self.clock.tick(60)
            # 1秒ごとに残り時間を更新
            if time.time() - last_time >= 1:
                remain_time -= 1
                last_time = time.time()
                self.graphics.timer_update(self.current_turn, remain_time)

            if remain_time <= 0:
                #時間切れ
                if self.current_turn == 1:
                    self.your_remaining_time = remain_time
                else:
                    self.opp_remaining_time = remain_time
                return "timeout"
            for event in pygame.event.get():
                #バツボタンを押してやめた時
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    #通常クリック
                    if self.current_turn == 1:
                        self.your_remaining_time = remain_time
                    else:
                        self.opp_remaining_time = remain_time
                    return self.inputer.click_where("play", event.pos, self.graphics)

    # ④ 入力処理 → 移動判定 → ⑤移動処理 → ⑥勝敗判定 → ⑦手番交代
    def handle_turn(self):
        self.will_move = 0
        self.selected_pos = None

        while True:
            selected = self.input_player()
            if selected is None or selected == "timeout":
                self.will_move = 0
                self.graphics.board_update(self.board.grid, self.gamestate.hands)
                self.switch_turn_god()
                return

            #どこを押したか(ボード,手駒),手駒であれば自分か相手か,押した駒の種類, 押した位置
            place_type, player, piece_code, pos = selected

            if place_type == "retire":
                self.end_tyekku()
                continue

            elif place_type in {"board", "tegoma"}:
                x, y = pos

                # === クリック1回目：駒の選択 ===
                if self.will_move == 0:
                    #１回目のクリック場所と駒の種類を記憶しておく
                    self.selected_pos = pos
                    self.pis = piece_code
                    self.board.update_all_valid_moves(self.current_turn)
    
                    if place_type == "board":
                        clicked_piece = self.board.grid[y][x]
                        if self.board.is_own(clicked_piece, self.current_turn):
                            self.zahyo = [0, pos] 
                            self.graphics.board_update(self.board.grid, self.gamestate.hands)
                            self.graphics.blight(self.zahyo)
                            self.will_move = 1
                    else:
                        if player == 1 and self.current_turn == 1:
                            self.zahyo = [1, pos]
                            self.graphics.board_update(self.board.grid, self.gamestate.hands)
                            self.graphics.blight(self.zahyo)
                            self.will_move = 2
                        elif player == 2 and self.current_turn == 2: 
                            self.zahyo = [2, pos]
                            self.graphics.board_update(self.board.grid, self.gamestate.hands)
                            self.graphics.blight(self.zahyo)
                            self.will_move = 2
                    continue

                # === 2回目：移動先の選択 ===
                #１回目がボードなら
                elif self.will_move == 1:
                    self.graphics.bl_cancel()
                    #移動判定
                    #選択した駒の合法手を取得(方向のみ)
                    valid_moves = self.board.get_valid_moves(self.selected_pos[0], self.selected_pos[1], self.current_turn)
                    #もし打てるなら
                    if (x, y) in valid_moves:
                        #反則判定
                        #if True:
                            #continue
                        # 移動処理（簡易版：成り判定・捕獲・持ち駒管理などは未処理）
                        if self.board.is_enemy(self.board.grid[y][x], self.current_turn):
                            captured = self.board.grid[y][x]
                            base_piece = self.board.unpromote(captured) % 10   # 成りを戻して基本の駒コードへ
                            # 手駒のコードは全て10以下の値に統一してあるので%10が必要

                            if base_piece not in self.gamestate.hands[self.current_turn]:
                                self.gamestate.hands[self.current_turn][base_piece] = 0
                            self.gamestate.hands[self.current_turn][base_piece] += 1
                        if self.board.grid[y][x] == 1 or self.board.grid[y][x] == 11:
                            self.gamestate.winner = self.current_turn
                        self.board.grid[y][x] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]]
                        self.board.grid[self.selected_pos[1]][self.selected_pos[0]] = 0
                        self.graphics.draw_exe(self.turn_count)
                        self.graphics.board_update(self.board.grid, self.gamestate.hands)
                        
                        #なり判定
                        if (self.current_turn == 1 and y == 2 and self.board.grid[y][x]//20 == 0) or (self.current_turn == 2 and y == 6 and self.board.grid[y][x]//20 == 0) or (self.current_turn == 1 and y == 3 and self.selected_pos[1] == 2 and self.board.grid[y][x]//20 == 0) or (self.current_turn == 2 and y == 5 and self.selected_pos[1] == 6 and self.board.grid[y][x]//20 == 0):
                            self.zahyo = [0, [x, y]]
                            self.graphics.blight(self.zahyo)
                            if self.nari_tyekku():
                                self.board.grid[y][x] = self.board.grid[y][x] % 20 + 20
                            self.graphics.bl_cancel()
                            self.graphics.draw_board(self.turn_count)

                        if (self.current_turn == 1 and y <= 1) or (self.current_turn == 2 and y >= 7):
                            self.board.grid[y][x] = self.board.grid[y][x] % 20 + 20
                        print(self.gamestate.hands)
                        
                        #ターン切り替え
                        self.switch_turn_god()

                        return
                    #打てないなら
                    else:
                        self.damedayo()
                        continue
                #1回目が手駒で、2回目がボードなら    
                else:
                    self.graphics.bl_cancel()
                    if  place_type == "board":
                        if self.current_turn == 2:
                            self.pis += 10
                        
                        # 1. 既にマスが埋まっている
                        if self.board.grid[y][x] != 0:
                            self.damedayo()
                            continue

                        # 2. 二歩チェック
                        if self.pis in [8, 18] and self.board.is_double_pawn(x, self.current_turn):
                            self.damedayo()
                            print("2hu")
                            continue

                        # 3. 桂・香・歩の打てない段チェック
                        if self.pis in [8, 6, 7]:
                            if y == 0 or (self.pis == 6 and y == 1):
                                print("自分前すぎやて")
                                self.damedayo()
                                continue
                        elif self.pis in [18, 16, 17]:
                            if y == 8 or (self.pis == 16 and y == 7):
                                print("相手前すぎやて")
                                self.damedayo()
                                continue
                                            # 5. 実際に置く
                        self.board.grid[y][x] = self.pis
                        if self.current_turn == 2:
                            self.pis -= 10
                        self.gamestate.hands[self.current_turn][self.pis] -= 1
                        #ターン切り替え
                        self.switch_turn_god()
                    self.damedayo()

    # ターン切り替え
    def switch_turn_god(self):
        #ターン数のカウント
        self.turn_count += 1
        #勝敗チェック
        self.gamestate.check_winner()
        if self.gamestate.is_game_over():
            self.state_end()
        #勝敗がついていなければターン交代
        else:
            if self.your_remaining_time <= 20:
                self.your_remaining_time = 20
            if self.opp_remaining_time <= 20:
                self.opp_remaining_time = 20
            self.gamestate.switch_turn()
            self.current_turn = self.gamestate.current_turn
            self.graphics.draw_exe(self.turn_count)
            self.graphics.board_update(self.board.grid, self.gamestate.hands)
            self.will_move = 0    

    def damedayo(self):
        ##不正な手ですってことを表示するポップアップ##
        print("おけないよん")
        # 不正な場所なら選択解除してリセット
        self.will_move = 0
        self.graphics.draw_exe(self.turn_count)
        self.graphics.board_update(self.board.grid, self.gamestate.hands)

    def end_tyekku(self):
        msg = "give up ?"
        self.graphics.make_pop("play", msg, "no", "yes")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.pop_lr_click(event.pos, self.graphics)
                    if choice == "leftbutton":
                        print(132)
                        self.display_update()
                        return True
                    elif choice == "rightbutton":
                        self.state_end()     

    def nari_tyekku(self):
        msg = "promote piece ?"
        self.graphics.make_migipop("play", msg, "YES", "NO")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.migipop_lr_click(event.pos, self.graphics)
                    if choice == "leftbutton":
                        return True
                    elif choice == "rightbutton":
                        return None 

    # ⑧ 勝敗の表示 → 終了選択
    def state_end(self):
        winner = self.gamestate.winner
        msg = "you win" if winner == 1 else "opp win"
        self.graphics.make_pop("play", msg, "restart", "end")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.pop_lr_click(event.pos ,self.graphics)
                    if choice == "leftbutton":
                        self.__init__()
                        self.run()
                        return
                    elif choice == "rightbutton":
                        pygame.quit()
                        sys.exit()

    # メインループ
    def run(self):
        self.graphics.make_window()
        self.display_update()
        while self.running:
            self.handle_turn()

if __name__ == "__main__":
    game = Shogi()
    game.run()


'''打ち歩詰めはバグるので一旦なし
                    # 4. 打ち歩詰め（歩で王手詰みする場合）
                    if self.pis in [8, 18]:
                        # 仮に駒を置いてみる
                        original = self.board.grid[y][x]
                        self.board.grid[y][x] = self.pis

                        if self.board.is_checkmate(3 - self.current_turn):  # 相手が詰んでいたら
                            self.board.grid[y][x] = original
                            self.damedayo()
                            print("詰んでしもてるやん")
                            continue

                        self.board.grid[y][x] = original  # 戻す
'''
