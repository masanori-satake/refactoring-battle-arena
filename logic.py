import random

# 原則無視: 名前重要
V1 = "O"
V2 = "X"

class GameAgent:
    def __init__(self, m=V1):
        self.m = m

    def get_action(self, b, s_type="normal", grid_size=3, is_3d=False, network_timeout=30):
        """
        ★YAGNI違反: 未使用の引数（grid_size, is_3d等）が蔓延。
        ★OCP違反: 戦略を増やすたびにこの関数を改造する必要がある。
        """
        if is_3d:
            pass # 未来のための予約（YAGNI違反）

        # 勝利優先戦略
        if s_type == "win_priority":
            # 横の判定（DRY違反：コピペの山）
            if b[0] == self.m and b[1] == self.m and b[2] is None: return 2
            if b[3] == self.m and b[4] == self.m and b[5] is None: return 5
            if b[6] == self.m and b[7] == self.m and b[8] is None: return 8
            # ... (縦・斜めも同様に続く)
        
        # デフォルトはランダム（SLAP違反：低レベルなループ処理が混在）
        res = []
        for i in range(len(b)):
            if b[i] is None:
                res.append(i)
        return random.choice(res) if res else None