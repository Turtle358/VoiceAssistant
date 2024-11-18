# Before loading anything, check if API keys are present
from CLI import startupChecks
from assets.keysGUI import AddKeys

# Check if startup checks found keys, if not, prompt the user to add keys
if 'False' in startupChecks():
    AddKeys()

"""
Now that Startup checks have passed successfully/new keys have been added,
we can start the GUI and run the voice assistant, importing any necessary procedures for that
"""
from Commands.VoiceRecognition.predictAudio import PredictAudio
from Commands.Radio.radioPlayback import RadioControl
from Commands.options import CondensedIfStatements
from Commands.TTSService.textToSpeech import TTS
from PIL import Image, ImageTk
from threading import Thread
from sys import platform
import customtkinter as ctk
import playsound
import colorsys
import requests
import time
import io

# Create instances of various components needed for the Voice Assistant
radioControl = RadioControl()
optionsManager = CondensedIfStatements()
automaticSpeechRecognition = PredictAudio()


# Define the main class for the Voice Assistant GUI
class VoiceAssistantUI:
    def __init__(self):
        """
        Creates a tkinter GUI for the Voice Assistant
        Reference: https://customtkinter.tomschimansky.com/
        """
        # Get window dimensions, fonts, and sizes based on the OS
        self.windowHeight, \
        self.windowWidth, \
        self.font, \
        self.labelHeight, \
        self.labelWidth, \
        self.buttonHeight, \
        self.buttonWidth, \
        self.imageSize, \
        self.radius = self.getHeightAndWidth()

        self.updatePaused = False

        # Create the main application window
        self.root = ctk.CTk()
        ctk.set_appearance_mode('dark')
        if platform == 'win32':
            self.root.iconbitmap('./assets/VoiceAssistant.ico')

        # Configure the main window
        self.root.configure(bg='black', width=self.windowWidth, height=self.windowHeight)
        self.root.title("VoiceAssistant GUI")

        # Set up the Voice Assistant icon and label
        self.image = Image.open("./assets/VoiceAssistant.ico")
        self.iconImage = ctk.CTkImage(self.image, size=self.imageSize)
        self.root.after(5000, self.updateImage)
        self.imageLabel = ctk.CTkLabel(self.root, image=self.iconImage, text='')
        self.imageLabel.pack(padx=10, pady=10, side=ctk.LEFT)

        # Create a Text box on the left side
        self.textBox = ctk.CTkLabel(self.root,
                                    height=self.labelHeight,
                                    width=self.labelWidth,
                                    text='Welcome to voice assistant',
                                    wraplength=200,
                                    font=self.font,
                                    corner_radius=8)
        self.textBox.pack(side=ctk.LEFT, padx=10, pady=10)

        # Create a button for triggering voice recognition
        self.listenButton = ctk.CTkButton(self.root,
                                          text="Listen",
                                          command=self.listenButtonClick,
                                          height=self.buttonHeight,
                                          width=self.buttonWidth,
                                          corner_radius=self.radius,
                                          font=self.font,
                                          fg_color=self.getMeanColourInImage(),
                                          text_color=self.getTextColour(),
                                          hover_color=self.getAnalogousColour())
        self.listenButton.pack(side=ctk.LEFT, padx=10, pady=10)

        # Start the main event loop
        self.root.resizable(False, False)
        self.root.mainloop()

    def getHeightAndWidth(self) -> tuple[int, int, tuple[str, int], int, int, int, int, tuple[int, int], int]:
        # Determine dimensions and sizes based on the OS
        if platform == 'win32':
            windowWidth: int = 180
            windowHeight: int = 40
            font: tuple[str, int] = ('Roboto', 14)
            labelHeight: int = 120
            labelWidth: int = 200
            buttonHeight: int = 120
            buttonWidth: int = 120
            imageSize: tuple[int, int] = (120, 120)
            radius: int = 20
        else:
            windowWidth: int = 360
            windowHeight: int = 200
            font: tuple[str, int] = ('Roboto', 24)
            labelHeight: int = 240
            labelWidth: int = 340
            buttonHeight: int = 220
            buttonWidth: int = 220
            imageSize: tuple[int, int] = (240, 240)
            radius: int = 37
        return windowWidth, windowHeight, font, labelHeight, labelWidth, buttonHeight, buttonWidth, imageSize, radius

    def updateImage(self) -> None:
        """
        Downloads image from supplied URL and sets currently playing image for GUI
        """
        # Load the new image
        if not self.updatePaused:
            if optionsManager.radioPlaying:
                # Display BBC Radio image if radio is playing
                newImage = Image.open('./assets/BBCRadio.jpg')
                newImage = newImage.resize((150, 150))
                newImage = ImageTk.PhotoImage(newImage)
                self.textBox.configure(text=optionsManager.options(':internal:getplayinginfo'))
            else:
                # Download and display the album cover image
                try:
                    self.downloadImage(optionsManager.options(':internal:albumcoverget'))
                except:
                    self.image = Image.open('./assets/VoiceAssistant.ico')
                newImage = self.image
                newImage = ctk.CTkImage(newImage, size=self.imageSize)
                self.textBox.configure(text=optionsManager.options(':internal:getplayinginfo'))

            # Update button and label colors based on the new image
            self.listenButton.configure(fg_color=self.getMeanColourInImage(),
                                        text_color=self.getTextColour(),
                                        hover_color=self.getAnalogousColour())
            self.imageLabel.configure(image=newImage)
            self.imageLabel.image = newImage

        # Schedule the next update after 10 seconds
        self.root.after(10000, self.updateImage)
        self.updatePaused = False

    def updateImageOnce(self) -> None:
        """
        Downloads image from supplied URL and sets currently playing image for GUI
        Used for when a music option is selected
        """
        time.sleep(1)
        self.downloadImage(optionsManager.options('albumcoverget'))
        newImage = ctk.CTkImage(self.image, size=self.imageSize)

        # Update the image in the label
        self.imageLabel.configure(image=newImage)
        self.imageLabel.image = newImage

    def listenButtonClick(self) -> None:
        """
        Uses neural network model to get options from text to speech
        """
        # Pause so that the neural network can hear clearly
        optionsManager.options(':internal:pause')

        # Predict user speech using automatic speech recognition
        try:
            playsound.playsound('./assets/wakeSound.mp3')
        except playsound.PlaysoundException:
            playsound.playsound('./assets/wakeSound.mp3')
        userSpeech = automaticSpeechRecognition.predict()
        playsound.playsound('./assets/sleepSound.mp3')
        print(userSpeech)
        output = optionsManager.options(userSpeech.split('\n')[0])

        # Start a thread for text-to-speech synthesis to avoid GUI freezing
        Thread(target=TTSManager, args=(userSpeech, output,)).start()

        # Update the image if a music option is selected
        if any(i in userSpeech for i in CondensedIfStatements().musicOptions):
            self.updateImageOnce()

        if ':tts:' in output:
            # Set Label
            if ':wait:' in output:
                output = output.split(':tts:')[-1]
                output = f'{output.split(":wait:")[0]}\n\n{output.split(":wait:")[-1]}'
            self.textBox.configure(text=output.split(':tts:')[-1].split('|')[-1])
            self.updatePaused = True
        else:
            optionsManager.options(':internal:continue')

    def downloadImage(self, url):
        """
        Downloads image from the supplied URL
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            self.image = Image.open(io.BytesIO(response.content))
        except:
            # Use a default image if download fails
            with open('./assets/VoiceAssistant.ico', 'rb') as logo:
                self.image = Image.open(logo.read())

    def getRGB(self):
        # Get RGB values from the image
        pixels = list(self.image.getdata())

        try:
            # If any extra values (such as brightness) included, ignore them
            redValues, greenValues, blueValues, *_ = zip(*pixels)
        except TypeError:
            # If the image is black and white, use the default color scheme
            redValues, greenValues, blueValues = [176], [220], [238]

        meanRed = sum(redValues) // len(redValues)
        meanGreen = sum(greenValues) // len(greenValues)
        meanBlue = sum(blueValues) // len(blueValues)
        return meanRed, meanGreen, meanBlue

    def getMeanColourInImage(self) -> str:
        # Get the most common color in the image
        r, g, b = self.getRGB()
        meanColourHex = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return meanColourHex

    def getTextColour(self) -> str:
        # Determine text color based on image brightness
        r, g, b = self.getRGB()
        brightness = sum([r, g, b]) / 3

        if brightness >= 128:
            return 'black'
        return 'white'

    def getAnalogousColour(self) -> str:
        # Determine an analogous color based on the image's primary color
        r, g, b = self.getRGB()
        hsvColour = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        analogousColours = []

        for i in range(5):
            hue = (hsvColour[0] + i * 1 / 12) % 1.0
            rgbAnalogous = colorsys.hsv_to_rgb(hue, hsvColour[1], hsvColour[2])
            analogousColours.append(tuple(int(c * 255) for c in rgbAnalogous))

        r, g, b = analogousColours[1]
        meanColourHex = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return meanColourHex


# Function for managing TTS in a separate thread
def TTSManager(userinput, output) -> None:
    """
    Used in a thread (with threading library) to prevent the Tkinter GUI from getting a "not responding" error
    """
    if ':tts:' in output:
        # Run TTS API
        TTS().synthesiseSpeech(output)
        if not any(i in userinput for i in CondensedIfStatements().musicOptions):
            optionsManager.options('continue')


if __name__ == '__main__':
    VoiceAssistantUI()
