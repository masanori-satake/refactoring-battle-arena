import sys
import argparse
import io

# 標準出力をUTF-8に設定（Windows環境での文字化け対策）
if isinstance(sys.stdout, io.TextIOWrapper) and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if isinstance(sys.stderr, io.TextIOWrapper) and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
from loader import get_agent_class

def print_board(board, size):
    print("\n")
    for r in range(size):
        row_cells = []
        for c in range(size):
            idx = r * size + c
            cell = board[idx] if board[idx] is not None else str(idx)
            row_cells.append(f"{cell:^3}")
        print(" | ".join(row_cells))
        if r < size - 1:
            print("-" * (size * 6 - 1))

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

def play_game(agent_class, size):
    while True:
        print("\n=== 三目並べ: 人間 vs AI ===")

        print("\nAIの戦略を選択してください:")
        print("1: デフォルト")
        print("2: オリジナル")
        strat_choice = input("選択 (1 or 2): ")
        strategy_type = "original" if strat_choice == "2" else "normal"

        print("\n先攻・後攻を選択してください:")
        print("1: 人間 (O)")
        print("2: AI (O)")
        order_choice = input("選択 (1 or 2): ")

        if order_choice == "2":
            human_mark = "X"
            ai_mark = "O"
            turn = "AI"
        else:
            human_mark = "O"
            ai_mark = "X"
            turn = "Human"

        agent = agent_class(mark=ai_mark)
        board = [None] * (size * size)

        while True:
            print_board(board, size)
            winner = check_winner(board, size)

            if winner:
                if winner == "Draw":
                    print("\n引き分けです！")
                else:
                    winner_name = "あなた" if winner == human_mark else "AI"
                    print(f"\n{winner_name} ({winner}) の勝ちです！")
                break

            if turn == "Human":
                while True:
                    try:
                        move = int(input(f"あなたの番 ({human_mark})。0-{size*size-1}の番号を入力してください: "))
                        if 0 <= move < size * size and board[move] is None:
                            board[move] = human_mark
                            turn = "AI"
                            break
                        else:
                            print("無効な手です。空いているマスの番号を入力してください。")
                    except ValueError:
                        print("数字を入力してください。")
            else:
                print(f"AIの番 ({ai_mark})...")
                # 選択された戦略を使用
                move = agent.get_action(board, strategy_type=strategy_type)
                if move is not None and board[move] is None:
                    board[move] = ai_mark
                    print(f"AIは {move} を選択しました。")
                    turn = "Human"
                else:
                    print("AIが有効な手を選択できませんでした。")
                    break

        retry = input("\nもう一度対戦しますか？ (y/n): ").lower()
        if retry != 'y':
            print("対戦を終了します。お疲れ様でした！")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='三目並べ: 人間 vs AI')
    parser.add_argument('--dir', type=str, default='original_py', help='エージェントのロジックが含まれるディレクトリ')
    parser.add_argument('--size', type=int, default=3, help='盤面のサイズ (N x N)')
    args = parser.parse_args()

    AgentClass = get_agent_class(args.dir)
    if not AgentClass:
        print(f"エラー: {args.dir} にエージェントが見つかりませんでした")
        sys.exit(1)
    play_game(AgentClass, args.size)
