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
    Returns 'O' if agent_o wins, 'X' if agent_x wins, 'Draw' if draw.
    If an agent raises an exception, it loses.
    If both raise (not really possible in turn-based, but let's be careful), Draw.
    """
    board = [None] * 9

    # We need to track if they've already errored
    # But in turn-based, the first one to error loses immediately.

    turn = 'O'
    for _ in range(10): # Max 9 moves + 1 safety
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
            # Current agent failed. Check if the other agent also fails on the same board.
            other_agent = agent_x if turn == 'O' else agent_o
            try:
                other_move = other_agent.get_action(board[:], strategy_type=strategy_type)
                if other_move is None or not (0 <= other_move <= 8) or board[other_move] is not None:
                    return 'Draw' # Both failed
                return 'X' if turn == 'O' else 'O' # Only current failed
            except Exception:
                return 'Draw' # Both failed

        turn = 'X' if turn == 'O' else 'O'

    return 'Draw'

def main():
    parser = argparse.ArgumentParser(description='Tenkaichi Budokai: Tic-Tac-Toe Tournament')
    parser.add_argument('--strategy', type=str, default='normal', help='Strategy type to use (normal/original)')
    parser.add_argument('--count', type=int, default=10, help='Number of games to play for each turn (first/second)')
    args = parser.parse_args()

    # Find all agents
    agents_info = []
    for root, dirs, files in os.walk('.'):
        # Exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        dir_name = os.path.relpath(root, '.')
        if dir_name == '.': continue # Skip root directory

        AgentClass = get_agent_class(dir_name)
        if AgentClass:
            try:
                agent_instance = AgentClass(mark='O')
                name = agent_instance.get_name()

                # Validation: non-original dir claiming 'original' name
                if name == 'original' and dir_name != 'original':
                    print(f"Disqualifying {dir_name}: Claiming name 'original' outside original directory.")
                    continue

                agents_info.append({
                    'dir': dir_name,
                    'name': name,
                    'agent_class': AgentClass
                })
            except Exception as e:
                print(f"Error initializing agent from {dir_name}: {e}")

    if len(agents_info) < 2:
        print("Not enough agents found to run a tournament.")
        return

    print(f"Starting Tournament with strategy: {args.strategy}")
    print(f"Each pair plays {args.count} games as first and {args.count} games as second.")
    print("-" * 50)

    # results[agent_name][opponent_name] = {'win': 0, 'loss': 0, 'draw': 0}
    # Use dir as unique key in case names collide (though we should show names)
    results = defaultdict(lambda: defaultdict(lambda: {'win': 0, 'loss': 0, 'draw': 0}))

    agent_names = {a['dir']: a['name'] for a in agents_info}
    dirs = [a['dir'] for a in agents_info]

    for i in range(len(dirs)):
        for j in range(i + 1, len(dirs)):
            dir1 = dirs[i]
            dir2 = dirs[j]

            AgentClass1 = agents_info[i]['agent_class']
            AgentClass2 = agents_info[j]['agent_class']

            # Games where dir1 is O (first)
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

            # Games where dir2 is O (first)
            for _ in range(args.count):
                a1 = AgentClass1(mark='X')
                a2 = AgentClass2(mark='O')
                res = run_match(a2, a1, args.strategy)
                if res == 'O': # a2 wins
                    results[dir2][dir1]['win'] += 1
                    results[dir1][dir2]['loss'] += 1
                elif res == 'X': # a1 wins
                    results[dir2][dir1]['loss'] += 1
                    results[dir1][dir2]['win'] += 1
                else:
                    results[dir2][dir1]['draw'] += 1
                    results[dir1][dir2]['draw'] += 1

    # Output table
    print(f"\nTournament Result (Strategy: {args.strategy})")
    header = f"{'Agent (Dir)':<30} | {'Win':<5} | {'Loss':<5} | {'Draw':<5}"
    print(header)
    print("-" * len(header))

    # Sort agents by wins
    sorted_dirs = sorted(dirs, key=lambda d: sum(results[d][opp]['win'] for opp in results[d]), reverse=True)

    for d in sorted_dirs:
        name = agent_names[d]
        total_win = sum(results[d][opp]['win'] for opp in results[d])
        total_loss = sum(results[d][opp]['loss'] for opp in results[d])
        total_draw = sum(results[d][opp]['draw'] for opp in results[d])
        print(f"{f'{name} ({d})':<30} | {total_win:<5} | {total_loss:<5} | {total_draw:<5}")

if __name__ == "__main__":
    main()
