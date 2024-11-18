import _ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def getMainVolume():
    """
    Returns
    -------
    gets volume for Windows devices
    Reference
    ---------
    https://pypi.org/project/pycaw/
    """
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    currentVolume = volume.GetMasterVolumeLevelScalar() * 100
    currentVolume = round(currentVolume)
    return currentVolume


def setMainVolume(volume) -> str:
    """
    Parameters
    ----------
    volume
    Returns
    -------
    Sets volume using ctypes and pycaw
    """
    volume = volume/100
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

        volumeObject = cast(interface, POINTER(IAudioEndpointVolume))
        volumeObject.SetMasterVolumeLevelScalar(volume, None)
        return f"Volume set to {volume * 100}"
    except _ctypes.COMError:
        return "Invalid volume, please choose from 0-100%"
