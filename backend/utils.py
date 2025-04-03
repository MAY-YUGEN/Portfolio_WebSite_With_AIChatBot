import os
import random
import json
import pickle
import numpy as np
import nltk
import g4f  # Import g4f for chatbot responses
from nltk.stem import WordNetLemmatizer
from tensorflow import keras

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

# Load model and data
lemmatizer = WordNetLemmatizer()
intents_path = os.path.join(BASE_DIR, "model", "intents.json")
intents = json.load(open(intents_path))
words = pickle.load(open(os.path.join(MODEL_DIR, "words.pkl"), 'rb'))
classes = pickle.load(open(os.path.join(MODEL_DIR, "classes.pkl"), 'rb'))
model = keras.models.load_model(os.path.join(MODEL_DIR, "chatbot_model.keras"))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    ERROR_THRESHOLD = 0.95 # its can give wrong answer if it is too low
    bag = bow(sentence, words)
    res = model.predict(np.array([bag]))[0]
    print("Model Prediction Output:", res)
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if not results:
        return [{'intent': 'unknown', 'probability': '0'}]
    for r in results:
        if r[0] < len(classes):  # Ensure index is within range
            return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list if return_list else [{'intent': 'unknown', 'probability': '0'}]


def get_response(intent_list, intents_json, user_message):
    """Get response from chatbot model or use g4f if no valid response exists"""

    # If no intent is detected OR confidence is low, use g4f
    if not intent_list or float(intent_list[0]['probability']) < 0.95:
        print("No confident intent found, using g4f")  # Debugging
        return g4f_chatbot_response(user_message)

    tag = intent_list[0]['intent']

    # Ensure full question matches intent
    for intent in intents_json['intents']:
        if intent['tag'] == tag:
            for pattern in intent['patterns']:
                if pattern.lower() == user_message.lower():
                    return random.choice(intent['responses'])  # Return matched response

    # If no full match, use g4f
    print("No exact match, using g4f")  # Debugging
    return g4f_chatbot_response(user_message)


def g4f_chatbot_response(prompt):
    """Get response from g4f"""
    short_prompt = prompt + " (Reply in one or two sentences only.)"
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        provider=g4f.Provider.Free2GPT,
        messages=[{"role": "user", "content": short_prompt}]
    )
    return response
