from transformers import AutoProcessor, AutoModelForCTC
import soundfile as sf
import torch
import pyaudio
import torchaudio
import numpy as np
import requests


class PredictAudio:
    def __init__(self, path='./Commands/VoiceRecognition/savedModel'):
        self.processor = AutoProcessor.from_pretrained(path)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForCTC.from_pretrained(path).to(device)
        # load the model

        print("Model loaded successfully")
        self.numbers = {'zero': 0,
                        'one': 1,
                        'two': 2,
                        'three': 3,
                        'four': 4,
                        'five': 5,
                        'six': 6,
                        'seven': 7,
                        'eight': 8,
                        'nine': 9,
                        'ten': 10,
                        'eleven': 11,
                        'twelve': 12,
                        'thirteen': 13,
                        'fourteen': 14,
                        'fifteen': 15,
                        'sixteen': 16,
                        'seventeen': 17,
                        'eighteen': 18,
                        'nineteen': 19,
                        'twenty': 20,
                        'thirty': 30,
                        'forty': 40,
                        'fifty': 50,
                        'sixty': 60,
                        'seventy': 70,
                        'eighty': 80,
                        'ninety': 90}

    def __recordAudio(self, outputFile='./output.wav', duration=4, sampleRate=16000):
        """
        Parameters
        ----------
        outputFile
        duration
        sampleRate

        Returns
        -------
        Outputs audio file (recorded.wav)
        """
        chunk = 64
        format = pyaudio.paInt16
        channels = 1
        print('Recording audio...')

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=sampleRate, input=True, frames_per_buffer=chunk)

        frames = []
        numChunks = int(sampleRate * duration / chunk)
        for i in range(0, numChunks):
            data = stream.read(chunk)
            frames.append(data)

        print('Recording Finished')
        stream.stop_stream()
        stream.close()
        p.terminate()
        audioData = np.frombuffer(b''.join(frames), dtype=np.int16)
        sf.write(outputFile, audioData, sampleRate, format='WAV')

    def predict(self):
        self.__recordAudio()
        audioArray, _ = torchaudio.load('./output.wav', format='WAV')
        inputs = self.processor(audioArray.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**inputs).logits

        predictedIds = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predictedIds)[0]
        # Adjusting for common mistakes not picked up by autocorrect
        corrected = self.autoCorrect(transcription)
        if corrected != "":
            transcription = corrected
        transcription = transcription.replace('whatsoever', 'the weather')
        transcription = transcription.replace('vorim', 'volume')
        transcription = transcription.replace('voiim', 'volume')
        transcription = transcription.replace('what is the ever', 'what is the weather')
        transcription = transcription.replace("what's the ever", "what's the weather")
        transcription = transcription.replace('to day','today')
        transcription = self.convTosNumbers(transcription)
        return transcription

    def convTosNumbers(self, decodedText: str) -> str:
        """
        Parameters
        ----------
        decodedText
        Returns
        -------
        Converts worded number like seventeen into 17
        """
        # A little thing to prevent errors
        decodedText = 'agjhggh1 '+decodedText + ' agjhggh2'
        words = decodedText.split(' ')
        for i in range(len(words)-1, 0, -1):
            word = words[i]
            if word in self.numbers:
                num = self.numbers[word]
            else:
                num = word
            words[i] = str(num)
            if words[i].isdigit() and words[i - 1].isdigit():
                words[i - 1] = str(int(words[i]) + int(words[i - 1]))
                del words[i]
        for i, word in enumerate(words):
            if word.isdigit() and words[i+1].isdigit():
                words[i] = str(int(word) + int(words[i+1]))
                del word
                del words[i+1]
        decodedText = ' '.join(words)
        decodedText = decodedText.split('agjhggh1 ')[-1].split(' agjhggh2')[0]
        return decodedText

    def autoCorrect(self, text: str) -> str:
        # Since no audio is sent out, this is seen as secure

        URL = "https://api.typewise.ai/latest/correction/whole_sentence"
        toCorrect = {
            "session_id": "string",
            "team_uid": "string",
            "token": "string",
            "languages": ["en"],
            "text": text,
            "keyboard": "QWERTY",
            "remove_low_prob_tokens": False
        }
        request = requests.post(URL, json=toCorrect)
        if request.status_code == 200:
            correctedText = request.json()['corrected_text']
        else:
            correctedText = ""
        return correctedText.lower()


if __name__ == '__main__':
    p = PredictAudio(path='./savedModel')
    print(p.predict())
