#駒ごとの移動ルール、成り判定、二歩の反則などを管理
##今回の将棋での「自分」とは「駒を下から上に動かす方」を指します。相手は逆
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

class Board:
    def __init__(self):
        # 将棋の初期配置
        self.size = 9
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        # 相手の駒を上に配置
        self.grid[0] = [17, 16, 15, 14, 11, 14, 15, 16, 17]  # 上段
        self.grid[1][7] = 13  # 角
        self.grid[1][1] = 12  # 飛車
        self.grid[2] = [18 for _ in range(9)]  # 歩兵
        # 自分の駒を下に配置
        self.grid[8] = [7, 6, 5, 4, 1, 4, 5, 6, 7]
        self.grid[7][7] = 2  # 飛車
        self.grid[7][1] = 3  # 角行
        self.grid[6] = [8 for _ in range(9)]
        # 全駒の合法手を保持するマップ（キャッシュ用）
        self.valid_moves_map = {}

    def is_enemy(self, piece, current_turn):
        # 指定された駒が敵の駒かを判定
        if piece == 0:
            return False
        return (current_turn == 1 and ( 10 < piece < 20 or 30 < piece < 40)) or (current_turn == 2 and ( 0 < piece < 10 or 20 < piece < 30))

    def is_own(self, piece, current_turn):
        # 指定された駒が自分の駒かを判定
        if piece == 0:
            return False
        return (current_turn == 1 and ( 0 < piece < 10 or 20 < piece < 30)) or (current_turn == 2 and ( 10 < piece < 20 or 30 < piece < 40))

    def should_promote(self, piece, from_y, to_y, current_turn):
        # 成りが可能な状況かを判定する（UI側のボタン表示用）
        if not self.is_promotable(piece):
            return False

        # 敵陣（自分なら0〜2段目、相手なら6〜8段目）に関係するか
        if current_turn == 1:
            return from_y <= 2 or to_y <= 2
        else:
            return from_y >= 6 or to_y >= 6

    def is_promotable(self, piece):
        # 成れる駒かを判定
        return piece in [2, 3, 5, 6, 7, 8, 12, 13, 15, 16, 17, 18]

    def promote(self, piece):
        # 成り駒へ変換
        promote_dict = {
            2: 22, 3: 23, 5: 25, 6: 26, 7: 27, 8: 28,
            12: 32, 13: 33, 15: 35, 16: 36, 17: 37, 18: 38
        }
        return promote_dict.get(piece, piece)

    def unpromote(self, piece):
        # 成り駒を元に戻す（持ち駒化や判別用）
        unpromote_dict = {
            22: 2, 23: 3, 25: 5, 26: 6, 27: 7, 28: 8,
            32: 12, 33: 13, 35: 15, 36: 16, 37: 17, 38: 18
        }
        return unpromote_dict.get(piece, piece)

    def is_double_pawn(self, x, current_turn):
        # 二歩の反則チェック：同じ列に自分の歩があればTrueを返す
        target_code = 8 if current_turn == 1 else 18
        for y in range(9):
            if self.grid[y][x] == target_code:
                return True
        return False
    
    def get_valid_moves(self, x, y, current_turn):
        # 指定マスの駒に対し、合法な移動先座標リストを返す
        piece = self.grid[y][x]
        if not self.is_own(piece, current_turn):
            return []

        raw_piece = self.unpromote(piece % 20)  # 成り駒から基本種別へ
        promoted = (piece >= 20)

        # 各駒の移動範囲定義（すべて絶対座標で返す）
        if raw_piece % 10 == 1:  # 玉将
            return self.step_directions(
                [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)],
                x, y, current_turn
            )
        elif raw_piece % 10 == 2:  # 飛車（＋成り）
            moves = self.line_directions(
                [(0,1),(0,-1),(1,0),(-1,0)], x, y, current_turn
            )
            if promoted:
                moves += self.step_directions(
                    [(-1,-1),(1,-1),(-1,1),(1,1)], x, y, current_turn
                )
            return moves
        elif raw_piece % 10 == 3:  # 角行（＋成り）
            moves = self.line_directions(
                [(-1,-1),(1,-1),(-1,1),(1,1)], x, y, current_turn
            )
            if promoted:
                moves += self.step_directions(
                    [(0,1),(0,-1),(1,0),(-1,0)], x, y, current_turn
                )
            return moves
        elif raw_piece % 10 == 4 or (promoted and raw_piece in [5,6,7,8,15,16,17,18]):  # 金＆成り銀桂香歩
            dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(0,1)] if current_turn == 1 else \
                [(-1,1),(0,1),(1,1),(-1,0),(1,0),(0,-1)]
            return self.step_directions(dirs, x, y, current_turn)
        elif raw_piece % 10 == 5:  # 銀将
            dirs = [(-1,-1),(0,-1),(1,-1),(-1,1),(1,1)] if current_turn == 1 else \
                [(-1,1),(0,1),(1,1),(-1,-1),(1,-1)]
            return self.step_directions(dirs, x, y, current_turn)
        elif raw_piece % 10 == 6:  # 桂馬
            dirs = [(-1,-2),(1,-2)] if current_turn == 1 else [(-1,2),(1,2)]
            return self.step_directions(dirs, x, y, current_turn)
        elif raw_piece % 10 == 7:  # 香車
            return self.line_directions(
                [(0,-1)] if current_turn == 1 else [(0,1)], x, y, current_turn
            )
        elif raw_piece % 10 == 8:  # 歩兵
            dirs = [(0,-1)] if current_turn == 1 else [(0,1)]
            return self.step_directions(dirs, x, y, current_turn)

        return []
    
    def update_all_valid_moves(self, current_turn):
    # 現在の盤面上の「自分のすべての駒」の合法手を更新する
        self.valid_moves_map = {}
        for y in range(9):
            for x in range(9):
                if self.is_own(self.grid[y][x], current_turn):
                    moves = self.get_valid_moves(x, y, current_turn)
                    if moves:
                        self.valid_moves_map[(x, y)] = moves

    def get_cached_valid_moves(self, x, y):
        # update_all_valid_movesで保存した移動先を返す（選択時など）
        return self.valid_moves_map.get((x, y), [])

    def line_directions(self, dirs, x, y, turn):
        # 複数マス直線移動の処理（飛車・角など）
        moves = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 9 and 0 <= ny < 9:
                target = self.grid[ny][nx]
                if self.is_own(target, turn):
                    break
                moves.append((nx, ny))
                if self.is_enemy(target, turn):
                    break
                nx += dx
                ny += dy
        return moves

    def step_directions(self, dirs, x, y, turn):
        # 1マスのみ移動の処理（玉将、成り追加移動など）
        moves = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                target = self.grid[ny][nx]
                if not self.is_own(target, turn):
                    moves.append((nx, ny))
        return moves

    def is_check(self, current_turn):
        # 相手の玉が王手されているかを判定する
        target_king = 11 if current_turn == 1 else 1

        # 玉の位置を探す
        king_pos = None
        for y in range(9):
            for x in range(9):
                if self.grid[y][x] == target_king:
                    king_pos = (x, y)
                    break
            if king_pos:
                break

        if not king_pos:
            return False  # 玉がいない（すでに負け）

        # 自分のすべての駒から合法手を見て、玉に効いているか確認
        for y in range(9):
            for x in range(9):
                if self.is_own(self.grid[y][x], current_turn):
                    moves = self.get_valid_moves(x, y, current_turn)
                    if king_pos in moves:
                        return True
        return False
    def is_check(self, current_turn):
            # 相手の玉が王手されているかを判定する
            target_king = 11 if current_turn == 1 else 1

            # 玉の位置を探す
            king_pos = None
            for y in range(9):
                for x in range(9):
                    if self.grid[y][x] == target_king:
                        king_pos = (x, y)
                        break
                if king_pos:
                    break

            if not king_pos:
                return False  # 玉がいない（すでに負け）

            # 自分のすべての駒から合法手を見て、玉に効いているか確認
            for y in range(9):
                for x in range(9):
                    if self.is_own(self.grid[y][x], current_turn):
                        moves = self.get_valid_moves(x, y, current_turn)
                        if king_pos in moves:
                            return True
            return False

    def is_checkmate(self, current_turn):
        # 相手の玉(王)が詰んでいるかを判定する（全逃げ道が塞がれていて、王手されている状態）
        target_king = 11 if current_turn == 1 else 1
        enemy_turn = 2 if current_turn == 1 else 1

        # 玉(王)の位置を探す
        king_pos = None
        for y in range(9):
            for x in range(9):
                if self.grid[y][x] == target_king:
                    king_pos = (x, y)
                    break
            if king_pos:
                break

        if not king_pos:
            return True  # 玉(王)がいなければ詰んでる

        # 玉の周囲マスのうち合法な逃げ先をチェック
        directions = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
        for dx, dy in directions:
            nx, ny = king_pos[0] + dx, king_pos[1] + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                dest_piece = self.grid[ny][nx]
                if not self.is_enemy(dest_piece, current_turn):
                    # このマスに逃げたとして、敵駒が効いてなければ詰みではない
                    test_grid = [row[:] for row in self.grid]
                    test_grid[king_pos[1]][king_pos[0]] = 0
                    test_grid[ny][nx] = target_king

                    # 仮想盤面で敵駒から王が攻撃されないかチェック
                    for y2 in range(9):
                        for x2 in range(9):
                            if self.is_own(self.grid[y2][x2], enemy_turn):
                                enemy_moves = self.get_valid_moves(x2, y2, enemy_turn)
                                if (nx, ny) in enemy_moves:
                                    break
                        else:
                            continue
                        break
                    else:
                        return False  # 一つでも安全な逃げ道があれば詰んでいない

        return self.is_check(current_turn)  # 王手がかかっている場合のみ詰み