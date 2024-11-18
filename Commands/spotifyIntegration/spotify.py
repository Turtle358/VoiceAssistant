import spotipy
import pickle
import time
import webbrowser
import subprocess
import random
from spotipy.oauth2 import SpotifyOAuth
from sys import platform


class Spotify:
    """
    References
    ---------
    https://spotipy.readthedocs.io/en/2.22.1/
    """
    def __init__(self, path="./assets/Spotify.keys") -> None:
        """
        Function
        --------
        This loads the api keys from the Spotify pickle and authenticates with Spotify services
        with the required scopes and stores the connection in an object
        """
        # Get keys
        with open(path, 'rb') as file:
            keys = pickle.load(file)

        # Authenticating with spotify
        authManager = SpotifyOAuth(client_id=keys['spotify_id'], client_secret=keys['spotify_secret'],
                                    redirect_uri='http://google.com/callback',
                                    scope='user-library-read,user-read-playback-state,user-modify-playback-state,\
                                    streaming,user-read-currently-playing,playlist-read-private,playlist-read-collaborative,\
                                    user-follow-read,user-top-read')

        self.sp = spotipy.Spotify(auth_manager=authManager)

    # Starting web player in your default browser
    def spotifywebPlayer(self):
        if platform == "win32":
            subprocess.Popen("python -m http.server 8000")

        elif platform == "linux" or platform == "linux2":
            subprocess.Popen(["python3", "-mhttp.server"])
        webbrowser.open('http://127.0.0.1:8000/Commands/SpotifyIntegration/index.html')

    # Spotify Commands
    def songSearch(self, song: str) -> str:
        """
        Parameters
        ----------
        song name
        Returns
        -------
        searches for and plays the song via the spotify API
        """
        try:
            # search for a track
            if 'polish cow' in song or 'polska cow' in song or 'polish cow song' in song:
                song = ['dancing polish cow']

            elif 'doom' in song:
                song = ['The only thing they fear is you']

            try:
                results = self.sp.search(q=f'track:{song[0]} artist:{song[1]}', type='track')
            except IndexError:
                results = self.sp.search(q=f'track:{song[0]}', type='track')

            trackUri = results['tracks']['items'][0]['uri']
            # play the track on the selected device
            self.sp.start_playback(device_id=self.deviceID(), uris=[trackUri])

            # Say what is playing
            try:
                # Sleep time - being the shortest time I found to work - to allow for API to reply
                # Effects of this may differ depending on internet speeds
                time.sleep(0.4)
                songInfo = self.sp.current_playback()
                return f":tts:Playing {songInfo['item']['name']} by {songInfo['item']['artists'][0]['name']}"
            except:
                return f":tts:Playing {song[0]}"

        except IndexError:
            # Little Easter egg which will play a rick roll if no song is found
            rick = ['Never gonna give you up']
            results = self.sp.search(q=f'track:{rick}', type='track')
            trackUri = results['tracks']['items'][0]['uri']
            self.sp.start_playback(device_id=self.deviceID(), uris=[trackUri])
            return f":tts:{song[0]} not found"

    def artistPlaylist(self, artist: str) -> str:
        """
        Parameters
        ----------
        artist
        --------
        This searches for the artists top mix and plays it for the user
        """
        artistName = artist.split('songs by ')[1]
        results = self.sp.search(q=f'artist:{artistName}', type='artist', limit=1)
        artist = results['artists']['items'][0]
        artistId = artist['id']
        topTracks = self.sp.artist_top_tracks(artistId)
        trackUris = []

        for track in topTracks['tracks']:
            trackUris.append(track['uri'])
            # play the track on the selected device
            self.sp.start_playback(device_id=self.deviceID(), uris=trackUris)
            return f':tts:Playing songs by {artistName.title()}'

    def userPlaylist(self) -> str:
        """
        Returns
        -------
        Plays the user's liked playlist
        """
        results = self.sp.current_user_saved_tracks()
        trackUris = [item['track']['uri'] for item in results['items']]

        # play the track on the selected device
        self.sp.start_playback(device_id=self.deviceID(), uris=trackUris)
        return ':tts:Playing your liked songs'

    def topTracks(self) -> str:
        """
        Returns
        -------
        Plays the top suggested songs for the user
        """
        results = self.sp.current_user_top_tracks(limit=20)
        topTracksPlaylist = results['items']
        trackUris = [track['uri'] for track in topTracksPlaylist]

        # play the track on the selected device
        self.sp.start_playback(device_id=self.deviceID(), uris=trackUris)

        # Enabling shuffle (if not already on)
        self.sp.shuffle(device_id=self.deviceID(), state=True)
        return ':tts:Playing your top songs'

    def onRepeat(self) -> str:
        """
        Returns
        -------
        Plays the users on repeat playlist
        """
        mixUri = None
        mixes = self.sp.current_user_playlists()

        for playlist in mixes['items']:
            if playlist['name'] == "On Repeat":
                mixUri = playlist['uri']
                break

        if mixUri:
            # play the mix using the Spotify SDK
            self.sp.start_playback(context_uri=mixUri, device_id=self.deviceID())
            return ":tts:Playing your most played songs"
        else:
            return ":tts:Mix playlist not found."

    def deviceID(self) -> str:
        """
        Returns
        -------
        Gets the device ID for the JS implementation of the spotify SDK
        """

        devices = self.sp.devices()
        deviceId = None

        for device in devices['devices']:
            if device['is_active']:
                deviceId = device['id']
                break

        # if no active device is found, use the first available device
        for device in devices['devices']:
            if device['name'] == 'Voice Assistant':
                deviceId = device['id']
                break
        return deviceId

    def pausePlay(self, option: str) -> str:
        """
        Parameters
        ----------
        option: pause || continue
        Returns
        -------
        Will pause or continue playback, depending on the user's input
        """
        if option in ['pause', 'stop']:
            try:
                self.sp.pause_playback(device_id=self.deviceID())
            except:
                return ':tts:Nothing is playing'

        elif option == 'continue':
            self.sp.start_playback(device_id=self.deviceID())
        return ""

    def skipBack(self, option: str) -> str:
        """
        Parameters
        ----------
        option: skip || back || previous
        """
        if option in ['skip', 'next']:
            self.sp.next_track(device_id=self.deviceID())

        elif option in ['back', 'previous']:
            self.sp.previous_track(device_id=self.deviceID())

        elif option == 'shuffle':
            self.sp.shuffle(device_id=self.deviceID(), state=True)
            # Monkey patch, to fix it not resuming after shuffling
            self.pausePlay('play')
            return ":tts:Shuffle mode activated"

        return ""
    
    def whatsPlaying(self, option: str) -> str:
        """
        Parameters
        ----------
        option
        Returns
        -------
        what is currently playing in spotify (if audio is playing)
        """
        try:
            # Gets Current Playback info and formats it for artist name, album cover and song name
            result = self.sp.current_playback()
            artist = result['item']['artists'][0]['name']
            songName = result['item']['name']

            if option in ['who is this', "who's this", "whos this"]:
                output = f'This is {songName} by {artist.title()}'

            else:
                output = f'Currently playing {songName} by {artist.title()}\n'
            return f':tts:{output}'

        except:
            # If nothing is playing, to prevent crashes
            return ":tts:Nothing is currently playing"

    def getAlbumCover(self) -> str:
        """
        Returns
        -------
        Gets album cover URL for the GUI
        """
        result = self.sp.current_playback()
        albumCover = result['item']['album']['images'][0]['url']
        return albumCover

    def getCurrentPlayback(self) -> str:
        """
        Returns
        -------
        Gets what's currently playing for GUI
        """
        try:
            result = self.sp.current_playback()
            artist = result['item']['artists'][0]['name']
            songName = result['item']['name']
            return f'{songName}\n- {artist}'

        except:
            return ''

    def audioPlaying(self) -> bool:
        """
        Returns
        -------
        Checks if audio is playing for GUI
        """

        # Check if Audio is playing
        results = self.sp.current_playback()
        try:
            device = results['device']['name']
            if device == 'Voice Assistant':
                return True
            return False

        except TypeError:
            return False

    def currentPlayingSong(self) -> str:
        try:
            result = self.sp.current_playback()
            songName = result['item']['name']
            return songName
        except:
            return ''

    def musicSelections(self, option) -> str:
        """
        Parameters
        ----------
        options for music
        Returns
        -------
        returns to any of the spotify related functions
        """
        try:
            option = option.lower().split('on spotify')[0].split("?")[0]
            # Changing formatting
            if 'play ' in option:
                option = option.split('play ')[1]

            # User didn't give a option
            if option == 'play' or option == ':internal:play':
                output = 'What would you like to play?'

            elif "songs by " in option:
                output = self.artistPlaylist(option)

            # Play the users liked playlist
            elif any(i in option for i in ["my playlist", "my songs", "my liked songs", 'my play list']):
                output = self.userPlaylist()

            # Play/ Pause
            elif any(i in option for i in ["pause", "continue", "stop", ':internal:pause', ':internal:play']):
                output = self.pausePlay(option.replace(':internal:', ''))

            elif option == 'skip' or option == 'back' or option == 'shuffle' or option == 'next':
                output = self.skipBack(option)

            # Top tracks
            elif 'top tracks' in option or 'music' in option:
                tmp = random.randint(0, 1)

                if tmp == 0:
                    output = self.topTracks()

                else:
                    output = self.onRepeat()

            # Currently Playing
            elif any(i in option for i in ["what's playing",
                                           "whats playing",
                                           "stop",
                                           "what is this",
                                           'who is this',
                                           "who's this"]):
                output = self.whatsPlaying(option)

            # Functions used internally
            elif option == 'AudioCheck':
                self.audioPlaying()

            elif option == ':internal:albumcoverget':
                return self.getAlbumCover()

            elif option == ':internal:getplayinginfo':
                return self.getCurrentPlayback()

            elif option == ':internal:currentplayingsong':
                return self.currentPlayingSong()

            # Search for song
            else:
                # More formatting...
                if ", " in option:
                    option = option.split(", ")
                else:
                    option = option.split(" by ")
                output = self.songSearch(option)
            return output
        except:
            return ':tts:No devices found'

