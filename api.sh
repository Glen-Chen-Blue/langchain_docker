curl -X 'POST' \
  'http://localhost:4000/chat/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "messages": [
    {
      "content": "你是誰",
      "role": "user"
    }
  ],
  "model": "llama3.2:1b",
  "stream": false,
  "temperature": 0.9
}
'

curl -X 'POST' \
  'http://localhost:7861/chat/kb_chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "what is p1935",
  "mode": "local_kb",
  "kb_name": "samples",
  "top_k": 3,
  "score_threshold": 0.3,
  "stream": false,
  "model": "llama3.2:1b",
  "temperature": 0.8,
  "max_tokens": 3000,
  "prompt_name": "default",
  "return_direct": false
}
'


curl -X 'POST' \
  'http://localhost:4000/knowledge_base/local_kb/samples/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "messages": [
    {
      "content": "what is edge computing",
      "role": "user"
    }
  ],
  "model": "llama3.2:1b",
  "stream": false,
  "temperature": 0.9,
  "return_direct": false
}
'