import flask
from flask import request, jsonify, render_template
import subprocess
import threading
import time


app = flask.Flask(__name__)
pod_data = {"output": ""}
# HTML = open("index.html", "r").read()
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Test Site</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
        }
        button {
            padding: 20px;
            font-size: 20px;
            margin-bottom: 20px;
        }
        pre {
            padding: 10px;
            border: 1px solid #ccc;
            width: 80%;
            max-width: 600px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <button onclick="sendMessage()">Click me</button>
    <h1>Pod Status</h1>
    <pre id="pod-output">Loading...</pre>
    <script>
        function sendMessage() {
            fetch('/button-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({message: 'ボタンクリック'})
            });
        }

        async function fetchPodData() {
            try {
                const response = await fetch('/pods');
                const data = await response.json();
                document.getElementById('pod-output').textContent = data.output;
            } catch (error) {
                document.getElementById('pod-output').textContent = 'Error fetching data';
            }
        }

        setInterval(fetchPodData, 500);
        fetchPodData();
    </script>
</body>
</html>
"""


def fetch_pod_data():
    global pod_data
    while True:
        try:
            result = subprocess.check_output(["kubectl", "get", "pod"], text=True)
            pod_data["output"] = result
        except subprocess.CalledProcessError as e:
            pod_data["output"] = f"Error fetching pods: {e}"
        time.sleep(0.5)


@app.route('/')
def index():
    return HTML

@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.json
    message = data.get('message', '')
    subprocess.run(['kubectl', 'delete', 'pod', '--all', '--force'], \
        encoding='utf-8', stdout=subprocess.PIPE)
    return jsonify({'reply': f'Server received: {message}'})

@app.route('/pods')
def get_pods():
    return jsonify(pod_data)


if __name__ == '__main__':
    thread = threading.Thread(target=fetch_pod_data, daemon=True)
    thread.start()
    app.run()