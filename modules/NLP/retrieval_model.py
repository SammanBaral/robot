import json
from modules.NLP.preprocess_and_search import (preprocess_question, search_json) 

def answer_question(question):
    keywords = preprocess_question(question)
    results = list(search_json(museum_data, keywords))

    if not results:
        return "I'm sorry, I couldn't find information related to your question."

    # Sort results by the number of keyword matches in the path
    sorted_results = sorted(results, key=lambda x: sum(any(keyword in part.lower() for keyword in keywords) for part in x[0]), reverse=True)

    best_match = sorted_results[0]
    path, value = best_match

    # Construct the answer
    if isinstance(value, (str, int, float)):
        return f"{value}"
    elif isinstance(value, dict):
        return f"{json.dumps(value, indent=2)}"
    elif isinstance(value, list):
        return f"{', '.join(map(str, value))}"
    
# Load the JSON file
with open('knowledge_base/museum_data.json', 'r') as f:
    museum_data = json.load(f)