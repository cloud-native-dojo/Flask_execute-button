import flask
from flask import request, jsonify, render_template
import subprocess
import threading
import time
import sys

args = sys.argv


app = flask.Flask(__name__)
pod_data = {"output": ""}
#HTML = open("index.html", "r").read()


def fetch_pod_data():
    global pod_data
    while True:
        try:
            result = subprocess.check_output(["kubectl", "get", "pod", "-l", f"app={args[1]}"], text=True)
            pod_data["output"] = result
        except subprocess.CalledProcessError as e:
            pod_data["output"] = f"Error fetching pods: {e}"
        time.sleep(0.5)


@app.route('/')
def index():
    return render_template("index.html", arg=args[1])

@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.json
    message = data.get('message', '')
    subprocess.run(['kubectl', 'delete', 'pod', '-l', f"app={args[1]}", '--force'], \
        encoding='utf-8', stdout=subprocess.PIPE)
    with open("log.txt", "a") as f:
        f.write(f'{message}\n')
    return jsonify({'reply': f'Server received: {message}'})

@app.route('/pods')
def get_pods():
    return jsonify(pod_data)


if __name__ == '__main__':
    thread = threading.Thread(target=fetch_pod_data, daemon=True)
    thread.start()
    app.run(port=5003)