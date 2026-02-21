const AGENT_NAME = "original_js";

class GameAgent {
    constructor(mark) {
        this.mark = mark;
        this.opp_mark = mark === "O" ? "X" : "O";
    }

    get_name() {
        return AGENT_NAME;
    }

    get_action(payload_buffer, strategy_type = "normal") {
        try {
            return this._execute_internal(payload_buffer, strategy_type);
        } catch (e) {
            return null;
        }
    }

    _execute_internal(data, strategy) {
        if (strategy === "original") {
            const lines = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],
                [0, 3, 6], [1, 4, 7], [2, 5, 8],
                [0, 4, 8], [2, 4, 6]
            ];

            // 自分の勝利チェック
            for (const line of lines) {
                const vals = line.map(i => data[i]);
                if (vals.filter(v => v === this.mark).length === 2 && vals.includes(null)) {
                    return line[vals.indexOf(null)];
                }
            }

            // 相手の阻止チェック
            for (const line of lines) {
                const vals = line.map(i => data[i]);
                if (vals.filter(v => v === this.opp_mark).length === 2 && vals.includes(null)) {
                    return line[vals.indexOf(null)];
                }
            }
        }

        const available = data.map((v, i) => v === null ? i : null).filter(v => v !== null);
        if (available.length === 0) return null;
        return available[Math.floor(Math.random() * available.length)];
    }
}

module.exports = { GameAgent, AGENT_NAME };
