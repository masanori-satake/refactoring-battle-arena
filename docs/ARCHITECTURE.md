# 🏗 ポリグロット・アーキテクチャ・ガイド

本プロジェクトでは、Python と JavaScript という異なる言語で書かれたエージェントを、あたかも同じ言語で書かれているかのように透過的に扱う仕組み(ポリグロット構成)を導入しています。

このドキュメントでは、その仕組みの裏側を、図解を交えて詳しく解説します。

既存システムで異なる言語での拡張をサポートしたい、あるいは異なる言語間の連携にトライしたい皆さんにとって、有用な情報かと思います。

---

## 🌍 全体像

全体の構成は、Python 側の「親(ホスト)」が JavaScript 側の「子(エージェント)」をコントロールする形になっています。

![Diagram](images/auto-generated/mermaid-180b2df2f711e6413260e8e37be65242.png)
<details>
<summary>Mermaid source</summary>

```mermaid
graph LR
    subgraph "Python World (Host)"
        P_CLI[play.py / budokai.py] --> P_LOADER[loader.py]
        P_LOADER --> P_JS_AGENT[JsGameAgent]
    end

    subgraph "Node.js World (Agent)"
        P_JS_AGENT -- "Standard Input (JSON)" --> JS_BRIDGE[Bridge Logic]
        JS_BRIDGE -- "get_action()" --> JS_LOGIC[logic.js]
        JS_LOGIC -- "Result" --> JS_BRIDGE
        JS_BRIDGE -- "Standard Output (JSON)" --> P_JS_AGENT
    end

    style P_CLI fill:#f9f,stroke:#333
    style JS_LOGIC fill:#bbf,stroke:#333
```
</details>

> **💡 コラム: ポリグロット (Polyglot) とは？**
> 「複数の言語を話す」という意味です。一般には、単一のシステムで複数のプログラミング言語を組み合わせて使う構成を指します。各言語の得意分野(Pythonの豊富なAIライブラリ、JSのWeb表現力等)を活かせるメリットがあります。

---

## 🚀 エージェントのロードと初期化

エージェントがどのようにロードされるか、そのシーケンスを見てみましょう。

`loader.py` は、指定されたディレクトリに `logic.py` があれば Python 版を、 `logic.js` があれば JavaScript 版(`JsGameAgent`)を自動的に選択します。

![Diagram](images/auto-generated/mermaid-58683e24cfe60b9fed17c1e79c431c9e.png)
<details>
<summary>Mermaid source</summary>

```mermaid
sequenceDiagram
    participant Main as play.py / budokai.py
    participant Loader as loader.py
    participant JS_Agent as JsGameAgent (Python)
    participant Node as Node.js Process

    Main->>Loader: get_agent_class(dir)
    Loader->>Main: GameAgent Class (or Lambda)

    Main->>JS_Agent: __init__(mark)
    JS_Agent->>Node: Spawn process (node -e '(bridge_code)')
    activate Node
    JS_Agent->>Node: Send {"method": "init", "mark": "O"}
    Node->>Node: new GameAgent("O")
    Node-->>JS_Agent: {"status": "ok"}
    deactivate Node
    Main->>JS_Agent: get_name()
    JS_Agent->>Node: Send {"method": "get_name"}
    Node-->>JS_Agent: {"result": "my-js-agent"}
    JS_Agent-->>Main: "my-js-agent"
```
</details>

### 🌉 ブリッジ・コードの工夫
`JsGameAgent` は Node.js プロセスを立ち上げる際、 `-e` オプションを使用して**インラインで JavaScript の待受用コード(ブリッジ・コード)を流し込んでいます**。これにより、別途JavaScriptファイルを用意することなく、動的に Python からJavaScriptの世界を繋ぐことができます。

---

## 🧠 思考(get_action)のやり取り

ゲーム中、次の手を選ぶ際のやり取りは「JSON-RPC」のような形式で行われます。

![Diagram](images/auto-generated/mermaid-3ec4878fecf6ed5de7f09546b01bc27c.png)
<details>
<summary>Mermaid source</summary>

```mermaid
sequenceDiagram
    participant P as Python (JsGameAgent)
    participant J as Node.js (Bridge)

    P->>J: {"method": "get_action", "payload": [null, "O", ...], "strategy": "normal"}
    Note right of J: logic.js の get_action を呼び出し
    J-->>P: {"result": 4}
```
</details>

### 🛠️ データの通り道: 標準入出力
Python と Node.js の間では、以下のルートでデータが流れます。
1. **Python `stdin.write()`** -> Node.js の標準入力へ
2. **Node.js `console.log()`** -> Python の `stdout.readline()` へ

