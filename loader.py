import os
import sys
import importlib.util
import subprocess
import json
import shutil

class JsGameAgent:
    def __init__(self, directory, mark):
        self.directory = os.path.abspath(directory)
        self.js_path = os.path.join(self.directory, "logic.js")
        self.mark = mark
        self.process = None
        self._start_process()

    def _start_process(self):
        # Node.jsの実行ファイルを探す（Windows環境対策）
        node_bin = shutil.which('node') or shutil.which('node.exe') or 'node'

        # PythonとJSを橋渡しするための小さなヘルパースクリプト
        # Windowsのパス（バックスラッシュ）がJSの文字列内で正しくエスケープされるようにjson.dumpsを使用
        js_path_escaped = json.dumps(self.js_path)
        bridge_code = f"""
const {{ GameAgent }} = require({js_path_escaped});
const readline = require('readline');
const rl = readline.createInterface({{ input: process.stdin, output: process.stdout, terminal: false }});
let agent;

rl.on('line', (line) => {{
    try {{
        const req = JSON.parse(line);
        if (req.method === 'init') {{
            agent = new GameAgent(req.mark);
            console.log(JSON.stringify({{ status: 'ok' }}));
        }} else if (req.method === 'get_name') {{
            // AGENT_NAMEは定数であるか、get_name()によって返される可能性があります
            const name = agent.get_name();
            console.log(JSON.stringify({{ result: name }}));
        }} else if (req.method === 'get_action') {{
            const result = agent.get_action(req.payload, req.strategy);
            console.log(JSON.stringify({{ result: result }}));
        }}
    }} catch (e) {{
        console.error(e);
        console.log(JSON.stringify({{ error: e.message }}));
    }}
}});
"""
        self.process = subprocess.Popen(
            [node_bin, '-e', bridge_code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        # エージェントを初期化
        self._send({"method": "init", "mark": self.mark})

    def _send(self, data):
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("JSプロセスが実行されていません")
        self.process.stdin.write(json.dumps(data) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            err = self.process.stderr.read()
            raise RuntimeError(f"JSプロセスが予期せず終了しました: {err}")
        return json.loads(line)

    def get_name(self):
        resp = self._send({"method": "get_name"})
        return resp.get("result")

    def get_action(self, payload_buffer, strategy_type="normal"):
        resp = self._send({
            "method": "get_action",
            "payload": payload_buffer,
            "strategy": strategy_type
        })
        return resp.get("result")

    def __del__(self):
        if hasattr(self, 'process') and self.process:
            try:
                self.process.terminate()
                # プロセスが確実に終了するのを待機
                self.process.wait(timeout=1)
            except:
                # タイムアウトや既に終了している場合は無視
                pass

def get_agent_class(directory):
    logic_py = os.path.join(directory, "logic.py")
    logic_js = os.path.join(directory, "logic.js")

    if os.path.exists(logic_py):
        spec = importlib.util.spec_from_file_location(f"logic_{directory.replace(os.sep, '_')}", logic_py)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.GameAgent
    elif os.path.exists(logic_js):
        # インスタンス化されたときにJsGameAgentを返すクラス（ラムダ）を返す
        return lambda mark: JsGameAgent(directory, mark)
    else:
        return None
