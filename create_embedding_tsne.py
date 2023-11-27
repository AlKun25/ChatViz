import torch
from transformers import T5Tokenizer, T5EncoderModel
from sklearn.manifold import TSNE
import numpy as np
import json
import csv
import ast

if torch.cuda.is_available():
    torch.set_default_tensor_type(torch.cuda.FloatTensor)

# Initialize the T5 model and tokenizer
encoder_model = T5EncoderModel.from_pretrained("t5-large").to("cuda")
tokenizer = T5Tokenizer.from_pretrained("t5-large")

def getEmbeddingFromText(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to("cuda")
    with torch.no_grad():
        outputs = encoder_model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
        embeddings_vec = outputs.last_hidden_state
        embeddings_mean = torch.mean(embeddings_vec, dim=1)
        return embeddings_mean.detach().cpu().numpy()[0].tolist()

def reduce_dimensions(embeddings, n_components=3):
    tsne = TSNE(n_components=n_components)
    reduced_embeddings = tsne.fit_transform(embeddings)
    return reduced_embeddings

# Reads a CSV and create embedding for each message
def read_csv_and_generate_embeddings(csv_filename, json_output_filename):
    message_data = []
    embeddings = []

    with open(csv_filename, mode="r", newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            json_content = row['content']
            message = ast.literal_eval(json_content)
            content_str = message['content']
            embedding = getEmbeddingFromText(content_str)
            embeddings.append(embedding)
            message['embedding'] = embedding
            message_data.append(message)

    # Perform dimensionality reduction on the embedding using T-SNE
    embeddings_array = np.array(embeddings)
    reduced_embeddings = reduce_dimensions(embeddings_array)

    # Update message data with reduced embeddings
    for i, message in enumerate(message_data):
        message['embedding_reduced'] = reduced_embeddings[i].tolist()

    # Save message data with reduced embeddings to JSON file
    with open(json_output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(message_data, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    read_csv_and_generate_embeddings('./data/proc/gpt-3.5-turbo.csv', 'messages_with_reduced_embeddings.json')
    
