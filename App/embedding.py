import os
import glob
import requests
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd
from langchain.schema import Document


model_name = "nomic-embed-text"
class OllamaEmbeddings(Embeddings):
    def __init__(self, model: str = model_name):
        self.model = model
    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]
    def embed_query(self, text):
        return self._embed(text)
    def _embed(self, text: str):
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        return response.json()["embedding"]


def build_faiss_from_pdfs(topic: str):
    pdf_files = glob.glob(os.path.join("dataset", topic, "article", "*.pdf"))
    all_documents = []
    for pdf in pdf_files:
        loader = PyPDFLoader(pdf)
        documents = loader.load()
        all_documents.extend(documents)

    csv_files = glob.glob(os.path.join("dataset", topic, "qa", "*.csv"))
    all_dfs = [pd.read_csv(csv_file) for csv_file in csv_files]
    merged_df = pd.concat(all_dfs, ignore_index=True)

    for _, row in merged_df.iterrows():
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()
        if question and answer:
            qa_text = f"Question：{question}\nAnswer：{answer}"
            all_documents.append(Document(page_content=qa_text, metadata={"source": "qa"}))

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(all_documents)

    embedding = OllamaEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embedding)
    save_path = os.path.join("dataset", topic, "embedding")
    vectorstore.save_local(save_path)
    print(f"已建立並儲存向量庫到：{save_path}")



def search_similar_documents(topic: str, query: str, top_k: int = 5):
    embedding = OllamaEmbeddings()
    vectorstore = FAISS.load_local(
        f"./dataset/{topic}/embedding",
        embedding,
        allow_dangerous_deserialization=True
    )
    results = vectorstore.similarity_search(query, k=top_k)
    result_texts = []
    for i, doc in enumerate(results, 1):
        print(f"--- 結果 {i} ---")
        print(doc.page_content)
        print()
        result_texts.append(doc.page_content)
    return result_texts


build_faiss_from_pdfs(topic = "mental_health")