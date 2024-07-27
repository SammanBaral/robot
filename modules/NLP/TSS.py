# import pyttsx3
# # Initialize the TTS engine
# speaker = pyttsx3.init()

# # Set properties (optional)
# speaker.setProperty('rate', 180)  # Speed of speech (words per minute)
# speaker.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

# def speak(text):
#     # Convert text to speech and play it
#     speaker.say(text)
#     # Wait for the speech to finish
#     print(f"before runAndWait")
#     speaker.runAndWait()
#     print(f"after runAndWait")

import pyttsx3

def speak(text):
    speaker = pyttsx3.init()
    speaker.setProperty('rate', 180)
    speaker.setProperty('volume', 0.6)
    print("Before speaking")
    speaker.say(text)
    speaker.runAndWait()
    print("After speaking")
    speaker.stop()