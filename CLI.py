import pickle
import warnings
# TODO -> Music (Spotify)✔      Bug check -> ✔
# TODO -> Weather (OpenWeatherMap)✔      Bug check -> ✔
# TODO -> Volume control ✔      Bug check -> ✔
# TODO -> Radio ✔      Bug check -> ✔
# TODO -> Web search (Duck w/ Bing) ✔       Bug check -> ✔
# TODO -> Voice recognition Neural Network (PyTorch) ✔       Bug check -> ✔
# TODO -> Translate ✔       Bug check -> ✔
# TODO -> Integrate it all together ✔      Bug check -> ✔
# TODO -> Jokes ✔      Bug check -> ✔
# TODO -> Timer & alarm ✔      Bug check -> ✔
# TODO -> Unit conversions ✔      Bug check -> ✔
# TODO -> Google Calendar ✔      Bug check -> ✔
# TODO -> Tkinter GUI ✔      Bug check -> ✔
# TODO -> TTS ✔      Bug check -> ✔
# Test if API keys exist


def startupChecks() -> str:
    """
    Returns
    -------
    Checks that API key files exist
    """
    try:
        with open("./assets/.keys", "rb") as file:
            output = 'True'
    # If API keys don't exist, ask for them

    except FileNotFoundError:
        output = 'False'

    try:
        with open('./assets/Spotify.keys', 'rb') as file:
            output += 'True'

    except FileNotFoundError:
        output += 'False'
    return output


def addKeys() -> None:
    with open("./assets.keys", "wb") as file:
        keys = {'Weather': input("Please enter your weather API key: "),
                'Bing': input("Please enter your Bing Search API key: "),
                'Translate': input('Please enter your Bing Translate API Key: '),
                'TTS': input('Please input your text to speech key: ')}
        pickle.dump(keys, file)


def addSpotifyKeys() -> None:
    with open('./assets/Spotify.keys', 'wb') as file:
        keys = {'spotify_id': input("Please enter your spotify Client ID: "),
                'spotify_secret': input("Please Enter your spotify Client Secret: ")}
        pickle.dump(keys, file)

    # Get user to add key to html file
    try:
        player = ''
        with open('Commands/spotifyIntegration/spotifySDKConnection.js', 'r') as webplayer:
            for line in webplayer.readlines():
                player += line
            player = player.replace('CLIENT_ID', keys["spotify_id"])

        with open('Commands/spotifyIntegration/spotifySDKConnection.js', 'w') as webplayer:
            webplayer.write(player)
    except FileNotFoundError:
        print("Please go to ./Commands/spotifyIntegration/spotifySDKConnection.js to add your client id\
        to the web page for web playback")


if __name__ == '__main__':
    if startupChecks() == 'TrueTrue':
        pass

    elif startupChecks() == 'FalseTrue':
        addKeys()

    elif startupChecks() == 'TrueFalse':
        addSpotifyKeys()

    else:
        addKeys()
        addSpotifyKeys()

# Once Checks have been performed, run the main program
from Commands.VoiceRecognition.predictAudio import PredictAudio
if __name__ == '__main__':
    warnings.warn('This code is depreciated, please use GUI.py instead', DeprecationWarning)
    asr = PredictAudio()
    while True:
        from Commands.options import CondensedIfStatements

        input('')
        CondensedIfStatements().options('pause')
        option = asr.predict()
        print(CondensedIfStatements().options(option).split(':tts:')[-1])
        if option not in ['pause', 'stop']:
            option('play')
