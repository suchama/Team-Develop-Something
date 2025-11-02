import pygame
import math
import os
from pygame.locals import *

class Graphics(pygame.sprite.Sprite):
    cell = 60 #最小単位
    boardsize = 9
    windowsize_x, windowsize_y = 21, 11
    board_rect = {0:((0,0), (0,0))}
    board_rect["board"] = (((windowsize_x-1)/2-4,1), ((windowsize_x-1)/2+4,9)) #盤の左上、右下
    board_rect["bg"] = (((windowsize_x-1)/2-4-0.5,0.5), ((windowsize_x-1)/2+4+0.5,9+0.5))
    tegoma_rect = {0:((0,0),(0,0))}
    tegoma_rect["opp"] = ((1,1), (4,5))
    timer_rect = {0:((0,0),(0,0))}
    timer_rect["timer"] = ((18,1), (19,2))
    timer_rect["teban"] = ((16,1), (17,2))
    buttonA_rect = {0:((0,0),(0,0))}
    buttonA_rect["slf"] = ((16,3), (17,4))
    buttonB_rect = {0:((0,0),(0,0))}
    buttonB_rect["slf"] = ((18,3), (19,4))
    buttonC_rect = {0:((0,0),(0,0))}
    buttonC_rect["slf"] = ((1,7), (4,7.5))
    buttonD_rect = {0:((0,0),(0,0))}
    buttonD_rect["slf"] = ((1,9), (4,9.5))
    button_list = {"state":"buttonlist"}
    button_rect_list = {"state"+"buttonlist":"rect"}
    pop_rect = {0:((0,0),(0,0))}
    pop_rect["bg"] = (((windowsize_x-1)/2-4,1), ((windowsize_x-1)/2+4,9))
    pop_rect["text"] = (((windowsize_x-1)/2-4,1), ((windowsize_x-1)/2+4,5))
    pop_rect["daibg"] = ((1,1), (19,9))
    pop_rect["daitext"] = ((2,2), (18,4))
    pop_rect["left"] = ((7,6),(9,8))
    pop_rect["right"] = ((11,6), (13,8))
    """もともと右にあったポップの元の座標
    pop_rect["migi_bg"] = ((16,3), (19,6))
    pop_rect["migi_text"] = ((16,3), (19,4))
    pop_rect["migi_left"] = ((16,5), (17,6))
    pop_rect["migi_right"] = ((18,5), (19,6))
    """
    pop_rect["migi_bg"] = ((1,6.5), (4,9.5))

    pop_rect["migi_text"] = {0:1}
    pop_rect["migi_left"] = {0:1}
    pop_rect["migi_right"] = {0:1}

    pop_rect["migi_text"][1] = ((1,6.5), (4,7.5))
    pop_rect["migi_left"][1] = ((1,8.5), (2,9.5))
    pop_rect["migi_right"][1] = ((3,8.5), (4,9.5))
    pop_rect["migi_text"][2] = ((1,8.5), (4,9.5))
    pop_rect["migi_right"][2] = ((1,6.5), (2,7.5))
    pop_rect["migi_left"][2] = ((3,6.5), (4,7.5))


    color = {0:(255,0,0)}
    color["board"] = (200, 200, 100)
    color["tegoma"] = (70, 70, 35)
    color["buttonA"] = (200, 100, 100)
    color["buttonB"] = (100, 200, 100)
    color["buttonC"] = (200, 200, 100)
    color["buttonD"] = (100, 200, 200)
    color["timer"] = (200,200,200)
    color["pop"] = (0,200,200)
    turn = {0:"?", "slf":1, "opp":2}
    turn[1] = "あなた"
    turn[2] = "相手"
    turn[3] = "slf"
    turn[4] = "opp"


    def __init__(self):
        #描画するための見本となる画像用意
        self.image = [[],[[0 for _ in range(4)] for _ in range(15)], [[0 for _ in range(4)] for _ in range(15)]]
        self.image_toosi = {-1:"None"}
        self.image_toosi[1] = {-1:"None"}
        self.image_toosi[2] = {-1:"None"}#相手側のlist用(つまり１８０度回転させたもの)
        self.image_blight = [[],[[0 for _ in range(4)] for _ in range(15)], [[0 for _ in range(4)] for _ in range(15)]]

        #フォントとサイズ
        pygame.font.init()
        self.font = pygame.font.Font('ipaexm.ttf', 70)

        self.text_dvd = []
        self.button = []
        self.buttonD = ""
        self.info_mochi = {
            1: [] , # 自分
            2: []   # 相手
                            }#持ち駒用の配列
        Graphics.tegoma_rect["slf"] = self.opposite(Graphics.tegoma_rect["opp"])

        Graphics.tgm = {1:[[0 for _ in range(4)]for _ in range(4)], 2:[[0 for _ in range(4)]for _ in range(4)] }

        '''
            0123
            4567
            89ab
            cdef

            fedc
            ba98
            7654
            3210

        '''

        for i in range(4):
            for l in range(4):
                Graphics.tgm[1][i][l] = pygame.Rect(0,0, Graphics.cell-4, Graphics.cell-4)
                Graphics.tgm[2][i][l] = pygame.Rect(0,0, Graphics.cell-4, Graphics.cell-4)
                Graphics.tgm[1][i][l].center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*l, i*15 + self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*i)
                Graphics.tgm[2][i][l].center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*l, -i*15 + self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*i)

        self.kiroku =(0,0,0,0,0)
        self.grid_copy = 0
        self.hands_copy = 0
        self.turn_copy = 0
        self.glgrid = [[0 for _ in range(9)] for _ in range(9)]
        for x in range(9):
            self.glgrid[x][x] = 1
    
    def make_window(self):
        self.screen = pygame.display.set_mode((Graphics.windowsize_x*Graphics.cell+100, Graphics.windowsize_y*Graphics.cell))#ウィンドウ作成
        pygame.display.set_caption("軍議")# 画面上部に表示するタイトル
        self.screen.fill((50,50,50))
        self.koma_set()
    
    def koma_set(self):
        for i in range(1, 15, 1):
            self.image_toosi[1][i] = { -1:"None"}
            self.image_toosi[2][i] = { -1:"None"}
            self.image_toosi[1][100+i] = { -1:"None"}
            self.image_toosi[2][100+i] = { -1:"None"}
            for j in range(1,4):
                url1 = os.path.join("駒画像", "siro", str(i)+"_"+str(j)+".png")
                url2 = os.path.join("駒画像", "kuro", str(i+100)+"_"+str(j)+".png")
                self.image[1][i][j] = pygame.image.load(url1).convert_alpha()
                self.image[2][i][j] = pygame.image.load(url2).convert_alpha()
                self.image[1][i][j] = pygame.transform.scale(self.image[1][i][j], (Graphics.cell - 4, Graphics.cell - 4))
                self.image_toosi[1][i][j] = self.image[1][i][j]
                self.image_toosi[2][i][j] = pygame.transform.rotate(self.image_toosi[1][i][j], 180)
                self.image_blight[1][i][j] = pygame.image.load(url1).convert_alpha()#self.image[1][i].copy#駒を光らせる用の画像
                self.image_blight[1][i][j] = pygame.transform.scale(self.image_blight[1][i][j], (Graphics.cell - 4, Graphics.cell - 4))
                self.image_blight[1][i][j].set_alpha(128)#半透明にする
                self.image[2][i][j] = pygame.transform.scale(self.image[2][i][j], (Graphics.cell - 4, Graphics.cell - 4))
                self.image_toosi[1][100+i][j] = self.image[2][i][j]
                self.image[2][i][j] = pygame.transform.rotate(self.image[2][i][j], 180)
                self.image_toosi[2][100+i] = self.image[2][i][j]
                self.image_blight[2][i][j] = pygame.image.load(url2).convert_alpha()#self.image[2][i].copy#駒を光らせる用の画像
                self.image_blight[2][i][j] = pygame.transform.scale(self.image_blight[2][i][j], (Graphics.cell - 4, Graphics.cell - 4))
                self.image_blight[2][i][j] = pygame.transform.rotate(self.image_blight[2][i][j], 180)
                self.image_blight[2][i][j].set_alpha(128)#半透明にする

    
    def opposite(self, a): #a=((x,y), (z,w))
        return ((Graphics.windowsize_x-1-a[1][0],Graphics.windowsize_y-1-a[1][1]), (Graphics.windowsize_x-1-a[0][0],Graphics.windowsize_y-1-a[0][1]))

    def draw_board(self, turn_count):
        self.screen.fill((0,0,0))
        pygame.draw.rect(self.screen, Graphics.color["board"], self.rect(Graphics.board_rect["bg"]))
        #盤面の線を描画
        for i in range(Graphics.boardsize+1):#たて
            pygame.draw.line(self.screen, (0,0,0), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][0][1])*Graphics.cell), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][1][1]+1)*Graphics.cell),3)
        for i in range(Graphics.boardsize+1):#よこ
            pygame.draw.line(self.screen, (0,0,0), (Graphics.board_rect["board"][0][0]*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell), ((Graphics.board_rect["board"][1][0] + 1)*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell),3)
        
        pygame.draw.rect(self.screen, Graphics.color["tegoma"], self.rect(Graphics.tegoma_rect["opp"]))
        pygame.draw.rect(self.screen, Graphics.color["tegoma"], self.rect(Graphics.tegoma_rect["slf"]))

        self.font = pygame.font.Font('ipaexm.ttf', 30)#フォントとサイズ
        #self.draw_rect("play",1, Graphics.buttonA_rect["slf"], "buttonA", 0,  Graphics.color["buttonA"])
        #self.draw_rect("play",1, Graphics.buttonB_rect["slf"], "buttonB", 0,  Graphics.color["buttonB"])
        self.draw_rect("play",0, Graphics.buttonC_rect["slf"], "ターン数："+str(turn_count), 0,  Graphics.color["buttonC"])
        self.draw_rect(self.buttonD,1, Graphics.buttonD_rect["slf"], self.buttonD, 0,  Graphics.color["buttonD"])
        self.font = pygame.font.Font('ipaexm.ttf', 70)#フォントとサイズ

        self.draw_rect("play",0, Graphics.tegoma_rect["slf"], "", 0,  Graphics.color["tegoma"])
        self.draw_rect("play",0, Graphics.tegoma_rect["opp"], "", 1,  Graphics.color["tegoma"])

    
    def board_update(self, grid, hands, turn_count):#各マスの情報から画像を描画、※画面更新する
        self.screen.fill((0,0,0))
        self.font = pygame.font.Font('ipaexm.ttf', 30)#フォントとサイズ
        self.draw_rect("play",0, Graphics.buttonC_rect["slf"], "ターン数："+str(turn_count), 0,  Graphics.color["buttonC"])
        self.draw_rect(self.buttonD,1, Graphics.buttonD_rect["slf"], self.buttonD, 0,  Graphics.color["buttonD"])
        self.font = pygame.font.Font('ipaexm.ttf', 70)#フォントとサイズ
        self.grid_copy = grid
        self.hands_copy = hands
        #盤面自体を描画
        pygame.draw.rect(self.screen, Graphics.color["board"], self.rect(Graphics.board_rect["bg"]))
        #盤面の線を描画
        for i in range(Graphics.boardsize+1):#たて
            pygame.draw.line(self.screen, (0,0,0), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][0][1])*Graphics.cell), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][1][1]+1)*Graphics.cell),3)
        for i in range(Graphics.boardsize+1):#よこ
            pygame.draw.line(self.screen, (0,0,0), (Graphics.board_rect["board"][0][0]*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell), ((Graphics.board_rect["board"][1][0] + 1)*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell),3)
        #駒を表示
        for row in range(Graphics.boardsize):
            for column in range(Graphics.boardsize):
                for floor in range(3):
                    if grid[row][column][floor] != 0 and grid[row][column][floor] <=14:
                        self.image_rect = ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, -floor*5+(Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4)
                        self.screen.blit(self.image[1][grid[row][column][floor]][floor + 1], pygame.Rect(self.image_rect))#駒を描画
                    
                    if grid[row][column][floor] != 0 and grid[row][column][floor] >=101:
                        self.image_rect = ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, -floor*5+(Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4)
                        self.screen.blit(self.image[2][grid[row][column][floor]-100][floor + 1], pygame.Rect(self.image_rect))#駒を描画

        
        #持駒を描画
        self.draw_rect("play",0, Graphics.tegoma_rect["slf"], "", 0,  Graphics.color["tegoma"])
        self.draw_rect("play",0, Graphics.tegoma_rect["opp"], "", 1,  Graphics.color["tegoma"])
        for j in {1,2}:
            self.info_mochi[j] = []#一回空に
            for i in range(1,15,1):
                count = hands[j].get(i+100*(j-1),0)
                m = min([1,count])
                for k in range(m):
                    self.info_mochi[j].append(i)#1枚以上保持している駒の情報（何枚かは不明）
            
            k = math.ceil((len(self.info_mochi[j])) /4)#持ち駒が何行にわたるか計算
            '''
            0123
            4567
            89ab
            cdef

            fedc
            ba98
            7654
            3210

            '''
            for i in range(k):
                for l in range(4):
                    self.rectt = pygame.Rect(0,0, Graphics.cell-4, Graphics.cell-4)
                    if 4*i+l > len(self.info_mochi[j])-1:#すべて持ち駒を描画し終えたら終了
                        break
                    for m in range(hands[j].get(self.info_mochi[j][4*i+l]+100*(j-1),0)):
                        if j == 1:
                            self.rectt.center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*l, 5+i*15-m*5 + self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*i)
                            self.screen.blit(self.image[j][self.info_mochi[j][4*i+l]][1], self.rectt)
                        if j == 2:
                            self.rectt.center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*l, -5-i*15+m*5 + self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*i)
                            self.screen.blit(self.image[j][self.info_mochi[j][4*i+l]][1], self.rectt)
        
    def list(self, selected_pos):
        #list(0)と入力されたらlistを消す
        if selected_pos == 0:
            wid = 10
            pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(960+wid,180+wid,240-2*wid,120-2*wid))
            return
        
        #そこに重なりがなければ終了、重なりがあれば続行
        row, column = selected_pos[1], selected_pos[0]#ここ逆かも rowがｙでcolumnがｘ
        non_zero_elements = [item for item in self.grid_copy[row][column] if item != 0]
        floor = len(non_zero_elements)-1#最上段の回数(下から-1(駒なし),0,1,2)
        cell = Graphics.cell
        if floor <=0:
            return
        #表示のための背景の長方形の描画

        for wid in range(5,30,1):
            wid = 2*wid
            pygame.draw.rect(self.screen, (70-wid,70-wid,70-wid), pygame.Rect(960+wid,180+wid,240-2*wid,120-2*wid))

        for flr in range(floor+1):#flr=0,1,...
            if self.turn_copy == 1:
                self.screen.blit(self.image_toosi[1][self.grid_copy[row][column][flr]][flr + 1], pygame.Rect(42+960+(cell-10)*flr,222-10*flr,cell,cell))
            if self.turn_copy == 2:
                self.screen.blit(self.image_toosi[2][self.grid_copy[row][column][flr]][flr + 1], pygame.Rect(42+960+(cell-10)*flr,202+10*flr,cell,cell))
        pygame.display.update()

    def glory(self, glgrid):
        self.glgrid_copy = glgrid
        for column, row in glgrid:
                if self.grid_copy[row][column][0] == 0:#おける場所に駒がないとき
                    pygame.draw.rect(self.screen, (0,250,250), pygame.Rect(Graphics.board_rect["board"][0][0]*Graphics.cell+column*Graphics.cell+2, Graphics.board_rect["board"][0][1]*Graphics.cell+row*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4))
                if self.grid_copy[row][column][0] != 0:#おける場所に駒があるとき
                    self.blight(self.grid_copy, self.hands_copy, 0, "board", (column,row))
        
        pygame.display.update()

    def blight(self, grid, hands, current_turn, where1, where2):#画面更新あり
