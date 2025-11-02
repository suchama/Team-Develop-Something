import pygame
import math
from pygame.locals import *
from graphics import Graphics

class Inputer(pygame.sprite.Sprite):
    def __init__(self):
        #マウスのクリック当たり判定分割
        self.cdn = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                self.cdn[i][j]=pygame.Rect(Graphics.board_rect["board"][0][0]*Graphics.cell+j*Graphics.cell+2, Graphics.board_rect["board"][0][1]*Graphics.cell+i*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4)
    
    #situationごとに判定すべきボタンや盤面上のマスを判定する
    #デフォルトのsitu;
    #play:マス、手ごま、元から表示されてるボタン
    #
    def click_where(self, situ, event_pos, graphics):#position = (x, y)
        cursor_x,cursor_y = event_pos
        #situがplayかつクリックがboard上のとき
        if situ == "play" and graphics.rect(Graphics.board_rect["board"]).collidepoint(event_pos):
            cursor_mat_x = math.floor((cursor_x-Graphics.board_rect["board"][0][0]*Graphics.cell)/Graphics.cell)#カーソルの座標を0~7までに振り分け
            cursor_mat_y = math.floor((cursor_y-Graphics.board_rect["board"][0][1]*Graphics.cell)/Graphics.cell)
            #カーソルのあるであろう場所の周囲９マスと当たり判定
            for i in range(3):
                for j in range(3):
                    zero_x = zero_y = 1
                    if cursor_mat_x == 0:
                        if i-1 <0:
                            zero_x = 0
                        else:
                            zero_x = 1
                    if cursor_mat_x == 8:
                        if i-1 >0:
                            zero_x = 0
                        else:
                            zero_x = 1
                    if cursor_mat_y == 0:
                        if j-1 <0:
                            zero_y = 0
                        else:
                            zero_y = 1
                    if cursor_mat_y == 8:
                        if j-1 >0:
                            zero_y = 0
                        else:
                            zero_y = 1
                    
                    if self.cdn[(j-1)*zero_y+cursor_mat_y][(i-1)*zero_x+cursor_mat_x].collidepoint(event_pos):
                        return ("board", None, None, ((i-1)*zero_x+cursor_mat_x,(j-1)*zero_y+cursor_mat_y))#(クリックされた行列座標,"board")を返す
        if situ == "play":
            for p in ["opp", "slf"]:
                if graphics.rect(Graphics.tegoma_rect[p]).collidepoint(event_pos):
                    k = math.ceil((len(graphics.info_mochi[Graphics.turn[p]])) /4)
                    for i in range(k):
                        for l in range(4):
                            if 4*i+l > len(graphics.info_mochi[Graphics.turn[p]])-1:
                                break
                            if graphics.rectt[Graphics.turn[p]][4*i+l].collidepoint(event_pos):
                                return ("tegoma", Graphics.turn[p], graphics.info_mochi[Graphics.turn[p]][4*i+l],(l,i))#return どの駒か
        for button in graphics.button_list[situ]:
            if graphics.rect(graphics.button_rect_list[situ + button]).collidepoint(event_pos):
                return (button, None, None, None)#pauseをかえす
        return ("None", None, None, None)
    
    def pop_lr_click(self, event_pos, graphics):#ボタン付きポップのボタン入力チェック
        if graphics.rect(Graphics.pop_rect["left"]).collidepoint(event_pos):
            return "leftbutton"
        if graphics.rect(Graphics.pop_rect["right"]).collidepoint(event_pos):
            return "rightbutton"
        return None
    
    def migipop_lr_click(self, event_pos, graphics):#ボタン付きポップのボタン入力チェック
        if graphics.rect(Graphics.pop_rect["migi_left"]).collidepoint(event_pos):
            return "leftbutton"
        if graphics.rect(Graphics.pop_rect["migi_right"]).collidepoint(event_pos):
            return "rightbutton"
        return None
        