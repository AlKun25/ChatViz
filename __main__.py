import os
from dotenv import load_dotenv
from dataloader import filter_dataset
from preprocessing import create_message_csv

load_dotenv()

original_data_dir = os.environ["ORIGINAL_CSV_DIR"]
processed_data_dir = os.environ["PROCESSED_CSV_DIR"]

llms = [
    "palm-2",
    "gpt-3.5-turbo",
    "gpt4all-13b-snoozy",
]

# Loop through all the LLM models required
for llm in llms:
    # filters the whole dataset on the required constraints.
    if(not os.path.exists(os.path.join(original_data_dir, f"{llm}.csv"))):
        filter_dataset(model=llm, save_path=original_data_dir)
    else:
        # create the message-level CSV
        if(not os.path.exists(os.path.join(processed_data_dir, f"{llm}.csv"))):
            create_message_csv(model=llm, save_path=processed_data_dir, load_path=original_data_dir)
        else:
            pass