> **💡 コラム: JSON-RPC とは？**
> JSON形式を使って、別の場所(プロセスやサーバー)にある関数を呼び出すためのシンプルな規約です。「どの関数を(method)」「どんな引数で(params/payload)」呼び出すかを送ります。

---

## ⚠️ 異常系とエラーハンドリング

もし `logic.js` の中でエラー(例外)が発生したり、Node.js プロセスがクラッシュしたりした場合の振る舞いです。

![Diagram](images/auto-generated/mermaid-b2f592c6873c19c88ebcdd073f8d22b2.png)
<details>
<summary>Mermaid source</summary>

```mermaid
sequenceDiagram
    participant P as Python (JsGameAgent)
    participant J as Node.js (Bridge)

    P->>J: {"method": "get_action", ...}
    activate J
    Note right of J: logic.js で例外発生！
    J->>J: try-catch で捕捉
    J-->>P: {"error": "Unexpected token..."}
    deactivate J
    Note left of P: RuntimeError例外をRaise
```
</details>

### プロセスの死活監視
`JsGameAgent` は、Node.js プロセスにデータを送る前に必ずプロセスの状態をチェックしています。
- プロセスが予期せず終了していた場合(`poll()` が None でない場合)、 `RuntimeError` を発生させます。
- 読み取り時にデータが空だった場合も、 `stderr`(標準エラー出力)からエラー内容を読み取って報告します。

---

## 📦 やり取りされるデータの詳細仕様

詳細な設計の参考に、やり取りされる JSON の構造を記します。

### 1. 初期化 (`init`)
- **送信**: `{ "method": "init", "mark": "O" | "X" }`
- **返信**: `{ "status": "ok" }`

### 2. 名前取得 (`get_name`)
- **送信**: `{ "method": "get_name" }`
- **返信**: `{ "result": "エージェント名" }`

### 3. 行動取得 (`get_action`)
- **送信**:
  ```json
  {
    "method": "get_action",
    "payload": [null, "O", "X", null, ...],
    "strategy": "normal" | "original"
  }
  ```
- **返信**: `{ "result": 0 }` (マスのインデックス)

---

## 💻 クロスプラットフォームへの配慮

Windows と Linux/macOS の両方で動作させるために、以下の工夫を凝らしています。

