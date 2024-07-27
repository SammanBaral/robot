import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to record and transcribe audio
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        print("Recording... Speak now.")

        recognizer.pause_threshold = 1.0
        recognizer.energy_threshold = 300

        audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
        print("Finished recording.")

        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return None