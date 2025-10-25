import http.server
import socketserver
import subprocess
import sys
import json
import os
import datetime
import zoneinfo
import threading

# Default starting port; will try incrementally if in use
PORT = 8001
# server.py is in the 'src' directory, so the project root is one level up.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JST = zoneinfo.ZoneInfo('Asia/Tokyo')
BASE_DATE = datetime.datetime.now(JST).date().isoformat()
print(f"BASE_DATE set to (JST): {BASE_DATE}")

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
            # スクリプトファイルの存在確認
            if not os.path.exists(full_script_path):
                raise FileNotFoundError(f"スクリプトファイルが見つかりません: {full_script_path}")
                
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
                cwd=PROJECT_ROOT,
                timeout=300  # 5分タイムアウト
            )
            
            print(f"Script {full_script_path} finished (returncode={result.returncode})")
            if result.stdout:
                print("--- stdout ---")
                print(result.stdout[:2000])  # 出力を制限
                if len(result.stdout) > 2000:
                    print(f"... (出力が長すぎるため省略。全{len(result.stdout)}文字)")
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

        except subprocess.TimeoutExpired:
            print(f"タイムアウト: {full_script_path} の実行が5分を超えました")
            sys.stdout.flush()
            response_data = {
                "status": "error",
                "message": f"'{process_name}' プロセスがタイムアウトしました（5分）。",
                "output": "実行時間が制限を超えました"
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            sys.stdout.flush()
            response_data = {
                "status": "error",
                "message": f"スクリプトファイルが見つかりません: {script_path}",
                "output": str(e)
            }
            self.send_response(404)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
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
            print(f"予期しないエラー: {e}")
            sys.stdout.flush()
            self.send_error(500, f"予期しないエラーが発生しました: {e}")

# 日本語のファイルパスを扱えるようにディレクトリを変更
os.chdir(PROJECT_ROOT)

def _open_browser_when_ready(port, path='/dashboard/index.html'):
    """Start the default browser to the dashboard URL. Polls the server until it's responsive.

    Returns True if browser was opened, False otherwise.
    """
    import webbrowser
    import time
    import urllib.request
    import urllib.error

    url = f'http://localhost:{port}{path}'

    # Wait for server to be ready before opening browser (use socket connect to check accept loop)
    import socket
    wait_seconds = 0.1
    total_wait = 0.0
    max_wait = 5.0
    while total_wait < max_wait:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                # connection succeeded; server is accepting connections
                break
        except Exception:
            time.sleep(wait_seconds)
            total_wait += wait_seconds
            wait_seconds = min(wait_seconds * 1.5, 1.0)
    else:
        print("警告: サーバーの起動確認に失敗しました（接続タイムアウト）。手動でURLを開いてください。")
        return False

    # Open browser after confirming server is ready
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"ブラウザ起動エラー: {e}")
        return False


def _start_server_with_fallback(port, handler, max_tries=10):
    """Try to bind the server starting from port, incrementing on EADDRINUSE up to max_tries.
    Uses ThreadingTCPServer with allow_reuse_address to decrease chance of transient bind failures.
    Returns (httpd, used_port) on success or (None, None) on failure.
    """
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        daemon_threads = True
        allow_reuse_address = True

    for attempt in range(max_tries):
        try_port = port + attempt
        try:
            httpd = ThreadingHTTPServer(("", try_port), handler)
            return httpd, try_port
        except OSError as e:
            # Address already in use -> try next
            if getattr(e, 'winerror', None) == 10048 or 'Address already in use' in str(e):
                print(f"ポート {try_port} は使用中のためスキップします。次のポートを試行します...")
                continue
            else:
                print(f"サーバーのバインドに失敗しました: {e}")
                return None, None
    return None, None


httpd, used_port = _start_server_with_fallback(PORT, Handler)
if httpd is None:
    print(f"サーバーを起動できませんでした。ポート {PORT} から {PORT + 9} の範囲で全て失敗しました。")
    sys.exit(1)

dashboard_url = f"http://localhost:{used_port}/dashboard/index.html"
print(f"サーバーを {dashboard_url} で起動しています。")

# Start the server loop in a background thread so we can probe readiness and open a browser
server_thread = threading.Thread(target=httpd.serve_forever, name="httpd-serve", daemon=True)
server_thread.start()

print("既定のブラウザでダッシュボードを開きます...")
try:
    opened = _open_browser_when_ready(used_port)
    if not opened:
        print("ブラウザを自動で開けませんでした。手動でURLを開いてください:")
        print(dashboard_url)
except Exception as e:
    print(f"ブラウザ起動時に例外が発生しました: {e}")

print("サーバーを停止するには Ctrl+C を押してください。")
try:
    # Keep the main thread alive waiting for KeyboardInterrupt
    while True:
        threading.Event().wait(1.0)
except KeyboardInterrupt:
    print('\nサーバーを停止します。')
    try:
        httpd.shutdown()
    except Exception:
        pass
    server_thread.join(timeout=2)
    try:
        httpd.server_close()
    except Exception:
        pass
