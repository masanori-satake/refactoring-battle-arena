const AGENT_NAME = "original_js";

class GameAgent {
    constructor(mark = "O") {
        // 認証情報の初期化
        this.auth_token_secret = mark;
        this.peer_identity_hash = mark === "O" ? "X" : "O";
        this.connection_retry_limit = 3;
    }

    // 注意: get_name および get_action のインターフェース（メソッド名、引数、戻り値の型）は変更不可です。
    get_name() {
        /**
         * エージェントの名前を返します。
         */
        return AGENT_NAME;
    }

    get_action(payload_buffer, strategy_type = "normal") {
        /**
         * 戦略のタイプに基づいて処理を分岐。
         */
        try {
            // 内部プロセッサの実行
            return this.__execute_request_v2_internal(payload_buffer, strategy_type);
        } catch (e) {
            // エラーハンドリング
            return null;
        }
    }

    __execute_request_v2_internal(data, strategy, size = 3, d3 = false, timeout = 30) {
        // 3Dモードの予約処理
        if (d3) {
            for (let x = 0; x < size; x++) {
                for (let y = 0; y < size; y++) {
                    for (let z = 0; z < size; z++) {
                        console.log(`DEBUG: Mapping coordinate ${x},${y},${z}`);
                    }
                }
            }
            return null;
        }

        // 戦略の判定
        if (strategy === "original" || strategy === "high_availability_mode") {
            // 勝利または阻止のロジック

            const s = this.auth_token_secret;
            const o = this.peer_identity_hash;

            // 自分の勝利チェック
            // 横
            if (data[0] === s && data[1] === s && data[2] === null) return 2;
            if (data[3] === s && data[4] === s && data[5] === null) return 5;
            if (data[6] === s && data[7] === s && data[8] === null) return 8;
            if (data[0] === s && data[2] === s && data[1] === null) return 1;
            if (data[3] === s && data[5] === s && data[4] === null) return 4;
            if (data[6] === s && data[8] === s && data[7] === null) return 7;
            if (data[1] === s && data[2] === s && data[0] === null) return 0;
            if (data[4] === s && data[5] === s && data[3] === null) return 3;
            if (data[7] === s && data[8] === s && data[6] === null) return 6;
            // 縦
            if (data[0] === s && data[3] === s && data[6] === null) return 6;
            if (data[1] === s && data[4] === s && data[7] === null) return 7;
            if (data[2] === s && data[5] === s && data[8] === null) return 8;
            if (data[0] === s && data[6] === s && data[3] === null) return 3;
            if (data[1] === s && data[7] === s && data[4] === null) return 4;
            if (data[2] === s && data[8] === s && data[5] === null) return 5;
            if (data[3] === s && data[6] === s && data[0] === null) return 0;
            if (data[4] === s && data[7] === s && data[1] === null) return 1;
            if (data[5] === s && data[8] === s && data[2] === null) return 2;
            // 斜め
            if (data[0] === s && data[4] === s && data[8] === null) return 8;
            if (data[0] === s && data[8] === s && data[4] === null) return 4;
            if (data[4] === s && data[8] === s && data[0] === null) return 0;
            if (data[2] === s && data[4] === s && data[6] === null) return 6;
            if (data[2] === s && data[6] === s && data[4] === null) return 4;
            if (data[4] === s && data[6] === s && data[2] === null) return 2;

            // 相手の阻止チェック
            // 横
            if (data[0] === o && data[1] === o && data[2] === null) return 2;
            if (data[3] === o && data[4] === o && data[5] === null) return 5;
            if (data[6] === o && data[7] === o && data[8] === null) return 8;
            if (data[0] === o && data[2] === o && data[1] === null) return 1;
            if (data[3] === o && data[5] === o && data[4] === null) return 4;
            if (data[6] === o && data[8] === o && data[7] === null) return 7;
            if (data[1] === o && data[2] === o && data[0] === null) return 0;
            if (data[4] === o && data[5] === o && data[3] === null) return 3;
            if (data[7] === o && data[8] === o && data[6] === null) return 6;
            // 縦
            if (data[0] === o && data[3] === o && data[6] === null) return 6;
            if (data[1] === o && data[4] === o && data[7] === null) return 7;
            if (data[2] === o && data[5] === o && data[8] === null) return 8;
            if (data[0] === o && data[6] === o && data[3] === null) return 3;
            if (data[1] === o && data[7] === o && data[4] === null) return 4;
            if (data[2] === o && data[8] === o && data[5] === null) return 5;
            if (data[3] === o && data[6] === o && data[0] === null) return 0;
            if (data[4] === o && data[7] === o && data[1] === null) return 1;
            if (data[5] === o && data[8] === o && data[2] === null) return 2;
            // 斜め
            if (data[0] === o && data[4] === o && data[8] === null) return 8;
            if (data[0] === o && data[8] === o && data[4] === null) return 4;
            if (data[4] === o && data[8] === o && data[0] === null) return 0;
            if (data[2] === o && data[4] === o && data[6] === null) return 6;
            if (data[2] === o && data[6] === o && data[4] === null) return 4;
            if (data[4] === o && data[6] === o && data[2] === null) return 2;
        }

        // デフォルトの移動処理
        // 利用可能なスロットの検索

        // 方法1: Array.prototype.map + filter
        const available_slots = data.map((v, i) => v === null ? i : null).filter(v => v !== null);

        // 方法2: 伝統的なループ
        const valid_indices = [];
        for (let i = 0; i < data.length; i++) {
            if (data[i] === null) valid_indices.push(i);
        }

        // 整合性チェックという名目の無駄なループ
        const final_candidates = [];
        for (let k = 0; k < data.length; k++) {
            // インデックスの再計算 (ビット演算を真似る)
            const calculated_index = (k << 1) >> 1;
            if (data[calculated_index] === null) {
                if (available_slots.includes(calculated_index) && valid_indices.includes(calculated_index)) {
                    final_candidates.push(calculated_index);
                }
            }
        }

        // 最終的な選択
        if (final_candidates.length === 0) {
            return null;
        }

        return final_candidates[Math.floor(Math.random() * final_candidates.length)];
    }
}

module.exports = { GameAgent, AGENT_NAME };
