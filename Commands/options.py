# Importing all commands & features
from Commands.VolumeControl.volumeControl import mainVolControl
from Commands.Search.duckDuckGoSearch import searchDuckDuckGo
from Commands.spotifyIntegration.spotify import Spotify
from Commands.GCalendar.googleCalendar import GCalendar
from Commands.Radio.radioPlayback import RadioControl
from Commands.Translate.translate import Translator
from Commands.Weather.weatherMain import GetWeather
from Commands.Convert.unitConvert import Convert
from Commands.Timer_Alarm.timer import addTimer
from Commands.Timer_Alarm.alarm import addAlarm
from Commands.Jokes.jokes import Jokes
from time import sleep
spotifyControl = Spotify()
spotifyControl.spotifywebPlayer()



class CondensedIfStatements:
    def __init__(self):
        self.musicOptions = ['play',
                             'songs',
                             'pause',
                             ":internal:pause",
                             'continue',
                             ":internal:continue",
                             'shuffle',
                             'skip',
                             'next',
                             'stop',
                             'back',
                             ':internal:albumcoverget',  # For GUI
                             ':internal:getplayinginfo']  # For GUI
        self.whatsPlaying = ["what's playing",
                             "whats playing",
                             "what song is this",
                             "who's this",
                             "who is this"]
        self.volumeOptions = ['volume',
                              "louder",
                              "quieter",
                              "what's the volume"]
        self.weatherOptions = ['what is the weather like',
                               "what's the weather like",
                               "what's the weather",
                               "weather",
                               "what's the temperature",
                               "what's it like outside"]
        self.radioOptions = ["radio",
                             'fm',
                             'heart']
        self.countdown = ['timer', 'time']
        self.alarm = ['alarm']
        self.unitConversions = ['kilometre',
                                'metre',
                                'centimetre',
                                'millimetre',
                                'litre',
                                'millilitre',
                                'gram',
                                'kilogram',
                                'celsius',
                                'kilometres',
                                'metres',
                                'centimetres',
                                'millimetres',
                                'litres',
                                'millilitre',
                                'grams',
                                'kilogram',
                                'yard',
                                'mile',
                                'inch',
                                'ounce',
                                'pound',
                                'stone',
                                'fl ounce',
                                'fluid ounce',
                                'pint',
                                'gallon',
                                'fahrenheit',
                                'yards',
                                'miles',
                                'inches',
                                'ounces',
                                'pounds',
                                'fl ounces',
                                'fluid ounces',
                                'pints',
                                'gallons']
        self.jokeList = ['joke', 'something funny']
        self.calendar = ["what's coming up",
                         "what's my calendar",
                         "what have i got today",
                         'what have i got this month',
                         "what's in my calendar"]
        self.search = ['search', 'what']
        self.radioPlaying = False
        self.translator = Translator()
        self.radioControl = RadioControl()

    def options(self, option: str) -> str:
        """
        Parameters
        ----------
        option

        Returns
        -------
        master option control for all input of voice assistant
        """
        # Volume control
        if any(item in option for item in self.volumeOptions):
            return mainVolControl(option)

        # Stop Radio
        elif option == 'stop':
            if self.radioPlaying:
                self.radioControl.exitRadio()
                self.radioPlaying = False
            else:
                spotifyControl.musicSelections('stop')

        # Radio
        elif any(item in option for item in self.radioOptions):
            self.radioPlaying = True
            output = self.radioControl.playRadio(option.split('play ')[-1])
            return output

        # Spotify API
        elif any(i in option for i in self.musicOptions) or any(i in option for i in self.whatsPlaying):
            # Check if radio is playing, so 2 sources don't play at once
            if self.radioPlaying and ":internal:" not in option:
                self.radioControl.exitRadio()
                self.radioPlaying = False
                sleep(5)
            return spotifyControl.musicSelections(option)

        # Weather API
        elif any(i in option for i in self.weatherOptions):
            return GetWeather().getWeather(option)

        # Convert self.unitConversions
        elif any(i in option for i in self.unitConversions):
            return Convert.converter(option)

        # Set timer
        elif any(i in option for i in self.countdown):
            return addTimer(option)

        # Set self.alarm
        elif any(i in option for i in self.alarm):
            return addAlarm(option)

        # Get a joke
        elif any(i in option for i in self.jokeList):
            return Jokes().getJoke()

        # Access translate API
        elif any(i in option for i in self.translator.getLang()):
            return self.translator.translate(option)

        # Get coming up events
        elif any(i in option for i in self.calendar):
            if 'today' in option:
                return GCalendar().getInfo(days=1)
            if 'month' in option:
                return GCalendar().getInfo(days=30)
            return GCalendar().getInfo()

        # Search web
        elif any(i in option for i in self.search):
            return searchDuckDuckGo(option)

        else:
            return f":tts:Sorry, I didn't quite get that.\n I heard: {option}"