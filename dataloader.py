'''
This file filters the dataset based on certain constraints from HuggingFace Hub, and saves them as CSVs by LLM in `data` folder.
Dataset : https://huggingface.co/datasets/lmsys/lmsys-chat-1m
Current constraints : turn < 23, language=="English", (implicit: it should have toxicity)
'''


import os
from dotenv import load_dotenv
from datasets import load_dataset
from huggingface_hub import login

load_dotenv()

hf_hub_token = os.environ["HUGGINGFACE_HUB_TOKEN"]
login(token=hf_hub_token)

# If the dataset is gated/private, make sure you have run huggingface-cli login
dataset = load_dataset("lmsys/lmsys-chat-1m", split="train")
iter_dataset = dataset
print(iter_dataset, type(iter_dataset))

# select LLM models which contain toxic message for some constraints
llm_models = [
    "palm-2",
    "gpt-3.5-turbo",
    "gpt4all-13b-snoozy",
]


for llm in llm_models:
    if llm != "vicuna-13b":
        print("For model: ", llm)
        filter_data = iter_dataset.filter(
            lambda x: x["turn"] < 23
            and x["language"] == "English"
            and x["model"] == llm
        )
        print(filter_data)
        filter_data.to_csv(f"./data/{llm}.csv")
