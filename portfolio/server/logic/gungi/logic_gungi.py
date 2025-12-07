# logic_gungi
 
from typing import Dict, List, Tuple
from .board import Board
from .gamestate import GameState
import random

def game_start() -> Dict:
    """
    初期盤面を返す
    """
    b = Board()
    gs = GameState()

    # 初期配置が決まっているモード用の初期配置
    # 敵駒
    b.grid[0][4][0] = 101
    b.grid[0][3][0] = 103
    b.grid[0][5][0] = 102
    b.grid[1][1][0] = 108
    b.grid[1][2][0] = 113
    b.grid[1][4][0] = 106
    b.grid[1][6][0] = 113
    b.grid[1][7][0] = 107
    b.grid[2][0][0] = 109
    b.grid[2][2][0] = 110
    b.grid[2][3][0] = 105
    b.grid[2][4][0] = 109
    b.grid[2][5][0] = 105
    b.grid[2][6][0] = 110
    b.grid[2][8][0] = 108
    # 自駒
    b.grid[8][4][0] = 1
    b.grid[8][5][0] = 3
    b.grid[8][3][0] = 2
    b.grid[7][7][0] = 8
    b.grid[7][6][0] = 13
    b.grid[7][4][0] = 6
    b.grid[7][2][0] = 13
    b.grid[7][1][0] = 7
    b.grid[6][8][0] = 9
    b.grid[6][6][0] = 10
    b.grid[6][5][0] = 5
    b.grid[6][4][0] = 9
    b.grid[6][3][0] = 5
    b.grid[6][2][0] = 10
    b.grid[6][0][0] = 8
    # 高さを記憶しておく
    for _ in range(b.size):
        for a in range(b.size):
            if b.grid[_][a][0] != 0:
                b.high_memory[_][a] = 1
    # 初期配置が決まっているモード用の持ち駒
    gs.hands = {
        1: {4:2, 6:2, 7:1, 8:1, 9:1, 11:1, 12:1, 14:1},  # 自分
        2: {104:2, 106:2, 107:1, 108:1, 109:1, 111:1, 112:1, 114:1}   # 相手
    }

    return {
        "board": b.grid,
        "tegoma": gs.hands,
        "remaining_time": {1: 300, 2: 300},
        "current_turn": gs.current_turn,
        "high_memory": b.high_memory,
    }

def get_valid_moves(board: List[List[List[int]]],
                    tegoma: Dict[int, Dict[int, int]],
                    player: int,
                    place: str,
                    pos: List[int],
                    high_memory: List[List[int]],              
                    ):
    """
    1回目クリック時の処理
    画面のどこかを選択する。有効な場所をクリックしていたら、そこを返す。
    """
    b = Board()
    b.grid = [[layer[:] for layer in row] for row in board]
    b.high_memory = high_memory

    if place == "board":
        x, y = pos
        return b.get_valid_moves(x, y, player)
    
    elif place == "tegoma":
        piece = pos[0]
        moves = []
        for y in range(9):
            for x in range(9):
                if b.high_memory[y][x] >= 3: 
                    continue
                if b.high_memory[y][x] > 0:
                    top_piece = b.grid[y][x][b.high_memory[y][x]-1]
                    if top_piece == 1 + 100*(player-1):
                        continue
                # 自陣のみ配置可能
                if player == 1 and y < 6:
                    continue
                if player == 2 and y > 2:
                    continue
                moves.append((x, y))
        return moves
    return [[]]


