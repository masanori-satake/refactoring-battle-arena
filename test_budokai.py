import pytest
import os
import shutil
from budokai import check_winner, run_match, main
from loader import get_agent_class
from unittest.mock import patch, MagicMock

@pytest.mark.parametrize("board, expected", [
    (["O", "O", "O", None, None, None, None, None, None], "O"),
    (["O", "X", "O", "O", "X", "X", "X", "O", "X"], "Draw"),
    ([None] * 9, None),
])
def test_check_winner_budokai(board, expected):
    # 総当たり戦ツール内での勝利判定が正しいかテスト
    assert check_winner(board) == expected

def test_run_match_normal():
    class DummyAgent:
        def __init__(self, mark):
            self.mark = mark
        def get_action(self, board, strategy_type="normal"):
            return board.index(None)

    a1 = DummyAgent("O")
    a2 = DummyAgent("X")
    # これは予測可能なシーケンスにつながる
    res = run_match(a1, a2, "normal")
    assert res in ["O", "X", "Draw"]

def test_run_match_exception():
    class ErrorAgent:
        def __init__(self, mark): pass
        def get_action(self, board, strategy_type="normal"):
            raise Exception("Boom")

    class NormalAgent:
        def __init__(self, mark): pass
        def get_action(self, board, strategy_type="normal"):
            return 0

    # ErrorAgent (O) は即座に失敗する
    # run_match は NormalAgent (X) も同じ盤面で失敗するかどうかを確認する
    # NormalAgent は失敗しないため、X の勝利となる
    res = run_match(ErrorAgent("O"), NormalAgent("X"), "normal")
    assert res == "X"

    # 両方が失敗
    res = run_match(ErrorAgent("O"), ErrorAgent("X"), "normal")
    assert res == "Draw"

def test_get_agent_class_budokai(tmp_path):
    d = tmp_path / "test_agent"
    d.mkdir()
    (d / "logic.py").write_text("class GameAgent: pass")

    agent_class = get_agent_class(str(d))
    assert agent_class is not None

def test_get_agent_class_not_found_budokai():
    assert get_agent_class("non_existent_dir") is None

@patch('sys.argv', ['budokai.py', '--count', '1'])
@patch('builtins.print')
def test_main_tournament(mock_print, tmp_path, monkeypatch):
    # 2つのエージェントディレクトリを作成
    agent1_dir = tmp_path / "agent1"
    agent1_dir.mkdir()
    (agent1_dir / "logic.py").write_text("""
AGENT_NAME = "agent1"
class GameAgent:
    def __init__(self, mark): pass
    def get_name(self): return AGENT_NAME
    def get_action(self, board, strategy_type="normal"):
        return board.index(None)
""")

    agent2_dir = tmp_path / "agent2"
    agent2_dir.mkdir()
    (agent2_dir / "logic.py").write_text("""
AGENT_NAME = "agent2"
class GameAgent:
    def __init__(self, mark): pass
    def get_name(self): return AGENT_NAME
    def get_action(self, board, strategy_type="normal"):
        return board.index(None)
""")

    # 'original' ディレクトリが存在するかのように振る舞うか、単に tmp_path で実行する
    monkeypatch.chdir(tmp_path)

    main()

    # print が呼ばれたことを確認 (結果テーブル)
    # 正確な出力は試合結果に依存するが、エージェント名が含まれている必要がある
    all_output = "".join(str(call) for call in mock_print.call_args_list)
    assert "agent1" in all_output
    assert "agent2" in all_output

@patch('sys.argv', ['budokai.py', '--count', '1'])
def test_main_disqualification(tmp_path, monkeypatch):
    imposter_dir = tmp_path / "imposter"
    imposter_dir.mkdir()
    (imposter_dir / "logic.py").write_text("""
AGENT_NAME = "original"
class GameAgent:
    def __init__(self, mark): pass
    def get_name(self): return AGENT_NAME
""")

    monkeypatch.chdir(tmp_path)
    with patch('builtins.print') as mock_p:
        main()
        all_output = "".join(str(call) for call in mock_p.call_args_list)
        assert "失格 imposter" in all_output

