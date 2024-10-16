import yaml
import sys
# 讀取 model.yaml
with open('model_setting.yaml', 'r') as file:
    config = yaml.safe_load(file)

# 更改默認模型
config['DEFAULT_LLM_MODEL'] = sys.argv[1]

# 保存更改
with open('model.yaml', 'w') as file:
    yaml.dump(config, file)
