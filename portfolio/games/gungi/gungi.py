# 軍議ゲームの統合クラス
import pygame
from pygame.locals import *
import sys
import time
import random
from board import Board
from gamestate import GameState
from graphics import Graphics
from inputer import Inputer
class Gungi:
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
        remaining_time = 600 # 持ち時間
        self.your_remaining_time = remaining_time
        self.opp_remaining_time = remaining_time
        self.turn_count = 1
        self.last_time = time.time()
        self.remain_time_full = remaining_time

    # ②画面の描画：ウィンドウ生成と初期盤面表示
    def display_update(self):
        self.graphics.draw_board(self.turn_count)
        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)

    #  ③プレイヤーの入力待ち
    def input_player(self):
        if self.gamestate.game_state == "start" and (self.turn_count == 1 or self.turn_count == 2):
            self.selected_pos = [0,0]
            self.pis = 1 + (self.current_turn-1) * 100
            self.board.update_all_valid_moves(self.current_turn)
            self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
            self.graphics.blight(self.board.grid, self.gamestate.hands, self.current_turn, "tegoma", self.selected_pos)
            self.will_move = 2
        if self.current_turn == 1:
            remain_time = self.your_remaining_time
        else:
            remain_time = self.opp_remaining_time
        #self.last_time = time.time()  # 最後に更新した時間

        # ターンの表示＋タイマー初期表示
        self.graphics.timer_update(self.current_turn, remain_time)

        while True:
            self.clock.tick(60)
            # 1秒ごとに残り時間を更新
            if (time.time() - self.last_time) >= (self.remain_time_full - remain_time + 1):#右辺はディスプレイ上の経過時間＋１
                remain_time -= 1
                
                self.graphics.timer_update(self.current_turn, remain_time)

            if remain_time <= 0:
                #時間切れ
                if self.current_turn == 1:
                    self.your_remaining_time = remain_time
                    if self.gamestate.your_state == "start":
                        self.gamestate.your_state = "run"
                else:
                    self.opp_remaining_time = remain_time
                    if self.gamestate.opps_state == "start":
                        self.gamestate.opps_state = "run"
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
                    buttonD = self.inputer.click_where(self.graphics.buttonD, event.pos, self.graphics)
                    if buttonD[0] == 'None':
                        return self.inputer.click_where("play", event.pos, self.graphics)
                    else:
                        return buttonD

    # ⑤ 入力処理 → 移動判定 → ⑥移動処理 → ⑦勝敗判定 → ⑧手番交代
    def handle_turn(self):
        self.will_move = 0
        self.selected_pos = None

        while True:

            #self.clock.tick(60)
            selected = self.input_player()
            if selected is None or selected == "timeout":
                if self.gamestate.game_state == "start" and (self.turn_count == 1 or self.turn_count == 2):
                    if self.current_turn == 1:
                        pos = [4, 7]
                    else:
                        pos = [4, 1]
                    selected = ["board", self.current_turn, 1 + (self.current_turn - 1) * 100, pos]
                else:
                    self.will_move = 0
                    self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                    self.switch_turn_god()
                    continue

            #どこを押したか(ボード,手駒),手駒であれば自分か相手か,押した駒の種類, 押した位置
            place_type, player, piece_code, pos = selected

            ##初期配置中のクリック処理
            if place_type == "終了":
                if self.finish_tyekku():
                    if self.gamestate.your_state == "run" and self.gamestate.opps_state == "run":
                        self.gamestate.game_state = "run"
                        self.turn_count = 1
                        self.current_turn = self.gamestate.first
                        self.graphics.buttonD = "降参"
                        self.graphics.draw_exe(self.turn_count)
                        self.display_update()
                    self.switch_turn_god()
                self.will_move = 0
                continue

            elif self.gamestate.game_state == "start" and place_type in {"board", "tegoma"}:
                x, y = pos
                # === クリック1回目：駒の選択 ===
                if self.will_move == 0:
                    if place_type == "board":
                        self.selected_pos = pos
                        self.graphics.list(self.selected_pos)
                        continue
                    self.selected_pos = pos
                    self.pis = piece_code
                    self.graphics.list(self.selected_pos)
                    #１回目のクリック場所と駒の種類を記憶しておく
                    if self.board.is_enemy(piece_code,self.current_turn) or piece_code ==0:
                        continue
                    self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                    self.valid_moves = self.board.get_valid_moves(self.selected_pos[0], self.selected_pos[1], self.current_turn)
                    if self.current_turn == 1:
                        remain_time = self.your_remaining_time
                    else:
                        remain_time = self.opp_remaining_time
                    self.graphics.timer_update(self.current_turn, remain_time)
                    self.graphics.blight(self.board.grid, self.gamestate.hands, self.current_turn, place_type, self.selected_pos)
                    self.will_move = 2
                    continue

                #1回目が手駒で、2回目がボードなら    
                else:
                    if place_type == "board":
                        # 1. 自陣(3列目まで)の範囲か
                        if (self.current_turn == 1 and (not 6 <= y <= 8)) or (self.current_turn == 2 and (not 0 <= y <= 2)):
                            self.damedayo()
                            continue

                        # 2. 既に3つの駒が重なっているか
                        if self.board.high_memory[y][x] == 3:
                            self.damedayo()
                            continue

                        # 3.帥にはツケることができない
                        if self.board.grid[y][x][self.board.high_memory[y][x] -1 ] == 1 + 100 * (self.current_turn -1 ):
                            self.damedayo()
                            continue
                        
                        # 4. 実際に置く
                        if self.board.high_memory[y][x] == 0:
                            self.board.grid[y][x][0] = self.pis
                            self.board.high_memory[y][x] = 1
                        else:
                            self.board.grid[y][x][self.board.high_memory[y][x]] = self.pis
                            self.board.high_memory[y][x] += 1

                        # 5.置いた駒を手駒から減らす
                        self.gamestate.hands[self.current_turn][self.pis] -= 1

                        # 6.もし手駒が0になったら初期配置は終了
                        if all(value == 0 for value in self.gamestate.hands[self.current_turn].values()):
                            if self.current_turn == 1:
                                self.gamestate.your_state = "run"
                            else:
                                self.gamestate.opps_state = "run"
                        #相手が初期配置を終了していなければターン切り替え
                        if (self.gamestate.your_state == "start" and self.current_turn == 2) or (self.gamestate.opps_state == "start" and self.current_turn == 1):
                            self.switch_turn_god()
                        #どちらも初期配置を終了していたら対局開始
                        elif self.gamestate.your_state == "run" and self.gamestate.opps_state == "run":
                            self.gamestate.game_state = "run"
                            self.turn_count = 1
                            self.current_turn = self.gamestate.first
                            self.graphics.buttonD = "降参"
                            self.graphics.draw_exe(self.turn_count)
                            self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                        else:
                            self.graphics.list(self.selected_pos)
                            self.switch_turn_god()
                            self.turn_count -= 1
                            self.switch_turn_god()
                        continue
                    self.damedayo()

            ##対局中のクリック処理
            elif place_type == "降参":
                self.end_tyekku()
                self.will_move = 0
                continue

            elif self.gamestate.game_state == "run" and place_type in {"board", "tegoma"}:
                x, y = pos
                # === クリック1回目：駒の選択 ===
                if self.will_move == 0:
                    #１回目のクリック場所と駒の種類を記憶しておく
                    self.selected_pos = pos
                    self.pis = piece_code
                    self.board.update_all_valid_moves(self.current_turn)
    
                    if place_type == "board":
                        clicked_piece = self.board.grid[y][x][self.board.high_memory[y][x] - 1]
                        if self.board.is_enemy(clicked_piece, self.current_turn) or clicked_piece == 0:
                            self.graphics.list(self.selected_pos)
                            continue
                        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                        self.valid_moves = self.board.get_valid_moves(self.selected_pos[0], self.selected_pos[1], self.current_turn)
                        for x,y in self.valid_moves:
                            if self.board.grid[y][x][self.board.high_memory[y][x] - 1 ] == 1 + 100 * (self.current_turn -1 ):
                                self.valid_moves.remove((x,y))
                        if self.current_turn == 1:
                            remain_time = self.your_remaining_time
                        else:
                            remain_time = self.opp_remaining_time
                        self.graphics.timer_update(self.current_turn, remain_time)
                        self.graphics.glory(self.valid_moves)
                        self.graphics.blight(self.board.grid, self.gamestate.hands, self.current_turn, place_type, self.selected_pos)
                        self.graphics.list(self.selected_pos)
                        self.will_move = 1
                    else:
                        if self.board.is_enemy(piece_code,self.current_turn) or piece_code == 0:
                            continue
                        self.selected_pos = pos
                        self.pis = piece_code
                        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                        self.valid_moves = self.board.get_valid_moves(self.selected_pos[0], self.selected_pos[1], self.current_turn)
                        if self.current_turn == 1:
                            remain_time = self.your_remaining_time
                        else:
                            remain_time = self.opp_remaining_time
                        self.graphics.timer_update(self.current_turn, remain_time)
                        self.graphics.blight(self.board.grid, self.gamestate.hands, self.current_turn, place_type, self.selected_pos)
                        self.will_move = 2
                    continue

                # === 2回目：移動先の選択 ===
                #１回目がボード、2回目もボードなら
                elif self.will_move == 1:
                    if place_type == "board":
                        #同じ場所には移動しない
                        if (x,y) == self.selected_pos:
                            self.damedayo()
                            continue
                        #移動判定
                        #もし打てるなら
                        if (x, y) in self.valid_moves:
                            # 移動処理
                            #移動先に駒がなかったとき
                            if self.board.high_memory[y][x] == 0:
                                self.board.grid[y][x][self.board.high_memory[y][x]] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                self.board.high_memory[y][x] += 1
                                self.graphics.draw_exe(self.turn_count)
                                self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                            #移動先が敵の駒だったとき
                            elif self.board.is_enemy(self.board.grid[y][x][self.board.high_memory[y][x] - 1], self.current_turn):
                                #帥を取ったら勝ち
                                if self.board.grid[y][x][self.board.high_memory[y][x] - 1] == 1 or self.board.grid[y][x][self.board.high_memory[y][x] - 1] == 101:
                                    self.gamestate.winner = self.current_turn
                                #移動先が相手の帥ではなく、さらにツケることが可能なとき
                                elif (self.board.high_memory[y][x] == 1 or self.board.high_memory[y][x] == 2):
                                    #ツケる
                                    if self.tuke_tyekku():
                                        self.board.grid[y][x][self.board.high_memory[y][x]] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                        self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                        self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                        self.board.high_memory[y][x] += 1
                                        self.graphics.draw_exe(self.turn_count)
                                        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                    #ツケない
                                    else:
                                        #1段の相手駒を取る
                                        if self.board.high_memory[y][x] == 1:
                                            self.board.grid[y][x][self.board.high_memory[y][x] - 1] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                            self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                            self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                        #2段の駒を取るとき、2段とも相手駒だった場合
                                        elif self.board.high_memory[y][x] ==  2 and self.board.is_enemy(self.board.grid[y][x][0], self.current_turn):
                                            self.board.grid[y][x][0] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                            self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                            self.board.grid[y][x][1] = 0
                                            self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                            self.board.high_memory[y][x] = 1
                                        #2段の駒を取るとき、1段目は自駒だった場合
                                        else:
                                            self.board.grid[y][x][self.board.high_memory[y][x] - 1] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                            self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                            self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                        self.graphics.draw_exe(self.turn_count)
                                        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                    self.bou_tyekku(x,y)
                                #ツケれないとき(3段目が相手の駒)
                                else:
                                    #2段目が自駒だった場合
                                    if self.board.is_own(self.board.grid[y][x][1], self.current_turn):
                                        self.board.grid[y][x][self.board.high_memory[y][x] - 1] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                        self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                        self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                    #1段目が自駒だった場合
                                    elif self.board.is_own(self.board.grid[y][x][0], self.current_turn):
                                        self.board.grid[y][x][1] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                        self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                        self.board.grid[y][x][2] = 0
                                        self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -=  1
                                        self.board.high_memory[y][x] = 2
                                    #3段とも相手の駒だった場合
                                    else:
                                        self.board.grid[y][x][0] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                        self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                        self.board.grid[y][x][1] = 0
                                        self.board.grid[y][x][2] = 0
                                        self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                        self.board.high_memory[y][x] = 1                                         
                                    self.graphics.draw_exe(self.turn_count)
                                    self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                    self.bou_tyekku(x,y)
                            #移動先が自分の駒(1,2)だったとき(3はvalidで弾かれる)
                            elif (self.board.high_memory[y][x] == 1 or self.board.high_memory[y][x] == 2):
                                #帥にはツケることができない
                                if self.board.grid[y][x][self.board.high_memory[y][x] -1 ] == 1 + 100 * (self.current_turn -1 ):
                                    self.damedayo()
                                    continue
                                self.board.grid[y][x][self.board.high_memory[y][x]] = self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1]
                                self.board.grid[self.selected_pos[1]][self.selected_pos[0]][self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] - 1] = 0
                                self.board.high_memory[self.selected_pos[1]][self.selected_pos[0]] -= 1
                                self.board.high_memory[y][x] += 1
                                self.graphics.draw_exe(self.turn_count)
                                self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                self.bou_tyekku(x,y)                                   
                            else:
                                self.damedayo()
                                continue
                            #ターン切り替え
                            self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                            self.switch_turn_god()
                        else:
                            self.damedayo()
                            continue
                        return
                    #打てないなら
                    else:
                        self.damedayo()
                        continue
                #1回目が手駒で、2回目がボードなら    
                else:
                    if place_type == "board":  
                        # 1. 自駒の最奥までの範囲か
                        self.saioku = self.saioku_tyekku(self.current_turn)
                        if (self.current_turn == 1 and (not self.saioku <= y <= 8)) or (self.current_turn == 2 and (not 0 <= y <= self.saioku)):
                            self.damedayo()
                            continue

                        # 2. 既に3つの駒が重なっているか
                        if self.board.high_memory[y][x] == 3:
                            self.damedayo()
                            continue

                        # 3.帥にはツケることができない
                        if self.board.grid[y][x][self.board.high_memory[y][x] -1 ] == 1 + 100 * (self.current_turn -1 ):
                            self.damedayo()
                            continue
                        
                        # 4.一番上が敵のコマだったら(謀以外の駒は)新はできない
                        if self.board.is_enemy(self.board.grid[y][x][self.board.high_memory[y][x] - 1], self.current_turn) and (not (self.pis % 100 == 14)):
                            self.damedayo()
                            continue

                        # 5. 実際に置く
                        if self.board.high_memory[y][x] == 0:
                            self.board.grid[y][x][0] = self.pis
                            self.board.high_memory[y][x] = 1
                        else:
                            self.board.grid[y][x][self.board.high_memory[y][x]] = self.pis
                            self.board.high_memory[y][x] += 1

                        # 6.置いた駒を手駒から減らす
                        self.gamestate.hands[self.current_turn][self.pis] -= 1

                        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                        self.bou_tyekku(x,y)
                        #ターン切り替え
                        self.switch_turn_god()
                    else:
                        self.damedayo()
                        continue
            elif place_type == "帥を配置せよ":
                continue
            else:
                self.damedayo()

    # ターン切り替え
    def switch_turn_god(self):
        #self.graphics.list(0)
        #ターン数のカウント
        self.turn_count += 1
        # 初期配置中であり、3ターン目(両者とも帥を置いた後)であれば、finishボタンを表示
        if self.gamestate.game_state == "start" and self.turn_count == 3:
            self.graphics.buttonD = "終了"
            self.display_update()

        #対局中であれば勝敗チェック
        if self.gamestate.game_state == "run":
            self.gamestate.check_winner([self.board.grid])
            if self.gamestate.is_game_over():
                self.state_end()
        #勝敗がついていなければターン交代
        if self.your_remaining_time <= 60:
            self.your_remaining_time = 60
        if self.opp_remaining_time <= 60:
            self.opp_remaining_time = 60
        self.gamestate.switch_turn()
        self.current_turn = self.gamestate.current_turn
        self.graphics.draw_exe(self.turn_count)
        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
        self.will_move = 0   
        if self.current_turn == 1:
            self.remain_time_full = self.your_remaining_time
        if self.current_turn == 2:
            self.remain_time_full = self.opp_remaining_time
        self.last_time = time.time()  # 最後に更新した時間
        
    def bou_tyekku(self, x, y):
        #self.graphics.list(0)
        if (self.current_turn == 1 and self.board.grid[y][x][self.board.high_memory[y][x] - 1] == 14 and (not self.board.high_memory[y][x] == 1)) or (self.current_turn == 2 and self.board.grid[y][x][self.board.high_memory[y][x] - 1] == 114 and (not self.board.high_memory[y][x] == 1)):
            negaereru = []
            if self.board.high_memory[y][x] == 2:
                if self.board.is_enemy(self.board.grid[y][x][0], self.current_turn):
                    if (self.board.grid[y][x][0] + ((self.current_turn -1 ) * (200) - 100)) in self.gamestate.hands[self.current_turn]:
                        if not self.gamestate.hands[self.current_turn][self.board.grid[y][x][0] + ((self.current_turn -1 ) * (200) - 100)] == 0:
                            negaereru.append(0)
            else:
                if self.board.is_enemy(self.board.grid[y][x][0], self.current_turn):
                    if (self.board.grid[y][x][0] + ((self.current_turn -1 ) * (200) - 100)) in self.gamestate.hands[self.current_turn]:
                        if not self.gamestate.hands[self.current_turn][self.board.grid[y][x][0] + ((self.current_turn -1 ) * (200) - 100)] == 0:
                            negaereru.append(0)
                if self.board.is_enemy(self.board.grid[y][x][1], self.current_turn):
                    if (self.board.grid[y][x][1] + ((self.current_turn -1 ) * (200) - 100)) in self.gamestate.hands[self.current_turn]:
                        if not self.gamestate.hands[self.current_turn][self.board.grid[y][x][1] + ((self.current_turn -1 ) * (200) - 100)] == 0:
                            negaereru.append(1)
            if negaereru != []:
                msg = "寝返らせる?"
                self.graphics.make_migipop("寝返らせるか確認ポップ", msg, "いいえ", "はい")
                if self.current_turn == 1:
                    remain_time = self.your_remaining_time
                else:
                    remain_time = self.opp_remaining_time
                #last_time = time.time()  # 最後に更新した時間

                # ターンの表示＋タイマー初期表示
                self.graphics.timer_update(self.current_turn, remain_time)

                while True:
                    self.clock.tick(60)
                    # 1秒ごとに残り時間を更新
                    if time.time() - self.last_time >= self.remain_time_full - remain_time + 1:
                        remain_time -= 1
                        self.graphics.timer_update(self.current_turn, remain_time)

                    if remain_time <= 0:
                        #時間切れ
                        if self.current_turn == 1:
                            self.your_remaining_time = remain_time
                            if self.gamestate.your_state == "start":
                                self.gamestate.your_state = "run"
                        else:
                            self.opp_remaining_time = remain_time
                            if self.gamestate.opps_state == "start":
                                self.gamestate.opps_state = "run"
                        return None
                    for event in pygame.event.get():
                        if self.current_turn == 1:
                            self.your_remaining_time = remain_time
                        else:
                            self.opp_remaining_time = remain_time
                        if self.your_remaining_time <= 60:
                            self.your_remaining_time = 60
                        if self.opp_remaining_time <= 60:
                            self.opp_remaining_time = 60
                        if event.type == MOUSEBUTTONDOWN and event.button == 1:
                            place_type, player, piece_code, pos = self.inputer.click_where("play", event.pos, self.graphics)
                            if place_type == "board":
                                self.graphics.list(pos)
                            else:
                                choice = self.inputer.click_where("寝返らせるか確認ポップ", event.pos, self.graphics)
                            if choice[0] == "いいえ":
                                return False
                            elif choice[0] == "はい":
                                if len(negaereru) == 2:
                                    #1,2段目が共に寝返り可能であれば、どこかにその座標の情報を表示する or 選択肢に入れ替える駒を反映することが望ましい。未実装
                                    msg = "どっち?"
                                    self.graphics.make_migipop("寝返らせる段確認ポップ", msg, "1段目", "2段目")
                                    if self.current_turn == 1:
                                        remain_time = self.your_remaining_time
                                    else:
                                        remain_time = self.opp_remaining_time
                                    #last_time = time.time()  # 最後に更新した時間

                                    # ターンの表示＋タイマー初期表示
                                    self.graphics.timer_update(self.current_turn, remain_time)
                                    while True:
                                        self.clock.tick(60)
                                        # 1秒ごとに残り時間を更新
                                        if time.time() - self.last_time >= self.remain_time_full - remain_time + 1:
                                            remain_time -= 1
                                            self.graphics.timer_update(self.current_turn, remain_time)

                                        if remain_time <= 0:
                                            #時間切れ
                                            if self.current_turn == 1:
                                                self.your_remaining_time = remain_time
                                                if self.gamestate.your_state == "start":
                                                    self.gamestate.your_state = "run"
                                            else:
                                                self.opp_remaining_time = remain_time
                                                if self.gamestate.opps_state == "start":
                                                    self.gamestate.opps_state = "run"
                                            return None
                                        for event in pygame.event.get():
                                            if self.current_turn == 1:
                                                self.your_remaining_time = remain_time
                                            else:
                                                self.opp_remaining_time = remain_time
                                            if self.your_remaining_time <= 60:
                                                self.your_remaining_time = 60
                                            if self.opp_remaining_time <= 60:
                                                self.opp_remaining_time = 60
                                            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                                                place_type, player, piece_code, pos = self.inputer.click_where("play", event.pos, self.graphics)
                                                if place_type == "board":
                                                    self.graphics.list(pos)
                                                else:
                                                    choice = self.inputer.click_where("寝返らせる段確認ポップ", event.pos, self.graphics)
                                                if choice[0] == "1段目":
                                                    kaeruyatu = 0
                                                    self.board.grid[y][x][kaeruyatu] = self.board.grid[y][x][kaeruyatu] + ((self.current_turn -1 ) * (200) - 100)
                                                    self.gamestate.hands[self.current_turn][self.board.grid[y][x][kaeruyatu]] -= 1
                                                    self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                                    return True
                                                elif choice[0] == "2段目":
                                                    kaeruyatu = 1
                                                    self.board.grid[y][x][kaeruyatu] = self.board.grid[y][x][kaeruyatu] + ((self.current_turn -1 ) * (200) - 100)
                                                    self.gamestate.hands[self.current_turn][self.board.grid[y][x][kaeruyatu]] -= 1
                                                    self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                                    return True
                                elif len(negaereru) == 1:
                                    kaeruyatu = negaereru[0]
                                    self.board.grid[y][x][kaeruyatu] = self.board.grid[y][x][kaeruyatu] + ((self.current_turn -1 ) * (200) - 100)
                                    self.gamestate.hands[self.current_turn][self.board.grid[y][x][kaeruyatu]] -= 1
                                    self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)
                                    return True


    def damedayo(self):
        #self.graphics.list(0)
        ##不正な手ですってことを表示するポップアップ##
        print("おけないよん")
        # 不正な場所なら選択解除してリセット
        self.will_move = 0
        self.graphics.board_update(self.board.grid, self.gamestate.hands, self.turn_count)

    def end_tyekku(self):
        msg = "諦める ?"
        self.graphics.make_pop("降参確認ポップ", msg, "まだやる", "諦め")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.click_where("降参確認ポップ", event.pos, self.graphics)
                    if choice[0] == "まだやる":
                        self.display_update()
                        return True
                    elif choice[0] == "諦め":
                        self.state_end()     

    def finish_tyekku(self):
        msg = "初期配置を終了しますか?"
        self.graphics.make_pop("初期配置終了ポップ", msg, "いいえ", "はい")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.click_where("初期配置終了ポップ", event.pos, self.graphics)
                    if choice[0] == "いいえ":
                        self.display_update()
                        return False
                    elif choice[0] == "はい":
                        if self.current_turn == 1:
                            self.gamestate.your_state = "run"
                        else:
                            self.gamestate.opps_state = "run"
                        self.display_update()
                        return True

    def tuke_tyekku(self):
        #self.graphics.list(0)
        msg = "ツケますか ?"
        self.graphics.make_migipop("ツケるか確認ポップ", msg, "倒す", "ツケる")
        if self.current_turn == 1:
            remain_time = self.your_remaining_time
        else:
            remain_time = self.opp_remaining_time
        #last_time = time.time()  # 最後に更新した時間

        # ターンの表示＋タイマー初期表示
        self.graphics.timer_update(self.current_turn, remain_time)

        while True:
            self.clock.tick(60)
            # 1秒ごとに残り時間を更新
            if time.time() - self.last_time >= self.remain_time_full - remain_time + 1:
                remain_time -= 1
                self.graphics.timer_update(self.current_turn, remain_time)

            if remain_time <= 0:
                #時間切れ
                if self.current_turn == 1:
                    self.your_remaining_time = remain_time
                    if self.gamestate.your_state == "start":
                        self.gamestate.your_state = "run"
                else:
                    self.opp_remaining_time = remain_time
                    if self.gamestate.opps_state == "start":
                        self.gamestate.opps_state = "run"
                return None
            for event in pygame.event.get():
                if self.current_turn == 1:
                    self.your_remaining_time = remain_time
                else:
                    self.opp_remaining_time = remain_time
                if self.your_remaining_time <= 60:
                    self.your_remaining_time = 60
                if self.opp_remaining_time <= 60:
                    self.opp_remaining_time = 60
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    place_type, player, piece_code, pos = self.inputer.click_where("play", event.pos, self.graphics)
                    if place_type == "board":
                        self.graphics.list(pos)
                    else:
                        choice = self.inputer.click_where("ツケるか確認ポップ", event.pos, self.graphics)
                        if choice[0] == "倒す":
                            return None
                        elif choice[0] == "ツケる":
                            return True 
    
    def saioku_tyekku(self,turn):
        if turn == 1:
            count = 1
            y_max = 0
        else:
            count = -1
            y_max = 8
        while True:
            for l in self.board.grid[y_max]:
                if self.board.is_own(l[2], turn):
                    return y_max
                elif (l[2] == 0) and self.board.is_own(l[1], turn):
                    return y_max
                elif (l[1] == 0) and self.board.is_own(l[0], turn):
                    return y_max
            y_max += count 

    # ⑧ 勝敗の表示 → 終了選択
    def state_end(self):
        winner = self.gamestate.winner
        msg = "あなたの勝ち" if winner == 1 else "相手の勝ち"
        self.graphics.make_pop("終了画面ポップ", msg, "もう一度", "終了")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.click_where("終了画面ポップ", event.pos, self.graphics)
                    if choice[0] == "もう一度":
                        game = Gungi()
                        game.run()
                        return
                    elif choice[0] == "終了":
                        pygame.quit()
                        sys.exit()

    def mode_select(self):
        msg = "どちらのモードでプレイしますか?"
        self.graphics.make_daipop("ゲームモード選択ポップ", msg, ["初心者", "上級者"])
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    choice = self.inputer.click_where("ゲームモード選択ポップ", event.pos, self.graphics)
                    if choice[0] == "初心者":
                        # 初期配置が決まっているモード用の初期配置
                        # 敵駒
                        self.board.grid[0][4][0] = 101
                        self.board.grid[0][3][0] = 103
                        self.board.grid[0][5][0] = 102
                        self.board.grid[1][1][0] = 108
                        self.board.grid[1][2][0] = 113
                        self.board.grid[1][4][0] = 106
                        self.board.grid[1][6][0] = 113
                        self.board.grid[1][7][0] = 107
                        self.board.grid[2][0][0] = 109
                        self.board.grid[2][2][0] = 110
                        self.board.grid[2][3][0] = 105
                        self.board.grid[2][4][0] = 109
                        self.board.grid[2][5][0] = 105
                        self.board.grid[2][6][0] = 110
                        self.board.grid[2][8][0] = 108
                        # 自駒
                        self.board.grid[8][4][0] = 1
                        self.board.grid[8][5][0] = 3
                        self.board.grid[8][3][0] = 2
                        self.board.grid[7][7][0] = 8
                        self.board.grid[7][6][0] = 13
                        self.board.grid[7][4][0] = 6
                        self.board.grid[7][2][0] = 13
                        self.board.grid[7][1][0] = 7
                        self.board.grid[6][8][0] = 9
                        self.board.grid[6][6][0] = 10
                        self.board.grid[6][5][0] = 5
                        self.board.grid[6][4][0] = 9
                        self.board.grid[6][3][0] = 5
                        self.board.grid[6][2][0] = 10
                        self.board.grid[6][0][0] = 8
                        # 高さを記憶しておく
                        for _ in range(self.board.size):
                            for a in range(self.board.size):
                                if self.board.grid[_][a][0] != 0:
                                    self.board.high_memory[_][a] = 1
                        # 初期配置が決まっているモード用の持ち駒
                        self.gamestate.hands = {
                            1: {4:2, 6:2, 7:1, 8:1, 9:1, 11:1, 12:1, 14:1},  # 自分
                            2: {104:2, 106:2, 107:1, 108:1, 109:1, 111:1, 112:1, 114:1}   # 相手
                        }
                        #初期配置決定版用
                        self.gamestate.game_state = "run"
                        self.graphics.buttonD = "降参"
                        return True
                    elif choice[0] == "上級者":
                        self.graphics.buttonD = "帥を配置せよ"
                        return True

    # メインループ
    def run(self):
        self.graphics.make_window()
        self.mode_select()
        self.display_update()
        while self.running:
            self.handle_turn()

if __name__ == "__main__":
    game = Gungi()
    game.run()