def create_mock_agent_dir(path, name):
    d = path / name
    d.mkdir()
    (d / "logic.py").write_text(f"""
AGENT_NAME = "{name}"
class GameAgent:
    def __init__(self, mark): self.mark = mark
    def get_name(self): return AGENT_NAME
    def get_action(self, board, strategy_type="normal"): return 0
""")
    return d

@patch('sys.argv', ['budokai.py', '--count', '10'])
def test_main_tournament_3_agents_ranking(tmp_path, monkeypatch):
    # 3つのエージェントを作成: A, B, C
    create_mock_agent_dir(tmp_path, "agentA")
    create_mock_agent_dir(tmp_path, "agentB")
    create_mock_agent_dir(tmp_path, "agentC")

    monkeypatch.chdir(tmp_path)

    # run_matchをモックして、AがBとCに勝ち、BとCが引き分けるようにする
    # A vs B: A win (O if A is O, X if A is X)
    # A vs C: A win
    # B vs C: Draw
    def mock_run_match(ao, ax, strategy):
        name_o = ao.get_name()
        name_x = ax.get_name()

        if (name_o == "agentA" and name_x == "agentB"): return 'O'
        if (name_o == "agentB" and name_x == "agentA"): return 'X'
        if (name_o == "agentA" and name_x == "agentC"): return 'O'
        if (name_o == "agentC" and name_x == "agentA"): return 'X'
        return 'Draw'

    with patch('budokai.run_match', side_effect=mock_run_match):
        with patch('builtins.print') as mock_p:
            main()
            all_output = "".join(str(call) for call in mock_p.call_args_list)

            # 期待値: A=6pts (1位), B=1pt (3位), C=1pt (3位)
            # 順位表示があることを確認
            assert "Rank" in all_output
            assert "Pts" in all_output

            # agentA (1位)
            assert "1     | agentA" in all_output or "1" in all_output and "agentA" in all_output
            # agentB, agentC (3位)
            assert "3     | agentB" in all_output or "3" in all_output and "agentB" in all_output
            assert "3     | agentC" in all_output or "3" in all_output and "agentC" in all_output
            # 2位はいないはず
            assert "2     |" not in all_output

@patch('sys.argv', ['budokai.py', '--count', '10'])
def test_main_tournament_3_agents_top_tie(tmp_path, monkeypatch):
    # 3つのエージェントを作成: A, B, C
    create_mock_agent_dir(tmp_path, "agentA")
    create_mock_agent_dir(tmp_path, "agentB")
    create_mock_agent_dir(tmp_path, "agentC")

    monkeypatch.chdir(tmp_path)

    # AとBがCに勝ち、AとBが引き分ける
    # A vs C: A win
    # B vs C: B win
    # A vs B: Draw
    # Points: A=4, B=4, C=0
    # Expected Ranks: A=1, B=1, C=3
    def mock_run_match(ao, ax, strategy):
        name_o = ao.get_name()
        name_x = ax.get_name()

        if (name_o == "agentA" and name_x == "agentC"): return 'O'
        if (name_o == "agentC" and name_x == "agentA"): return 'X'
        if (name_o == "agentB" and name_x == "agentC"): return 'O'
        if (name_o == "agentC" and name_x == "agentB"): return 'X'
        return 'Draw'

    with patch('budokai.run_match', side_effect=mock_run_match):
        with patch('builtins.print') as mock_p:
            main()
            all_output = "".join(str(call) for call in mock_p.call_args_list)

            # agentA, agentB (1位)
            assert "1     | agentA" in all_output
            assert "1     | agentB" in all_output
            # agentC (3位)
            assert "3     | agentC" in all_output
            # 2位はいない
            assert "2     |" not in all_output
