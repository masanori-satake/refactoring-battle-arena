# 🚀 Refactoring Battle Arena

## ⚔️ バトルのルール
1. **テストを死守せよ**: `test_logic.py` は変更禁止。`pytest` を命綱にしてください。
2. **AI(ChatGPT等)は封印**: 自分の指で原則を書き込んでください。メッキは剥げます。

## ⚙️ 環境セットアップ

本プロジェクトでは Python と JavaScript の両方でエージェントを開発できます。

### Python で参加する場合
- Python 3.10 以上がインストールされていることを確認してください。
- 依存ライブラリのインストール:
  ```bash
  pip install -r requirements.txt
  ```

### JavaScript で参加する場合
- Python 3.10 以上に加え、**Node.js (v20以上推奨)** がインストールされていることを確認してください。
- Python の依存ライブラリも必要です（テストやツールの実行に使用します）:
  ```bash
  pip install -r requirements.txt
  ```

## 🧪 テストの実行方法
本プロジェクトでは `pytest` を使用して動作確認を行います。以下のコマンドでテストを実行できます。
```bash
# デフォルト (originalディレクトリ) のテスト
pytest test_logic.py

# Pythonエージェントのテスト
AGENT_DIR=participant_py pytest test_logic.py

# JavaScriptエージェントのテスト
AGENT_DIR=participant_js pytest test_logic.py
```
すべてのテストがパスすることを確認しながら進めてください。

### テストカバレッジの測定
テストがコードのどの部分をカバーしているかを確認するには、以下のコマンドを実行します。
```bash
pytest --cov=original test_logic.py
```

## 🎮 対戦ツールの実行方法
作成したエージェントと実際にターミナル上で対戦して動作を確認することができます。**このツールは Python (`logic.py`) と JavaScript (`logic.js`) のどちらのロジックでも共通して利用できます。**

```bash
# デフォルト (originalディレクトリ) のエージェントと対戦
python3 play.py

# 特定のディレクトリのエージェントと対戦する場合
python3 play.py --dir participant1
```
- **機能**:
  - 人間 vs AI の対戦（3x3 三目並べ）
  - 先攻・後攻の選択
  - 勝敗・引き分けの判定
  - 継続プレイの確認

## 🏆 天下一武道会（総当たり戦）
複数のディレクトリに存在するエージェント同士を戦わせるツールです。**Python 同士、JavaScript 同士だけでなく、Python 対 JavaScript の異種言語間対戦も可能です。**

```bash
python3 budokai.py --strategy original --count 10
```
- **オプション**:
  - `--strategy`: 使用する戦略（`normal` または `original`）を指定します。
  - `--count`: 各ペアで、先攻・後攻をそれぞれ何回ずつプレイするかを指定します（デフォルト10回、計20試合）。
- **ルール**:
  - `.` で始まる隠しディレクトリ以外のすべてのサブディレクトリから `logic.py` または `logic.js` を探します。
  - `original` 以外のディレクトリで `AGENT_NAME` が `"original"` のままの場合、そのエージェントは失格となります。
  - エージェントが実行中に例外を投げた場合、その試合は負けとなります（双方が投げた場合は引き分け）。

## 🚩 作業フロー（ブランチとPR）
1. **基準ブランチ**: 運営が指定するブランチ（例: `round_1st`）
2. **自分のフィールド(ベース)**: 基準ブランチから `(基準名)_(社員ID)` ブランチを作成。
3. **ミッション開始**: 自分のベースから Workブランチを切り、自分のベースに向けてマージするPRを作成してください。レビューアには主催者と仲間を招待しましょう！

---

## 📖 インターフェース仕様

JavaScript で参加する場合、ディレクトリ内に `logic.js` を作成してください。Python の場合は `logic.py` を作成します。

### Python (`logic.py`)
#### 定数
- `AGENT_NAME` (str): エージェントの識別名。※`original` は使用禁止。

#### メソッド
- `GameAgent.get_name()`: `AGENT_NAME` を返す。
- `GameAgent.get_action(payload_buffer, strategy_type="normal")`: 次の手（0-8）を返す。

### JavaScript (`logic.js`)
`module.exports` を使用して `GameAgent` クラスをエクスポートしてください。

#### 実装例 (`logic.js`)
```javascript
const AGENT_NAME = "my-js-agent";

class GameAgent {
    constructor(mark) {
        this.mark = mark; // "O" または "X"
    }

    get_name() {
        return AGENT_NAME;
    }

    get_action(payload_buffer, strategy_type = "normal") {
        // payload_buffer: 9要素のリスト (null, "O", "X")
        // strategy_type: "normal" または "original"
        // 戻り値: 0-8 の数値、または置ける場所がない場合は null

        // ここにロジックを記述
        return payload_buffer.indexOf(null);
    }
}

module.exports = { GameAgent };
```

### 共通仕様
#### `GameAgent.get_action(payload_buffer, strategy_type="normal")`
- **引数**:
- `payload_buffer` (list): 盤面の状態を表す 9 要素のリスト。
  - `None`: 空きマス
  - `"O"`: プレイヤーOのマーク
  - `"X"`: プレイヤーXのマーク
  - インデックスと盤面の対応は以下の通りです。
    | | | |
    | :---: | :---: | :---: |
    | 0 | 1 | 2 |
    | 3 | 4 | 5 |
    | 6 | 7 | 8 |
- `strategy_type` (str): 使用する戦略のタイプ。
  - `"normal"`: デフォルト
  - `"original"`: オリジナル

### 戻り値
- `int` または `None`: 次に置くマスのインデックス (0-8)。置ける場所がない場合は `None`。

---

## 🏆 二段階のミッション

### 【STEP 1】 ミニマム・サバイバル
3x3の三目並べで、次の手を選択するエージェントを実装してください。
- **基本仕様**:
  - 3x3の盤面（9要素のリスト）を受け取り、空いている場所（`None`）のインデックスを返す。
  - 自分がリーチ（あと1手で3つ並ぶ状態）の場合は、そのマスを優先的に選ぶ。
  - 相手がリーチの場合は、そのマスを阻止するように選ぶ。
  - 空きマスがない場合は `None` を返す。
- **課題**:
  - 基本仕様を満たしつつ、現状のコードをより読みやすく、メンテナンスしやすい形に自由に改善してください。

### 【STEP 2】 エキスパート・アップデート
エージェントに「性格（戦略）」の切り替え機能を追加します。
- **追加仕様**:
  - これまでの「オリジナル」戦略に加え、「角取り優先（空いていれば四隅を優先的に取る）」戦略を選択可能にしてください。
- **課題**:
  - **「既存のメインロジック（get_action等）を修正することなく」**、新しい戦略を追加できる設計を目指してください。