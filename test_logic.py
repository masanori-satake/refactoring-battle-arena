import pytest
import os
import sys
from loader import get_agent_class

def load_game_agent():
    directory = os.environ.get('AGENT_DIR', 'original')
    agent_class = get_agent_class(directory)
    if not agent_class:
        print(f"Error: No agent found in {directory}")
        sys.exit(1)
    return agent_class

GameAgent = load_game_agent()

@pytest.mark.parametrize("board, expected, strategy, mark", [
    # 自分の勝利チェック
    (["O", "O", None, "X", None, "X", None, None, None], 2, "original", "O"),
    # 相手の阻止チェック
    (["X", "X", None, "O", None, None, None, None, None], 2, "original", "O"),
    # 空きマスがない場合はNoneを返す
    (["O", "X", "O", "O", "X", "O", "X", "O", "X"], None, "normal", "O"),
    # 斜めの勝利チェック
    (["O", None, "X", None, "O", "X", None, None, None], 8, "original", "O"),
    # 斜めの阻止チェック
    (["X", None, None, None, "X", None, None, None, None], 8, "original", "O"),
    # エージェントがマークXの場合の阻止チェック
    (["O", "O", None, None, None, None, None, None, None], 2, "original", "X"),
    # すでに埋まっている場所は選ばない
    (["O", "X", "O", "O", "X", "O", "X", "O", None], 8, "normal", "O"),
])
def test_action_scenarios(board, expected, strategy, mark):
    # 特定のパターンで期待されるマスを選択するかテスト
    agent = GameAgent(mark=mark)
    assert agent.get_action(board, strategy_type=strategy) == expected

def test_basic_move():
    # 最低限、空いている場所のいずれかを選択する
    agent = GameAgent(mark="O")
    board = [None] * 9
    move = agent.get_action(board)
    assert 0 <= move <= 8