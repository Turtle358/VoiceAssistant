from datetime import datetime
import threading
import time
from playsound import playsound
from Commands.spotifyIntegration.spotify import Spotify

alarms = []
afternoonTimes = ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']


def formatTime(userTime: str) -> dict:
    """
    Parameters
    ----------
    userTime
    Returns
    -------
    Formats the time into the 24hr format
    """
    alarm = ''.join(item for item in userTime if item.isdigit()).zfill(4)
    hour = int(alarm[:2])
    minute = int(alarm[2:])

    if any(item in str(hour) for item in afternoonTimes):
        hour = hour - 12

    if 'half' in userTime:
        hour = userTime.split('half ')[1]
        return {'hour': hour, 'minute': 30, 'second': 00}

    elif 'quarter past' in userTime:
        hour = userTime.split('past ')[1]
        return {'hour': hour, 'minute': 15, 'second': 00}

    elif 'quarter to' in userTime:
        hour = int(''.join(item for item in userTime if item.isdigit()))
        return {'hour': hour, 'minute': 45, 'second': 00}

    return {'hour': hour, 'minute': minute % 60, 'second': datetime.now().strftime('%S')}


def addAlarm(usrTime) -> str:
    """
    Parameters
    ----------
    usrTime
    Returns
    -------
    Adds alarm to the list of alarms that are being kept track off
    """
    currentHour = int(datetime.now().strftime('%H'))
    formattedTime = formatTime(usrTime)

    if 'am' in usrTime and formattedTime['hour'] <= 12:
        hour = formattedTime['hour']

    elif 'pm' in usrTime and formattedTime['hour'] <= 12:
        hour = (formattedTime['hour'] + 12) % 24

    elif 'tomorrow' in usrTime:
        hour = (formattedTime['hour'])

    elif currentHour >= 12 >= formattedTime['hour']:
        hour = formattedTime['hour'] + 12

    else:
        hour = formattedTime['hour']

    alarms.append(f'{hour}:{str(formattedTime["minute"]).zfill(2)}:00')
    alarmThread = threading.Thread(target=alarmTracker)
    alarmThread.start()

    return f':tts:Alarm set for {hour}:{str(formattedTime["minute"]).zfill(2)}'

def alarmTracker() -> None:
    """
    Returns
    -------
    tracks the timers using subprocess
    plays alarm sound
    """
    while True:
        for i, timer in enumerate(alarms):
            if datetime.now().strftime('%H:%M:%S') == timer:
                del alarms[i]
                # Pause spotify playback, pass if nothing is playing
                Spotify().pausePlay('pause')
                playsound('./Commands/Timer_Alarm/TimerUp.mp3')
                Spotify().pausePlay('continue')
                # Continue Spotify payback, pass if nothing is playing
        time.sleep(1)


alarmThread = threading.Thread(target=alarmTracker)
alarmThread.start()
