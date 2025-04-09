#!/bin/bash

nvidia-smi
echo "Get Model $My_Model"
echo "Get Topic $My_Topic"
echo "Get IP $My_IP"
echo "Get Port $My_Port"
echo "Get Control Port $My_ControlPort"

ollama serve & sleep 10

if [ "$My_Model" = 3_1_8b ]; then
    echo "MODEL_NAME=llama3.1" > .env
elif [ "$My_Model" = 3_2_3b ]; then
    echo "MODEL_NAME=llama3.2:3b" > .env
elif [ "$My_Model" = 3_2_1b ]; then
    echo "MODEL_NAME=llama3.2:1b" > .env
else
    echo "None"
    exit 1
fi
echo "TOPIC=$My_Topic" >> .env
echo "IP=$My_IP" >> .env
echo "PORT=$My_Port" >> .env
echo "CONTROL_PORT=$My_ControlPort" >> .env
python3 changeModel.py

chatchat kb -r
chatchat kb -i
chatchat start -a & sleep 10

echo "Start Server"
python3 server_compute.py
# tail -f /dev/null
