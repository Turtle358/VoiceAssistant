from sys import platform
import subprocess


class VolControl:

    # if linux - Using terminal commands
    def linuxGetOutputVolume(self) -> int:
        from pulsectl import Pulse
        """
        Returns
        -------
        If the device is linux, pulsectl is used to get the current volume
        """
        with Pulse('volume-check') as pulse:
            sink = pulse.sink_list()[0]
            volume = round(sink.volume.value_flat * 100)
            return volume

    def setVolumeLinux(self, volume: str) -> str:
        """
        Parameters
        ----------
        volume
        Returns
        -------
        gets digits from the volume and runs terminal command to modify volume
        """
        if volume in ["volume", "what's the volume"]:
            return f":tts:volume is at {self.linuxGetOutputVolume()}%"

        elif volume.split(" ")[0] == "louder":
            if self.linuxGetOutputVolume() >= 100:
                return "Volume is already at 100%"
            subprocess.run(f"pactl set-sink-volume 0 +10%", shell=True)
            return "Volume decreased by 10%"

        elif volume.split(" ")[0] == "quieter":
            subprocess.run(f"pactl set-sink-volume 0 -10%", shell=True)
            return "Volume decreaed by 10%"

        elif volume.split(" ")[1] in ["up","add","increase"]:
            try:
                volume = int(volume.split(" ")[-1])
                if self.linuxGetOutputVolume() + volume > 100:
                    vol = 100
                else:
                    vol = volume + self.linuxGetOutputVolume()
            except:
                volume = 10
                vol = self.linuxGetOutputVolume() + volume
            subprocess.run(f"pactl set-sink-volume 0 {int(vol)}%", shell=True)
            return f"volume increased by {volume}%"

        elif volume.split(" ")[1] in ["down", "decrease"]:
            try:
                vol = volume.split(" ")[-1]
                volume = self.linuxGetOutputVolume() - vol
            except:
                vol = 10
                volume = self.linuxGetOutputVolume() - vol
            subprocess.run(f"pactl set-sink-volume 0 {volume}%", shell=True)
            return f"volume decreased by {vol}%"

        else:
            volume = int(volume.split(" ")[-1])
            if volume > 100:
                volume = 100
            subprocess.run(f"pactl set-sink-volume 0 {int(volume)}%",shell=True)
            return f"Volume set to {volume}"
    # if windows - using c code from libraries usage in windowsVolControl.py

    def setVolumeWindows(self, volume):
        """
        Parameters
        ----------
        volume
        Returns
        -------
        if device is windows, uses Ctypes and pycaw to modify volume
        """
        from Commands.VolumeControl import windowsVolControl as WVC

        if volume in ["volume", "what's the volume"]:
            return f":tts:volume is at {WVC.getMainVolume()}%"

        elif volume.split(" ")[0] == "louder":
            if WVC.getMainVolume() >= 100:
                return "Volume is already at 100%"
            WVC.setMainVolume(WVC.getMainVolume() + 10)
            return "Volume increased by 10%"

        elif volume.split(" ")[0] == "quieter":
            WVC.setMainVolume(WVC.getMainVolume() - 10)
            return "Volume decreased by 10%"

        elif volume.split(" ")[1] in ["up","add","increase"]:
            try:
                volume = int(volume.split(" ")[-1])
                if WVC.getMainVolume() + volume > 100:
                    vol = 100
                else:
                    vol = volume + WVC.getMainVolume()
            except:
                volume = 10
                vol = WVC.getMainVolume() + volume
            WVC.setMainVolume(vol)
            return f"volume increased by {volume}%"

        elif volume.split(" ")[1] in ["down", "decrease"]:
            try:
                vol = volume.split(" ")[-1]
                volume = WVC.getMainVolume() - vol
            except:
                vol = 10
                volume = WVC.getMainVolume() - vol
            WVC.setMainVolume(volume)
            return f"volume decreased by {vol}%"

        else:
            volume = int(volume.split(" ")[-1])
            if volume > 100:
                volume = 100
            WVC.setMainVolume(int(volume))
            return f"Volume set to {volume}%"


VolControl = VolControl()


def mainVolControl(vol):
    """
    Parameters
    ----------
    vol
    Returns
    -------
    Master interface for controlling volume
    """
    if platform == "linux" or platform == "linux2":
        return VolControl.setVolumeLinux(vol)

    elif platform == "win32":
        return VolControl.setVolumeWindows(vol)

    elif platform == "dawin":
        # If user is on macOS, give an appropriate response
        return ":tts:Why are you using macOS? Crazy person"
    else:
        return ':tts:This operating system is not supported'
