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
            margin: 20px; /* Increased margin */
        }
        .pod-image {
            width: 150px; /* Increased width */
            height: 150px; /* Increased height */
            margin: 10px; /* Increased margin */
        }
        .pod-name {
            margin-top: 10px; /* Increased margin */
            font-size: 18px; /* Increased font size */
        }
        .pod-wrapper {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 40px; /* Added margin-bottom */
        }
        button {
            padding: 50px; /* Increased padding */
            font-size: 32px; /* Increased font size */
            margin-top: 40px; /* Added margin-top */
        }
    </style>
</head>
<body>
    <h1>Pod Status</h1>
    <div id="pod-images" class="pod-wrapper">Loading...</div>
    <button onclick="sendMessage()">REBOOT</button>
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
                const podOutput = data.output;
                const podImagesDiv = document.getElementById('pod-images');
                podImagesDiv.innerHTML = '';
                const podLines = podOutput.split('\\n').slice(1); // Skip the header line
                podLines.forEach(line => {
                    if (line.trim()) {
                        const columns = line.split(/\s+/);
                        const name = columns[0]; // Assuming name is in the first column
                        const status = columns[2]; // Assuming status is in the third column
                        const podContainer = document.createElement('div');
                        podContainer.className = 'pod-container';
                        const img = document.createElement('img');
                        if (status === 'Running') {
                            img.src = "{{ url_for('static', filename='images/computer_green.png') }}";
                        } else {
                            img.src = "{{ url_for('static', filename='images/computer_gray.png') }}";
                        }
                        img.className = 'pod-image';
                        const podName = document.createElement('div');
                        podName.className = 'pod-name';
                        podName.textContent = name;
                        podContainer.appendChild(img);
                        podContainer.appendChild(podName);
                        podImagesDiv.appendChild(podContainer);
                    }
                });
            } catch (error) {
                document.getElementById('pod-images').textContent = 'Error fetching data';
            }
        }

        setInterval(fetchPodData, 1000);
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
    # return render_template('index.html')
    return HTML

@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.json
    message = data.get('message', '')
    subprocess.run(['kubectl', 'delete', 'pod', '--all', '--force'], encoding='utf-8', stdout=subprocess.PIPE)
    return jsonify({'reply': f'Server received: {message}'})

@app.route('/pods')
def get_pods():
    return jsonify(pod_data)


if __name__ == '__main__':
    thread = threading.Thread(target=fetch_pod_data, daemon=True)
    thread.start()
    app.run()