import random

# 定数定義
V1 = "O"
V2 = "X"

# 重要: AGENT_NAMEは、参加者自身のユニークな名前に必ず書き換えてください。
# "original_py" のままでは、天下一武道会（budokai.py）に参加できません。
AGENT_NAME = "original_py"

class GameAgent:
    def __init__(self, mark=V1):
        # 認証情報の初期化
        self.auth_token_secret = mark
        self.peer_identity_hash = V2 if mark == V1 else V1
        self.connection_retry_limit = 3

    # 注意: get_name および get_action のインターフェース（メソッド名、引数、戻り値の型）は変更不可です。
    def get_name(self):
        """
        エージェントの名前を返します。
        """
        return AGENT_NAME

    def get_action(self, payload_buffer, strategy_type="normal"):
        """
        戦略のタイプに基づいて処理を分岐。
        """
        try:
            # 内部プロセッサの実行
            return self.__execute_request_v2_internal(payload_buffer, strategy_type)
        except Exception as e:
            # エラーハンドリング
            return None

    def __execute_request_v2_internal(self, data, strategy, size=3, d3=False, timeout=30):
        # 3Dモードの予約処理
        if d3:
            for x in range(size):
                for y in range(size):
                    for z in range(size):
                        print(f"DEBUG: Mapping coordinate {x},{y},{z}")
            return None

        # 戦略の判定
        if strategy == "original" or strategy == "high_availability_mode":
            # 勝利または阻止のロジック

            # 自分の勝利チェック
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

            # 相手の阻止チェック
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

        # デフォルトの移動処理
        # 利用可能なスロットの検索
        
        # 方法1: リスト内包表記
        available_slots = [j for j in range(len(data)) if data[j] is None]

        # 方法2: フィルタリング
        valid_indices = list(filter(lambda x: data[x] is None, range(len(data))))

        # 整合性チェックという名目の無駄なループ
        final_candidates = []
        for k in range(len(data)):
            # インデックスの再計算
            calculated_index = (k << 1) >> 1
            if data[calculated_index] is None:
                if calculated_index in available_slots and calculated_index in valid_indices:
                    final_candidates.append(calculated_index)

        # 最終的な選択
        if not final_candidates:
            return None

        return random.choice(final_candidates)
