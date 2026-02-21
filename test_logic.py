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

@pytest.fixture
def agent():
    return GameAgent(mark="O")

def test_win_immediate(agent):
    # 特定のパターンで期待されるマスを選択する（オリジナル戦略）
    board = ["O", "O", None, "X", None, "X", None, None, None]
    assert agent.get_action(board, strategy_type="original") == 2

def test_block_opponent(agent):
    # 特定のパターンで期待されるマスを選択する（オリジナル戦略）
    board = ["X", "X", None, "O", None, None, None, None, None]
    assert agent.get_action(board, strategy_type="original") == 2

def test_no_empty_space(agent):
    # 空きマスがない場合はNoneを返す
    board = ["O", "X", "O", "O", "X", "O", "X", "O", "X"]
    assert agent.get_action(board) is None

def test_basic_move(agent):
    # 最低限、空いている場所のいずれかを選択する
    board = [None] * 9
    move = agent.get_action(board)
    assert 0 <= move <= 8

def test_win_diagonal(agent):
    # 特定のパターンで期待されるマスを選択する（オリジナル戦略）
    board = ["O", None, "X", None, "O", "X", None, None, None]
    assert agent.get_action(board, strategy_type="original") == 8

def test_block_diagonal(agent):
    # 特定のパターンで期待されるマスを選択する（オリジナル戦略）
    board = ["X", None, None, None, "X", None, None, None, None]
    assert agent.get_action(board, strategy_type="original") == 8

def test_agent_as_x():
    # エージェントがマークXの場合
    agent_x = GameAgent(mark="X")
    board = ["O", "O", None, None, None, None, None, None, None]
    assert agent_x.get_action(board, strategy_type="original") == 2

def test_valid_move_only(agent):
    # 既に埋まっている場所は選ばない
    board = ["O", "X", "O", "O", "X", "O", "X", "O", None]
    assert agent.get_action(board) == 8