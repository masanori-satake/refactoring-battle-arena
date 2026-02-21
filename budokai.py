import os
import sys
import argparse
from collections import defaultdict
from loader import get_agent_class

def check_winner(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # 横
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # 縦
        [0, 4, 8], [2, 4, 6]             # 斜め
    ]
    for line in lines:
        if board[line[0]] == board[line[1]] == board[line[2]] and board[line[0]] is not None:
            return board[line[0]]
    if all(cell is not None for cell in board):
        return "Draw"
    return None

def run_match(agent_o, agent_x, strategy_type):
    """
    agent_oが勝てば'O'を、agent_xが勝てば'X'を、引き分けなら'Draw'を返します。
    エージェントが例外を投げた場合は負けとなります。
    両方が投げた場合は引き分けとなります。
    """
    board = [None] * 9

    # すでにエラーが発生したかどうかを追跡する必要があります
    # しかし、ターン制では、最初にエラーを出した方が即座に負けます。

    turn = 'O'
    for _ in range(10): # 最大9手 + 1つの安全策
        winner = check_winner(board)
        if winner:
            return winner

        current_agent = agent_o if turn == 'O' else agent_x
        mark = turn

        try:
            move = current_agent.get_action(board[:], strategy_type=strategy_type)
            if move is None or not (0 <= move <= 8) or board[move] is not None:
                raise ValueError("Invalid move")
            board[move] = mark
        except Exception:
            # 現在のエージェントが失敗しました。もう一方のエージェントも同じ盤面で失敗するか確認します。
            other_agent = agent_x if turn == 'O' else agent_o
            try:
                other_move = other_agent.get_action(board[:], strategy_type=strategy_type)
                if other_move is None or not (0 <= other_move <= 8) or board[other_move] is not None:
                    return 'Draw' # 両方が失敗
                return 'X' if turn == 'O' else 'O' # 現在のエージェントのみが失敗
            except Exception:
                return 'Draw' # 両方が失敗

        turn = 'X' if turn == 'O' else 'O'

    return 'Draw'

def main():
    parser = argparse.ArgumentParser(description='天下一武道会: 三目並べトーナメント')
    parser.add_argument('--strategy', type=str, default='normal', help='使用する戦略タイプ (normal/original)')
    parser.add_argument('--count', type=int, default=10, help='各ターン（先攻/後攻）でプレイするゲーム数')
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

                # バリデーション: originalディレクトリ以外で 'original' という名前を名乗っている場合
                if name == 'original' and dir_name != 'original':
                    print(f"失格 {dir_name}: originalディレクトリ以外で 'original' という名前を使用しています。")
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
                res = run_match(a1, a2, args.strategy)
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
                res = run_match(a2, a1, args.strategy)
                if res == 'O': # a2 が勝利
                    results[dir2][dir1]['win'] += 1
                    results[dir1][dir2]['loss'] += 1
                elif res == 'X': # a1 が勝利
                    results[dir2][dir1]['loss'] += 1
                    results[dir1][dir2]['win'] += 1
                else:
                    results[dir2][dir1]['draw'] += 1
                    results[dir1][dir2]['draw'] += 1

    # 結果テーブル出力
    print(f"\nトーナメント結果 (戦略: {args.strategy})")
    header = f"{'Agent (Dir)':<30} | {'Win':<5} | {'Loss':<5} | {'Draw':<5}"
    print(header)
    print("-" * len(header))

    # エージェントを勝利数でソート
    sorted_dirs = sorted(dirs, key=lambda d: sum(results[d][opp]['win'] for opp in results[d]), reverse=True)

    for d in sorted_dirs:
        name = agent_names[d]
        total_win = sum(results[d][opp]['win'] for opp in results[d])
        total_loss = sum(results[d][opp]['loss'] for opp in results[d])
        total_draw = sum(results[d][opp]['draw'] for opp in results[d])
        print(f"{f'{name} ({d})':<30} | {total_win:<5} | {total_loss:<5} | {total_draw:<5}")

if __name__ == "__main__":
    main()
