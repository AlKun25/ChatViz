import pandas as pd
import json

conv_csv_cols = ['conversation_id','model','conversation','turn','language','openai_moderation','redacted']
msg_csv_cols = ['message_id', 'model', 'turn', 'role', 'content', 'toxicity', 'openai_moderation']


def conversation_to_messages(conv: list[dict], id: str, model: str, openai_moderation:str) -> pd.DataFrame:
    """
    Convert a conversation represented as a list of dictionaries of messages into a DataFrame of messages.

    Args:
        conv (list[dict]): List of dictionaries representing a conversation.
        id (str): Unique identifier for the conversation.
        model (str): LLM name associated with the conversation.
        openai_moderation (str): Moderation/toxicity information for all messages in conversation.

    Returns:
        pd.DataFrame: DataFrame containing messages extracted from the conversation.
    """    
    df = pd.DataFrame(
        columns=msg_csv_cols # embedding and openai_moderation can be added as columns
    )
    messages = []
    for i in range(len(conv)):
        message_turn = i//2 + 1
        is_toxic = openai_moderation[i]["flagged"]
        new_message = {
            'message_id': id+"_"+str(i),
            'model': model,
            'turn': message_turn, 
            'role': conv[i]['role'], 
            'content': conv[i],
            'toxicity': is_toxic,
            'openai_moderation': openai_moderation[i],
            # embeddings can be created for assistant messages or None in other cases
            # conditional moderation value can be added for message of toxic conversations or None in other cases
        }
        messages.append(new_message)
    df = pd.concat([df, pd.DataFrame(messages, columns=msg_csv_cols)])
    df.set_index(['message_id']).index.is_unique
    return df


def create_message_csv(model: str) -> None:
    """
    Process original LLM-specific conversation data and create a CSV file containing individual extracted messages.

    Args:
        model (str): LLM name associated with the conversation data.
    """
    df_orig = pd.read_csv(f"data/orig/{model}.csv")
    df_proc = pd.DataFrame(
        columns=msg_csv_cols,
    )
    for i in range(len(df_orig)):
        conv_list = eval(df_orig.conversation[i].replace("}", "},"))
        moderation = eval((df_orig.openai_moderation[i]).replace("}", "},").replace("},,", "},"))
        
        df_proc = pd.concat([df_proc,
            conversation_to_messages(
                conv=conv_list,
                id=df_orig.conversation_id[i],
                model=df_orig.model[i],
                openai_moderation = moderation
            )],
            ignore_index=True,
        )
    df_proc.to_csv(f"./data/proc/{model}.csv", index=False)
    print(model,":",len(df_proc))


llm_models = [
    "palm-2",
    "gpt-3.5-turbo",
    "gpt4all-13b-snoozy",
]
for llm in llm_models:
    create_message_csv(model=llm)