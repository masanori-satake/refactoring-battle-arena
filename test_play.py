import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from play import check_winner, play_game
from loader import get_agent_class

def test_check_winner():
    # Horizontal wins
    assert check_winner(["O", "O", "O", None, None, None, None, None, None]) == "O"
    assert check_winner([None, None, None, "X", "X", "X", None, None, None]) == "X"
    assert check_winner([None, None, None, None, None, None, "O", "O", "O"]) == "O"

    # Vertical wins
    assert check_winner(["X", None, None, "X", None, None, "X", None, None]) == "X"

    # Diagonal wins
    assert check_winner(["O", None, None, None, "O", None, None, None, "O"]) == "O"
    assert check_winner([None, None, "X", None, "X", None, "X", None, None]) == "X"

    # Draw
    assert check_winner(["O", "X", "O", "O", "X", "X", "X", "O", "X"]) == "Draw"

    # Ongoing
    assert check_winner(["O", "X", None, None, None, None, None, None, None]) is None

def test_get_agent_class():
    # Test loading from 'original'
    AgentClass = get_agent_class("original")
    assert AgentClass is not None
    agent = AgentClass(mark="O")
    assert agent.get_name() == "original"

def test_get_agent_class_not_found():
    assert get_agent_class("non_existent_dir") is None

@patch('play.check_winner')
@patch('builtins.input')
@patch('builtins.print')
def test_play_game_basic(mock_print, mock_input, mock_check):
    # Mock inputs: strategy, order, human move, retry
    mock_input.side_effect = ["1", "1", "0", "n"]
    # Mock check_winner: None, then "O" (Human wins after one move)
    mock_check.side_effect = [None, "O"]

    # We need a mock agent class
    class MockAgent:
        def __init__(self, mark):
            self.mark = mark
        def get_action(self, board, strategy_type="normal"):
            # Return first available slot
            for i, cell in enumerate(board):
                if cell is None:
                    return i
            return None

    # Since play_game takes agent_class as argument
    play_game(MockAgent)

    # Verify that 'n' was called to exit
    assert mock_input.call_count == 4

@patch('play.check_winner')
@patch('builtins.input')
@patch('builtins.print')
def test_play_game_ai_first(mock_print, mock_input, mock_check):
    # 1: strategy (normal), 2: order (AI first), 1: human move, n: retry
    mock_input.side_effect = ["1", "2", "1", "n"]
    # AI moves (0), then Human moves (1), then AI wins
    mock_check.side_effect = [None, None, "O"]

    class MockAgent:
        def __init__(self, mark):
            self.mark = mark
        def get_action(self, board, strategy_type="normal"):
            return 0 # AI always takes 0

    play_game(MockAgent)
    assert mock_input.call_count == 4
