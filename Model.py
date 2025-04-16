import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer


## Import Saved Model and use with generate_playlist function
model = GPT2LMHeadModel.from_pretrained("./models/gpt2_Combined_Song_Artists", local_files_only = True)
tokenizer = GPT2Tokenizer.from_pretrained("./models/gpt2_Combined_Song_Artists", local_files_only = True)

tokenizer.pad_token = tokenizer.eos_token

device = torch.device('cpu')
model.to(device)


def generate_playlist(prompt, max_length=200):
    input_text = f"### Prompt: {prompt}\n### Playlist:\n"
    encoded = tokenizer(input_text, return_tensors="pt", return_attention_mask=True)
    
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    attention_mask = encoded["attention_mask"].to(model.device)

    output = model.generate(
        input_ids = input_ids.to('cpu'),
        attention_mask=attention_mask,
        max_length=max_length,
        temperature=0.9,
        top_p=0.95,
        do_sample=True,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )

    result = tokenizer.decode(output[0], skip_special_tokens=True)
    return result.split("### Playlist:\n")[1].strip()

def prompt(query):
    print(generate_playlist(query))