#!/bin/bash

nvidia-smi
s1=$1
echo "Get type $s1"
# 啟動 ollama 服務並等待 10 秒
ollama serve & sleep 10

# 根據傳入的參數選擇模型並更新 .env 文件
if [ "$s1" = 3_1_8b ]; then
    echo "MODEL_NAME=llama3.1" > .env
    # ollama pull llama3.1
    # ollama pull mxbai-embed-large
elif [ "$s1" = 3_2_3b ]; then
    echo "MODEL_NAME=llama3.2:3b" > .env
    ollama run llama3.2:3b
    ollama pull mxbai-embed-large
elif [ "$s1" = 3_2_1b ]; then
    echo "MODEL_NAME=llama3.2:1b" > .env
    # ollama run llama3.2:1b
    # ollama pull mxbai-embed-large
else
    echo "None"
    exit 1
fi
python3 changeModel.py

chatchat kb -r
chatchat start -a & sleep 10

python3 edge_proxy.py
# tail -f /dev/null
