#駒ごとの移動ルールなどを管理
##今回の軍議での「自分」とは「駒を下から上に動かす方」を指します。相手は逆
# 駒の番号定義：
#1.	帥（すい）: 1枚
#2.	大将（たいしょう）: 1枚
#3.	中将（ちゅうじょう）: 1枚
#4.	小将（しょうしょう）: 2枚
#5.	侍（さむらい）: 2枚
#6.	槍（やり）: 3枚
#7.	忍（しのび）: 2枚
#8.	騎馬（きば）: 2枚
#9.	兵（ひょう）: 4枚
#10.	砦（とりで）: 2枚
#11.	砲（ほう）: 1枚
#12.	筒（つつ）: 1枚
#13.	弓（ゆみ）: 2枚
#14.	謀（ぼう）: 1枚
#101〜114: 相手の駒（+100）
#'駒の番号'_'段数'.png
#例: 1_3.png → 自分の帥の3段目


class Board:
    def __init__(self):
        # 初期配置(何も置かれない)
        self.size = 9
        self.grid = [[[0 for _ in range(3)] for _ in range(self.size)] for _ in range(self.size)]  

        # 現状の盤面の重なりを記憶しておく
        self.high_memory = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # 全駒の合法手を保持するマップ（キャッシュ用）
        self.valid_moves_map = {}


    def is_enemy(self, piece, current_turn):
        # 指定された駒が敵の駒かを判定
        if piece == 0:
            return False
        return (current_turn == 1 and ( 101 <= piece <= 114)) or (current_turn == 2 and ( 1 <= piece <= 14))

    def is_own(self, piece, current_turn):
        # 指定された駒が自分の駒かを判定
        if piece == 0:
            return False
        return (current_turn == 1 and ( 1 <= piece <= 14)) or (current_turn == 2 and ( 101 <= piece <= 114))
    
    #統合では、if is_own(self.grid[y][x][self.high_memory[y][x]],current_turn) == Trueなら以下の関数を呼び出すようにする
    def get_valid_moves(self, x, y, current_turn):
        z = self.high_memory[y][x]
        # 指定マスの駒に対し、合法な移動先座標リストを返す
        piece = self.grid[y][x][z - 1]
        if not self.is_own(piece, current_turn):
            return []
        # 各駒の移動範囲定義
        if piece % 100 == 1:  # 帥
            return self.line_directions_tuke(
                [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)],
                x, y, z, current_turn
            )
        elif piece % 100 == 2:  # 大将
            moves = self.line_directions_inf(
                [(0,1),(0,-1),(1,0),(-1,0)], x, y, z, current_turn
            )+self.line_directions_tuke(
                [(1,1),(1,-1),(-1,1),(-1,-1)], x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 3:  # 中将
            moves = self.line_directions_tuke(
                [(0,1),(0,-1),(1,0),(-1,0)], x, y, z, current_turn
            )+self.line_directions_inf(
                [(1,1),(1,-1),(-1,1),(-1,-1)], x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 4: # 少将
            dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(0,1)] if current_turn == 1 else \
                [(-1,1),(0,1),(1,1),(-1,0),(1,0),(0,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 5:  # 侍
            dirs = [(-1,-1),(0,-1),(1,-1),(0,1)] if current_turn == 1 else \
                [(-1,1),(0,1),(1,1),(0,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 6:  # 槍
            dirs = [(-1,-1),(1,-1),(0,1)] if current_turn == 1 else [(-1,1),(1,1),(0,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            dirs = [(0,-1)] if current_turn == 1 else [(0,1)]
            moves += self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )    
            return moves
        elif piece % 100 == 7:  # 忍
            dirs = [(-1,-1),(1,-1),(-1,1),(1,1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 8:  # 騎馬
            dirs = [(0,-1),(0,1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            dirs = [(-1,0),(1,0)]
            moves += self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 9:  # 兵
            dirs = [(0,-1),(0,1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 10:  # 砦
            dirs = [(-1,0),(0,-1),(1,0),(-1,1),(1,1)] if current_turn == 1 else \
                [(-1,0),(0,1),(1,0),(-1,-1),(1,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 11:  # 砲
            dirs = [(-1,0),(1,0),(0,1)] if current_turn == 1 else \
                [(-1,0),(1,0),(0,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )+self.line_directions_jump(
                piece, x, y, z, current_turn
            )
            return moves           
        elif piece % 100 == 12:  # 筒
            dirs = [(-1,1),(1,1)] if current_turn == 1 else \
                [(-1,-1),(1,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )+self.line_directions_jump(
                piece, x, y, z, current_turn
            )
            return moves
        elif piece % 100 == 13:  # 弓
            if current_turn == 1: 
                dirs = [(0,1)]
            else:
                dirs = [(0,-1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )+self.line_directions_jump(
                piece, x, y, z, current_turn
            )
            return moves   
        elif piece % 100 == 14:  # 謀
            dirs = [(0,1),(-1,-1),(1,-1)] if current_turn == 1 else \
                [(0,-1),(-1,1),(1,1)]
            moves = self.line_directions_tuke(
                dirs, x, y, z, current_turn
            )
            return moves
        return []
    
    def update_all_valid_moves(self, current_turn):
    # 現在の盤面上の「自分のすべての駒」の合法手を更新する
        self.valid_moves_map = {}
        for y in range(9):
            for x in range(9):
                if self.is_own(self.grid[y][x][self.high_memory[y][x] - 1], current_turn):
                    moves = self.get_valid_moves(x, y, current_turn)
                    if moves:
                        self.valid_moves_map[(x, y)] = moves

    def get_cached_valid_moves(self, x, y):
        z = self.high_memory[y][x]
        # update_all_valid_movesで保存した移動先を返す（選択時など）
        return self.valid_moves_map.get((x, y, z), [])

    def line_directions_inf(self, dirs, x, y, z, turn):
        # 複数マス直線移動の処理（大将・中将）
        moves = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 9 and 0 <= ny < 9:
                if self.high_memory[ny][nx] == 0:
                    moves.append((nx, ny))
                else:
                    target = self.grid[ny][nx][self.high_memory[ny][nx] -1 ]
                    if self.is_own(target, turn):
                        if z < self.high_memory[ny][nx] or self.high_memory[ny][nx] == 3:
                            break
                        else:
                            moves.append((nx, ny))
                            break
                    elif self.is_enemy(target, turn):
                        if z < self.high_memory[ny][nx]:
                            break
                        else:
                            moves.append((nx, ny))
                            break
                    else:
                        break
                nx += dx
                ny += dy
        return moves
    
    def line_directions_tuke(self, dirs, x, y, z, turn):
        # 直線移動の処理 ただし、飛越可能な方向は別の関数
        moves = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            #1段目から2マス進めるやつは動きを伸ばす
            if (
                self.grid[y][x][self.high_memory[y][x] - 1] % 100 == 6 and (dirs == [(0,-1)] or dirs == [(0,1)])
                ) or (
                    self.grid[y][x][self.high_memory[y][x] - 1] % 100 == 7 and (dirs == [(-1,-1),(1,-1),(-1,1),(1,1)])
                    ) or (
                        self.grid[y][x][self.high_memory[y][x] - 1] % 100 == 8 and (dirs == [(0,-1),(0,1)] or [(-1,0),(1,0)])):
                roop = z+1
            else:
                roop = z

            for _ in range(roop):
                if not (0 <= nx < 9 and 0 <= ny < 9):
                    break
                if self.high_memory[ny][nx] == 0:
                    moves.append((nx, ny))
                else:
                    target = self.grid[ny][nx][self.high_memory[ny][nx] -1 ]
                    if self.is_own(target, turn):
                        if z < self.high_memory[ny][nx] or self.high_memory[ny][nx] == 3:
                            break
                        else:
                            moves.append((nx, ny))
                            break
                    elif self.is_enemy(target, turn):
                        if z < self.high_memory[ny][nx]:
                            break
                        else:
                            moves.append((nx, ny))
                            break
                    else:
                        break
                nx += dx
                ny += dy
        return moves
    
    def line_directions_jump(self, piece, x, y, z, turn):
        # 飛越方向の処理(11,12,13 ,111,112,113)
        moves = []
        dirs = []
        if piece == 11:
            if y-2 < 0:
                return moves
            elif self.high_memory[y-1][x] <= z and self.high_memory[y-2][x] <= z:
                y -= 2
                dirs = [(0, -1)]
        elif piece == 111:
            if y+2 > 8:
                return moves
            elif self.high_memory[y+1][x] <= z and self.high_memory[y+2][x] <= z:
                y += 2
                dirs = [(0, 1)]
        elif piece == 12:
            if y-1 < 0:
                return moves
            elif self.high_memory[y-1][x] > z:
                return moves
            dirs = [(0, -1)]
            y -= 1    
        elif piece == 112:
            if y+1 > 8:
                return moves
            elif self.high_memory[y+1][x] > z:
                return moves
            dirs = [(0, 1)]
            y += 1

        elif piece == 13:
            if y-1 < 0:
                return moves
            if self.high_memory[y-1][x] <= z:
                y -= 1
                if x-1 >= 0:
                    if self.high_memory[y][x-1] <= z:
                        dirs += [(-1, -1)]
                if x+1 <= 8:
                    if self.high_memory[y][x+1] <= z:
                        dirs += [(1, -1)]  
                if dirs != []:
                    dirs += [(0, -1)]
                   
        elif piece == 113:
            if y+1 > 8:
                return moves
            elif self.high_memory[y+1][x] <= z:
                y += 1
                if x-1 >= 0:
                    if self.high_memory[y][x-1] <= z:
                        dirs += [(-1, 1)]
                if x+1 <= 8:
                    if self.high_memory[y][x+1] <= z:
                        dirs += [(1, 1)]
                if dirs != []:
                    dirs += [(0, 1)]
        if dirs == []:
            return moves
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            for _ in range(z):
                if not (0 <= nx < 9 and 0 <= ny < 9):
                    break
                if self.high_memory[ny][nx] == 0:
                    moves.append((nx, ny))
                else:
                    target = self.grid[ny][nx][self.high_memory[ny][nx] -1 ]
                    if self.is_own(target, turn):
                        if z < self.high_memory[ny][nx] or self.high_memory[ny][nx] == 3:
                            break
                        else:
                            moves.append((nx, ny))
                            break
                    elif self.is_enemy(target, turn):
                        if z < self.high_memory[ny][nx]:
                            break
                        else:
                            moves.append((nx, ny))
                            break
                    else:
                        break
                nx += dx
                ny += dy
        return moves

    def is_check(self, current_turn):
        # 相手の帥が王手されているかを判定する
        target_king = 101 if current_turn == 1 else 1

        # 玉の位置を探す
        king_pos = None
        for y in range(9):
            for x in range(9):
                if self.grid[y][x][self.high_memory[y][x] -1 ] == target_king:
                    king_pos = (x, y)
                    break
            if king_pos:
                break

        if not king_pos:
            return False  # 帥がいない（すでに負け）

        # 自分のすべての駒から合法手を見て、玉に効いているか確認
        for y in range(9):
            for x in range(9):
                if self.is_own(self.grid[y][x][self.high_memory[y][x]], current_turn):
                    moves = self.get_valid_moves(x, y, current_turn)
                    if king_pos in moves:
                        return True
        return False

    def is_checkmate(self, current_turn):
        # 相手の帥が詰んでいるかを判定する（全逃げ道が塞がれていて、かつ王手されている状態）
        #まず王手されているか
        if not self.is_check(current_turn):
            return False
        target_king = 101 if current_turn == 1 else 1

        # 帥の位置を探す
        king_pos = None
        for y in range(9):
            for x in range(9):
                if self.grid[y][x][self.high_memory[y][x]] == target_king:
                    king_pos = (x, y)
                    break
            if king_pos:
                break

        if not king_pos:
            return True  # 玉(王)がいなければ詰んでる

        # 帥の周囲マスのうち合法な逃げ先をチェック
        way = self.get_valid_moves(king_pos[0],king_pos[1],current_turn)
        for nx, ny, z in way:
            dest_piece = self.grid[ny][nx][self.high_memory[ny][nx]]
            if not self.is_enemy(dest_piece, current_turn):
                # このマスに逃げたとして、敵駒が効いてなければ詰みではない
                test_grid = [row[:] for row in self.grid]
                test_grid[king_pos[1]][king_pos[0]][self.high_memory[king_pos[1]][king_pos[0]]] = 0
                test_grid[ny][nx] = target_king

                # 仮想盤面で敵駒から王が攻撃されないかチェック
                for y2 in range(9):
                    for x2 in range(9):
                        if self.is_enemy(test_grid[y2][x2][self.high_memory[y2][x2]], current_turn):
                            enemy_moves = self.get_valid_moves(x2, y2, (current_turn +1) % 2)
                            if (nx, ny) in enemy_moves:
                                break
                    else:
                        continue
                    break
                else:
                    return False  # 一つでも安全な逃げ道があれば詰んでいない

        return True