from unsloth import FastLanguageModel, is_bfloat16_supported
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
import pandas as pd
from datasets import Dataset
import shutil
import subprocess
import sys
import glob

def train_unsloth_lora_model(model_name: str, dataset_path: str, output_name: str):
    max_seq_length = 2048
    dtype = None
    load_in_4bit = True
    alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Input:
{}

### Response:
{}"""

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )
    EOS_TOKEN = tokenizer.eos_token

    csv_files = glob.glob(f"./dataset/{dataset_path}/qa/*.csv")
    all_dfs = [pd.read_csv(csv_file) for csv_file in csv_files]
    merged_df = pd.concat(all_dfs, ignore_index=True)
    dataset = Dataset.from_pandas(merged_df)
    def format_dataset(examples):
        texts = []
        for question, answer in zip(examples["question"], examples["answer"]):
            if not question or not answer:
                continue
            text = alpaca_prompt.format(question, answer) + EOS_TOKEN
            texts.append(text)
        return {"text": texts}
    dataset = dataset.map(format_dataset, batched=True)

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 10,
            num_train_epochs = 1,
            learning_rate = 2e-4,
            fp16 = not is_bfloat16_supported(),
            bf16 = is_bfloat16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
            report_to = "none",
        ),
    )

    gpu_stats = torch.cuda.get_device_properties(0)
    start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
    print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
    print(f"{start_gpu_memory} GB of memory reserved.")

    trainer_stats = trainer.train()

    used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
    used_percentage = round(used_memory / max_memory * 100, 3)
    lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)
    print(f"{trainer_stats.metrics['train_runtime']} seconds used for training.")
    print(f"{round(trainer_stats.metrics['train_runtime'] / 60, 2)} minutes used for training.")
    print(f"Peak reserved memory = {used_memory} GB.")
    print(f"Peak reserved memory for training = {used_memory_for_lora} GB.")
    print(f"Peak reserved memory % of max memory = {used_percentage} %.")
    print(f"Peak reserved memory for training % of max memory = {lora_percentage} %.")

    model.save_pretrained_gguf(f"./dataset/{dataset_path}/model", tokenizer, quantization_method="f16")
    shutil.copy("Modelfile", f"./dataset/{dataset_path}/model/Modelfile")
    subprocess.run(
        ["ollama", "create", output_name, "-f", f"./dataset/{dataset_path}/model/Modelfile"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )   

train_unsloth_lora_model(
    model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    dataset_path = "mental_health",
    output_name = "test"
)

model = ["meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B", "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"]


# ollama create test -f ./Modelfile
