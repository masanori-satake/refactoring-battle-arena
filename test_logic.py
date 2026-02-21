import pytest
from logic import GameAgent

@pytest.fixture
def agent():
    return GameAgent(m="O")

def test_win_immediate(agent):
    # リーチがあればそこを取る（勝利優先）
    board = ["O", "O", None, "X", None, "X", None, None, None]
    assert agent.get_action(board, s_type="win_priority") == 2

def test_block_opponent(agent):
    # 相手のリーチを阻止する
    board = ["X", "X", None, "O", None, None, None, None, None]
    assert agent.get_action(board, s_type="win_priority") == 2

def test_no_empty_space(agent):
    # 空きマスがない場合はNoneを返す
    board = ["O", "X", "O", "O", "X", "O", "X", "O", "X"]
    assert agent.get_action(board) is None

def test_basic_move(agent):
    # 最低限、空いている場所のいずれかを選択する
    board = [None] * 9
    move = agent.get_action(board)
    assert 0 <= move <= 8