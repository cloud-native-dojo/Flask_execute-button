import flask
from flask import request, jsonify, render_template
import subprocess
import threading
import time
import sys
import logging

# ロガーの取得
werkzeug_logger = logging.getLogger("werkzeug")
# レベルの変更
werkzeug_logger.setLevel(logging.ERROR)


args = sys.argv


app = flask.Flask(__name__)
pod_data = {"output": ""}

def fetch_pod_data():
    global pod_data
    while True:
        try:
            result = subprocess.run(["timeout", "1", "kubectl", "get", "pod", "-l", f"app={args[1]}"], capture_output=True, text=True)
            if result.returncode == 0:
                pod_data["output"] = result.stdout
        except subprocess.CalledProcessError as e:
            pod_data["output"] = f"Error fetching pods: {e}"


@app.route('/')
def index():
    return render_template("index.html", arg=args[1])

@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.json
    message = data.get('message', '')
    if message == 'create':
        subprocess.run(['kubectl', 'scale', '--replicas=1', "deployment", args[1]], encoding='utf-8')
        pass
    elif message == 'delete':
        subprocess.run(['kubectl', 'scale', '--replicas=0', "deployment", args[1]], encoding='utf-8')
        time.sleep(0.5)
        subprocess.run(['kubectl', 'delete', 'pod', "-l", f"app={args[1]}", '--force'], encoding='utf-8')
    return jsonify({'reply': f'Server received: {message}'})

@app.route('/pods')
def get_pods():
    return jsonify(pod_data)


if __name__ == '__main__':
    thread = threading.Thread(target=fetch_pod_data, daemon=True)
    thread.start()
    app.run(port=args[2])
