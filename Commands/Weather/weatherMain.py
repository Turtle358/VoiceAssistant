import requests
import pickle


class GetWeather:
    def __init__(self, path='./assets/.keys'):
        # Get OpenWeatherMap API key
        with open(path, 'rb') as file:
            keys = pickle.load(file)
        self.KEY = keys['Weather']
    
    def getWeather(self, option: str) -> str:
        """
        Parameters
        ----------
        option
    
        Returns
        -------
        weather information for london (default) or chosen city
        """
        # Format option
        city = option.split(" ")[-1]
        url = "http://api.openweathermap.org/data/2.5/weather"
        info = f"q={city}&APPID={self.KEY}"
        response = requests.get(f"{url}?{info}")
        weatherData = response.json()
    
        if response.status_code == 200:
            return self.formatWeather(city=city, weatherData=weatherData)
        # if city does not exist, default to London
        else:
            city = "London"
            url = "http://api.openweathermap.org/data/2.5/weather"
            info = f"q={city}&APPID={self.KEY}"
            response = requests.get(f"{url}?{info}")
            weatherData = response.json()
            if response.status_code == 200:
                return self.formatWeather(weatherData=weatherData)
            else:
                return "An Error occurred, please try again later"
    
    # Format the weather nicely
    def formatWeather(self, weatherData: dict, city: str = "london") -> str:
        city = city.title()
        temp = weatherData["main"]['temp']
        desc = weatherData['weather'][0]['description']
        humidity = weatherData['main']['humidity']
        windSpeed = weatherData['wind']['speed']
        country = weatherData["sys"]["country"]
    
        return f':tts:In {city.title()} {country}, it is currently {str(temp - 273.15)[:4]}°C, {desc},\
         with humidity of {humidity}% and a wind speed of {windSpeed}km/h'