def handle_player_move(board,
                       tegoma,
                       player,
                       selected_place,  # str
                       selected_pos,    # list
                       to_pos,
                       high_memory: List[List[int]],  
                       ) -> Dict:
    """
    2回目クリック時の処理
    1回目で選択したものをどうするかの処理
    ・移動のみ
    ・駒捕り
    ・ツケ
    ・謀
    """
    b = Board()
    b.grid = [row[:] for row in board]
    b.high_memory = high_memory
    gs = GameState()
    gs.hands = {1: dict(tegoma[1]), 2: dict(tegoma[2])}
    gs.board = b

    if selected_place == "board":
        x0, y0 = selected_pos
    x1, y1 = to_pos

    tuke_check = False
    bou_check = False
    winner = None
    
    # 盤面をクリックした場合
    if selected_place == "board":

        z0 = b.high_memory[y0][x0] - 1
        z1 = b.high_memory[y1][x1] - 1

        piece = b.grid[y0][x0][z0]
        if b.high_memory[y1][x1] > 0:
            to_piece = b.grid[y1][x1][z1]  
        else:
            to_piece = 0

        ## 駒の移動のみ
        if to_piece == 0:
            b.grid[y1][x1][0] = piece
            b.grid[y0][x0][z0] = 0
            b.high_memory[y0][x0] -= 1
            b.high_memory[y1][x1] = 1

            return {
                "winner": winner,
                "tuke_check": tuke_check,
                "bou_check": bou_check,
                "board_grid": b.grid,
                "tegoma": gs.hands,
                "current_turn": gs.current_turn,
                "high_memory": b.high_memory,
            }

        ## ツケチェック
        if to_piece != 0 and b.high_memory[y1][x1] < 3:
            if to_piece % 100 != 1:
                tuke_check = True
                print("つけられるよ！！！！！！！！！！")
                return {
                    "winner": winner,
                    "tuke_check": tuke_check,
                    "bou_check": bou_check,
                    "board_grid": b.grid,
                    "tegoma": gs.hands,
                    "current_turn": gs.current_turn,
                    "high_memory": b.high_memory,
                }
             
        ## 駒捕り
        print(f"to_piece:{to_piece}")
        print(b.is_enemy(to_piece, player))
        print(f"z0, z1:{z0, z1}")
        if to_piece != 0 and b.is_enemy(to_piece, player) and z0 >= z1:
            print("ここまで")
            koma_type = to_piece % 100
            ### 勝利判定
            if koma_type == 1:
                winner = player
                return {
                "winner": winner,
                "tuke_check": tuke_check,
                "bou_check": bou_check,
                "board_grid": b.grid,
                "tegoma": gs.hands,
                "current_turn": gs.current_turn,
                "high_memory": b.high_memory,
                }
            ### 盤面の更新
            b.grid[y1][x1][0] = piece
            b.grid[y1][x1][1] = b.grid[y1][x1][2] = 0
            b.grid[y0][x0][z0] = 0
            b.high_memory[y0][x0] -= 1
            b.high_memory[y1][x1] = 1


        ## 謀チェック
        ### 動かす駒が謀、高さ条件、行先が帥でない、を満たしているか
        if piece % 100 == 14 and z1 <= z0 <= 2 and to_piece % 100 != 1:

            ### 最上段が敵駒の場合
            if b.is_enemy(to_piece, player):
                # 手駒に敵駒と同じ駒があるか
                if gs.hands[player].get(to_piece % 100, 0) > 0:
                    bou_check = True

            ### 最下段が敵駒の場合
            elif b.is_enemy(b.grid[y1][x1][0], player):
                if gs.hands[player].get(b.grid[y1][x1][0] % 100, 0) > 0:
                    bou_check = True
                               
    
    # 手駒をクリックした場合。新の処理
    else:
        koma_type = selected_pos[0]
        ## 空きマスに置く
        if b.high_memory[y1][x1] == 0:
            b.grid[y1][x1][0] = koma_type + 100*(player - 1)
            b.high_memory[y1][x1] = 1
            gs.hands[player][koma_type] -= 1

            ### 使用した種類が0個になったら、手駒リストからその種類を削除
            if gs.hands[player][koma_type] == 0:
                del gs.hands[player][koma_type]

        ## ツケる
        elif 1 <= b.high_memory[y1][x1] <= 2 and b.is_own(b.grid[y1][x1][b.high_memory[y1][x1]], player):
            ### 自分の駒にツケる
            if (player == 1 and 6 <= y1 <= 8) or (player == 2 and 0 <= y1 <= 2):
                b.grid[y1][x1][b.high_memory[y1][x1]] = koma_type + 100*(player - 1)    #####
                b.high_memory[y1][x1] += 1
                gs.hands[player][koma_type] -= 1

                if gs.hands[player][koma_type] == 0:
                    del gs.hands[player][koma_type]

            ### 新で謀をツケ、1段目が敵駒の場合
            if koma_type == 14 and b.is_enemy(b.grid[y1][x1][0], player):
                # 手駒に敵駒と同じ駒があるか
                if gs.hands[player].get(b.grid[y1][x1][0] % 100, 0) > 0:
                    bou_check = True
        
    return {
        "winner": winner,
        "tuke_check": tuke_check,
        "bou_check": bou_check,
        "board_grid": b.grid,
        "tegoma": gs.hands,
        "current_turn": gs.current_turn,
        "high_memory": b.high_memory,
    }





