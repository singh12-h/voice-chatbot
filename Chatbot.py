# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 21:41:32 2023

@author: DELL
"""
import speech_recognition as sr
from gtts import gTTS
import transformers
import os
import time
import datetime
import numpy as np
import requests
import spacy


class Chatbot():
    def __init__(self, name):
        print("----- Starting up", name, "-----")
        self.name = name
        self.nlp = spacy.load("en_core_web_sm")

    def speech_to_text(self):
        recognizer = sr.Recognizer()

        # Change the recognizer engine here
        recognizer.energy_threshold = 12000  # Adjust this threshold as needed
        with sr.Microphone() as mic:
            print("Listening...")
            audio = recognizer.listen(mic)
            self.text = "ERROR"
        try:
            self.text = recognizer.recognize_google(audio)
            print("Me  --> ", self.text)
        except:
            print("Me  -->  ERROR")


    @staticmethod
    def text_to_speech(text):
        print("Dev --> ", text)
        speaker = gTTS(text=text, lang="en", slow=False)
        speaker.save("res.mp3")
        statbuf = os.stat("res.mp3")
        mbytes = statbuf.st_size / 1024
        duration = mbytes / 200
        os.system('start res.mp3')  # if you are using mac->afplay or else for windows->start
        time.sleep(int(50 * duration))
        os.remove("res.mp3")

    def wake_up(self, text):
        return True if self.name in text.lower() else False

    @staticmethod
    def action_time():
        return datetime.datetime.now().time().strftime('%H:%M')

    def extract_entities(self, message):
        doc = self.nlp(message)
        entities = [ent.text for ent in doc.ents]
        return entities

    def get_weather(self, location):
        # Replace with your actual weather API endpoint and key
        api_key = '7cde793d37d33f6883000753f11f780d'
        url = f'https://home.openweathermap.org...'
        params = {
            'location': location,
            'apiKey': api_key,
        }
        response = requests.get(url, params=params)
        data = response.json()
        weather_info = data['weather_info']
        return f"The weather in {location} is {weather_info['description']} with a temperature of {weather_info['temperature']}°C."


# Running the AI
if __name__ == "__main__":
    ai = Chatbot(name="dev")
    nlp = transformers.pipeline("conversational", model="microsoft/DialoGPT-medium")
    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    ex = True

    while ex:
        ai.speech_to_text()

        if ai.wake_up(ai.text) is True:
            res = "Hello, I am Dave the AI. What can I do for you?"

        elif "time" in ai.text:
            res = ai.action_time()

        elif any(i in ai.text for i in ["thank", "thanks"]):
            res = np.random.choice(["You're welcome!", "Anytime!", "No problem!", "Cool!", "I'm here if you need me!", "Mention not"])

        elif any(i in ai.text for i in ["exit", "close"]):
            res = np.random.choice(["Tata", "Have a good day", "Bye", "Goodbye", "Hope to meet soon", "Peace out!"])
            ex = False

        elif "weather" in ai.text:
            entities = ai.extract_entities(ai.text)
            if entities:
                location = entities[0]  # Assuming the location is the first recognized entity
                res = ai.get_weather(location)
            else:
                res = "Please specify a location for the weather."

        else:
            if ai.text == "ERROR":
                res = "Sorry, could you please repeat that?"
            else:
                chat = nlp(transformers.Conversation(ai.text), pad_token_id=50256)
                res = str(chat)
                res = res[res.find("bot >> ") + 6:].strip()

        ai.text_to_speech(res)

    print("----- Closing down Dev -----")

