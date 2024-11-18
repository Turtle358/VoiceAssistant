import requests
import pickle
import uuid


class Translator:
    def __init__(self, path='./assets/.keys'):
        with open(path, 'rb') as file:
            keys = pickle.load(file)
        
        self.KEY = keys['Translate']
        self.ENDPOINT = 'https://api.cognitive.microsofttranslator.com/translate'
    
    def translate(self, toTranslate: str, directory: str = './Commands/Translate/language.codes') -> str:
        """
        Parameters
        ----------
        toTranslate
        directory
        
        Returns
        -------
        Translates the given phrase into the given language
        """
        toTranslate = toTranslate.split('what is')[-1]
        
        with open(directory,'rb') as codes:
            lanCodes = pickle.load(codes)
            language = lanCodes[toTranslate.split(' ')[-1].title()]
    
        toTranslate = toTranslate.split(f' in {language}')[0]
        params = {
            'api-version': '3.0',
            'from': 'en',
            'to': language}
    
        headers = {
            'Ocp-Apim-Subscription-Key': self.KEY,
            'Ocp-Apim-Subscription-Region': 'uksouth',
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())}
        body = [{'text': toTranslate}]
    
        request = requests.post(self.ENDPOINT, params=params, headers=headers, json=body)
        response = request.json()[0]['translations'][0]['text']
        return f':tts:{language}|{response}'

    def getLang(self, directory: str = './Commands/Translate/language.codes') -> list:
        """
        Parameters
        ----------
        directory
        Returns
        -------
        Gets language codes from language code file
        """
        with open(directory, 'rb') as languages:
            language = pickle.load(languages)
    
        languages = [key.lower() for key in language.keys()]
        return languages


if __name__ == '__main__':
    print(Translator('../../assets/.keys').translate(input(''), directory='./language.codes'))
