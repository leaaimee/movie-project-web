import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "http://www.omdbapi.com/"


def fetch_movie_data(title):
    """ Fetch movie data from the OMDb API by title """
    try:
        url = f"{OMDB_URL}?apikey={API_KEY}&t={title}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                logging.info(f"Successfully fetched data for: {title}")
                return data
            else:
                logging.warning(f"OMDb API returned an error: {data.get('Error')}")
                return {"Error": data.get("Error", "Movie not found!")}

        logging.error(f"OMDb API request failed with status code {response.status_code}")
        return {"Error": f"Request failed with status code {response.status_code}"}

    except Exception as e:
        logging.exception(f"Unexpected error fetching movie data: {e}")
        return None


def extract_movie_data(raw_data):
    """ Extracts relevant fields from raw OMDb data """
    try:
        title = raw_data.get("Title", "N/A")
        director = raw_data.get("Director", "N/A")
        year = raw_data.get("Year", "N/A")
        rating = raw_data.get("imdbRating", "N/A")
        poster = raw_data.get("Poster", "N/A")

        logging.info(f"🎬 Extracted movie data: Title={title}, Year={year}, Rating={rating}, Poster={poster}")
        return {"Title": title, "Director": director, "Year": year, "Rating": rating, "Poster": poster}

    except Exception as e:
        logging.exception(f"🔥 Error extracting movie data: {e}")
        return {"Error": str(e)}