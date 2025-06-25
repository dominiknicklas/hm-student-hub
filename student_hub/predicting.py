import tensorflow as tf
import numpy as np
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "toxicity.keras")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.keras")

vectorizer = None
model = None

def load_model_and_vectorizer():
    global model, vectorizer

    # Loads the pre-trained toxicity model (automatically when this module is imported)
    model = tf.keras.models.load_model(MODEL_PATH)

    # Loads the pre-trained vectorizer (automatically when this module is imported)
    vectorizer = tf.keras.models.load_model(VECTORIZER_PATH)
    #with open(VECTORIZER_PATH, 'rb') as f:
    #    vectorizer = pickle.load(f)


def is_toxic(comment: str):
    """
    Checks if a comment is toxic based on the model's predictions.
    If any predicted toxicity score exceeds 0.3, the comment is considered toxic.

    Args:
        comment (str): The comment to check.

    Returns:
        result (bool): True if the comment is toxic, False otherwise.
    """

    toxicity_score = predict_toxicity(comment)
    for score in toxicity_score.values():
        if score > 0.3: return True
    return False

def predict_toxicity(input_data: str):
    """
    Predicts the toxicity of a given input comment using a pre-trained model.

    Args:
        input_data (str): The comment to analyze.

    Returns:
        prediction (dict): A dictionary with predicted toxicity scores for categories such as
            'toxic', 'severe_toxic', 'obscene', 'threat', 'insult', and 'identity_hate'.
    """

    global model, vectorizer
    if model is None or vectorizer is None:
        raise RuntimeError("Model and vectorizer must be loaded first using load_model_and_vectorizer()")
    
    # Vectorize the input data (comment)
    input_str = vectorizer(input_data)
    
    # Predicts the toxicity levels of the comment using the pre-trained model
    res = model.predict(np.expand_dims(input_str, 0))
    return {"toxic": res.tolist()[0][0],
            "severe_toxic": res.tolist()[0][1],
            "obscene": res.tolist()[0][2],
            "threat": res.tolist()[0][3],
            "insult": res.tolist()[0][4],
            "identity_hate": res.tolist()[0][5],
            }