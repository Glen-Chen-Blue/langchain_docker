#!/bin/bash

# 检查并终止使用端口 11434, 8501, 7861 的进程
nvidia-smi
s1=$1
echo "Get type $s1"

ollama serve & sleep 10
if [ "$s1" -eq 1 ]; then
    python changeModel.py llama3.1
    ollama pull llama3.1
    ollama pull mxbai-embed-large
elif [ "$s1" -eq 2 ]; then
    python changeModel.py llama3.2:3b
    ollama run llama3.2:3b
    ollama pull mxbai-embed-large
elif [ "$s1" -eq 3 ]; then
    python changeModel.py llama3.2:1b
    ollama run llama3.2:1b
    ollama pull mxbai-embed-large
else
    echo "无效的选项"
    exit 1
fi

chatchat kb -r
chatchat start -a
