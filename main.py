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
        }
    </style>
</head>
<body>
    <ul id="pod-list">Loading...</ul>
    <script>
        async function fetchPodData() {
            try {
                const response = await fetch('/pods');
                const data = await response.json();
                const podList = data.output.split('\\n');
                const podListElement = document.getElementById('pod-list');
                podListElement.innerHTML = '';
                podList.forEach(pod => {
                    const listItem = document.createElement('li');
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
            } catch (error) {
                document.getElementById('pod-list').textContent = 'Error fetching data';
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
