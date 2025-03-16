
class imputer:
    def __init__(self):
        self.cdn =[[0 for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                self.cdn[i][j]=pygame.Rect(i*78+1,j*78+1,76,76)
    def boardclick(self, turn):
        if event.type == MOUSEBUTTONDOWN:
            cursor_x,cursor_y = event.pos
            if event.button == 1 and x <= 78*8-1:
                cursor_mat_x = math.floor(x/78)#0~7まで
                cursor_mat_y = math.floor(y/78)#0~7まで
                for i in range(3):
                    for j in range(3):

                        if self.cdn[i-1+cursor_mat_x][j-1+cursor_mat_y].collidepoint(event.pos):
                            break
                            


    
        