1. **実行ファイルの探索**: `shutil.which('node')` を使い、OSごとの `node` または `node.exe` の場所を自動で見つけます。
2. **パスのエスケープ**: `json.dumps()` を使ってパスを文字列化することで、Windows のバックスラッシュ (`\`) がJavaScriptの文字列内で正しく扱われるようにしています。
3. **文字コード**: `encoding='utf-8'` を明示し、日本語(エージェント名など)が文字化けしないようにしています。
4. **プロセスのクリーンアップ**: Python 側の `__del__`(デストラクタ)で、Node.js プロセスを確実に終了させるようにしています。

---

## 🛠️ pre-commit による多言語環境の自動構築

本プロジェクトでは、開発者が自身のマシンに Node.js や特定のライブラリを手動でインストールしていなくても、テストやツールを実行できる仕組みとして `pre-commit` を活用しています。

ここでは、`pre-commit` がどのようにして Python と JavaScript の仮想環境を使い分け、依存関係を解決しているのかを解説します。

### 🏗️ 環境の分離とキャッシュ
`pre-commit` は、フックの実行に必要な環境をホスト環境(あなたのPCのグローバルな環境)から完全に切り離し、専用のキャッシュディレクトリ(通常は `~/.cache/pre-commit`)に構築します。

![Diagram](images/auto-generated/mermaid-e5d56b8205c48ed2d7a3a8d0f00509e1.png)
<details>
<summary>Mermaid source</summary>

```mermaid
graph TD
    PC[pre-commit 管理者] --> ENV_P[Python 仮想環境]
    PC --> ENV_JS[Node.js 仮想環境]

    subgraph "環境キャッシュ (~/.cache/pre-commit/)"
        ENV_P --> PY_BIN[python / pytest / pytest-cov]
        ENV_JS --> JS_BIN[node / npm / eslint / mmdc]
    end

    PC -- "フック実行" --> HOOK_PY[Python テストフック]
    PC -- "フック実行" --> HOOK_JS[ESLint / Mermaid 変換フック]

    HOOK_PY --> PY_BIN
    HOOK_JS --> JS_BIN
```
</details>

> **💡 コラム: 仮想環境の正体**
> `pre-commit` は、Python の場合は `virtualenv`、Node.js の場合は `nodeenv` というツールを使用して、最小限のバイナリとライブラリを含む独立したフォルダを作成します。実行時には、このフォルダ内の `bin`(または `Scripts`)ディレクトリを一時的に `PATH` 環境変数の先頭に追加することで、正しいバージョンのツールが優先的に呼び出されるようにしています。

### 🔄 フック実行のライフサイクル(例: ESLint の場合)

ESLint や Mermaid 変換ツールがどのように呼び出されるか、その裏側を見てみましょう。

![Diagram](images/auto-generated/mermaid-437028aac920f4498aeffdc6731a0c85.png)
<details>
<summary>Mermaid source</summary>

```mermaid
sequenceDiagram
    participant Dev as 開発者
    participant Git as Git Hook (pre-commit)
    participant PC as pre-commit Manager
    participant ENV as 独立した Node.js 環境

    Dev->>Git: git commit
    Git->>PC: フックのトリガー

    Note over PC: .pre-commit-config.yaml を確認

    alt 環境が未構築の場合
        PC->>PC: 環境の作成 (nodeenv)
        PC->>PC: npm install (additional_dependencies)
    end

    PC->>ENV: PATH 環境変数を設定(環境の有効化)
    PC->>ENV: 実行コマンド (例: eslint) を発行
    activate ENV
    Note right of ENV: 仮想環境内の ESLint が動作
    ENV-->>PC: 終了コード (0: 成功 / 1: 失敗)
    deactivate ENV

    alt 成功
        PC-->>Dev: コミットを許可
    else 失敗
        PC-->>Dev: コミットをブロック + エラー表示
    end
```
</details>

### 🔍 なぜ「インストール不要」で動くのか？

`additional_dependencies` に記述されたパッケージ(例: `@mermaid-js/mermaid-cli`)は、`pre-commit` がそのフック専用の仮想環境内に自動的に `npm install` します。

そのため：
1. **ホスト汚染がない**: あなたの PC のグローバルな `node_modules` を汚しません。
2. **バージョン固定**: `package.json` がなくても、`.pre-commit-config.yaml` に書かれたバージョンが確実に使われます。
3. **パス解決の自動化**: `pre-commit` が仮想環境内の `node_modules/.bin` を自動的に探索するため、開発者はフルパスを意識することなくコマンド名だけでツールを呼び出せます。

---

## 🔐 閉じたネットワーク(オンプレミス)での活用

もしあなたが「npmjs.com には公開されていない内製の ESLint プラグイン」などを、社内のオンプレミスなリポジトリやローカル環境から取得して使いたい場合も、`pre-commit` は柔軟に対応できます。

### 1. ローカルパスの指定
`additional_dependencies` には、パッケージ名だけでなくローカルのファイルパス(`file:./libs/my-plugin` など)を指定することも可能です。`pre-commit` はこれを受けて、`npm install <path>` を実行し、仮想環境内へ取り込みます。

### 2. プライベートレジストリの切り替え
`npm` の取得先(レジストリ)を社内のサーバーに切り替えたい場合は、環境変数 `NPM_CONFIG_REGISTRY` を活用します。`pre-commit` が `npm install` を実行する際、この環境変数が参照されるため、パッケージの取得先が自動的にオンプレミスなサーバーへと切り替わります。

![Diagram](images/auto-generated/mermaid-834302d6df450e4f602b134749ed4b49.png)
<details>
<summary>Mermaid source</summary>

```mermaid
graph LR
    subgraph "Local / Intranet"
        PLUGIN[内製プラグイン / Path]
        REGISTRY[社内 npm レジストリ]
    end

    PC[pre-commit] -- "NPM_CONFIG_REGISTRY" --> REGISTRY
    PC -- "file:..." --> PLUGIN

    PC --> ENV[仮想環境]
    REGISTRY --> ENV
    PLUGIN --> ENV
```
</details>

> **💡 コラム: .npmrc の役割**
> プロジェクトルートに `.npmrc` ファイルを置いて `registry=...` を記述しておく方法もあります。`pre-commit` の仮想環境内であっても、`npm` は実行ディレクトリの `.npmrc` を読み込むため、確実に社内サーバーを見に行くように設定できます。

---

このアーキテクチャのおかげで、私たちは言語の壁だけでなく、環境構築の壁も越えて、安全かつ迅速に開発を進めることができるのです。さあ、あなたも `logic.js` を作って、このポリグロットな世界に飛び込んでみましょう！