#        if self.kiroku[2] == current_turn and current_turn != 0:
#            self.blight_off(self.grid_copy, self.kiroku[1], self.kiroku[2], self.kiroku[3], self.kiroku[4])
        column, row = where2
        non_zero_elements = [item for item in grid[row][column] if item != 0]
        floor = len(non_zero_elements)-1#最上段の回数(下から-1(駒なし),0,1,2)
        if where1 == "board":
            if floor == -1:
                print("その座標に駒はありません")
                return
            self.image_rect = ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, -1*floor*5+(Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4)
            pygame.draw.rect(self.screen, (0,250,250), pygame.Rect(self.image_rect))
            if self.grid_copy[row][column][floor]>=100:
                hikarukomanojita = 2
            else:
                hikarukomanojita = 1
            self.screen.blit(self.image_blight[hikarukomanojita][self.grid_copy[row][column][floor] % 100][floor + 1], pygame.Rect(self.image_rect))#駒を描画
        
        if where1 == "tegoma":
            self.rectt = pygame.Rect(0,0, Graphics.cell-4, Graphics.cell-4)
            if current_turn == 1:
                m = hands[current_turn].get(self.info_mochi[current_turn][4*row+column],0) -1
                self.rectt.center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*column, 5+row*15-m*5 + self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*row)
                pygame.draw.rect(self.screen, (200,200,0), self.rectt)
                self.screen.blit(self.image_blight[current_turn][self.info_mochi[current_turn][4*row+column]][1], self.rectt)
            
            if current_turn == 2:
                m = hands[current_turn].get(self.info_mochi[current_turn][4*row+column]+100,0) -1
                self.rectt.center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*column, -5-row*15+m*5 + self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*row)
                pygame.draw.rect(self.screen, (200,200,0), self.rectt)
                self.screen.blit(self.image_blight[current_turn][self.info_mochi[current_turn][4*row+column]][1], self.rectt)
        
        self.kiroku = (grid, hands, current_turn, where1, where2)
        
        pygame.display.update()

    def blight_off(self, grid, hands, current_turn, where1, where2):#画面更新なし

        column, row = where2
        non_zero_elements = [item for item in grid[row][column] if item != 0]
        floor = len(non_zero_elements)-1
        if where1 == "board":
            if floor == -1:
                print("その座標に駒はありません")
                return
            if self.grid_copy[row][column][floor]>=100:
                hikarukomanojita = 2
            else:
                hikarukomanojita = 1
            self.image_rect = ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, floor*5+(Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4)
            self.screen.blit(self.image[hikarukomanojita][grid[row][column][floor] % 100][floor + 1], pygame.Rect(self.image_rect))#駒を描画
        
        if where1 == "tegoma":
            self.rectt = pygame.Rect(0,0, Graphics.cell-4, Graphics.cell-4)
            if current_turn == 1:
                m = hands[current_turn].get(self.info_mochi[current_turn][4*row+column] % 100,0) -1
                self.rectt.center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*column, 5+row*15-m*5 + self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*row)
                self.screen.blit(self.image[current_turn][self.info_mochi[current_turn][4*row+column]][1], self.rectt)
            
            if current_turn == 2:
                m = hands[current_turn].get(self.info_mochi[current_turn][4*row+column] % 100,0) +1
                self.rectt.center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*column, -5-row*15+m*5 + self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*row)
                self.screen.blit(self.image[current_turn][self.info_mochi[current_turn][4*row+column]][1], self.rectt)

    #ポップの作成text:popの内容、left:popの左ボタン
    def make_pop(self, situ, text, left, right):
        rgb = Graphics.color["pop"]
        self.draw_rect(situ,0, Graphics.pop_rect["bg"], "", 0, rgb)
        self.draw_rect(situ,0, Graphics.pop_rect["text"], text, 0, rgb)
        self.draw_rect(situ,1, Graphics.pop_rect["left"], left, 0, (rgb[0]+20,rgb[1]+20,rgb[2]+20))
        self.draw_rect(situ,1, Graphics.pop_rect["right"], right, 0, (rgb[0]+20,rgb[1]+20,rgb[2]+20))
    
        #画面への反映
        pygame.display.update()
    
    def make_migipop(self, situ, text, left, right):
        self.font = pygame.font.Font('ipaexm.ttf', 40)#フォントとサイズ
        rgb = Graphics.color["pop"]
        if left != "" or right != "":
            self.draw_rect(situ,0, Graphics.pop_rect["migi_bg"], "", 0, (100,100,100,100))
        #ボタンやテキストがない場合はボタンを描画しない
        upsidedown=1#self.turn_copy
        if text != "":
            self.draw_rect(situ,0, Graphics.pop_rect["migi_text"][upsidedown], text, upsidedown-1, (100,100,100,100))  #スペースがないので描画しない
        if left != "":
            self.draw_rect(situ,1, Graphics.pop_rect["migi_left"][upsidedown], left, upsidedown-1, Graphics.color["buttonA"])
        if right != "":
            self.draw_rect(situ,1, Graphics.pop_rect["migi_right"][upsidedown], right, upsidedown-1, Graphics.color["buttonB"])
        self.font = pygame.font.Font('ipaexm.ttf', 70)#フォントとサイズ
    
        #画面への反映
        pygame.display.update()
    
    #大popの作成（textは改行ごとにリスト内で分ける。sentakusiも各ボタンの名称をリストで入力
    def make_daipop(self, situ, text, sentakusi):
        rgb = Graphics.color["pop"]
        self.draw_rect(situ,0, Graphics.pop_rect["daibg"], "", 0, rgb)
        self.draw_rect(situ,0, Graphics.pop_rect["daitext"], text, 0, rgb)
        l = len(sentakusi)
        k = Graphics.pop_rect["daibg"][1][0]-Graphics.pop_rect["daibg"][0][0]+1
        c = (k / l)
        for b in range(l):
            self.draw_rect(situ,1, ((Graphics.pop_rect["daibg"][0][0]+b*c+0.2,7), (Graphics.pop_rect["daibg"][0][0]+b*c+c-1.2,8.5)), sentakusi[b], 0, (rgb[0]+20,rgb[1]+20,rgb[2]+20))

        #画面への反映
        pygame.display.update()
    
    #タイマーのアップデート（描画）（今の手番と【秒】数を指定）
    def timer_update(self, teban, number): #teban = 1:自分, 2:相手
        self.turn_copy = teban
        m = number // 60
        s = number % 60
        self.font = pygame.font.Font('ipaexm.ttf', 40)#フォントとサイズ
        if s < 10:
            self.draw_rect_outline(Graphics.timer_rect["timer"], str(m)+":0"+str(s), 0,  (100,100,100), Graphics.color["timer"])
        else:
            self.draw_rect_outline(Graphics.timer_rect["timer"], str(m)+":"+str(s), 0, (100,100,100), Graphics.color["timer"])
        self.draw_rect_outline(Graphics.timer_rect["teban"], ["手番:",Graphics.turn[teban]], 0, (100,100,100), Graphics.color["timer"])

        self.font = pygame.font.Font('ipaexm.ttf', 70)#フォントとサイズ
        #画面への反映
        pygame.display.update()

    def draw_exe(self, turn_count):
        pygame.draw.rect(self.screen, Graphics.color["board"], self.rect(Graphics.board_rect["bg"]))
        #盤面の線を描画
        for i in range(Graphics.boardsize+1):#たて
            pygame.draw.line(self.screen, (0,0,0), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][0][1])*Graphics.cell), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][1][1]+1)*Graphics.cell),3)
        for i in range(Graphics.boardsize+1):#よこ
            pygame.draw.line(self.screen, (0,0,0), (Graphics.board_rect["board"][0][0]*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell), ((Graphics.board_rect["board"][1][0] + 1)*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell),3)
        
        self.font = pygame.font.Font('ipaexm.ttf', 40)#フォントとサイズ
        pygame.draw.rect(self.screen, Graphics.color["tegoma"], self.rect(Graphics.tegoma_rect["opp"]))
        pygame.draw.rect(self.screen, Graphics.color["tegoma"], self.rect(Graphics.tegoma_rect["slf"]))
        self.draw_rect("play",0, Graphics.buttonC_rect["slf"], "ターン数："+str(turn_count), 0,  Graphics.color["buttonC"])
        self.font = pygame.font.Font('ipaexm.ttf', 70)#フォントとサイズ
        self.draw_rect(self.buttonD,1, Graphics.buttonD_rect["slf"], self.buttonD, 0,  Graphics.color["buttonD"])

    #テキストありの塗りつぶしrect描画
    def draw_rect(self, situ, add, rect, text, down, rgb):
        pygame.draw.rect(self.screen, rgb, self.rect(rect))
        if type(text) is str:#そのまま文字列が入っていたら（つまり行分割した["1行目","2行目","3行目"]みたいな入力でなかったら）
            text = [text]#いったん配列に入れる（行分割の場合と同じ入力の型にそろえる）
        l = len(text)#配列の要素数
        adding_text = [0,0]
        adding_text[0] = text[0]
        for i in range(1,l,1):
            adding_text[i%2] = adding_text[(i+1)%2] + text[i]
        adding_text[0] = adding_text[(l-1)%2]
        for i in range(l):#各要素について、再度横幅がはみ出る場合は分割を行う
            self.dvd_text(text[i], self.rect(rect).width)#分割して、self.text_dvdに一時的に入れる
            #★ここで注意：text_dvdはi=1,2,...lまでの分割が順次追加され、横幅調整後の"最大行分割"がなされたもの
        l = len(self.text_dvd)#結局テキストは何個に分割されたのかをlに入れる
        for i in range(l):#各分割を順番に表示していく
            textc = self.font.render(self.text_dvd[i], True, (255,255,255))#テキスト画像準備
            if down == 1:#上下逆の指定がある場合は１８０度回転させる
                textc = pygame.transform.rotate(textc, 180)
                i = l - i -1#行を逆から表示させるためのただの調整
            #以下４行、表示のための云々
            text_rect = textc.get_rect()
            h = text_rect.height
            text_rect.center = ((rect[1][0]+1)*Graphics.cell + rect[0][0]*Graphics.cell)/2, ((rect[1][1]+1)*Graphics.cell + rect[0][1]*Graphics.cell)/2 + i*h - (l-1)*(h/2)
            self.screen.blit(textc, text_rect)
        if add==1 and l > 0:#aボタン指定（つまりadd=1）かつテキストが空（つまり背景など用の描画）でない場合は
            if (situ in self.button_list) == False:#まだそのsitu（situation）でテキストありrectが作成されてなかったら、それをbutton_listに追加する
                self.button_list[situ]= set()
            if (adding_text[0] in self.button_list[situ]) == False:
                self.button_list[situ].add(adding_text[0])#situaton:situのbuttonlistに（主に）ボタンのtextの一行目を追加する
            self.button_rect_list[situ+adding_text[0]] = rect
            #print(situ+"にはいっているボタン...", self.button_list[situ])
        self.text_dvd = []
    
    #外枠ありのテキストありrectを描画
    def draw_rect_outline(self, rect, text, down, rgbout, rgbin):
        pygame.draw.rect(self.screen, rgbin, self.rect(rect))#内側の色
        pygame.draw.rect(self.screen, rgbout, self.rect(rect),5)
        if type(text) is str:
            self.dvd_text(text, self.rect(rect).width)
        else:
            l = len(text)
            for i in range(l):
                self.dvd_text(text[i], self.rect(rect).width)
        l = len(self.text_dvd)
        for i in range(l):
            textc = self.font.render(self.text_dvd[i], True, (255,255,255))
            if down == 1:
                textc = pygame.transform.rotate(textc, 180)
            text_rect = textc.get_rect()
            h = text_rect.height
            text_rect.center = ((rect[1][0]+1)*Graphics.cell + rect[0][0]*Graphics.cell)/2, ((rect[1][1]+1)*Graphics.cell + rect[0][1]*Graphics.cell)/2 + i*h - (l-1)*(h/2)
            self.screen.blit(textc, text_rect)
        self.text_dvd = []
    
    #Graphics.cell単位で指定したrectの左上と右下の座標（topleft,downright)をpygame.Rectで直す
    def rect(self, rect):
        return pygame.Rect(rect[0][0]*Graphics.cell, rect[0][1]*Graphics.cell, (rect[1][0]-rect[0][0]+1)*Graphics.cell, (rect[1][1]-rect[0][1]+1)*Graphics.cell)

    #テキスト(text)をwidthに合わせて折り返す　リストself.text_dvdに各行のテキストが入る
    def dvd_text(self, text, width):
        l = len(text)
        textc = self.font.render(text, True, (255,255,255))
        text_rect = textc.get_rect()
        for i in range(l):
            textc = self.font.render(text[:(l-i)], True, (255,255,255))
            text_rect = textc.get_rect()
            if text_rect.width <= width:#textのl-i文字目までが入りきってる場合（そうでないとき次のiを確認）
                self.text_dvd.append(text[:(l-i)]) #大事(それをリストに追加)
                if i == 0:#もう文字列が余ってなかったら終わり
                    break
                textc = text[(l-i):]#残りの文字列用意
                textc = self.font.render(textc, True, (255,255,255))
                text_rect = textc.get_rect()
                if text_rect.width > width:#残った文字列が入りきっていない場合
                    self.dvd_text(text[(l-i):], width)#もう一度折り返し処理
                else:#入りきってた場合
                    self.text_dvd.append(text[(l-i):])#リストに文字列追加
                break

