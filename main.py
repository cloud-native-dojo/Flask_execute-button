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
            justify-content: flex-start; /* Align items to the top */
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #a9a9a9; /* Lighter gray background */
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            padding: 10px;
            border: 1px solid #ccc;
            width: 90%;
            max-width: 1200px;
            overflow-x: auto;
            font-size: 24px; /* Larger font size */
            text-align: left; /* Left-align text */
            background-color: #fff;
            margin-bottom: 5px;
            margin-top: 5px; /* Add margin-top to move the items down */
        }
        h1 {
            font-size: 36px;
            margin-bottom: 20px;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px; /* Add gap between buttons */
            width: 100%;
            padding: 80px; /* Increase padding to move buttons further down */
            position: fixed;
            bottom: 20px; /* Fix the position at the bottom */
        }
        .button {
            padding: 30px 60px; /* Increase button size */
            font-size: 24px;
            border: none;
            cursor: pointer;
        }
        .create-button {
            background-color: red;
            color: white;
        }
        .delete-button {
            background-color: blue;
            color: white;
        }
    </style>
</head>
<body>
    <h1>コンテナ管理</h1>
    <ul id="pod-list">Loading...</ul>
    <div class="button-container">
        <button class="button create-button" onclick="createPod()">作成</button>
        <button class="button delete-button" onclick="deletePod()">削除</button>
    </div>
    <script>
        let currentPods = [];

        async function fetchPodData() {
            try {
                const response = await fetch('/pods');
                const data = await response.json();
                const newPods = data.output.split('\\n');
                const podListElement = document.getElementById('pod-list');

                // Find pods to add and remove
                const podsToAdd = newPods.filter(pod => !currentPods.includes(pod));
                const podsToRemove = currentPods.filter(pod => !newPods.includes(pod));

                // Remove old pods
                podsToRemove.forEach(pod => {
                    const listItem = document.getElementById(pod);
                    if (listItem) {
                        podListElement.removeChild(listItem);
                    }
                });

                // Add new pods
                podsToAdd.forEach(pod => {
                    const listItem = document.createElement('li');
                    listItem.id = pod;
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = pod;
                    checkbox.name = pod;
                    checkbox.value = pod;
                    const label = document.createElement('label');
                    label.htmlFor = pod;
                    label.appendChild(document.createTextNode(pod));
                    listItem.appendChild(checkbox);
                    listItem.appendChild(label);
                    podListElement.appendChild(listItem);
                });

                // Update currentPods
                currentPods = newPods;
            } catch (error) {
                document.getElementById('pod-list').textContent = 'Error fetching data';
            }
        }

        async function createPod() {
            const response = await fetch('/button-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: 'create' }),
            });
            const result = await response.json();
            alert(result.reply);
        }

        async function deletePod() {
            const response = await fetch('/button-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: 'delete' }),
            });
            const result = await response.json();
            alert(result.reply);
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
            result = subprocess.check_output(["kubectl", "get", "pod", "-o", "custom-columns=:metadata.name"], text=True)
            pod_data["output"] = result.strip()
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
    if message == 'create':
        # Add your pod creation logic here
        pass
    elif message == 'delete':
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
