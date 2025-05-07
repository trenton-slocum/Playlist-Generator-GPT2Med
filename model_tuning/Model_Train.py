import pandas as pd
from datasets import Dataset
import ast
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import Trainer, TrainingArguments
import os
import csv
import torch

df = pd.read_csv('../Additional Data/Combined_Songs_Artists.csv') ## Use the correct path to your CSV file

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

# Split the dataset into training and evaluation sets
# The dataset is split into 90% training and 10% evaluation
split_dataset = tokenized_dataset.train_test_split(test_size=0.1)
train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

# Define the training arguments
training_args = TrainingArguments(
    output_dir="./Models/gpt2_Combined_Song_Artists_Eval_Checkpoints",
    overwrite_output_dir=True,
    eval_strategy='steps',
    eval_steps=100,
    num_train_epochs=20,
    per_device_train_batch_size=2,
    save_steps=500,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=50,
    fp16=True if torch.cuda.is_available() else False,
    load_best_model_at_end=True,
    metric_for_best_model='loss',
    greater_is_better=False
    
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Train the model
trainer.train()

model.save_pretrained("./Models/gpt2_Combined_Song_Artists")
tokenizer.save_pretrained("./Models/gpt2_Combined_Song_Artists")