'''
This file filters the dataset based on certain constraints from HuggingFace Hub, and saves them as CSVs by LLM in `data` folder.
Dataset : https://huggingface.co/datasets/lmsys/lmsys-chat-1m
Current constraints : turn < 23, language=="English", (implicit: it should have toxicity)
'''

import os
from dotenv import load_dotenv
from datasets import load_dataset
from huggingface_hub import login

def authenticate_huggingface():
    load_dotenv()
    hf_hub_token = os.environ["HUGGINGFACE_HUB_TOKEN"]
    login(token=hf_hub_token)

def filter_dataset(model, save_path="./data"):
    authenticate_huggingface()

    # Load the dataset
    dataset = load_dataset("lmsys/lmsys-chat-1m", split="train")
    iter_dataset = dataset

    # filter the dataset
    if model != "vicuna-13b":
        print(f"For model: {model}")
        filter_data = iter_dataset.filter(
            lambda x: x["turn"] < 23
            and x["language"] == "English"
            and x["model"] == model
        )
        print(filter_data)
        csv_path = os.path.join(save_path, f"{model}.csv")
        filter_data.to_csv(csv_path)
        print(f"Filtered data saved to: {csv_path}")

