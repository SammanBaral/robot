import speech_recognition as sr

recognizer = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    print("Listening for command...")
    audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"Recognized: {command}")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
