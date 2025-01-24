# python server_control.py node1 192.168.60.215 8000 192.168.60.215 8100
# python server_control.py node2 192.168.60.215 8000 192.168.60.215 8200

from flask import Flask, request, jsonify, Response
import json
import os
import requests
import sys

app = Flask(__name__)

if len(sys.argv) != 6:
    print("Usage: python control_node_server.py <name> <ip> <port> <center_ip> <center_port>")
    sys.exit(1)

CONTROL_NODE_NAME = sys.argv[1]
CENTER_SERVER_IP = sys.argv[2]
CENTER_SERVER_PORT = sys.argv[3]
CONTROL_NODE_IP = sys.argv[4]
CONTROL_NODE_PORT = sys.argv[5]
CONTROL_NODE_FILE = f"{CONTROL_NODE_NAME}.json"

def load_data():
    if os.path.exists(CONTROL_NODE_FILE):
        with open(CONTROL_NODE_FILE, "r") as f:
            return json.load(f)
    else:
        initial_data = {"compute_node": []}
        save_data(initial_data)
        return initial_data

def save_data(data):
    with open(CONTROL_NODE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def register_with_center_server():
    control_node_info = {
        "name": CONTROL_NODE_NAME,
        "ip": CONTROL_NODE_IP,
        "port": CONTROL_NODE_PORT
    }
    try:
        response = requests.post(f"http://{CENTER_SERVER_IP}:{CENTER_SERVER_PORT}/add_control_node", json=control_node_info)
        if response.status_code == 200:
            data = response.json()  # 从响应中获取 JSON 数据
            save_data(data.get("data", {}))
            print("Successfully registered with center server.")
        else:
            print(f"Failed to register with center server. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error registering with center server: {e}")

@app.route("/check_compute_nodes", methods=["GET"])
def check_compute_nodes():
    data = load_data()
    valid_compute_nodes = []

    for compute_node in data["compute_node"]:
        if(compute_node["control_node"] != CONTROL_NODE_NAME): continue
        try:
            url = f"http://{compute_node['ip']}:{compute_node['port']}/status"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                node_info = response.json()
                node_info["control_node"] = CONTROL_NODE_NAME
                valid_compute_nodes.append(node_info)

        except Exception as e:
            print(f"Failed to contact compute node {compute_node['topic']}: {e}")
    print(valid_compute_nodes)
    return jsonify({"control_node": {
        "name": CONTROL_NODE_NAME,
        "ip": CONTROL_NODE_IP,
        "port": CONTROL_NODE_PORT
    }, "compute_node": valid_compute_nodes}), 200

@app.route("/update_nodes", methods=["POST"])
def update_nodes():
    new_data = request.json
    save_data(new_data)
    return jsonify({"message": "Nodes updated successfully."}), 200

@app.route("/add_compute_node", methods=["POST"])
def add_compute_node():
    center_server_url = f"http://{CENTER_SERVER_IP}:{CENTER_SERVER_PORT}/add_compute_node"
    new_compute_node = request.json
    new_compute_node["control_node"] = CONTROL_NODE_NAME
    print(new_compute_node)
    try:
        response = requests.post(center_server_url, json=new_compute_node)
        if response.status_code == 200:
            return jsonify({"message": "Compute node added successfully to center server.", "compute_node": new_compute_node}), 200
        else:
            return jsonify({"message": "Failed to add compute node to center server.", "status_code": response.status_code}), 400
    except Exception as e:
        return jsonify({"message": "Error contacting center server.", "error": str(e)}), 500

@app.route("/resend_request", methods=["POST"])
def resend_request():
    data = request.json
    topic = data.get("topic")
    machine_data = load_data()

    # 查找目标机器
    target_machine = next((node for node in machine_data["compute_node"] if node["topic"] == topic), None)
    if not target_machine:
        return jsonify({"error": "Machine not found."}), 400

    try:
        # 转发到目标机器的 /bot/ragChat
        response = requests.post(
            f"http://{target_machine['ip']}:{target_machine['port']}/bot/ragChat", 
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        if response.status_code == 200:
            # 直接返回目标机器的响应内容，确保格式一致
            return Response(response.text, mimetype='application/json')
        else:
            return jsonify({"error": "Failed to get response from compute node"}), response.status_code
    except Exception as e:
        return jsonify({"error": "Error contacting compute node", "details": str(e)}), 500


if __name__ == "__main__":
    register_with_center_server()
    app.run(debug=False, host="0.0.0.0", port=int(CONTROL_NODE_PORT))
