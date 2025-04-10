from dotenv import load_dotenv
import argparse
import logging
import os
import pandas as pd
import requests

def create_csv(data: dict):
    """Creates a .csv file with the data given.

    Args:
        data (dict): A dict containing media title, released year, type and vote average
    """

    data_for_csv = []

    for _, details in data.items():
        data_for_csv.append({
            'Title': details[0],
            'Year': details[1],
            'Type': details[2],
            'Vote Average': details[3]
    })
        
    df = pd.DataFrame(data_for_csv)
    df.to_csv('results.csv', index=False)

def get_from_tmdb(media_id: str, media_title: str) -> float:
    """Get the chosen media's vote average info.

    Args:
        media_id (str): The external id extracted from imdb API
        media_title (str): The movie title

    Returns:
        float: The vote avarage
    """

    TMDB_TOKEN = os.getenv("TMBD_TOKEN")

    url = f'https://api.themoviedb.org/3/find/{media_id}?external_source=imdb_id'

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = requests.get(url=url, headers=headers)

    result = response.json()

    try:
        result = result['movie_results'][0]
    except IndexError:
        return 0.0

    return result['vote_average']

def get_from_omdb(search: str) -> dict:
    """Get avaliable media data by the given string.

    Args:
        search (str): String for searching.

    Returns:
        dict: Avaliable media data
    """

    OMDB_KEY = os.getenv("OMDB_KEY")

    if not OMDB_KEY:
        logging.critical("An API key is required to run this software. Please, update the '.env' file. (See README if you need help)")
        return

    url = f"http://www.omdbapi.com/?apikey={OMDB_KEY}&s={search}"

    response = requests.get(url=url)

    if response.status_code != 200:
        logging.critical(f"Could not reach the API. Please, verify your API key or your internet connection. Status code: {response.status_code}")
        return

    media = response.json()
    media_data = None
    
    try:
        media_data = media['Search']
    except KeyError:
        print(f"There are no similar results for: {search}")
    finally:
        return media_data

def run(search: str):
    """Fetch media data based on the given string and stores it in a .csv file.

    Args:
        search (str): String for searching.
    """

    similar_results = get_from_omdb(search=search)

    if not similar_results:
        return

    media = {}
    user_choice = None

    print("\n ========== Similar Results ========== \n")

    for index, info in enumerate(similar_results):
        media[index + 1] = {info['imdbID']: [info['Title'], info['Year'], info['Type']]}

        print(f"{index + 1} - {info['Title']} ({info["Year"]})")

    while user_choice not in media.keys():
        try:
            user_choice = int(input("Select one for more info: "))
        except ValueError:
            print("Your answer must be an number.")
        except KeyError:
            print("Try again! You must select a movie by it's index number!")

    chosen_media = media[user_choice]

    for k, v in chosen_media.items():
        media_id = k
        media_title = v[0]

    vote_average = get_from_tmdb(media_id=media_id, media_title=media_title)
    chosen_media[media_id].append(vote_average)

    create_csv(data=chosen_media)

if __name__ == "__main__":
    logging.basicConfig(filename='./app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="Type the movie title")
    parser.add_argument("title")

    args = parser.parse_args()

    load_dotenv()

    run(search=args.title)