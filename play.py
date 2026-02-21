import sys
from logic import GameAgent

def print_board(board):
    print("\n")
    for i in range(0, 9, 3):
        # 盤面の値を表示。Noneの場合はインデックス番号を表示
        row = [board[j] if board[j] is not None else str(j) for j in range(i, i+3)]
        print(f" {row[0]} | {row[1]} | {row[2]} ")
        if i < 6:
            print("---+---+---")

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

def play_game():
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

        agent = GameAgent(mark=ai_mark)
        board = [None] * 9

        while True:
            print_board(board)
            winner = check_winner(board)

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
                        move = int(input(f"あなたの番 ({human_mark})。0-8の番号を入力してください: "))
                        if 0 <= move <= 8 and board[move] is None:
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
    play_game()
