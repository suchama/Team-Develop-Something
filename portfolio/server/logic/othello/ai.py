# ai.py — Reversi AI (x, y) coordinate convention
import random
from typing import List, Tuple, Iterable, Optional
from .board import Board

Coord = Tuple[int, int]  # (x, y)
Grid = List[List[int]]   # 8x8, 0=empty, 1=black, 2=white

DIRECTIONS: List[Coord] = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1,  1),
]


class AI:
    def __init__(self, difficulty: str = "normal"):
        """
        difficulty: 'easy' | 'normal' | 'hard'
        """
        self.difficulty = difficulty
        # 位置評価（[y][x] で参照） — 角/優位点を高く
        self.position_weights: Grid = [
            [100, -10,   8,   6,   6,   8, -10, 100],
            [-10, -25,  -4,  -4,  -4,  -4, -25, -10],
            [  8,  -4,   6,   4,   4,   6,  -4,   8],
            [  6,  -4,   4,   0,   0,   4,  -4,   6],
            [  6,  -4,   4,   0,   0,   4,  -4,   6],
            [  8,  -4,   6,   4,   4,   6,  -4,   8],
            [-10, -25,  -4,  -4,  -4,  -4, -25, -10],
            [100, -10,   8,   6,   6,   8, -10, 100],
        ]

    # ============ Public API ============

    def get_move(self, board, player: int) -> Optional[Coord]:
        """
        いまの盤面から 1 手選ぶ。
        - board: Board 互換オブジェクト（少なくとも .grid と .get_valid(player) を持つ）
        - player: 1 or 2
        返り値: (x, y) または None（パス）
        """
        # board.get_valid は (x, y) のリスト/集合を返す想定
        b = Board()
        b.update_valid(1)
        b.update_valid(2)
        
        valid_moves: Iterable[Coord] = board.get_valid(player)
        valid_moves = list(valid_moves)
        print(f"AI valid moves : {valid_moves}")

        if not valid_moves:
            return None

        if self.difficulty == "easy":
            return random.choice(valid_moves)

        if self.difficulty == "normal":
            return self._choose_by_position(board.grid, valid_moves)

        # 'hard' またはその他 → ミニマックス（1手先 + 相手1手の簡易2-ply）
        return self._minimax_one_ply(board.grid, valid_moves, player)

    # ============ Difficulty helpers ============

    def _choose_by_position(self, grid: Grid, valid_moves: List[Coord]) -> Coord:
        """
        位置評価（position_weights[y][x]）で最大の手を選ぶ。
        """
        best_score = -float("inf")
        best_move: Coord = valid_moves[0]

        for (x, y) in valid_moves:
            score = self.position_weights[y][x]
            # 同点バラけ用の微小ノイズ
            score += random.uniform(0, 5)
            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move

    def _minimax_one_ply(self, grid: Grid, valid_moves: List[Coord], player: int) -> Coord:
        """
        簡易ミニマックス（深さ2：自手1手 + 相手1手）
        - 自手の各手を適用 → 相手のベストスコアを引いて評価
        - スコアは石数＋位置評価の線形和（簡易）
        """
        best_score = -float("inf")
        best_move: Optional[Coord] = None
        opponent = 3 - player

        for (x, y) in valid_moves:
            # 自分が (x,y) に置いた後の盤面
            g1 = self._simulate_place_and_flip(grid, x, y, player)

            # 相手の合法手を列挙
            opp_moves = self._compute_valid_moves(g1, opponent)
            if not opp_moves:
                # 相手に手が無ければこちら大幅有利（評価を高く）
                score = self._evaluate_grid(g1, player) + 50.0
            else:
                # 相手が最善を尽くしたときの最悪ケース（min）
                opp_best = -float("inf")
                for (ox, oy) in opp_moves:
                    g2 = self._simulate_place_and_flip(g1, ox, oy, opponent)
                    s = self._evaluate_grid(g2, player)
                    if s > opp_best:
                        opp_best = s
                # 相手のベストは自分にとってマイナス影響として見る
                score = opp_best

            # 同点バラけ
            score += random.uniform(0, 2)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        if best_move is None:
            best_move = random.choice(valid_moves)
        return best_move

    # ============ Core helpers (x, y で統一) ============

    def _simulate_place_and_flip(self, grid: Grid, x: int, y: int, player: int) -> Grid:
        """
        (x, y) に player が置いた場合の盤面を返す（反転込み）。
        ※ 実ボードには影響しない（純関数）
        """
        new_grid = [row[:] for row in grid]
        new_grid[y][x] = player
        opponent = 3 - player

        for dx, dy in DIRECTIONS:
            cx, cy = x + dx, y + dy
            to_flip: List[Coord] = []

            while 0 <= cx < 8 and 0 <= cy < 8 and new_grid[cy][cx] == opponent:
                to_flip.append((cx, cy))
                cx += dx
                cy += dy

            if 0 <= cx < 8 and 0 <= cy < 8 and new_grid[cy][cx] == player and to_flip:
                # はさめている → 反転を適用
                for fx, fy in to_flip:
                    new_grid[fy][fx] = player

        return new_grid

    def _compute_valid_moves(self, grid: Grid, player: int) -> List[Coord]:
        """
        盤面 grid における player の合法手を (x, y) のリストで返す。
        """
        opponent = 3 - player
        moves: List[Coord] = []

        for y in range(8):
            for x in range(8):
                if grid[y][x] != 0:
                    continue
                if self._is_valid_at(grid, x, y, player, opponent):
                    moves.append((x, y))
        return moves

    def _is_valid_at(self, grid: Grid, x: int, y: int, player: int, opponent: int) -> bool:
        """
        (x, y) が合法手か？（8方向のどこかで1枚以上はさんで自石で止まれるか）
        """
        for dx, dy in DIRECTIONS:
            cx, cy = x + dx, y + dy
            seen = False

            # 1枚以上 相手石を見つけるまで進む
            while 0 <= cx < 8 and 0 <= cy < 8 and grid[cy][cx] == opponent:
                seen = True
                cx += dx
                cy += dy

            # 境界内で、相手石を1枚以上見て、最後が自石なら合法
            if seen and 0 <= cx < 8 and 0 <= cy < 8 and grid[cy][cx] == player:
                return True
        return False

    def _evaluate_grid(self, grid: Grid, me: int) -> float:
        """
        盤面評価（石数＋位置重みの簡易合算）
        """
        opp = 3 - me
        my_cnt = 0
        opp_cnt = 0
        pos_score = 0.0

        for y in range(8):
            row = grid[y]
            for x in range(8):
                v = row[x]
                if v == me:
                    my_cnt += 1
                    pos_score += self.position_weights[y][x]
                elif v == opp:
                    opp_cnt += 1
                    pos_score -= self.position_weights[y][x]

        # 石数差を重みづけ、位置スコアと合わせる
        return (my_cnt - opp_cnt) * 1.0 + pos_score * 0.2
