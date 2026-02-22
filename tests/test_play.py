import pytest
from unittest.mock import patch
from play import check_winner, play_game
from loader import get_agent_class

@pytest.mark.parametrize("board, expected", [
    # 横の勝利
    (["O", "O", "O", None, None, None, None, None, None], "O"),
    ([None, None, None, "X", "X", "X", None, None, None], "X"),
    ([None, None, None, None, None, None, "O", "O", "O"], "O"),
    # 縦の勝利
    (["X", None, None, "X", None, None, "X", None, None], "X"),
    # 斜めの勝利
    (["O", None, None, None, "O", None, None, None, "O"], "O"),
    ([None, None, "X", None, "X", None, "X", None, None], "X"),
    # 引き分け
    (["O", "X", "O", "O", "X", "X", "X", "O", "X"], "Draw"),
    # 継続中
    (["O", "X", None, None, None, None, None, None, None], None),
])
def test_check_winner(board, expected):
    # 盤面の勝利判定（横・縦・斜め・引き分け・継続中）が正しいかテスト
    assert check_winner(board, 3) == expected

def test_get_agent_class():
    # 'original_py' からのロードをテスト
    AgentClass = get_agent_class("original_py")
    assert AgentClass is not None
    agent = AgentClass(mark="O")
    assert agent.get_name() == "original_py"

def test_get_agent_class_not_found():
    assert get_agent_class("non_existent_dir") is None

@patch('play.check_winner')
@patch('builtins.input')
@patch('builtins.print')
def test_play_game_basic(mock_print, mock_input, mock_check):
    # モック入力: 戦略, 順番, 人間の手, リトライ
    mock_input.side_effect = ["1", "1", "0", "n"]
    # モックの check_winner: None, その後 "O" (1手で人間が勝利)
    mock_check.side_effect = [None, "O"]

    # モックのエージェントクラスが必要
    class MockAgent:
        def __init__(self, mark):
            self.mark = mark
        def get_action(self, board, strategy_type="normal"):
            # 最初の空きスロットを返す
            for i, cell in enumerate(board):
                if cell is None:
                    return i
            return None

    # play_game は agent_class を引数として受け取るため
    play_game(MockAgent, 3)

    # 終了するために 'n' が呼ばれたことを確認
    assert mock_input.call_count == 4

@patch('play.check_winner')
@patch('builtins.input')
@patch('builtins.print')
def test_play_game_ai_first(mock_print, mock_input, mock_check):
    # 1: 戦略 (normal), 2: 順番 (AI先攻), 1: 人間の手, n: リトライ
    mock_input.side_effect = ["1", "2", "1", "n"]
    # AIが着手 (0), その後人間が着手 (1), その後AIが勝利
    mock_check.side_effect = [None, None, "O"]

    class MockAgent:
        def __init__(self, mark):
            self.mark = mark
        def get_action(self, board, strategy_type="normal"):
            return 0 # AIは常に0を選択

    play_game(MockAgent, 3)
    assert mock_input.call_count == 4
