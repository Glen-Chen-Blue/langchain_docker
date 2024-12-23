#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <Folder> <Model> <Tag>"
    exit 1
fi

# Assign command-line arguments to variables
s1=$1  # Folder
s2=$2  # Model
s3=$3  # Tag

# Build the Docker image with the provided arguments
docker build --build-arg Folder=$s1 --build-arg Model=$s2 --no-cache -f Dockerfile.test -t $s3 .


#  ./build.sh data1 3 first_test
# docker network create chat
# docker run --gpus "device=0" --network chat -p 8000:6000 --name cloud cloud
# docker run --gpus "device=0" --network chat -p 6000:6000 --name edge edge
# curl -X POST http://brave_liskov:6000/bot/ragChat      -H "Content-Type: application/json"      -d '{"query": "甚麼是edge computing？"}'
# docker stop $(docker ps -q)