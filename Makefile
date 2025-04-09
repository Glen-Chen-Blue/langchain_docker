SHELL := /bin/bash

efo:
	source ./myenv/bin/activate && cd server && python server_efo.py $(P1)

control:
	source ./myenv/bin/activate && cd server && python server_control.py $(N) $(IP1) $(P1) $(IP2) $(P2)

compute:
	./build.sh $(F) $(M) $(T) $(P2) $(P3) $(G) $(N) > ./log/$(N).log 2>&1 &

# make efo P1=8000
# make control N=node1 IP1=192.168.60.215 P1=8000 IP2=192.168.60.215 P2=8100
# make compute F=llm_10 M=3_1_8b T=llm P2=8100 P3=8101 G=0 N=llm_10
# make compute F=edge_computing_10 M=3_2_3b T=edge_computing P2=8100 P3=8102 G=1 N=edge_computing_10
# make compute F=empty M=3_1_8b T=problem P2=8100 P3=8101 G=0 N=problem


# make compute F=empty M=3_2_1b T=no P2=8100 P3=8101 G=0 N=empty
# make compute F=rag_10 M=3_1_8b T=rag P2=8100 P3=8102 G=0 N=rag_10
# make compute F=edge_computing_100 M=3_1_8b T=edge_computing P2=8100 P3=8103 G=0 N=edge_computing_100
# make compute F=llm_1000 M=3_1_8b T=llm P2=8100 P3=8104 G=0 N=llm_1000
# make compute F=all M=3_1_8b T=all P2=8100 P3=8105 G=0 N=all


# curl -X POST "http://localhost:8101/bot/ragChat" -H "Content-Type: application/json" -d '{
#   "query": "What is edge computing?",
#   "topic": "all",
# 	"llm": false
# }'


# curl -X POST "http://localhost:8102/bot/llmChat" -H "Content-Type: application/json" -d '{
#   "query": "你是誰?"
# }'