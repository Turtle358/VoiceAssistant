from datetime import datetime
import threading
import time
from playsound import playsound
from Commands.spotifyIntegration.spotify import Spotify

timers = []


def addTimer(originalUserTime):
    """
    Parameters
    ----------
    originalUserTime
    Returns
    -------
    Much like alarm.py, it organises time into 24hr format
    If the alarm goes past midnight, it will rap back around
    It will also assume when a time is due to come off (if after a given time - like 6pm -
    it will assume that the alarm is due the next morning)
    """
    timeNow = time.time()
    timeToAdd = 0
    userTime = originalUserTime.split(' ')
    if 'half an hour' in originalUserTime:
        timeToAdd += 1800
    elif any(item in originalUserTime for item in ['quarter hour', 'quarter of an hour']):
        timeToAdd += 900
    else:
        for i in range(len(userTime)):
            if userTime[i-1].isdigit() and userTime[i] == 'second':
                timeToAdd += int(userTime[i-1])
            if userTime[i-1].isdigit() and userTime[i] == 'minute':
                timeToAdd += int(userTime[i-1]) * 60
            if userTime[i-1].isdigit() and userTime[i] == 'hour':
                timeToAdd += int(userTime[i-1]) * 3600
    outputTime = timeNow + timeToAdd
    hours, minutes, seconds = convertToReadable(outputTime)
    timers.append(f'{str(int(hours)).zfill(2)}:{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}')
    return f':tts:Timer will end at: {str(int(hours)).zfill(2)}:{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}'


def convertToReadable(seconds):
    hours = (seconds // 3600) % 24
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return hours, minutes, seconds


def timerTracker() -> None:
    """
    Returns
    -------
    tracks the timers using subprocess
    plays alarm sound
    """
    while True:
        for i, timer in enumerate(timers):
            if datetime.now().strftime('%H:%M:%S') == timer:
                del timers[i]
                # Pause spotify playback, pass if nothing is playing
                Spotify().pausePlay('pause')
                playsound('./Commands/Timer_Alarm/TimerUp.mp3')
                Spotify().pausePlay('continue')
                # Continue Spotify payback, pass if nothing is playing
        time.sleep(1)


timerThread = threading.Thread(target=timerTracker)
timerThread.start()

if __name__ == '__main__':
    print(addTimer(input('Timer length: ')))