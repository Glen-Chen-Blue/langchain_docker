SHELL := /bin/bash

efo:
	source ./myenv/bin/activate && cd server && python server_efo.py $(P1)

control:
	source ./myenv/bin/activate && cd server && python server_control.py $(N) $(IP1) $(P1) $(IP2) $(P2)

compute:
	./build.sh $(F) $(M) $(T) $(P2) $(P3) $(G) $(N)

# make efo P1=8000
# make control N=node1 IP1=192.168.60.215 P1=8000 IP2=192.168.60.215 P2=8100
# make compute F=llm_10 M=3_1_8b T=llm P2=8100 P3=8101 G=0 N=llm_10
# make compute F=edge_computing_10 M=3_2_3b T=edge_computing P2=8100 P3=8102 G=1 N=edge_computing_10
# make compute F=empty M=3_1_8b T=test P2=8100 P3=8101 G=0 N=test



# curl -X POST "http://localhost:8101/bot/ragChat" -H "Content-Type: application/json" -d '{
#   "query": "What is edge computing?",
#   "topic": "test",
# 	"llm": false
# }'


# curl -X POST "http://localhost:8101/bot/llmChat" -H "Content-Type: application/json" -d '{
#   "query": "你是誰?"
# }'