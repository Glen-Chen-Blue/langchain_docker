# python server_efo.py 8000
from flask import Flask, request, jsonify, after_this_request
import json
import os
import requests
import sys

app = Flask(__name__)

DATA_FILE = "efo.json"
CENTER_NODE_IP = sys.argv[1]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        initial_data = {"control_node": [], "compute_node": []}
        save_data(initial_data)
        return initial_data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def broadcast_nodes(name=None):
    print("Broadcasting nodes...")
    data = load_data()
    control_nodes = data["control_node"]
    for control_node in control_nodes:
        if name and control_node["name"] == name:
            continue
        try:
            print(f"Broadcasting to {control_node['name']}...")
            url = f"http://{control_node['ip']}:{control_node['port']}/update_nodes"
            response = requests.post(url, json=data)
            control_node["broadcast_status"] = response.status_code
        except Exception as e:
            control_node["broadcast_status"] = "failed"
            print(f"Failed to broadcast to {control_node['name']}: {e}")
    save_data(data)

@app.route("/add_control_node", methods=["POST"])
def add_control_node():
    data = load_data()
    new_node = request.json
    data["control_node"] = [node for node in data["control_node"] if node["name"] != new_node["name"]]
    data["control_node"].append(new_node)
    save_data(data)
    return jsonify({"message": "Control node added successfully.", "data": data}), 200

@app.route("/add_compute_node", methods=["POST"])
def add_compute_node():
    data = load_data()
    compute_data = request.json
    print(compute_data)
    if not compute_data:
        return jsonify({"message": "Invalid data: Compute_data error"}), 400
    data["compute_node"] = [node for node in data["compute_node"] if node["ip"] != compute_data["ip"] or node["port"] != compute_data["port"]]
    data["compute_node"].append(compute_data)
    save_data(data)
    @after_this_request
    def trigger_broadcast(response):
        broadcast_nodes()
        return response
    print("hello")
    return jsonify({"message": "Compute nodes updated successfully."}), 200

@app.route("/check_all_nodes", methods=["GET"])
def check_all_nodes():
    data = load_data()
    control_nodes = data["control_node"]
    updated_compute_nodes = []
    valid_control_nodes = []

    for control_node in control_nodes:
        try:
            url = f"http://{control_node['ip']}:{control_node['port']}/check_compute_nodes"
            response = requests.get(url)
            if response.status_code == 200:
                node_data = response.json()
                updated_compute_nodes.extend(node_data.get("compute_node", []))
                valid_control_nodes.append(control_node)
        except Exception as e:
            print(f"Failed to contact control node {control_node['name']}: {e}")

    data["compute_node"] = updated_compute_nodes
    data["control_node"] = valid_control_nodes
    save_data(data)
    broadcast_nodes()
    return jsonify({"message": "Check all nodes complete.", "data": data}), 200

# curl -X GET http://localhost:8000/check_all_nodes

@app.route("/broadcast_nodes", methods=["POST"])
def broadcast_nodes_api():
    broadcast_nodes()
    return jsonify({"message": "Broadcast complete."}), 200


if __name__ == "__main__":
    load_data()
    app.run(debug=False, host="0.0.0.0", port=CENTER_NODE_IP)
