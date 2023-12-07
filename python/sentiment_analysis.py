'''
We will be performing sentiment analysis as well as emotion analysis(similar to sentiment)
'''
# Load model directly
from transformers import pipeline
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

# def sentiment_analysis(text: str)->list:
#     """It returns results for sentiment analysis for 3 categories : {positive, neutral, negative}

#     Args:
#         text (str): It is the sentence that needs to be evaluated

#     Returns:
#         list: It returns softmax scores for sentiment analysis categories
#     """    
#     classifier = pipeline(task="text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest", tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest", top_k=None, max_length=500, truncation=True)
#     # sentences = ["Covid cases are increasing fast!"]
#     model_outputs = classifier([text])
#     return model_outputs[0]


def sentiment_analysis(text: str)->list:
    """It returns results for sentiment analysis for 3 categories : {positive, neutral, negative}

    Args:
        text (str): It is the sentence that needs to be evaluated

    Returns:
        list: It returns softmax scores for sentiment analysis categories
    """    
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    config = AutoConfig.from_pretrained(MODEL)
    # PT
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    # model.save_pretrained(MODEL)

    text = preprocess(text)
    encoded_input = tokenizer(text, return_tensors='pt', truncation=True, max_length=500)
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    ranking = np.argsort(scores)
    ranking = ranking[::-1]
    result = []
    for i in range(scores.shape[0]):
        l = config.id2label[ranking[i]]
        s = scores[ranking[i]]
        result.append({"category": l, "value": np.round(float(s), 4)})


def emotion_analysis(text: str)->list:
    """It returns results for sentiment analysis for 3 categories : {positive, neutral, negative}

    Args:
        text (str): It is the sentence that needs to be evaluated

    Returns:
        list: It returns softmax scores for sentiment analysis categories
    """ 
    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=10)
    # sentences = ["I felt devastated after hearing the news about the crash."]
    model_outputs = classifier([text])
    return model_outputs[0]