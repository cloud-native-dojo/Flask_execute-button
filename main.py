import flask
from flask import request, jsonify, render_template
import subprocess
import threading
import time


app = flask.Flask(__name__)
pod_data = {"output": ""}
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
        .pod-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 20px;
        }
        .pod-image {
            width: 150px;
            height: 150px;
            margin: 10px;
        }
        .pod-name {
            margin-top: 10px;
            font-size: 18px;
        }
        .pod-wrapper {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 40px;
        }
        button {
            padding: 10px;
            font-size: 16px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Pod Status</h1>
    <div id="pod-images" class="pod-wrapper">Loading...</div>
    <button onclick="sendMessage()">REBOOT ALL</button>
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

        function deletePod(podName) {
            fetch('/delete-pod', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({pod_name: podName})
            });
        }

        async function fetchPodData() {
            try {
                const response = await fetch('/pods');
                const data = await response.json();
                const podOutput = data.output;
                const podImagesDiv = document.getElementById('pod-images');
                podImagesDiv.innerHTML = '';
                const podLines = podOutput.split('\\n').slice(1);
                podLines.forEach(line => {
                    if (line.trim()) {
                        const [name, , status] = line.split(/\s+/);
                        const podContainer = document.createElement('div');
                        podContainer.className = 'pod-container';
                        const img = document.createElement('img');
                        img.src = status === 'Running' ? "images/computer_green.png" : "images/computer_gray.png";
                        img.className = 'pod-image';
                        const podName = document.createElement('div');
                        podName.className = 'pod-name';
                        podName.textContent = name;
                        const deleteButton = document.createElement('button');
                        deleteButton.textContent = 'Delete';
                        deleteButton.onclick = () => deletePod(name);
                        podContainer.appendChild(img);
                        podContainer.appendChild(podName);
                        podContainer.appendChild(deleteButton);
                        podImagesDiv.appendChild(podContainer);
                    }
                });
            } catch (error) {
                document.getElementById('pod-images').textContent = 'Error fetching data';
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
    subprocess.run(['kubectl', 'delete', 'pod', '--all', '--force'], encoding='utf-8', stdout=subprocess.PIPE)
    return jsonify({'reply': f'Server received: {message}'})

@app.route('/delete-pod', methods=['POST'])
def delete_pod():
    data = request.json
    pod_name = data.get('pod_name', '')
    if pod_name:
        subprocess.run(['kubectl', 'delete', 'pod', pod_name, '--force'], encoding='utf-8', stdout=subprocess.PIPE)
        return jsonify({'reply': f'Deleted pod: {pod_name}'})
    return jsonify({'reply': 'Pod name not provided'}), 400

@app.route('/pods')
def get_pods():
    return jsonify(pod_data)


if __name__ == '__main__':
    thread = threading.Thread(target=fetch_pod_data, daemon=True)
    thread.start()
    app.run()