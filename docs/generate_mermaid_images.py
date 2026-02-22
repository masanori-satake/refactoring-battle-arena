import os
import re
import hashlib
import subprocess
import sys
import shutil

# 設定
IMAGE_DIR = "docs/images/auto-generated"

def get_mermaid_cli():
    # 1. 環境パスから探す (pre-commit等の環境)
    cli = shutil.which("mmdc")
    if cli:
        return cli

    # 2. ローカルのnode_modulesから探す
    cli = os.path.join("node_modules", ".bin", "mmdc")
    if sys.platform == "win32":
        cli += ".cmd"
    if os.path.exists(cli):
        return cli

    return "mmdc" # 最後はフォールバック

def get_mermaid_hash(content):
    return hashlib.md5(content.strip().encode('utf-8')).hexdigest()

def process_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Mermaidブロックを抽出
    # グループ1: 前にある既存の画像リンク（あれば）
    # グループ2: Mermaidブロック本体
    pattern = re.compile(r'(?:!\[Diagram\]\((.*?)\)\s*\n)?```mermaid\n(.*?)\n```', re.DOTALL)

    mermaid_cli = get_mermaid_cli()

    def replace_mermaid(match):
        mermaid_code = match.group(2)
        m_hash = get_mermaid_hash(mermaid_code)
        image_filename = f"mermaid-{m_hash}.png"
        image_path = os.path.join(IMAGE_DIR, image_filename)

        # PNGがなければ生成
        if not os.path.exists(image_path):
            print(f"Generating diagram for {filepath} (hash: {m_hash})...")

            temp_mmd = f"temp-{m_hash}.mmd"
            with open(temp_mmd, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)

            try:
                # Puppeteerのために --no-sandbox が必要な場合がある
                # まずはそのまま試す
                res = subprocess.run([mermaid_cli, "-i", temp_mmd, "-o", image_path], capture_output=True, text=True)
                if res.returncode != 0:
                    # 失敗した場合は --no-sandbox (config経由) を試す
                    print(f"Retrying with puppeteer-config.json for {image_filename}")
                    config_path = "puppeteer-config.json"
                    with open(config_path, 'w') as f:
                        f.write('{"args": ["--no-sandbox"]}')
                    subprocess.run([mermaid_cli, "-i", temp_mmd, "-o", image_path, "-p", config_path], check=True)
                    if os.path.exists(config_path):
                        os.remove(config_path)
            except Exception as e:
                print(f"Failed to generate diagram: {e}", file=sys.stderr)
                return match.group(0)
            finally:
                if os.path.exists(temp_mmd):
                    os.remove(temp_mmd)

        # Markdown内のリンクを更新
        rel_image_path = os.path.relpath(image_path, os.path.dirname(filepath)).replace(os.sep, '/')
        return f"![Diagram]({rel_image_path})\n```mermaid\n{mermaid_code}\n```"

    new_content = pattern.sub(replace_mermaid, content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

def main():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # リポジトリ内のすべての.mdファイルをスキャン
    for root, dirs, files in os.walk('.'):
        # 除外ディレクトリ
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__')]

        for file in files:
            if file.endswith('.md'):
                process_markdown_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
