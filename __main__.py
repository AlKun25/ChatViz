import os
from dataloader import filter_dataset
from preprocessing import create_message_csv

llms = [
    "palm-2",
    "gpt-3.5-turbo",
    "gpt4all-13b-snoozy",
]

# Loop through all the LLM models required
for llm in llms:
    # filters the whole dataset on the required constraints.
    if(not os.path.exists(f"./data/orig/{llm}.csv")):
        filter_dataset(model=llm, save_path="./data/orig")
    else:
        # create the message-level CSV
        if(not os.path.exists(f"./data/orig/{llm}.csv")):
            create_message_csv(model=llm)
        else:
            pass
