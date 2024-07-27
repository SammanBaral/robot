import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def preprocess_question(question):
    # Tokenize and POS tag the question
    tokens = word_tokenize(question.lower())
    tagged = pos_tag(tokens)
    # Keep only nouns, verbs, and adjectives
    important_words = [word for word, tag in tagged if tag.startswith(('N', 'V', 'J', 'PRP'))]
    return important_words

def search_json(data, keywords, current_path=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = current_path + [key]
            if any(keyword in key.lower() for keyword in keywords):
                yield new_path, value
            if isinstance(value, (dict, list)):
                yield from search_json(value, keywords, new_path)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = current_path + [str(i)]
            if isinstance(item, (dict, list)):
                yield from search_json(item, keywords, new_path)