def handle_tuke(board,
                player,
                selected_pos,
                to_pos,
                high_memory: List[List[int]],  
                ) -> Dict:
    """
    ツケの処理
    """
    b = Board()
    b.grid = [[row[:] for row in line] for line in board]
    b.high_memory = high_memory
    x0, y0 = selected_pos
    x1, y1 = to_pos
    z0 = b.high_memory[y0][x0] - 1
    piece = b.grid[y0][x0][z0]

    b.grid[y1][x1][b.high_memory[y1][x1]] = piece
    b.high_memory += 1
    b.grid[y0][x0][z0] = 0
    b.high_memory -= 1

    return {"board_grid": b.grid, 
            "current_turn": player,
            "high_memory": b.high_memory, 
    }


def handle_bou( board,
                tegoma,
                player,
                selected_pos,
                to_pos,
                high_memory: List[List[int]],  
                )-> Dict:
    """
    謀の処理
    """
    b = Board()
    b.grid = [[row[:] for row in line] for line in board]
    b.high_memory = high_memory
    gs = GameState()
    gs.hands = {1: dict(tegoma[1]), 2: dict(tegoma[2])}

    x0, y0 = selected_pos
    x1, y1 = to_pos
    z1 = b.high_memory[y1][x1] - 1
    enemy_piece = b.grid[y1][x1][z1]
    koma_type = enemy_piece % 100
    
    b.grid[y1][x1][z1] 
    gs.hands[player][koma_type] = koma_type + 100*(player-1) #####
    gs.hands[player][koma_type] -= 1
    if gs.hands[player][koma_type] == 0:
        del gs.hands[player][koma_type]

    return {"board_grid": board, 
            "tegoma": {1:dict,2:dict}, 
            "current_turn": player,
            "high_memory": b.high_memory, 
    }


def handle_ai_move(gamestate_dict,
                   current_turn,
                   high_memory: List[List[int]],  
                   ) -> Dict:
    """
    AIの手の処理（ランダム行動版）
    - 盤上の自駒の合法手を全て取得し、その中からランダムに1手を選ぶ。
    - 手駒を使うことも考慮（自陣の空きマスへランダム配置）。
    """
    b = Board()
    board = gamestate_dict["board"]
    b.grid = [[layer[:] for layer in row] for row in board]
    b.high_memory = high_memory
    gs = GameState()
    tegoma = gamestate_dict["tegoma"]
    gs.hands = {1: dict(tegoma[1]), 2: dict(tegoma[2])}
    gs.board = b

    winner = None
    player = current_turn
    legal_moves = []

    # --- 1. 盤上の自駒の合法手を収集 ---
    for y in range(9):
        for x in range(9):
            if b.high_memory[y][x] == 0:
                continue
            piece = b.grid[y][x][b.high_memory[y][x] - 1]
            if b.is_own(piece, player):
                valid = b.get_valid_moves(x, y, player)
                if valid:
                    for vx, vy in valid:
                        legal_moves.append({
                            "place": "board",
                            "from": [x, y],
                            "to": [vx, vy]
                        })

    # --- 2. 手駒からの打ち手も追加（新） ---
    for piece_code in list(gs.hands[player].keys()):
        for y in range(9):
            for x in range(9):
                # 自陣のみ配置可能
                if player == 1 and y < 6:
                    continue
                if player == 2 and y > 2:
                    continue
                if b.high_memory[y][x] >= 3:
                    continue
                if b.high_memory[y][x] > 0:
                    top_piece = b.grid[y][x][b.high_memory[y][x]-1]
                    # 帥の上には置けない
                    if top_piece == 1 + 100*(player-1):
                        continue
                legal_moves.append({
                    "place": "tegoma",
                    "from": [piece_code],
                    "to": [x, y]
                })

    # --- 3. 打てる手がなければパス ---
    if not legal_moves:
        gs.switch_turn()
        return {
            "board_grid": b.grid,
            "current_turn": gs.current_turn,
            "winner": None,
            "tegoma": gs.hands
        }

    # --- 4. ランダムに1手選択 ---
    move = random.choice(legal_moves)

    # --- 5. 実行 ---
    if move["place"] == "board":
        result = handle_player_move(
            board=b.grid,
            tegoma=gs.hands,
            player=player,
            selected_place="board",
            selected_pos=move["from"],
            to_pos=move["to"],
            high_memory=high_memory,
        )
    else:
        result = handle_player_move(
            board=b.grid,
            tegoma=gs.hands,
            player=player,
            selected_place="tegoma",
            selected_pos=move["from"],
            to_pos=move["to"],
            high_memory=high_memory,
        )

    # --- 6. 結果を返す ---
    # 勝敗が決していれば winner に 1 or 2 が入る
    return {
        "board_grid": result.get("board_grid", b.grid),
        "current_turn": 1 if player == 2 else 2,
        "winner": result.get("winner", None),
        "tegoma": result.get("tegoma", gs.hands),
        "high_memory": b.high_memory,
    }
