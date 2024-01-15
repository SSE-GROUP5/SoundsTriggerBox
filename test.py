from vosk import Model, KaldiRecognizer
import pyaudio
import json
from Levenshtein import distance as levenshtein_distance

model = Model(r"./vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(rate=16000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=960)
stream.start_stream()

while True:
    data = stream.read(960, exception_on_overflow=False)
    if len(data) == 0:
        break

    if len(data) == 0:
        break
    

    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        result = result["text"].lower()
        print("")
        print(result)
        leven_on = levenshtein_distance(result.strip(), "open")
        leven_off = levenshtein_distance(result.strip(), "close")
        if leven_on < 10 and leven_on < leven_off:
            print("Turn on")
        elif leven_off < 10 and leven_off < leven_on:
            print("Turn off")
    else:
        # showing spinning animation while listening for command
        print("Listening...", end="\r")

        
