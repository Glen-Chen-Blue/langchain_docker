import os
import re
import glob
import fitz
import torch
import numpy as np
import pandas as pd
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics import f1_score

MODEL_NAME = "microsoft/deberta-base"
MAX_LEN = 128
BATCH_SIZE = 64
EPOCHS = 5
LR = 2e-5
THRESHOLD = 0.5
MODEL_SAVE_PATH = "./deberta_multilabel_model.pt"

def extract_sentences_from_pdf(file_path):
    doc = fitz.open(file_path)
    all_text = "".join(page.get_text() for page in doc)
    all_text = all_text.replace('\n', '')
    sentences = re.split(r'[。！？!?\.]+', all_text)
    return [s.strip() for s in sentences if s.strip()]

def extract_sentences_from_folder(folder_path):
    sentence_list = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file_path.endswith(".pdf"):
            sentence_list += extract_sentences_from_pdf(file_path)
    return sentence_list

def load_qa_sentences_from_csv(folder_path):
    sentences = []
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            q = str(row.get("question", "")).strip()
            a = str(row.get("answer", "")).strip()
            if q and a:
                sentences.append(q)
                sentences.append(a)
    return sentences

def get_all_topics(dataset_dir="./dataset"):
    return [name for name in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, name))]

def build_multilabel_data(dataset_dir="./dataset"):
    topics = get_all_topics(dataset_dir)
    data = []
    for i, topic in enumerate(topics):
        label = [0] * len(topics)
        label[i] = 1
        article_path = os.path.join(dataset_dir, topic, "article")
        qa_path = os.path.join(dataset_dir, topic, "qa")
        sentences = extract_sentences_from_folder(article_path) + load_qa_sentences_from_csv(qa_path)
        data.extend({"text": s, "labels": label} for s in sentences)
    np.random.shuffle(data)
    return data, topics

class MultiLabelDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer(
            item['text'],
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors="pt"
        )
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.FloatTensor(item['labels'])
        }

class DebertaForMultiLabel(nn.Module):
    def __init__(self, model_name, num_labels):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        self.classifier = nn.Linear(self.backbone.config.hidden_size, num_labels)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_output)
        probs = torch.sigmoid(logits)
        if labels is not None:
            loss_fn = nn.BCELoss()
            loss = loss_fn(probs, labels)
            return {"loss": loss, "logits": probs}
        return {"logits": probs}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
data, topics = build_multilabel_data()
model = DebertaForMultiLabel(MODEL_NAME, len(topics)).to(device)

def train_deberta_multilabel_model():
    dataset = MultiLabelDataset(data, tokenizer, max_len=MAX_LEN)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        all_preds = []
        all_labels = []
        for batch in dataloader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids, attention_mask, labels)
            loss = outputs["loss"]
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            preds = (outputs["logits"] > THRESHOLD).int().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())
        f1 = f1_score(np.array(all_labels), np.array(all_preds), average="micro")
        print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss:.4f} - F1: {f1:.4f}")

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"模型已儲存至：{MODEL_SAVE_PATH}")
    return model, tokenizer, topics

def predict_topic(text, threshold=0.5, max_len=128, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    model.load_state_dict(torch.load(MODEL_SAVE_PATH))
    model.to(device)
    encoding = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=max_len,
        return_tensors="pt"
    )
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)
    with torch.no_grad():
        output = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = output["logits"].cpu().numpy()[0]
        preds = (probs > threshold).astype(int)
    np.set_printoptions(suppress=True, precision=2)
    print("📝 測試句子：", text.strip())
    print("📊 預測機率：", probs * 100)
    print("✅ 預測主題：", [topics[i] for i, p in enumerate(preds) if p == 1])
    return probs, preds


# model, tokenizer, topics = train_deberta_multilabel_model()
test_text = "what is panic attack?"
predict_topic(test_text, threshold=0.5, max_len=128)