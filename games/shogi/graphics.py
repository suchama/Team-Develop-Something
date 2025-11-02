import pygame
import math
import os
from pygame.locals import *

'''
0123456789abcdefghijk  <-20

022221111111111100000 0
022221111111111144330 1
022221111111111144330 2
022221111111111100000 3
000001111111111100000 4
000001111111111100000 5
003301111111111122220 6
003301111111111122220 7
000001111111111122220 8
000001111111111122220 9
000001111111111100000 10
'''

class Graphics(pygame.sprite.Sprite):
    #定数
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
    pop_rect["migi_bg"] = ((16,3), (19,6))
    pop_rect["migi_text"] = ((16,3), (19,4))
    pop_rect["migi_left"] = ((16,5), (17,6))
    pop_rect["migi_right"] = ((18,5), (19,6))
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
    turn[1] = "you"
    turn[2] = "opp"
    turn[3] = "slf"
    turn[4] = "opp"

# 駒の番号定義：
# 1: 玉将（自分）
# 2: 飛車
# 3: 角行
# 4: 金将
# 5: 銀将
# 6: 桂馬
# 7: 香車
# 8: 歩兵
# 11〜18: 相手の駒（+10）
# 22: 成飛（竜王）
# 23: 成角（竜馬）
# 25: 成銀
# 26: 成桂
# 27: 成香
# 28: と金
# 32〜38: 相手の成駒（+10）
    url_key = {0:0}
    for i in {0,10}:
        url_key[1+i] = os.path.join("将棋駒", "osho.png") 
        url_key[2+i] = os.path.join("将棋駒", "hissya.png")
        url_key[3+i] = os.path.join("将棋駒", "kaku.png")
        url_key[4+i] = os.path.join("将棋駒", "kin.png")
        url_key[5+i] = os.path.join("将棋駒", "gin.png")
        url_key[6+i] = os.path.join("将棋駒", "keima.png")
        url_key[7+i] = os.path.join("将棋駒", "kyosha.png")
        url_key[8+i] = os.path.join("将棋駒", "hohei.png")
        url_key[22+i] = os.path.join("将棋駒", "narihissya.png")
        url_key[23+i] = os.path.join("将棋駒", "uma.png")
        url_key[25+i] = os.path.join("将棋駒", "narigin.png")
        url_key[26+i] = os.path.join("将棋駒", "narikeima.png")
        url_key[27+i] = os.path.join("将棋駒", "narikyosha.png")
        url_key[28+i] = os.path.join("将棋駒", "narihohei.png")

    url_key[11] = os.path.join("将棋駒", "gyokusho.png")

    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 70)#フォントとサイズ
        #変数
        self.grid = [[0 for _ in range(Graphics.boardsize)] for _ in range(Graphics.boardsize)]
        # 相手の駒を上に配置
        self.grid[0] = [17, 16, 15, 14, 11, 14, 15, 16, 17]  # 上段
        self.grid[1] = [0 for _ in range(9)]
        self.grid[1][1] = 12
        self.grid[1][7] = 13
        self.grid[2] = [18 for _ in range(9)]  # 歩兵
        # 自分の駒を下に配置
        self.grid[8] = [7, 6, 5, 4, 1, 4, 5, 6, 7]
        self.grid[7] = [0 for _ in range(9)]
        self.grid[6] = [8 for _ in range(9)]
        self.grid[7][7] = 2
        self.grid[7][1] = 3

        self.text_dvd = []
        self.button = []
        self.image = [[0 for _ in range(Graphics.boardsize)]for _ in range(Graphics.boardsize)]#駒の画像用配列
        self.image_rect = [[0 for _ in range(Graphics.boardsize)]for _ in range(Graphics.boardsize)]#駒の位置とサイズ用配列
        self.info_mochi = {
            1: [] , # 自分
            2: []   # 相手
                            }#持ち駒用の配列
        self.image_mochi = [[0],[0 for _ in range(60)],[0 for _ in range(60)]]
        self.rectt = [[0],[0 for _ in range(60)],[0 for _ in range(60)]]

        Graphics.tegoma_rect["slf"] = self.opposite(Graphics.tegoma_rect["opp"])
        self.pre_zahyo = (-1,(0,0))
        self.k =(200,200,50,128)

    def make_window(self):
        self.screen = pygame.display.set_mode((Graphics.windowsize_x*Graphics.cell, Graphics.windowsize_y*Graphics.cell))#ウィンドウ作成
        pygame.display.set_caption("将棋")# 画面上部に表示するタイトル
        self.screen.fill((50,50,50))


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

        self.font = pygame.font.Font(None, 40)#フォントとサイズ
        #self.draw_rect("play", Graphics.buttonA_rect["slf"], "buttonA", 0,  Graphics.color["buttonA"])
        #self.draw_rect("play", Graphics.buttonB_rect["slf"], "buttonB", 0,  Graphics.color["buttonB"])
        self.draw_rect("play", Graphics.buttonC_rect["slf"], "turn"+str(turn_count), 0,  Graphics.color["buttonC"])
        self.draw_rect("play", Graphics.buttonD_rect["slf"], "retire", 0,  Graphics.color["buttonD"])
        self.font = pygame.font.Font(None, 70)#フォントとサイズ

        self.draw_rect("play", Graphics.tegoma_rect["slf"], "", 0,  Graphics.color["tegoma"])
        self.draw_rect("play", Graphics.tegoma_rect["opp"], "", 1,  Graphics.color["tegoma"])

    def draw_exe(self, turn_count):
        pygame.draw.rect(self.screen, Graphics.color["board"], self.rect(Graphics.board_rect["bg"]))
        #盤面の線を描画
        for i in range(Graphics.boardsize+1):#たて
            pygame.draw.line(self.screen, (0,0,0), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][0][1])*Graphics.cell), ((Graphics.board_rect["board"][0][0] + i)*Graphics.cell,(Graphics.board_rect["board"][1][1]+1)*Graphics.cell),3)
        for i in range(Graphics.boardsize+1):#よこ
            pygame.draw.line(self.screen, (0,0,0), (Graphics.board_rect["board"][0][0]*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell), ((Graphics.board_rect["board"][1][0] + 1)*Graphics.cell,(Graphics.board_rect["board"][0][1] + i)*Graphics.cell),3)
        
        self.font = pygame.font.Font(None, 40)#フォントとサイズ
        pygame.draw.rect(self.screen, Graphics.color["tegoma"], self.rect(Graphics.tegoma_rect["opp"]))
        pygame.draw.rect(self.screen, Graphics.color["tegoma"], self.rect(Graphics.tegoma_rect["slf"]))
        self.draw_rect("play", Graphics.buttonC_rect["slf"], "turn"+str(turn_count), 0,  Graphics.color["buttonC"])
        self.font = pygame.font.Font(None, 70)#フォントとサイズ

    def board_update(self, grid, hands):
        #各マスの情報から駒の画像を配列に入れて、描画
        for row in range(Graphics.boardsize):
            for column in range(Graphics.boardsize):
                if grid[row][column] == 0:
                    self.image[row][column] = pygame.image.load(Graphics.url_key[1]).convert_alpha()#駒の置かれてない部分は白石の画像を与えて、場外に表示させて隠す
                    bye=1#空白判定用
                else:
                    self.image[row][column] = pygame.image.load(Graphics.url_key[grid[row][column]]).convert_alpha()
                    bye=0
                    if 11 <= grid[row][column] and grid[row][column] <=18:
                        self.image[row][column] = pygame.transform.rotate(self.image[row][column], 180)
                    if 32 <= grid[row][column] and grid[row][column] <=38:
                        self.image[row][column] = pygame.transform.rotate(self.image[row][column], 180)

                self.image[row][column] = pygame.transform.scale(self.image[row][column], (Graphics.cell-4, Graphics.cell-4))#サイズ変更
                self.image_rect[row][column] = (-2000*bye+(Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, (Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2, Graphics.cell-4, Graphics.cell-4)
                self.screen.blit(self.image[row][column], pygame.Rect(self.image_rect[row][column]))#駒を描画

        
        #持駒を描画
        for j in {1,2}:
            self.info_mochi[j] = []
            for i in range(8):
                count = hands[j].get(i + 1, 0)
                for k in range(count):
                    self.info_mochi[j].append(i+1)
            
            k = math.ceil((len(self.info_mochi[j])) /4)
            '''
            0123
            4567

            '''
            for i in range(k):
                for l in range(4):
                    if 4*i+l > len(self.info_mochi[j])-1:
                        break
                    self.image_mochi[j][4*i+l] = pygame.image.load(Graphics.url_key[self.info_mochi[j][4*i+l]]).convert_alpha()
                    self.image_mochi[j][4*i+l] = pygame.transform.scale(self.image_mochi[j][4*i+l], (Graphics.cell-4, Graphics.cell-4))#サイズ変更
                    if j == 2:
                        self.image_mochi[j][4*i+l] = pygame.transform.rotate(self.image_mochi[j][4*i+l], 180)
                    self.rectt[j][4*i+l] = self.image_mochi[j][4*i+l].get_rect()
                    if j == 1:
                        self.rectt[j][4*i+l].center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*l, self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*i)
                        self.screen.blit(self.image_mochi[j][4*i+l], self.rectt[j][4*i+l])
                    if j == 2:
                        self.rectt[j][4*i+l].center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*l, self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*i)
                        self.screen.blit(self.image_mochi[j][4*i+l], self.rectt[j][4*i+l])
                    

        self.pre_zahyo = (-1,(0,0))

        self.timer_update(1,100)#ここでdisplay.updateがなされている
        #画面への反映
        #pygame.display.update()
    
    def blight(self, zahyo):#zahyo = (basyo 1:自分の手ごま,2:相手の手ごま,0:盤上,(row,culumn))   k:透明度
        if self.pre_zahyo != zahyo and self.pre_zahyo[0] != -1 :
            if self.pre_zahyo[0] >= 1:
                i, l = self.pre_zahyo[1][1], self.pre_zahyo[1][0]
                self.image_mochi[self.pre_zahyo[0]][4*i+l] = self.original.copy()
                rectc = self.image_mochi[self.pre_zahyo[0]][4*i+l].get_rect()
                if self.pre_zahyo[0] == 1:
                    rectc.center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*l, self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*i)
                if self.pre_zahyo[0] == 2:
                    rectc.center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*l, self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*i)
                self.screen.blit(self.image_mochi[self.pre_zahyo[0]][4*i+l], rectc)
            elif self.pre_zahyo[0] == 0:
                row, column = self.pre_zahyo[1][1], self.pre_zahyo[1][0]
                self.image[row][column] = self.original.copy()
                self.screen.blit(self.image[row][column], ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, (Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2))
        
        if self.pre_zahyo == zahyo:
            return
        
        if zahyo[0] == 1:
            i, l = zahyo[1][1], zahyo[1][0]
            self.original = self.image_mochi[1][4*i+l].copy() # 自分の手駒が２個以上の時に２個目以降を選択するとエラー
            self.image_mochi[1][4*i+l].fill(self.k, special_flags=pygame.BLEND_ADD)
            rectc = self.image_mochi[1][4*i+l].get_rect()
            rectc.center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*l, self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*i)
            self.screen.blit(self.image_mochi[1][4*i+l], rectc)
        if zahyo[0] == 2:
            i, l = zahyo[1][1], zahyo[1][0]
            self.original = self.image_mochi[2][4*i+l].copy()
            self.image_mochi[2][4*i+l].fill(self.k, special_flags=pygame.BLEND_ADD)
            rectc = self.image_mochi[2][4*i+l].get_rect()
            rectc.center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*l, self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*i)
            self.screen.blit(self.image_mochi[2][4*i+l], rectc)
            
        if zahyo[0] == 0:
            row, column = zahyo[1][1], zahyo[1][0]
            self.original = self.image[row][column].copy()
            self.image[row][column].fill(self.k, special_flags=pygame.BLEND_ADD)
            self.screen.blit(self.image[row][column], ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, (Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2))
        
        self.pre_zahyo = zahyo
        #画面への反映
        pygame.display.update()


    def bl_cancel(self):
        if self.pre_zahyo[0] >= 1:
            i, l = self.pre_zahyo[1][1], self.pre_zahyo[1][0]
            self.image_mochi[self.pre_zahyo[0]][4*i+l] = self.original.copy()
            rectc = self.image_mochi[self.pre_zahyo[0]][4*i+l].get_rect()
            if self.pre_zahyo[0] == 1:
                rectc.center = (self.rect(Graphics.tegoma_rect["slf"]).left+Graphics.cell/2+Graphics.cell*l, self.rect(Graphics.tegoma_rect["slf"]).top+Graphics.cell/2+Graphics.cell*i)
            if self.pre_zahyo[0] == 2:
                rectc.center = (self.rect(Graphics.tegoma_rect["opp"]).right-Graphics.cell/2-Graphics.cell*l, self.rect(Graphics.tegoma_rect["opp"]).bottom-Graphics.cell/2-Graphics.cell*i)
            self.screen.blit(self.image_mochi[self.pre_zahyo[0]][4*i+l], rectc)
        elif self.pre_zahyo[0] == 0:
            row, column = self.pre_zahyo[1][1], self.pre_zahyo[1][0]
            self.image[row][column] = self.original.copy()
            self.screen.blit(self.image[row][column], ((Graphics.board_rect["board"][0][0]+column)*Graphics.cell+2, (Graphics.board_rect["board"][0][1]+row)*Graphics.cell+2))
        
        self.pre_zahyo = (-1,(0,0))
        #画面への反映
        pygame.display.update()

    #ポップの作成text:popの内容、left:popの左ボタン
    def make_pop(self, situ, text, left, right):
        rgb = Graphics.color["pop"]
        self.draw_rect(situ, Graphics.pop_rect["bg"], "", 0, rgb)
        self.draw_rect(situ, Graphics.pop_rect["text"], text, 0, rgb)
        self.draw_rect(situ, Graphics.pop_rect["left"], left, 0, (rgb[0]+20,rgb[1]+20,rgb[2]+20))
        self.draw_rect(situ, Graphics.pop_rect["right"], right, 0, (rgb[0]+20,rgb[1]+20,rgb[2]+20))
    
        #画面への反映
        pygame.display.update()
    
    def make_migipop(self, situ, text, left, right):
        self.font = pygame.font.Font(None, 40)#フォントとサイズ
        rgb = Graphics.color["pop"]
        if left != "" or right != "":
            self.draw_rect(situ, Graphics.pop_rect["migi_bg"], "", 0, (100,100,100,100))
        #ボタンやテキストがない場合はボタンを描画しない
        if text != "":
            self.draw_rect(situ, Graphics.pop_rect["migi_text"], text, 0, (100,100,100,100))  #スペースがないので描画しない
        if left != "":
            self.draw_rect(situ, Graphics.pop_rect["migi_left"], left, 0, Graphics.color["buttonA"])
        if right != "":
            self.draw_rect(situ, Graphics.pop_rect["migi_right"], right, 0, Graphics.color["buttonB"])
        self.font = pygame.font.Font(None, 70)#フォントとサイズ
    
        #画面への反映
        pygame.display.update()
    
        
    
    #大popの作成（textは改行ごとにリスト内で分ける。sentakusiも各ボタンの名称をリストで入力
    def make_daipop(self, situ, text, sentakusi):
        rgb = Graphics.color["pop"]
        self.draw_rect(situ, Graphics.pop_rect["daibg"], "", 0, rgb)
        self.draw_rect(situ, Graphics.pop_rect["daitext"], text, 0, rgb)
        l = len(sentakusi)
        k = Graphics.pop_rect["daibg"][1][0]-Graphics.pop_rect["daibg"][0][0]+1
        c = (k / l)
        for b in range(l):
            self.draw_rect(situ, ((Graphics.pop_rect["daibg"][0][0]+b*c+0.2,7), (Graphics.pop_rect["daibg"][0][0]+b*c+c-1.2,8.5)), sentakusi[b], 0, (rgb[0]+20,rgb[1]+20,rgb[2]+20))

        #画面への反映
        pygame.display.update()
    
    #タイマーのアップデート（描画）（今の手番と【秒】数を指定）
    def timer_update(self, teban, number): #teban = 1:自分, 2:相手
        m = number // 60
        s = number % 60
        self.font = pygame.font.Font(None, 40)#フォントとサイズ
        if s < 10:
            self.draw_rect_outline(Graphics.timer_rect["timer"], str(m)+":0"+str(s), 0,  (100,100,100), Graphics.color["timer"])
        else:
            self.draw_rect_outline(Graphics.timer_rect["timer"], str(m)+":"+str(s), 0, (100,100,100), Graphics.color["timer"])
        self.draw_rect_outline(Graphics.timer_rect["teban"], ["now:",Graphics.turn[teban]], 0, (100,100,100), Graphics.color["timer"])

        self.font = pygame.font.Font(None, 70)#フォントとサイズ
        #画面への反映
        pygame.display.update()

    #テキストありの塗りつぶしrect描画
    def draw_rect(self, situ, rect, text, down, rgb):
        pygame.draw.rect(self.screen, rgb, self.rect(rect))
        if type(text) is str:
            text = [text]
        l = len(text)
        for i in range(l):
            self.dvd_text(text[i], self.rect(rect).width)
        l = len(self.text_dvd)
        for i in range(l):
            textc = self.font.render(self.text_dvd[i], True, (255,255,255))
            if down == 1:
                textc = pygame.transform.rotate(textc, 180)
                i = l - i -1
            text_rect = textc.get_rect()
            h = text_rect.height
            text_rect.center = ((rect[1][0]+1)*Graphics.cell + rect[0][0]*Graphics.cell)/2, ((rect[1][1]+1)*Graphics.cell + rect[0][1]*Graphics.cell)/2 + i*h - (l-1)*(h/2)
            self.screen.blit(textc, text_rect)
        if l > 0:
            if (situ in self.button_list) == False:
                self.button_list[situ]= set()
            self.button_list[situ].add(text[0])#situaton:situのbuttonlistに（主に）ボタンのtextの一行目を追加する
            self.button_rect_list[situ+text[0]] = rect
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