import csv
import random
import pickle


class Jokes:
    def __init__(self) -> None:
        self.__jokes = []  # Private list to store jokes

    def __organiseJokes(self) -> None:
        """
        Organises jokes from a CSV file into a linked list and stores it in a pickle file.
        """

        # Read jokes from CSV file and process
        with open('funjokes.csv', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                joke = row[1]
                if joke == 'Joke':
                    pass  # Skip the header
                else:
                    joke = joke.split('?')
                    self.__jokes.append(joke)

        # Store organised jokes in a pickle file
        with open('joke.assistant', 'wb') as f:
            pickle.dump(self.__jokes, f)

    def getJoke(self) -> str:
        """
        Retrieves a random joke for the user.
        """

        # Load jokes from the pickle file
        with open('./Commands/Jokes/joke.assistant', 'rb') as file:
            jokes = pickle.load(file)
            joke = jokes[random.randint(0, len(jokes))]

        # Format the joke for TTS
        if len(joke) == 1:
            return f':tts:{joke}'
        return f':tts:{joke[0]}:wait:{joke[1]}'
