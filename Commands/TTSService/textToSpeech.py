import pickle
import azure.cognitiveservices.speech as speechsdk


class TTS:
    def __init__(self, keyDir: str = './assets/.keys') -> None:
        """
        References: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/index-text-to-speech
        """
        with open(keyDir, 'rb') as file:
            keys = pickle.load(file)
        self.key = keys['TTS']
        self.region = 'uksouth'

    def __textToSpeech(self, text: str) -> None:
        if "|" in text:
            lang = text.split('|')[0]
            text = text.split('|')[1]
            with open('./Commands/TTSService/lan.codes', 'rb') as codes:
                voices = pickle.load(codes)
            voice = voices.get(lang, 'en-GB-LibbyNeural')
        else:
            voice = 'en-GB-LibbyNeural'

        # Config audio to use default speaker and pass though api key and correct region
        speechConfig = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
        audioConfig = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        # Choose the language of the tts service
        speechConfig.speech_synthesis_voice_name = voice
        speechSynthesiser = speechsdk.SpeechSynthesizer(speech_config=speechConfig, audio_config=audioConfig)
        speechSynthesiser.speak_text_async(text).get()

    def synthesiseSpeech(self, text: str) -> None:
        text = text.split(':tts:')[-1]
        if ':wait:' in text:
            pt1 = text.split(':wait:')[0]
            pt2 = text.split(':wait:')[1]
            self.__textToSpeech(pt1)
            self.__textToSpeech(pt2)

        else:
            self.__textToSpeech(text)


if __name__ == '__main__':
    while True:
        TTS(keyDir='./.keys').synthesiseSpeech(input('Please enter your text: '))
