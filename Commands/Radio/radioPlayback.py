from sys import platform
import webbrowser
import subprocess,os

class RadioControl:
    def __init__(self) -> None:

        self.stations = {
            "1": "bbc_radio_one",
            "2": "bbc_radio_two",
            "3": "bbc_radio_three",
            "4": "bbc_radio_four",
            "5": "bbc_radio_five"}
    # Opens the BBC sounds website to play BBC radio

    def playRadio(self, radio: str) -> str:
        """
        Parameters
        ----------
        radio
        Returns
        -------
        Plays the given BBC radio channel for the user (i.e. BBC radio 1)
        """
        radio = radio.split("radio ")[-1]
        radio = radio.replace('on','1')
        radio = radio.replace('for','4')
        radio = radio.replace('free', '3')
        try:
            webbrowser.open(f'https://www.bbc.co.uk/sounds/play/live:{self.stations[radio]}', autoraise=False)
        except Exception as e:
            print(e)
            return f':tts:Station {radio} not found'
        self.RadioPlaying = True

        if 'heart' in radio:
            self.stationPlaying = 'Heart FM'
            return ':tts:Playing Heart FM'

        self.stationPlaying = f'BBC radio {radio}'
        return f":tts:Playing BBC Radio {radio}"

    def exitRadio(self):
        self.__killBrowsers()
        webbrowser.open('http://127.0.0.1:8000/Commands/SpotifyIntegration/index.html')

    def __killBrowsers(self):
        print(os.path)
        browsers = ['firefox', 'chrome', 'chromium', 'msedge']
        if platform == 'win32':
            for browser in browsers:
                print(browser)
                subprocess.run(f'taskkill /f /im {browser}.exe')
        elif platform in ['linux', 'linux2']:
            for browser in browsers:
                subprocess.run(['pkill', '-9', browser])
        else:
            return ':tts:Platform not recognised, unable to stop radio'


if __name__ == '__main__':
    while True:
        i = input('radio: ')
        if 'stop' in i:
            RadioControl().exitRadio()
        else:
            print(RadioControl().playRadio(i))
