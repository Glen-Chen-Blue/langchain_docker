#!/bin/bash

if [ "$#" -ne 7 ]; then
    echo "Usage: $0 <Folder> <Model> <Topic> <control port> <compute port> <gpu> <Tag>"
    exit 1
fi

s1=$1  # Folder
s2=$2  # Model
s3=$3  # Topic
s4=$5  # Port
s5=$4  # Control Port
s6=$6  # GPU
s7=$7  # Image name
internal_ip=$(ip route get 1.1.1.1 | awk '{print $7}' | head -n 1)

if [ -z "$internal_ip" ]; then
    echo "Error: Unable to determine internal IP."
    exit 1
fi

echo "Internal IP: $internal_ip"
echo "Internal Port: $s4"
echo "Control Port: $s5"
echo "Get type $s1"
echo "Get model $s2"
echo "Get topic $s3"
echo "Get GPU $s6"
echo "Get tag $s7"

# Build the Docker image with the provided arguments
docker build \
    --build-arg Folder=$s1 \
    --build-arg Model=$s2 \
    --build-arg Topic=$s3 \
    --build-arg InternalIP=$internal_ip \
    --build-arg Port=$s4 \
    --build-arg ControlPort=$s5 \
    --no-cache \
    -f Dockerfile.test \
    -t $s7 .
# if s7 container has been created, remove it
if [ "$(docker ps -aq -f name=$s7)" ]; then
    # docker stop $s7 || echo "Warning: Failed to stop container $s7"
    docker rm -f $s7 || echo "Warning: Failed to remove container $s7"
fi
# Run the Docker container
docker run --gpus "device=$s6" -p $s4:$s4 --name $s7 $s7

#  ./build.sh llm_1 3_2_1b llm 8101 8100 llm_1


# docker network create chat
# docker run --gpus "device=0" -p 6000:$6000 --name edge edge
# docker run --gpus "device=0" --network chat -p 6000:6000 --name edge edge
# curl -X POST http://brave_liskov:6000/bot/ragChat      -H "Content-Type: application/json"      -d '{"query": "甚麼是edge computing？"}'
# docker stop $(docker ps -q)