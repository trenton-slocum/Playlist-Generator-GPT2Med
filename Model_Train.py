import pandas as pd
from datasets import Dataset
import ast
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import Trainer, TrainingArguments
import os
import csv
import torch

df = pd.read_csv('../Additional Data/Combined_Songs_Artists.csv')

df["Playlist_Songs"] = df["Playlist_Songs"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)


def format_example(row):
    # Use the song-artist strings as-is
    playlist_body = "\n".join(row["Playlist_Songs"])
    return (
        f"### Prompt: {row['Playlist_Name']}\n"
        f"### Description: {row['Playlist_Description']}\n"
        f"### Playlist:\n{playlist_body}"
    )

df['text'] = df.apply(format_example, axis=1)

# Convert to Hugging Face Dataset
dataset = Dataset.from_dict({"text": df['text'].tolist()})

tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
tokenizer.pad_token = tokenizer.eos_token  # GPT-2 doesn't have a pad token

model = GPT2LMHeadModel.from_pretrained("gpt2-medium")
model.resize_token_embeddings(len(tokenizer))  # In case we add special tokens

# Tokenize
def tokenize(batch):
    encodings = tokenizer(batch["text"], padding="max_length", truncation=True, max_length=512)
    encodings["labels"] = encodings["input_ids"].copy()  # 🔥 Add this line
    return encodings
    
tokenized_dataset = dataset.map(tokenize, batched=True)
tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

training_args = TrainingArguments(
    output_dir="./models/gpt2_Combined_Song_Artists_Checkpoints",
    overwrite_output_dir=True,
    num_train_epochs=30,
    per_device_train_batch_size=2,
    save_steps=500,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=50,
    fp16=True if torch.cuda.is_available() else False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

trainer.train()

model.save_pretrained("./models/gpt2_Combined_Song_Artists")
tokenizer.save_pretrained("./models/gpt2_Combined_Song_Artists")