import re
import pandas as pd
from datasets import load_dataset

questions = []
answers = []

def extract_strings(text):
    pattern = r"<HUMAN>: (.*?)\s*<ASSISTANT>: (.*)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

# 載入資料集
dataset = load_dataset("heliosbrahma/mental_health_chatbot_dataset", split="train")
print("原始資料筆數：", len(dataset))

# 明確逐筆處理資料
for item in dataset:
    question, answer = extract_strings(item["text"])
    if question and answer:
        questions.append(question)
        answers.append(answer)

print("成功擷取問答數：", len(questions))

# 儲存為 CSV
df = pd.DataFrame({
    "question": questions,
    "answer": answers
})
df.to_csv("./dataset/mental_health_chatbot_dataset.csv", index=False, encoding='utf-8-sig')
