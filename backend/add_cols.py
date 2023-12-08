import os
import pandas as pd

from sentiment_analysis import sentiment_analysis
from preprocessing import num_tokens_from_string

llms = ["palm-2", "gpt-3.5-turbo", "gpt4all-13b-snoozy"]
dir_path = "/Users/kunalmundada/Documents/code/ChatViz/frontend/data/proc"

for llm in llms:
    file_path = os.path.join(dir_path, llm+".csv")
    df = pd.read_csv(file_path)
    df["sentiment"] = df["content"].apply(sentiment_analysis)
    df["token"] = df["content"].apply(num_tokens_from_string)
    df.to_csv(file_path, index=False)