'''
We will be performing sentiment analysis as well as emotion analysis(similar to sentiment)
'''
# Load model directly
from transformers import pipeline

def sentiment_analysis(text: str)->list:
    """It returns results for sentiment analysis for 3 categories : {positive, neutral, negative}

    Args:
        text (str): It is the sentence that needs to be evaluated

    Returns:
        list: It returns softmax scores for sentiment analysis categories
    """    
    classifier = pipeline(task="text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest", top_k=None)
    # sentences = ["Covid cases are increasing fast!"]
    model_outputs = classifier([text])
    return model_outputs[0]


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