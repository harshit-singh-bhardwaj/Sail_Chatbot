import openai
import pandas as pd
import os
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

nltk.download('stopwords')
nltk.download('wordnet')

openai.api_key = os.getenv("OPENAI_API_KEY")

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    words = text.split()
    words = [word for word in words if word not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)

def load_data():
    try:
        data = pd.read_csv('data/sail_faq.csv')
    except FileNotFoundError:
        data = pd.DataFrame({
            'Level1': ['About SAIL'],
            'Level2': ['Vision'],
            'Level3': ['-'],
            'Response': ['SAIL aims to be a leading steel producer.']
        })
    return data

def train_and_save_model(data):
    try:
        print("Training model...")
        with open('model/sail_tree.pkl', 'wb') as f:
            pickle.dump(data, f)
        print("Model saved!")
    except Exception as e:
        print(f"Error during training: {e}")

def load_model():
    with open('model/sail_tree.pkl', 'rb') as f:
        return pickle.load(f)

def get_next_level_options(user_input, data):
    user_input = user_input.strip().lower()
    level1_options = data['Level1'].dropna().unique()
    level2_options = data['Level2'].dropna().unique()
    level3_options = data['Level3'].dropna().unique()

    if user_input in [opt.lower() for opt in level1_options]:
        filtered = data[data['Level1'].str.lower() == user_input]
        return list(filtered['Level2'].dropna().unique())

    elif user_input in [opt.lower() for opt in level2_options]:
        filtered = data[data['Level2'].str.lower() == user_input]
        return list(filtered['Level3'].dropna().unique())

    elif user_input in [opt.lower() for opt in level3_options]:
        filtered = data[data['Level3'].str.lower() == user_input]
        if not filtered.empty:
            return filtered.iloc[0]['Response']

    return None

def get_generative_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response['choices'][0]['text'].strip()

def chatbot_response(user_input):
    try:
        data = load_model()
    except FileNotFoundError:
        data = load_data()
        train_and_save_model(data)
        data = load_model()

    result = get_next_level_options(user_input, data)

    if isinstance(result, list):
        if result:
            return {
                "response": "Please choose one of the following options:",
                "dropdown": result
            }
        else:
            return {
                "response": "No further options available.",
                "dropdown": None
            }

    elif isinstance(result, str):
        return {
            "response": result,
            "dropdown": None
        }

    else:
        return {
            "response": get_generative_response(user_input),
            "dropdown": None
        }

