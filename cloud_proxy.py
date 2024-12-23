import os
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
import requests
import json
load_dotenv()
model_name = os.getenv("MODEL_NAME")
app = Flask(__name__)

BACKEND_URL = "http://localhost:7861"

@app.route('/bot/ragChat', methods=['POST'])
def rag_chat():
    # 取得前端傳來的 JSON 請求
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # 發送請求到後端 API
        response = requests.post(
            f"{BACKEND_URL}/chat/kb_chat",
            json={
                "query": query,
                "mode": "local_kb",
                "kb_name": "samples",
                "top_k": 3,
                "score_threshold": 0.3,
                "stream": False,
                "model": model_name,
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

        # 處理後端的回應
        if response.status_code == 200:
            response_data = response.json()
            response_data = json.loads(response_data)
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', "")
            print("|||||||||||||||||||||||||||||||")
            print(content)
            print("|||||||||||||||||||||||||||||||")
            return Response(json.dumps({"content": content}, ensure_ascii=False), mimetype='application/json')
        else:
            return jsonify({"error": "Failed to get response from backend"}), response.status_code


    except requests.exceptions.RequestException as e:
        print("Error sending request to backend:", e)
        return jsonify({"error": "Backend request failed"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000)
