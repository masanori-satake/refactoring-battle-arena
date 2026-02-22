import pytest
import os
import sys
from loader import get_agent_class

def get_all_agents():
    """テスト対象となるエージェントのディレクトリ一覧を取得します。"""
    agents = []
    for entry in os.scandir('.'):
        if entry.is_dir() and not entry.name.startswith('.') and entry.name not in ('tests', 'node_modules', '__pycache__'):
            if os.path.exists(os.path.join(entry.path, 'logic.py')) or \
               os.path.exists(os.path.join(entry.path, 'logic.js')):
                agents.append(entry.name)
    return sorted(agents)

# AGENT_DIR環境変数が指定されている場合はそのディレクトリのみ、
# 指定されていない場合は全エージェントをテスト対象とします。
agent_dir_env = os.environ.get('AGENT_DIR')
if agent_dir_env:
    test_agents = [agent_dir_env]
else:
    test_agents = get_all_agents()

@pytest.fixture(params=test_agents, ids=lambda x: f"agent={x}")
def agent_class(request):
    directory = request.param
    cls = get_agent_class(directory)
    if not cls:
        pytest.fail(f"ディレクトリ '{directory}' にエージェントが見つかりませんでした。")
    return cls

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
def test_action_scenarios(agent_class, board, expected, strategy, mark):
    # 特定のパターンで期待されるマスを選択するかテスト
    agent = agent_class(mark=mark)
    assert agent.get_action(board, strategy_type=strategy) == expected

def test_basic_move(agent_class):
    # 最低限、空いている場所のいずれかを選択する
    agent = agent_class(mark="O")
    board = [None] * 9
    move = agent.get_action(board)
    assert 0 <= move <= 8
