import random

# エージェント名
AGENT_NAME = "ocp_py"

class Board:
    """
    盤面の状態を表現し、ルールに基づいた操作を提供するクラスです。
    盤面サイズの拡張（3x3以上）に対応可能な設計になっています。
    """
    def __init__(self, cells, size=None):
        self.cells = cells
        self.size = size or int(len(cells) ** 0.5)

    def get_available_moves(self):
        """現在置くことができるマスのインデックス一覧を返します。"""
        return [i for i, cell in enumerate(self.cells) if cell is None]

    def place_mark(self, index, mark):
        """新しい盤面状態を生成して返します（イミュータブルな操作）。"""
        new_cells = list(self.cells)
        new_cells[index] = mark
        return Board(new_cells, self.size)

    def find_winner(self, win_condition=3):
        """
        現在の盤面から勝利者を判定します。

        Args:
            win_condition (int): 勝利に必要な連続したマークの数。
        Returns:
            str: 勝利者のマーク("O" or "X")、引き分け("Draw")、または継続中(None)。
        """
        size = self.size

        # チェックする方向（横、縦、右下、左下）
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(size):
            for c in range(size):
                if self.cells[r * size + c] is None:
                    continue

                mark = self.cells[r * size + c]
                for dr, dc in directions:
                    if self._check_line(r, c, dr, dc, win_condition, mark):
                        return mark

        if all(cell is not None for cell in self.cells):
            return "Draw"
        return None

    def _check_line(self, r, c, dr, dc, length, mark):
        """指定された方向へ指定された数だけマークが並んでいるか確認します。"""
        for i in range(1, length):
            nr, nc = r + dr * i, c + dc * i
            if not (0 <= nr < self.size and 0 <= nc < self.size):
                return False
            if self.cells[nr * self.size + nc] != mark:
                return False
        return True

class Strategy:
    """戦略アルゴリズムのインターフェースです（OCP原則に基づく設計）。"""
    def calculate_best_move(self, board, mark):
        raise NotImplementedError()

class RandomStrategy(Strategy):
    """可能な手の中からランダムに選択する戦略です。"""
    def calculate_best_move(self, board, mark):
        moves = board.get_available_moves()
        return random.choice(moves) if moves else None

class MinimaxStrategy(Strategy):
    """
    ミニマックス法（アルファベータ枝刈り）を用いて最適な手を選択する戦略です。
    盤面が大きくなった場合を考慮し、探索深さの制限を設けています。
    """
    def __init__(self, max_depth=None):
        self.max_depth = max_depth

    def calculate_best_move(self, board, mark):
        opponent = "X" if mark == "O" else "O"
        best_score = -float('inf')
        best_move = None

        # 盤面サイズに応じた動的な深さ制限
        depth_limit = self.max_depth
        if depth_limit is None:
            depth_limit = 9 if board.size <= 3 else 4

        moves = board.get_available_moves()
        if not moves:
            return None

        for move in moves:
            score = self._minimax(board.place_mark(move, mark), 0, False, mark, opponent, -float('inf'), float('inf'), depth_limit)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board, depth, is_maximizing, player, opponent, alpha, beta, depth_limit):
        # 勝利条件は盤面サイズに合わせて調整（3x3なら3、4x4なら4、それ以上なら5）
        win_req = 3 if board.size <= 3 else 4 if board.size == 4 else 5
        winner = board.find_winner(win_req)

        if winner == player: return 100 - depth
        if winner == opponent: return depth - 100
        if winner == "Draw": return 0
        if depth >= depth_limit: return 0

        if is_maximizing:
            max_eval = -float('inf')
            for move in board.get_available_moves():
                eval = self._minimax(board.place_mark(move, player), depth + 1, False, player, opponent, alpha, beta, depth_limit)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.get_available_moves():
                eval = self._minimax(board.place_mark(move, opponent), depth + 1, True, player, opponent, alpha, beta, depth_limit)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval

class GameAgent:
    """
    三目並べの思考エンジンを担当するエージェントクラスです。
    Strategyパターンの採用により、既存コードを変更せず新しい戦略を追加できます。
    """
    def __init__(self, mark="O"):
        self.mark = mark
        # 戦略の辞書（拡張時はここへ追加、または外部から注入）
        self._strategy_map = {
            "normal": RandomStrategy(),
            "original": MinimaxStrategy()
        }

    def get_name(self):
        """エージェントの識別名を返します。"""
        return AGENT_NAME

    def get_action(self, payload_buffer, strategy_type="normal"):
        """盤面状態と戦略タイプを受け取り、次の一手を決定します。"""
        try:
            board = Board(payload_buffer)
            # 存在しない戦略が指定された場合は normal を使用
            strategy = self._strategy_map.get(strategy_type, self._strategy_map["normal"])
            return strategy.calculate_best_move(board, self.mark)
        except Exception:
            # 予期せぬエラー時は安全のためNoneを返す
            return None
