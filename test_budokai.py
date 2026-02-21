import pytest
import os
import shutil
from budokai import check_winner, run_match, load_game_agent, main
from unittest.mock import patch, MagicMock

def test_check_winner_budokai():
    assert check_winner(["O", "O", "O", None, None, None, None, None, None]) == "O"
    assert check_winner(["O", "X", "O", "O", "X", "X", "X", "O", "X"]) == "Draw"
    assert check_winner([None] * 9) is None

def test_run_match_normal():
    class DummyAgent:
        def __init__(self, mark):
            self.mark = mark
        def get_action(self, board, strategy_type="normal"):
            return board.index(None)

    a1 = DummyAgent("O")
    a2 = DummyAgent("X")
    # This will lead to a predictable sequence
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

    # ErrorAgent (O) fails immediately.
    # run_match will check if NormalAgent (X) also fails on the same board.
    # NormalAgent won't fail, so X wins.
    res = run_match(ErrorAgent("O"), NormalAgent("X"), "normal")
    assert res == "X"

    # Both fail
    res = run_match(ErrorAgent("O"), ErrorAgent("X"), "normal")
    assert res == "Draw"

def test_load_game_agent_budokai(tmp_path):
    d = tmp_path / "test_agent"
    d.mkdir()
    (d / "logic.py").write_text("class GameAgent: pass")

    module = load_game_agent(str(d))
    assert module is not None
    assert hasattr(module, "GameAgent")

def test_load_game_agent_not_found_budokai():
    assert load_game_agent("non_existent_dir") is None

@patch('sys.argv', ['budokai.py', '--count', '1'])
@patch('builtins.print')
def test_main_tournament(mock_print, tmp_path, monkeypatch):
    # Create two agent directories
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

    # Mock 'original' directory to exist or just run in tmp_path
    monkeypatch.chdir(tmp_path)

    main()

    # Verify print was called (results table)
    # The exact output depends on match results, but it should contain agent names
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
        assert "Disqualifying imposter" in all_output
