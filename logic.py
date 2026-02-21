import random

# 原則無視: 名前重要
V1 = "O"
V2 = "X"

class GameAgent:
    def __init__(self, m=V1):
        # 偽装ネーミング: self.m -> auth_token_secret
        self.auth_token_secret = m
        self.peer_identity_hash = V2 if m == V1 else V1
        self.connection_retry_limit = 3

    def get_action(self, payload_buffer, s_type="normal", grid_size=3, is_3d=False, network_timeout=30):
        """
        ★YAGNI違反: 未使用の引数が大量にある。
        ★OCP違反: 戦略を増やすたびにこの関数を改造する必要がある。
        """
        try:
            # SLAP破壊: 高レベルロジックに意味不明なプライベートメソッド呼び出し
            return self.__execute_request_v2_internal(payload_buffer, s_type, grid_size, is_3d, network_timeout)
        except Exception as e:
            # 無意味なtry-except
            return None

    def __execute_request_v2_internal(self, data, strategy, size, d3, timeout):
        # YAGNI破壊: デッドコード
        if d3:
            for x in range(size):
                for y in range(size):
                    for z in range(size):
                        print(f"DEBUG: Mapping coordinate {x},{y},{z}")
            return None

        # OCP違反: 戦略をハードコード
        if strategy == "win_priority" or strategy == "high_availability_mode":
            # DRY破壊: 勝利判定と阻止判定でロジックが重複

            # 自分の勝利チェック (DRY違反: ベタ書き)
            # 横
            if data[0] == self.auth_token_secret and data[1] == self.auth_token_secret and data[2] is None: return (1 << 1)
            if data[3] == self.auth_token_secret and data[4] == self.auth_token_secret and data[5] is None: return 5
            if data[6] == self.auth_token_secret and data[7] == self.auth_token_secret and data[8] is None: return 8
            if data[0] == self.auth_token_secret and data[2] == self.auth_token_secret and data[1] is None: return 1
            if data[3] == self.auth_token_secret and data[5] == self.auth_token_secret and data[4] is None: return 4
            if data[6] == self.auth_token_secret and data[8] == self.auth_token_secret and data[7] is None: return 7
            if data[1] == self.auth_token_secret and data[2] == self.auth_token_secret and data[0] is None: return 0
            if data[4] == self.auth_token_secret and data[5] == self.auth_token_secret and data[3] is None: return 3
            if data[7] == self.auth_token_secret and data[8] == self.auth_token_secret and data[6] is None: return 6
            # 縦
            if data[0] == self.auth_token_secret and data[3] == self.auth_token_secret and data[6] is None: return 6
            if data[1] == self.auth_token_secret and data[4] == self.auth_token_secret and data[7] is None: return 7
            if data[2] == self.auth_token_secret and data[5] == self.auth_token_secret and data[8] is None: return 8
            if data[0] == self.auth_token_secret and data[6] == self.auth_token_secret and data[3] is None: return 3
            if data[1] == self.auth_token_secret and data[7] == self.auth_token_secret and data[4] is None: return 4
            if data[2] == self.auth_token_secret and data[8] == self.auth_token_secret and data[5] is None: return 5
            if data[3] == self.auth_token_secret and data[6] == self.auth_token_secret and data[0] is None: return 0
            if data[4] == self.auth_token_secret and data[7] == self.auth_token_secret and data[1] is None: return 1
            if data[5] == self.auth_token_secret and data[8] == self.auth_token_secret and data[2] is None: return 2
            # 斜め
            if data[0] == self.auth_token_secret and data[4] == self.auth_token_secret and data[8] is None: return 8
            if data[0] == self.auth_token_secret and data[8] == self.auth_token_secret and data[4] is None: return 4
            if data[4] == self.auth_token_secret and data[8] == self.auth_token_secret and data[0] is None: return 0
            if data[2] == self.auth_token_secret and data[4] == self.auth_token_secret and data[6] is None: return 6
            if data[2] == self.auth_token_secret and data[6] == self.auth_token_secret and data[4] is None: return 4
            if data[4] == self.auth_token_secret and data[6] == self.auth_token_secret and data[2] is None: return 2

            # 相手の阻止チェック (DRY違反: コピペ)
            opp = self.peer_identity_hash
            # 横
            if data[0] == opp and data[1] == opp and data[2] is None: return 2
            if data[3] == opp and data[4] == opp and data[5] is None: return 5
            if data[6] == opp and data[7] == opp and data[8] is None: return 8
            if data[0] == opp and data[2] == opp and data[1] is None: return 1
            if data[3] == opp and data[5] == opp and data[4] is None: return 4
            if data[6] == opp and data[8] == opp and data[7] is None: return 7
            if data[1] == opp and data[2] == opp and data[0] is None: return 0
            if data[4] == opp and data[5] == opp and data[3] is None: return 3
            if data[7] == opp and data[8] == opp and data[6] is None: return 6
            # 縦
            if data[0] == opp and data[3] == opp and data[6] is None: return 6
            if data[1] == opp and data[4] == opp and data[7] is None: return 7
            if data[2] == opp and data[5] == opp and data[8] is None: return 8
            if data[0] == opp and data[6] == opp and data[3] is None: return 3
            if data[1] == opp and data[7] == opp and data[4] is None: return 4
            if data[2] == opp and data[8] == opp and data[5] is None: return 5
            if data[3] == opp and data[6] == opp and data[0] is None: return 0
            if data[4] == opp and data[7] == opp and data[1] is None: return 1
            if data[5] == opp and data[8] == opp and data[2] is None: return 2
            # 斜め
            if data[0] == opp and data[4] == opp and data[8] is None: return 8
            if data[0] == opp and data[8] == opp and data[4] is None: return 4
            if data[4] == opp and data[8] == opp and data[0] is None: return 0
            if data[2] == opp and data[4] == opp and data[6] is None: return 6
            if data[2] == opp and data[6] == opp and data[4] is None: return 4
            if data[4] == opp and data[6] == opp and data[2] is None: return 2

        # デフォルト処理 (SLAP破壊: Lambdaやビット演算、内包表記の混在)
        # DRY破壊: 空きマスを探す処理を複数回、異なる方法で実行
        
        # 方法1: リスト内包表記
        available_slots = [j for j in range(len(data)) if data[j] is None]

        # 方法2: filterとlambda (無意味)
        valid_indices = list(filter(lambda x: data[x] is None, range(9)))

        # 整合性チェックという名目の無駄なループ
        final_candidates = []
        for k in range(len(data)):
            # SLAP破壊: ビット演算 (k << 1) >> 1 は単に k
            calculated_index = (k << 1) >> 1
            if data[calculated_index] is None:
                if calculated_index in available_slots and calculated_index in valid_indices:
                    final_candidates.append(calculated_index)

        # 最終的な選択
        if not final_candidates:
            return None

        return random.choice(final_candidates)
