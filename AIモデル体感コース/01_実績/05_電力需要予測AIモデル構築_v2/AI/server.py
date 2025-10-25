import http.server
import socketserver
import subprocess
import sys
import json
import os
import threading

# Allow overriding the port via environment variable AI_SERVER_PORT (useful when port conflicts occur)
try:
    PORT = int(os.environ.get('AI_SERVER_PORT', '8002'))
except Exception:
    PORT = 8002
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(PROJECT_ROOT, 'server.log')

def _log(msg: str):
    try:
        ts = ''
        from datetime import datetime
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_POST(self):
        if self.path == '/run-data':
            # Expect JSON body: { "years": ["2019","2020"] }
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length else '{}'
            try:
                payload = json.loads(body)
            except Exception:
                payload = {}
            years = payload.get('years')
            _log(f"Received /run-data payload: {payload}")
            env = os.environ.copy()
            if years:
                env['AI_TARGET_YEARS'] = ','.join(years)
            out = self._run_script(os.path.join('data', 'data.py'), env=env)
            self._json_response(out)
        elif self.path == '/run-train':
            # body: { "model": "LightGBM" }
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length else '{}'
            try:
                payload = json.loads(body)
            except Exception:
                payload = {}
            model = payload.get('model', 'LightGBM')
            # allow optional years passed from client to restrict training data
            years = payload.get('years')
            _log(f"Received /run-train payload: {payload}")
            script_map = {
                'LightGBM': os.path.join('train', 'LightGBM', 'LightGBM_train.py'),
                'Keras': os.path.join('train', 'Keras', 'Keras_train.py'),
                'PyCaret': os.path.join('train', 'Pycaret', 'Pycaret_train.py'),
                'RandomForest': os.path.join('train', 'RandomForest', 'RandomForest_train.py')
                , 'Echo': os.path.join('tools', 'echo_env.py')
            }
            script = script_map.get(model, script_map['LightGBM'])
            # Always prepare an environment dict so _run_script can read SERVER_PYTHON or other keys.
            env = os.environ.copy()
            # データ制限を明示的に指定された場合のみ適用（デフォルトでは全データ使用）
            if years:
                env['AI_TARGET_YEARS'] = ','.join(years)
                _log(f"年指定あり: AI_TARGET_YEARS={env.get('AI_TARGET_YEARS')}")
            else:
                # 年指定がない場合は環境変数をクリアして全データを使用
                if 'AI_TARGET_YEARS' in env:
                    del env['AI_TARGET_YEARS']
                _log("年指定なし: 全データを使用")

            # If years provided, run data pipeline first so training reads filtered files
            combined_stdout = ''
            combined_stderr = ''
            if years:
                _log(f"Running data pipeline before training with AI_TARGET_YEARS={env.get('AI_TARGET_YEARS')}")
                data_out = self._run_script(os.path.join('data', 'data.py'), env=env)
                # If data pipeline failed, return its result immediately
                if data_out.get('returncode') not in (0, None):
                    self._json_response(data_out)
                    return
                combined_stdout += (data_out.get('stdout') or '')
                combined_stderr += (data_out.get('stderr') or '')

            # Now run training script
            train_out = self._run_script(script, env=env)
            combined_stdout += '\n--- TRAIN STDOUT ---\n' + (train_out.get('stdout') or '')
            combined_stderr += '\n--- TRAIN STDERR ---\n' + (train_out.get('stderr') or '')
            self._json_response({ 'status': 'ok', 'stdout': combined_stdout, 'stderr': combined_stderr, 'returncode': train_out.get('returncode') })
        elif self.path == '/run-tomorrow-data':
            # First, run temperature fetch script (temp.py) to ensure tomorrow/tomorrow.csv is updated
            _log("/run-tomorrow-data: invoking tomorrow/temp.py before tomorrow/data.py")
            temp_out = self._run_script(os.path.join('tomorrow', 'temp.py'))
            # If the temp script failed, return its output immediately so client can see the error
            if temp_out.get('returncode') not in (0, None):
                self._json_response(temp_out)
                return
            # Next, run the existing data pipeline to create Ytest etc.
            out = self._run_script(os.path.join('tomorrow', 'data.py'))
            # Combine outputs for client visibility
            combined = {
                'status': out.get('status'),
                'temp_stdout': temp_out.get('stdout'),
                'temp_stderr': temp_out.get('stderr'),
                'stdout': out.get('stdout'),
                'stderr': out.get('stderr'),
                'returncode': out.get('returncode')
            }
            self._json_response(combined)
        elif self.path == '/run-tomorrow':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length else '{}'
            try:
                payload = json.loads(body)
            except Exception:
                payload = {}
            model = payload.get('model', 'LightGBM')
            # optional years may be provided to control data selection for prediction preprocessing
            years = payload.get('years')
            _log(f"Received /run-tomorrow payload: {payload}")
            script_map = {
                'LightGBM': os.path.join('tomorrow', 'LightGBM', 'LightGBM_tomorrow.py'),
                'Keras': os.path.join('tomorrow', 'Keras', 'Keras_tomorrow.py'),
                'PyCaret': os.path.join('tomorrow', 'Pycaret', 'Pycaret_tomorrow.py'),
                'RandomForest': os.path.join('tomorrow', 'RandomForest', 'RandomForest_tomorrow.py')
            }
            script = script_map.get(model, script_map['LightGBM'])
            env = os.environ.copy()
            if years:
                env['AI_TARGET_YEARS'] = ','.join(years)
            out = self._run_script(script, env=env)
            self._json_response(out)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # If root is requested, serve the dashboard index.html content
        # directly. This avoids client-side caching/redirect issues and
        # guarantees the dashboard HTML is returned for '/'.
        if self.path in ('/', '/index.html'):
            try:
                dashboard_path = os.path.join(PROJECT_ROOT, 'dashboard', 'index.html')
                with open(dashboard_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                _log(f"Failed to serve dashboard index: {e}")
                self.send_response(500)
                self.end_headers()
            return

        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        if self.path == '/available-years':
            # Scan data directory for juyo-YYYY.csv and temperature-YYYY.csv and return common years
            try:
                import glob
                data_dir = os.path.join(PROJECT_ROOT, 'data')
                power_files = sorted(glob.glob(os.path.join(data_dir, 'juyo-*.csv')))
                temp_files = sorted(glob.glob(os.path.join(data_dir, 'temperature-*.csv')))
                power_years = [os.path.basename(f)[5:9] for f in power_files if len(os.path.basename(f)) >= 9]
                temp_years = [os.path.basename(f)[12:16] for f in temp_files if len(os.path.basename(f)) >= 16]
                common = sorted(list(set(power_years) & set(temp_years)))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'years': common}, ensure_ascii=False).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}, ensure_ascii=False).encode('utf-8'))
                return
        return super().do_GET()

    def _run_script(self, script_relpath, env=None):
        full = os.path.join(PROJECT_ROOT, script_relpath)
        if not os.path.exists(full):
            _log(f"script not found: {script_relpath}")
            return { 'status': 'error', 'message': f'file not found: {script_relpath}' }
        try:
            _log(f"Executing script: {full}")
            # Ensure subprocess uses UTF-8 for stdio to avoid encoding errors on Windows
            # Merge environments carefully: start from the current env, then overlay any provided env
            # so that values passed in `env` (e.g. AI_TARGET_YEARS) take precedence.
            child_env = os.environ.copy()
            if env:
                # env may be a copy of os.environ with modifications; overlay it
                child_env.update(env)
            # Ensure subprocess uses UTF-8 for stdio to avoid encoding errors on Windows
            child_env.setdefault('PYTHONIOENCODING', 'utf-8')
            # Allow overriding Python executable via SERVER_PYTHON environment variable (full path)
            server_python = child_env.get('SERVER_PYTHON')
            if server_python:
                _log(f"Using SERVER_PYTHON for subprocess: {server_python}")
                cmd = [server_python, full]
            else:
                cmd = [sys.executable, full]
            # If the caller provided a years list in env, also append as a command-line arg
            # so scripts that prefer argv over env still receive the intended years.
            years_arg = None
            if child_env.get('AI_TARGET_YEARS'):
                years_arg = child_env.get('AI_TARGET_YEARS')
                # append as single arg: e.g. "2024,2023"
                cmd.append(years_arg)

            # Log full child env subset for traceability (only important keys)
            try:
                logged_keys = {k: child_env.get(k) for k in ('AI_TARGET_YEARS','SERVER_PYTHON','PYTHONIOENCODING')}
                _log(f"Child env subset: {logged_keys}")
            except Exception:
                _log("Child env subset logging failed")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=child_env, cwd=PROJECT_ROOT, timeout=600)
            # log truncated stdout/stderr
            so = (result.stdout or '')[:20000]
            se = (result.stderr or '')[:20000]
            _log(f"Script finished: {script_relpath} returncode={result.returncode}")
            if so:
                _log(f"STDOUT:\n{so}")
            if se:
                _log(f"STDERR:\n{se}")
            status = 'ok' if result.returncode == 0 else 'error'
            return { 'status': status, 'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode }
        except Exception as e:
            _log(f"Script exception: {script_relpath} error: {e}")
            return { 'status': 'error', 'message': str(e) }

    def _json_response(self, data):
        self.send_response(200 if data.get('status') in ('ok', None) else 500)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def _start():
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
        daemon_threads = True

    httpd = ThreadingHTTPServer(('', PORT), Handler)
    # Print chosen port and PID to help diagnose port conflicts
    try:
        pid = os.getpid()
    except Exception:
        pid = None
    print(f"AI server running at http://localhost:{PORT}/ (serving from {PROJECT_ROOT}) PID={pid}")
    # By default, open the dashboard in the user's default browser in a single
    # tab after the server has bound and the dashboard URL responds with 200.
    # Set environment variable AI_OPEN_BROWSER='0' to disable automatic opening.
    try:
        print(f"Serving from PROJECT_ROOT={PROJECT_ROOT}")
    except Exception:
        pass

    try:
        if os.environ.get('AI_OPEN_BROWSER', '1') != '0':
            import webbrowser
            import threading as _threading
            def _open_root_once():
                url = f'http://localhost:{PORT}/'
                import time
                import urllib.request
                import urllib.error
                # wait up to ~10 seconds for server to be ready
                deadline = time.time() + 10.0
                opened = False
                while time.time() < deadline and not opened:
                    try:
                        req = urllib.request.Request(url, method='GET')
                        with urllib.request.urlopen(req, timeout=1) as resp:
                            if resp.status == 200:
                                # open in a new browser tab (if possible)
                                try:
                                    webbrowser.open(url, new=2)
                                except Exception:
                                    try:
                                        webbrowser.open(url)
                                    except Exception:
                                        pass
                                opened = True
                                break
                    except Exception:
                        # server not ready yet
                        time.sleep(0.25)
                # done
            _threading.Thread(target=_open_root_once, daemon=True).start()
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
        httpd.shutdown()


if __name__ == '__main__':
    _start()
