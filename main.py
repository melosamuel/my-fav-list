from dotenv import load_dotenv
import argparse
import logging
import os
import pandas as pd
import requests

def run(movie_title: str):
    """Fetch movies data based on the title given and stores it in a .csv file.

    Args:
        movie_title (str): The title to search that the user has typed as argument.
    """

    API_KEY = os.getenv("API_KEY")

    if not API_KEY:
        logging.critical("An API key is required to run this software. Please, update the '.env' file. (See README if you need help)")
        return

    url = f"http://www.omdbapi.com/?apikey={API_KEY}&s={movie_title}"

    response = requests.get(url=url)

    if response.status_code != 200:
        logging.critical(f"Could not reach the API. Please, verify your API key or your internet connection. Status code: {response.status_code}")
        return

    data = response.json()

    df = pd.json_normalize(data['Search'])
    df = df[["Title", "Year", "Type"]]
    df.to_csv('result.csv', index=False)

if __name__ == "__main__":
    logging.basicConfig(filename='./app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="Type the movie title")
    parser.add_argument("title")

    args = parser.parse_args()

    load_dotenv()

    run(movie_title=args.title)