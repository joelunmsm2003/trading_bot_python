import requests
import pyttsx3

import datetime
import json
import speech_recognition as sr
import pocketsphinx
engine = pyttsx3.init('sapi5')

newVoiceRate = 100

voices= engine.getProperty('voices') #getting details of current voice

print(voices)

engine.setProperty('rate',newVoiceRate)


engine.setProperty('voice', voices[0].id)

def speak(audio):

	engine.say(audio) 

	engine.runAndWait() #Without this command, speech will not be audible to us.


cry=requests.get('http://app01.comunica7.com:5500/api/v1/cryptos')	

for c in json.loads(cry.text)['results']:



	if c['nombre']=='bitcoin':



		if float(c['precio'])<56000:

			speak('es momento de comprar')

