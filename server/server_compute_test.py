# python server_compute_test.py topic1 192.168.60.215 8101 8100
# python server_compute_test.py topic2 192.168.60.215 8102 8100
# python server_compute_test.py topic3 192.168.60.215 8201 192.168.60.215 8200
# python server_compute_test.py topic4 192.168.60.215 8202 192.168.60.215 8200
import os
from flask import Flask, request, Response, jsonify
import requests
import json
import sys

app = Flask(__name__)

if len(sys.argv) != 5:
    print("Usage: python compute_node_server.py <topic> <ip> <port> <control_node_port>")
    sys.exit(1)

Topic = sys.argv[1]
Ip = sys.argv[2]
Port = sys.argv[3]
ControlPort = sys.argv[4]


BACKEND_URL = "http://localhost:7861"
CONTROL_NODE_URL = f"http://{Ip}:{ControlPort}"


def register_with_control_node():
    compute_node_info = {
        "topic": Topic,
        "ip": Ip,
        "port": Port,
    }
    try:
        response = requests.post(CONTROL_NODE_URL+"/add_compute_node", json=compute_node_info)
        if response.status_code == 200:
            print("Successfully registered with control node.")
        else:
            print(f"Failed to register with control node. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error registering with control node: {e}")

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "topic": Topic,
        "ip": Ip,
        "port": Port,
    }), 200

@app.route('/bot/ragChat', methods=['POST'])
def rag_chat():
    data = request.json
    query = data.get('query')
    topic = data.get('topic')

    if not query or not topic:
        return jsonify({"error": "Data loss"}), 400

    try:
        if topic == Topic:
            response = requests.post(
                f"{BACKEND_URL}/chat/kb_chat",
                json={
                    "query": query,
                    "mode": "local_kb",
                    "kb_name": "samples",
                    "top_k": 3,
                    "score_threshold": 0.3,
                    "stream": False,
                    "model": Model_name,
                    "temperature": 0.6,
                    "max_tokens": 3000,
                    "prompt_name": "default",
                    "return_direct": False,
                },
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    content = response_data.get('choices', [{}])[0].get('message', {}).get('content', "")
                    return jsonify({"content": content}), 200
                except (ValueError, KeyError) as e:
                    print(f"Error parsing response: {e}")
                    return jsonify({"error": "Invalid response format from backend"}), 500
            else:
                return jsonify({"error": "Failed to get response from backend"}), response.status_code
        else:
            response = requests.post(
                f"{CONTROL_NODE_URL}/resend_request",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            if response.status_code == 200:
                try:
                    forwarded_data = response.json()
                    content = forwarded_data.get('content', "Default response from control node")
                    return jsonify({"content": content}), 200
                except ValueError:
                    return jsonify({"error": "Invalid response from control node"}), 500
            else:
                return jsonify({"error": "Failed to get response from control node"}), response.status_code

    except requests.exceptions.RequestException as e:
        print("Error sending request to backend:", e)
        return jsonify({"error": "Backend request failed"}), 500


 
if __name__ == "__main__":
    register_with_control_node()
    app.run(debug=False, host="0.0.0.0", port=int(Port))
