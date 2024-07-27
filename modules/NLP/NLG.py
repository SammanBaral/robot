import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure the generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def generate_ai_response(text):
    response = chat.send_message(text, stream=True)
    ai_response = ""
    for chunk in response:
        ai_response += chunk.text
    first_sentence = ai_response.split(". ")[0].strip()
    return first_sentence

def main():
    print("What's up, How may I help you?")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "thank you":
            print("Assistant: You're welcome! Exiting...")
            break
        
        ai_response = generate_ai_response(user_input)
        print(f"Assistant: {ai_response}")

# if __name__ == "__main__":
#     main()