import os
import sys
import argparse

# 標準出力をUTF-8に設定（Windows環境での文字化け対策）
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
from collections import defaultdict
from loader import get_agent_class

def check_winner(board, size):
    win_req = 3 if size <= 3 else 4 if size == 4 else 5

    # 横
    for r in range(size):
        for c in range(size - win_req + 1):
            window = [board[r * size + c + i] for i in range(win_req)]
            if window[0] is not None and all(x == window[0] for x in window):
                return window[0]
    # 縦
    for c in range(size):
        for r in range(size - win_req + 1):
            window = [board[(r + i) * size + c] for i in range(win_req)]
            if window[0] is not None and all(x == window[0] for x in window):
                return window[0]
    # 斜め
    for r in range(size - win_req + 1):
        for c in range(size - win_req + 1):
            # 右下
            window = [board[(r + i) * size + (c + i)] for i in range(win_req)]
            if window[0] is not None and all(x == window[0] for x in window):
                return window[0]
            # 左下
            window = [board[(r + i) * size + (c + win_req - 1 - i)] for i in range(win_req)]
            if window[0] is not None and all(x == window[0] for x in window):
                return window[0]

    if all(cell is not None for cell in board):
        return "Draw"
    return None

def run_match(agent_o, agent_x, strategy_type, size):
    """
    agent_oが勝てば'O'を、agent_xが勝てば'X'を、引き分けなら'Draw'を返します。
    エージェントが例外を投げた場合は負けとなります。
    両方が投げた場合は引き分けとなります。
    """
    board = [None] * (size * size)

    turn = 'O'
    for _ in range(size * size + 1):
        winner = check_winner(board, size)
        if winner:
            return winner

        current_agent = agent_o if turn == 'O' else agent_x
        mark = turn

        try:
            move = current_agent.get_action(board[:], strategy_type=strategy_type)
            if move is None or not (0 <= move < size * size) or board[move] is not None:
                raise ValueError("Invalid move")
            board[move] = mark
        except Exception as e:
            # 現在のエージェントが失敗しました。もう一方のエージェントも同じ盤面で失敗するか確認します。
            # エラー内容を表示（特にJSプロセスの異常終了などを検知するため）
            if not isinstance(e, ValueError):
                print(f"警告: エージェント {turn} で予期せぬエラーが発生しました: {e}", file=sys.stderr)

            other_agent = agent_x if turn == 'O' else agent_o
            try:
                other_move = other_agent.get_action(board[:], strategy_type=strategy_type)
                if other_move is None or not (0 <= other_move < size * size) or board[other_move] is not None:
                    return 'Draw' # 両方が失敗
                return 'X' if turn == 'O' else 'O' # 現在のエージェントのみが失敗
            except Exception:
                return 'Draw' # 両方が失敗

        turn = 'X' if turn == 'O' else 'O'

    return 'Draw'

