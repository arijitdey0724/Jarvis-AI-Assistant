import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
import openai
from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
newsapi = os.getenv("NEWSAPI_KEY")

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Backup speak function using pyttsx3
def speak_old(text):
    engine.say(text)
    engine.runAndWait()

# Speak using gTTS
def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')

    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    os.remove("temp.mp3")

# AI processing using OpenAI ChatGPT
def aiProcess(command):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Assistant. Give short responses."},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return "Sorry, I couldn't connect to the AI service."

# Command processing
def processCommand(c):
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
    elif c.startswith("play"):
        parts = c.split(" ")
        if len(parts) > 1:
            song = parts[1]
            link = musicLibrary.music.get(song)
            if link:
                speak(f"Playing {song}")
                webbrowser.open(link)
            else:
                speak("Sorry, I couldn't find that song.")
        else:
            speak("Please specify a song name.")
    elif "news" in c:
        speak("Fetching top news headlines...")
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}"
        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                for article in articles[:5]:
                    title = article.get("title", "No title found")
                    speak(title)
            else:
                speak("Sorry, I couldn't fetch the news.")
        except:
            speak("Something went wrong while fetching news.")
    else:
        output = aiProcess(c)
        speak(output)

# Main loop
if __name__ == "__main__":
    speak("Initializing Jarvis...")
    while True:
        try:
            print("Listening for wake word...")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)
                word = recognizer.recognize_google(audio)

            if word.lower() == "jarvis":
                speak("Yes?")
                print("Jarvis activated. Listening for your command...")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    print(f"Command received: {command}")
                    processCommand(command)

        except Exception as e:
            print(f"Error: {e}")
