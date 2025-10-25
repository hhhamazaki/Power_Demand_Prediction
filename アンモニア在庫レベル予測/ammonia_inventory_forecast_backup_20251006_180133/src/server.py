import http.server
import socketserver
import subprocess
import sys
import json
import os

PORT = 8001
# server.py is in the 'src' directory, so the project root is one level up.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # ファイルを提供するディレクトリをプロジェクトルートに設定
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_POST(self):
        # ログを出して、POST リクエストが届いているか確認しやすくする
        try:
            client_ip, client_port = self.client_address
        except Exception:
            client_ip, client_port = (self.client_address, None)
        print(f"Received POST request from {client_ip}:{client_port} -> {self.path}")

        if self.path == '/run-train':
            self.run_script(os.path.join('src', 'train.py'), '学習')
        elif self.path == '/run-predict':
            self.run_script(os.path.join('src', 'predict.py'), '予測')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint Not Found')

    def do_GET(self):
        # ブラウザが /favicon.ico を自動で要求するため、存在しない場合は空応答(204)で抑制
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        # それ以外は通常の静的ファイル配信に委譲
        return super().do_GET()

    def run_script(self, script_path, process_name):
        """指定されたPythonスクリプトを実行し、結果をJSONで返す"""
        full_script_path = os.path.join(PROJECT_ROOT, script_path)
        try:
            print(f"Executing script for {process_name}: {full_script_path}")
            sys.stdout.flush()
            # スクリプトをプロジェクトルートで実行
            result = subprocess.run(
                [sys.executable, full_script_path],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace',
                cwd=PROJECT_ROOT
            )
            print(f"Script {full_script_path} finished (returncode={result.returncode})")
            if result.stdout:
                print("--- stdout ---")
                print(result.stdout)
            if result.stderr:
                print("--- stderr ---")
                print(result.stderr)
            sys.stdout.flush()
            response_data = {
                "status": "success",
                "message": f"'{process_name}' プロセスが正常に完了しました。",
                "output": result.stdout
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

        except FileNotFoundError:
            print("FileNotFoundError: Python interpreter not found when attempting to run script.")
            sys.stdout.flush()
            self.send_error(500, "Python interpreter not found. Please check your system's PATH.")
        except subprocess.CalledProcessError as e:
            # e.stderr may be None, str, or bytes. Normalize to str safely.
            stderr_text = ''
            if getattr(e, 'stderr', None) is None:
                stderr_text = ''
            elif isinstance(e.stderr, bytes):
                stderr_text = e.stderr.decode('utf-8', errors='replace')
            else:
                # assume it's already str
                stderr_text = str(e.stderr)

            print(f"CalledProcessError while running {full_script_path}: returncode={getattr(e, 'returncode', 'N/A')}")
            print(stderr_text)
            sys.stdout.flush()

            response_data = {
                "status": "error",
                "message": f"'{process_name}' プロセスでエラーが発生しました。",
                "output": stderr_text
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"An unexpected error occurred: {e}")

# 日本語のファイルパスを扱えるようにディレクトリを変更
os.chdir(PROJECT_ROOT)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"サーバーを http://localhost:{PORT}/dashboard/index.html で起動しています。")
    print("ブラウザで上記URLを開いてください。")
    print("サーバーを停止するには Ctrl+C を押してください。")
    httpd.serve_forever()