def main():
    parser = argparse.ArgumentParser(description='天下一武道会: 三目並べトーナメント')
    parser.add_argument('--strategy', type=str, default='normal', help='使用する戦略タイプ (normal/original)')
    parser.add_argument('--count', type=int, default=50, help='各ターン（先攻/後攻）でプレイするゲーム数')
    parser.add_argument('--size', type=int, default=3, help='盤面のサイズ (N x N)')
    args = parser.parse_args()

    # 全エージェントを検索
    agents_info = []
    for root, dirs, files in os.walk('.'):
        # 隠しディレクトリを除外
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        dir_name = os.path.relpath(root, '.')
        if dir_name == '.': continue # ルートディレクトリをスキップ

        AgentClass = get_agent_class(dir_name)
        if AgentClass:
            try:
                agent_instance = AgentClass(mark='O')
                name = agent_instance.get_name()

                # バリデーション: original_py/original_jsディレクトリ以外で 'original_py/original_js' という名前を名乗っている場合
                if (name == 'original_py' and dir_name != 'original_py') or (name == 'original_js' and dir_name != 'original_js'):
                    print(f"失格 {dir_name}: original_py/original_jsディレクトリ以外で '{name}' という名前を使用しています。")
                    continue

                agents_info.append({
                    'dir': dir_name,
                    'name': name,
                    'agent_class': AgentClass
                })
            except Exception as e:
                print(f"エージェントの初期化エラー {dir_name}: {e}")

    if len(agents_info) < 2:
        print("トーナメントを開催するのに必要なエージェントが見つかりませんでした。")
        return

    print(f"トーナメント開始 戦略: {args.strategy}")
    print(f"各ペアは先攻として {args.count} 回、後攻として {args.count} 回プレイします。")
    print("-" * 50)

    # results[agent_name][opponent_name] = {'win': 0, 'loss': 0, 'draw': 0}
    # 名前が衝突した場合に備えて、一意のキーとしてディレクトリ名を使用します（ただし、名前は表示します）
    results = defaultdict(lambda: defaultdict(lambda: {'win': 0, 'loss': 0, 'draw': 0}))

    agent_names = {a['dir']: a['name'] for a in agents_info}
    dirs = [a['dir'] for a in agents_info]

    for i in range(len(dirs)):
        for j in range(i + 1, len(dirs)):
            dir1 = dirs[i]
            dir2 = dirs[j]

            AgentClass1 = agents_info[i]['agent_class']
            AgentClass2 = agents_info[j]['agent_class']

            # dir1 が O (先攻) のゲーム
            for _ in range(args.count):
                a1 = AgentClass1(mark='O')
                a2 = AgentClass2(mark='X')
                res = run_match(a1, a2, args.strategy, args.size)
                if res == 'O':
                    results[dir1][dir2]['win'] += 1
                    results[dir2][dir1]['loss'] += 1
                elif res == 'X':
                    results[dir1][dir2]['loss'] += 1
                    results[dir2][dir1]['win'] += 1
                else:
                    results[dir1][dir2]['draw'] += 1
                    results[dir2][dir1]['draw'] += 1

            # dir2 が O (先攻) のゲーム
            for _ in range(args.count):
                a1 = AgentClass1(mark='X')
                a2 = AgentClass2(mark='O')
                res = run_match(a2, a1, args.strategy, args.size)
                if res == 'O': # a2 が勝利
                    results[dir2][dir1]['win'] += 1
                    results[dir1][dir2]['loss'] += 1
                elif res == 'X': # a1 が勝利
                    results[dir2][dir1]['loss'] += 1
                    results[dir1][dir2]['win'] += 1
                else:
                    results[dir2][dir1]['draw'] += 1
                    results[dir1][dir2]['draw'] += 1

    # マッチ結果の集計（統計的有意差を考慮）
    match_results = defaultdict(lambda: {'win': 0, 'loss': 0, 'draw': 0})
    for i in range(len(dirs)):
        for j in range(i + 1, len(dirs)):
            dir1 = dirs[i]
            dir2 = dirs[j]
            w1 = results[dir1][dir2]['win']
            w2 = results[dir1][dir2]['loss']

            # 有意差判定のロジック: |w1 - w2| > 1.96 * sqrt(w1 + w2)
            # w1 + w2 は決着がついたゲーム数
            decisive_games = w1 + w2
            if decisive_games > 0 and abs(w1 - w2) > 1.96 * (decisive_games**0.5):
                if w1 > w2:
                    match_results[dir1]['win'] += 1
                    match_results[dir2]['loss'] += 1
                else:
                    match_results[dir1]['loss'] += 1
                    match_results[dir2]['win'] += 1
            else:
                match_results[dir1]['draw'] += 1
                match_results[dir2]['draw'] += 1

    # ポイント計算
    agent_points = {}
    for d in dirs:
        agent_points[d] = match_results[d]['win'] * 3 + match_results[d]['draw'] * 1

    # 順位計算 (3つ以上のエージェントがいる場合のみ)
    is_tournament = len(dirs) >= 3
    ranks = {}
    if is_tournament:
        max_p = max(agent_points.values()) if agent_points else 0
        for d in dirs:
            if agent_points[d] == max_p:
                ranks[d] = 1
            else:
                # 自分以上のポイントを持つチームの総数 (同着の場合はそのグループの最下位順位)
                ranks[d] = sum(1 for other_d in dirs if agent_points[other_d] >= agent_points[d])

    # 結果テーブル出力
    print(f"\nトーナメント結果 (戦略: {args.strategy})")
    print("※勝敗は統計的有意差（p < 0.05, 二項検定近似）に基づいて判定されています。")

    if is_tournament:
        print("※順位点: 勝利 3点 / 引き分け 1点 / 敗北 0点")
        header = f"{'Rank':<5} | {'Agent (Dir)':<30} | {'Pts':<5} | {'Match Win':<10} | {'Match Loss':<10} | {'Match Draw':<10}"
    else:
        header = f"{'Agent (Dir)':<30} | {'Match Win':<10} | {'Match Loss':<10} | {'Match Draw':<10}"

    print(header)
    print("-" * len(header))

    # エージェントをポイントでソート（同点の場合は勝利数、さらに同じならディレクトリ名で安定化）
    sorted_dirs = sorted(dirs, key=lambda d: (agent_points[d], match_results[d]['win'], d), reverse=True)

    for d in sorted_dirs:
        name = agent_names[d]
        mw = match_results[d]['win']
        ml = match_results[d]['loss']
        md = match_results[d]['draw']
        pts = agent_points[d]
        if is_tournament:
            rank = ranks[d]
            print(f"{rank:<5} | {f'{name} ({d})':<30} | {pts:<5} | {mw:<10} | {ml:<10} | {md:<10}")
        else:
            print(f"{f'{name} ({d})':<30} | {mw:<10} | {ml:<10} | {md:<10}")

if __name__ == "__main__":
    main()
