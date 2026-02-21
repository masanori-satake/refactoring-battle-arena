const { GameAgent } = require('../original_js/logic');

describe('GameAgent', () => {
    test('get_name returns original_js', () => {
        const agent = new GameAgent("O");
        expect(agent.get_name()).toBe("original_js");
    });

    const scenarios = [
        { board: ["O", "O", null, "X", null, "X", null, null, null], expected: 2, strategy: "original", mark: "O", desc: "自分の勝利チェック" },
        { board: ["X", "X", null, "O", null, null, null, null, null], expected: 2, strategy: "original", mark: "O", desc: "相手の阻止チェック" },
        { board: ["O", "X", "O", "O", "X", "O", "X", "O", "X"], expected: null, strategy: "normal", mark: "O", desc: "空きマスがない場合はnullを返す" },
        { board: ["O", null, "X", null, "O", "X", null, null, null], expected: 8, strategy: "original", mark: "O", desc: "斜めの勝利チェック" },
        { board: ["X", null, null, null, "X", null, null, null, null], expected: 8, strategy: "original", mark: "O", desc: "斜めの阻止チェック" },
        { board: ["O", "O", null, null, null, null, null, null, null], expected: 2, strategy: "original", mark: "X", desc: "エージェントがマークXの場合の阻止チェック" },
        { board: ["O", "X", "O", "O", "X", "O", "X", "O", null], expected: 8, strategy: "normal", mark: "O", desc: "すでに埋まっている場所は選ばない" },
    ];

    scenarios.forEach(({ board, expected, strategy, mark, desc }) => {
        test(desc, () => {
            const agent = new GameAgent(mark);
            expect(agent.get_action(board, strategy)).toBe(expected);
        });
    });

    test('basic move: selects an available slot', () => {
        const agent = new GameAgent("O");
        const board = Array(9).fill(null);
        const move = agent.get_action(board);
        expect(move).toBeGreaterThanOrEqual(0);
        expect(move).toBeLessThanOrEqual(8);
    });
});
