import requests
import pickle
# Get the API key
try:
    with open("../../assets/.keys", "rb") as file:
        keys = pickle.load(file)

except FileNotFoundError:
    with open('./assets/.keys', 'rb') as file:
        keys = pickle.load(file)

key = keys['Bing']


def bingSearch(query):
    """
    Parameters
    ----------
    query
    Returns
    -------
    Backup search if DuckDuckGo returns nothing

    Function
    --------
    This works by sending an API request to the Azure cloud servers with the API key, market region
    and the query

    References
    ----------
    https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
    """
    # Search Using the Bing search API
    url = 'https://api.bing.microsoft.com/v7.0/search'
    headers = {'Ocp-Apim-Subscription-Key': key}
    params = {
        'q': query,
        'count': 1,
        'offset': 0,
        'mkt': 'en-GB'}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    try:
        data = data['entities']['value'][0]['description']
    except KeyError:
        data = data['webPages']['value'][0]['snippet']
    return f':tts:{data}'


if __name__ == "__main__":
    print(bingSearch(input("Please enter a query: ")))
