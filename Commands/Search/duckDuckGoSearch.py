import requests
from Commands.Search.bingSearch import bingSearch


def searchDuckDuckGo(query: str):
    """
    Parameters
    ----------
    query
    Returns
    -------
    Sends an API request to DuckDuckGo for a query
    If query returns nothing, run bing search to get a result
    """

    # Since Duck doesn't require an API key, you can just send a big request
    api_url = f'http://api.duckduckgo.com/?q={query}&format=json'
    response = requests.get(api_url)
    data = response.json()

    if data['AbstractText'] == '':
        # If duck api returns noting, it will send it to the bing api (which is less accurate)
        return bingSearch(query)
    return f":tts:{data['AbstractText']}"


if __name__ == "__main__":
    print(searchDuckDuckGo(input("Please enter a query: ")))
