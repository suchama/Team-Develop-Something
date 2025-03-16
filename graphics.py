#盤面の描画、駒配置の更新、時間タイマースタート、タイマーの数字更新、勝敗メッセージの表示、降参ボタンの表示

class Graphics(pygame.sprite.Sprite):
    def __init__(self):
        pygame.font.init()
        self.windowsizex = 1000#ウィンドウのサイズ
        self.windowsizey = 78*8
        self.white_img_pth = "画像2.png"#白石、黒石のパス
        self.black_img_pth = "画像1.png"
        self.screen = 0#使用するスクリーン
        self.stnsize = 60#駒のサイズ
        self.image = [[0 for _ in range(8)]for _ in range(8)]#駒用の配列
        self.font = pygame.font.Font(None, 80)#フォントとサイズ
        self.turnfinish = 0#自分の手番のとき０，手番が終わった時１
        self.screen = pygame.display.set_mode((self.windowsizex, self.windowsizey))#ウィンドウ作成
        pygame.display.set_caption("オセロゲーム")# 画面上部に表示するタイトル
        self.turn = 1
        self.timer_white = (78*8+(self.windowsizex-78*8)/2-15-130,50,130,180)#持ち時間ウィンドウの左上座標
        self.timer_black = (78*8+(self.windowsizex-78*8)/2+15,50,130,180)

    def window(self):#オセロ盤の描画
        self.screen.fill((0, 0, 0))#画面全体を黒で塗りつぶす
        pygame.draw.rect(self.screen, (100,255,100), (0,0,78*8,78*8))#緑色の盤面を描画
        #盤面のgridを描画
        for i in range(7):
            pygame.draw.line(self.screen, (100,100,200), (78*(i+1),0), (78*(i+1),78*8),3)
        for i in range(7):
            pygame.draw.line(self.screen, (100,100,200), (0,78*(i+1)), (78*8,78*(i+1)),3)
        #タイマー最初のもろもろ描画
        pygame.draw.rect(self.screen, (255,255,255), self.timer_white, 5)
        pygame.draw.line(self.screen, (255,255,255), (self.timer_white[0],self.timer_white[1]+50), (self.timer_white[0]+129,self.timer_white[1]+50), 5)
        pygame.draw.rect(self.screen, (100,100,255), self.timer_black, 5)
        pygame.draw.line(self.screen, (100,100,255), (self.timer_black[0],self.timer_black[1]+50), (self.timer_black[0]+129,self.timer_black[1]+50), 5)
        
        self.screen.blit(pygame.transform.scale(self.font.render("WHITE", True, (255, 255, 255)), (90,50)), (self.timer_white[0]+5,self.timer_white[1]+5))
        self.screen.blit(pygame.transform.scale(self.font.render("BLACK", True, (100, 100, 255)), (90,50)), (self.timer_black[0]+5,self.timer_black[1]+5))
        
        self.screen.blit(pygame.transform.scale(self.font.render("0", True, (255, 255, 255)), (60,60)), (self.timer_black[0]+35,self.timer_black[1]+85))#数字の描画
        self.screen.blit(pygame.transform.scale(self.font.render("0", True, (255, 255, 255)), (60,60)), (self.timer_white[0]+35,self.timer_white[1]+85))#数字の描
        #降参ボタン
        self.surrbtn = pygame.Rect(700,400,200,200)
        pygame.draw.rect(self.screen, (200,200,255), self.surrbtn)
        textsur = self.font.render("surrender", True, (255, 255, 255))
        textsur = pygame.transform.scale(textsur, (200, 100))#テキストをボタン上にサイズ調整
        self.screen.blit(textsur, (700,400))#テキストを指定の座標に表示

        #画面への反映
        pygame.display.update()

    def update(self, state, turn):#駒配置の更新（盤面状況のデータを受け取って駒の画像更新と表示）次のturn1:黒-1:白
        for row in range(8):#各マスの情報から駒の画像を入れていく
            for column in range(8):
                if state[row][column] == 0:
                    self.image[row][column] = pygame.image.load(self.white_img_pth).convert_alpha()#駒の置かれてない部分は白石の画像を与えて、場外に表示させて隠す
                    bye=1#空白判定用
                elif state[row][column] == 1:
                    self.image[row][column] = pygame.image.load(self.black_img_pth).convert_alpha()
                    bye=0
                elif state[row][column] == 2:
                    self.image[row][column] = pygame.image.load(self.white_img_pth).convert_alpha()
                    bye=0
                self.image[row][column] = pygame.transform.scale(self.image[row][column], (self.stnsize, self.stnsize))#サイズ変更
                self.screen.blit(self.image[row][column], (-1000*bye+78*column+39-self.stnsize/2, 78*row+39-self.stnsize/2))#imageを描画
        if turn == 1:
            pygame.draw.rect(self.screen, (0,0,0), (self.timer_white[0]+130-30,self.timer_white[1]+25, 20,20))
            self.screen.blit(pygame.transform.scale(self.font.render("@", True, (100, 100, 255)), (20,20)), (self.timer_black[0]+130-30,self.timer_black[1]+25))
        else:
            pygame.draw.rect(self.screen, (0,0,0), (self.timer_black[0]+130-30,self.timer_black[1]+25, 20,20))
            self.screen.blit(pygame.transform.scale(self.font.render("@", True, (255, 255, 255)), (20,20)), (self.timer_white[0]+130-30,self.timer_white[1]+25))
            
        #画面への反映  
        pygame.display.update()
        
    def timer(self, time, turn):#time秒のカウントダウンスタート turn1:黒-1:白
        self.turnfinish = 0
        self.time = time
        self.turn = turn
        self.countdown = pygame.USEREVENT#イベント設定
        pygame.time.set_timer(self.countdown, 1000)#1000ミリ秒ごとにself.countdownが発生？する

        texttim = self.font.render(str(self.time), True, (255, 255, 255))
        texttim = pygame.transform.scale(texttim, (60, 60))#サイズ調整
        if self.turn == 1:
            pygame.draw.rect(self.screen, (0,0,0), (self.timer_black[0]+35,self.timer_black[1]+85,60,60))#前の数字を黒で塗りつぶす
            self.screen.blit(texttim, (self.timer_black[0]+35,self.timer_black[1]+85))#数字の描画
        else:
            pygame.draw.rect(self.screen, (0,0,0), (self.timer_white[0]+35,self.timer_white[1]+85,60,60))#前の数字を黒で塗りつぶす
            self.screen.blit(texttim, (self.timer_white[0]+35,self.timer_white[1]+85))#数字の描画
        self.time += -1

        #画面への反映  
        pygame.display.update()        
        
    def timer_display(self, turn):#タイマーの数字更新 turn1:黒-1:白
        self.turn = turn
        if self.time == -1:#次の数字がー１になっていたら終了
            self.countdown = 0#カウントダウンのイベントを消去
            self.turn = self.turn*(-1)#ターン切り替え
            self.turnfinish = 1#手番終了　Gra.timer(turnfinish=0)→タイマー終了（turnfinish=1)
            return
        #数字の描画
        texttim = self.font.render(str(self.time), True, (255, 255, 255))
        texttim = pygame.transform.scale(texttim, (60, 60))#サイズ調整
        if self.turn == 1:
            pygame.draw.rect(self.screen, (0,0,0), (self.timer_black[0]+35,self.timer_black[1]+85,60,60))#前の数字を黒で塗りつぶす
            self.screen.blit(texttim, (self.timer_black[0]+35,self.timer_black[1]+85))#数字の描画
        else:
            pygame.draw.rect(self.screen, (0,0,0), (self.timer_white[0]+35,self.timer_white[1]+85,60,60))#前の数字を黒で塗りつぶす
            self.screen.blit(texttim, (self.timer_white[0]+35,self.timer_white[1]+85))#数字の描画
        self.time += -1
        #画面への反映
        pygame.display.update()

    def conclusion(self, position):#勝敗メッセージの表示(positionで勝ち負けを受け取る）（画像データを用意したほうがいいかもしれない）
        if position == "winner":#勝者メッセージを表示
            pygame.draw.rect(self.screen, (255,50,50), (500-200,78*8/2-100,400,200))
            text1 = self.font.render("You", True, (255, 255, 255))
            text2 = self.font.render("Are", True, (255, 255, 255))
            text3 = self.font.render("Winner", True, (255, 255, 255))
            self.screen.blit(text1, (500-200+20,78*8/2-100))
            self.screen.blit(text2, (500-200+20,78*8/2-100+55))
            self.screen.blit(text3, (500-200+20,78*8/2-100+110))
            #画面への反映
            pygame.display.update()

        else:#敗者メッセージ
            pygame.draw.rect(self.screen, (50,50,255), (500-200,78*8/2-100,400,200))
            text1 = self.font.render("You", True, (255, 255, 255))
            text2 = self.font.render("Are", True, (255, 255, 255))
            text3 = self.font.render("Loser", True, (255, 255, 255))
            self.screen.blit(text1, (500-200+20,78*8/2-100))
            self.screen.blit(text2, (500-200+20,78*8/2-100+55))
            self.screen.blit(text3, (500-200+20,78*8/2-100+110))
            #画面への反映
            pygame.display.update()


