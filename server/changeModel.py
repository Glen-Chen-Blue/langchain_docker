import yaml
import os
from dotenv import load_dotenv
load_dotenv()

with open('/app/model_settings.yaml', 'r') as file:
    config = yaml.safe_load(file)

# 更改默認模型
config['DEFAULT_LLM_MODEL'] = os.getenv("MODEL_NAME")
print("Model name changed to", config['DEFAULT_LLM_MODEL'])
# 保存更改
with open('model.yaml', 'w') as file:
    yaml.dump(config, file)
