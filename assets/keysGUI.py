import customtkinter as ctk
import pickle


class AddKeys:
    def __init__(self, path: str = './assets') -> None:
        """
        Creates a tkinter window to input API keys for VoiceAssistant
        Reference: https://customtkinter.tomschimansky.com/
        When the class is called, it creates a new tkinter window with 7 inputs for API keys.
        """
        self.path = path
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Create the tkinter window
        self.keyWindow = ctk.CTk()
        self.keyWindow.geometry("320x470")
        self.keyWindow.title('VoiceAssistant API keys')

        # Create a frame inside the window
        self.frame = ctk.CTkFrame(master=self.keyWindow)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Set up labels and entry fields for API keys
        self.label = ctk.CTkLabel(master=self.frame, text="API keys")
        self.label.pack(pady=12, padx=10)
        self.label.configure(font=("Roboto", 24))

        self.openWeatherMapInput = ctk.CTkEntry(master=self.frame, placeholder_text="openWeatherMap")
        self.openWeatherMapInput.pack(pady=12, padx=10)

        self.bingSearchInput = ctk.CTkEntry(master=self.frame, placeholder_text="bingSearch")
        self.bingSearchInput.pack(pady=12, padx=10)

        self.bingTranslateInput = ctk.CTkEntry(master=self.frame, placeholder_text='bingTranslate')
        self.bingTranslateInput.pack(pady=12, padx=10)

        self.bingTTSInput = ctk.CTkEntry(master=self.frame, placeholder_text='bingTTS')
        self.bingTTSInput.pack(pady=12, padx=10)

        self.spotifyIdInput = ctk.CTkEntry(master=self.frame, placeholder_text='spotifyID')
        self.spotifyIdInput.pack(pady=12, padx=10)

        self.spotifySecretInput = ctk.CTkEntry(master=self.frame, placeholder_text='spotifySecret')
        self.spotifySecretInput.pack(pady=12, padx=10)

        # Create a "Submit" button
        button = ctk.CTkButton(master=self.frame, text="Submit", command=self.submit, fg_color='#391273', hover_color='#4b0da6')
        button.pack(pady=12, padx=10)

        # Start the tkinter event loop
        self.keyWindow.mainloop()

    def submit(self) -> None:
        """
        Gets the fields the user has entered and writes them to binary files in ./assets/
        Stops this process and closes the tkinter window.
        """
        # Save API keys to binary files
        with open(f"{self.path}/.keys", "wb") as file:
            keys = {'Weather': self.openWeatherMapInput.get(),
                    'Bing': self.bingSearchInput.get(),
                    'Translate': self.bingTranslateInput.get(),
                    'TTS': self.bingTTSInput.get()}
            pickle.dump(keys, file)

        with open(f'{self.path}/Spotify.keys', 'wb') as file:
            keys = {'spotify_id': self.spotifyIdInput.get(),
                    'spotify_secret': self.spotifySecretInput.get()}
            pickle.dump(keys, file)

        # Update the Spotify SDK JavaScript file with the client id
        try:
            player = ''
            with open('./Commands/spotifyIntegration/spotifySDKConnection.js', 'r') as webPlayer:
                for line in webPlayer.readlines():
                    player += line
                player = player.replace('CLIENT_ID', keys["spotify_id"])

            with open('./Commands/spotifyIntegration/spotifySDKConnection.js', 'w') as webPlayer:
                webPlayer.write(player)
        except FileNotFoundError:
            print("Please go to ./Commands/spotifyIntegration/spotifySDKConnection.js to add your client id to the web\
             page for web playback")

        # Quit the tkinter window
        self.keyWindow.quit()


if __name__ == '__main__':
    AddKeys(path='./')
