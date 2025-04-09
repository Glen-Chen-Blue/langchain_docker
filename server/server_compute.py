import os
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
import requests
import json
load_dotenv()
Model_name = os.getenv("MODEL_NAME")
Topic = os.getenv("TOPIC")
Ip = os.getenv("IP")
Port = os.getenv("PORT")
ControlPort = os.getenv("CONTROL_PORT")

app = Flask(__name__)


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
    llm = data.get('llm')
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
                    "score_threshold": 0,
                    "stream": False,
                    "model": Model_name,
                    "temperature": 0.2,
                    "max_tokens": 1,
                    "prompt_name": "default",
                    "return_direct": not llm,
                },
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if isinstance(response_data, str):
                        response_data = json.loads(response_data)
                    if llm:
                        content = response_data.get('choices', [{}])[0].get('message', {}).get('content', "")
                    else:
                        content = "hello"
                    return Response(
                        json.dumps({"content": content}, ensure_ascii=False),
                        status=200,
                        mimetype='application/json'
                    )
                    
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
                    return Response(
                        json.dumps({"content": content}, ensure_ascii=False),
                        status=200,
                        mimetype='application/json'
                    )
                except ValueError:
                    return jsonify({"error": "Invalid response from control node"}), 500
            else:
                return jsonify({"error": "Failed to get response from control node"}), response.status_code

    except requests.exceptions.RequestException as e:
        print("Error sending request to backend:", e)
        return jsonify({"error": "Backend request failed"}), 500


@app.route('/bot/llmChat', methods=['POST'])
def llm_chat():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "Data loss"}), 400
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat/chat/completions",
            json={
                "messages": [
                    {
                        "content": query,
                        "role": "user"
                    }
                ],
                "model": Model_name,
                "stream": False,
                "temperature": 0.2,
                "max_tokens": 1,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        if response.status_code == 200:
            try:
                response_data = response.json()
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                content = response_data.get('choices', [{}])[0].get('message', {}).get('content', "")
                return Response(
                    json.dumps({"content": content}, ensure_ascii=False),
                    status=200,
                    mimetype='application/json'
                )
            except (ValueError, KeyError) as e:
                print(f"Error parsing response: {e}")
                return jsonify({"error": "Invalid response format from backend"}), 500
        else:
            return jsonify({"error": "Failed to get response from backend"}), response.status_code

    except requests.exceptions.RequestException as e:
        print("Error sending request to backend:", e)
        return jsonify({"error": "Backend request failed"}), 500
    

    
if __name__ == "__main__":
    print(f"Starting compute node on {Ip}:{Port}")
    register_with_control_node()
    app.run(debug=False, host="0.0.0.0", port=int(Port))
