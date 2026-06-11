import speech_recognition as sr
import pyttsx3
from chat_ai import ai_brain

engine = pyttsx3.init()

def speak(text):
    engine.say(str(text))
    engine.runAndWait()

def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return ""

while True:
    command = listen()

    if command:
        print("You:", command)
        response = ai_brain(command)
        print("AI:", response)
        speak(response)