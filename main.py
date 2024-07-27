from modules.NLP.STT import record_and_transcribe
from modules.NLP.create_JSON import create_museum_json
from modules.NLP.retrieval_model import answer_question
from modules.NLP.TSS import speak
from modules.NLP.NLG import generate_ai_response

def main():
    create_museum_json()
    speak("Hello, I am Nitro, your museum assistant, shall we start the tour ?")

    while True:
        user_question = record_and_transcribe()
        if user_question is None:
            speak("I didn't quite get it. Please repeat.")
            continue

        # Step 4: Use the answer_question function
        retrieved_answer = answer_question(user_question)
        print(f"Step 4: Context from answer_question: {retrieved_answer}")

        # Step 5: Generate AI response
        prompt = f"Question: {user_question}, context: {retrieved_answer}, based on context answer the question asked in humanly response"
        ai_response = generate_ai_response(prompt)

        speak(ai_response)

        # Ask if the user wants to continue
        print("Do you have any more questions? (yes/no)")
        speak("Do you have any more questions?")
        continue_response = record_and_transcribe()
        if continue_response and continue_response.lower() != "yes":
            break

    print("Thank you for using the museum assistant. Goodbye!")
    speak("Thank you for using the museum assistant. Goodbye!")



if __name__ == "__main__":
    main()