import requests
import pyttsx3

import datetime
import json
import speech_recognition as sr
import pocketsphinx
import json
import time
engine = pyttsx3.init('sapi5')

newVoiceRate = 100

voices= engine.getProperty('voices') #getting details of current voice

print(voices)

engine.setProperty('rate',newVoiceRate)

engine.setProperty('voice', voices[0].id)

def speak(audio):

	engine.say(audio) 

	engine.runAndWait() #Without this command, speech will not be audible to us.



with open('json_data.json', 'r') as outfile:
    data = json.load(outfile)
    print(data)

    for d in data:
	    speak(d['crypto'].split('-')[0])
	    time.sleep(3)