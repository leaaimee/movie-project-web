
from models import db, User, Movie
from datamanager.data_manager_interface import DataManagerInterface
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)



class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, database):
        """ Initializes the database manager with a Flask app and database connection """
        self.db = database
        self.app = app

    def get_all_users(self):
        """ Returns a list of all users or an empty list if an error occurs """
        try:
            users = User.query.all()
            return users
        except Exception as e:
            logging.error(f" Error getting users: {e}")
            return []

    def get_user_movies(self, user_id):
        """ Returns a list of movies for a given user or an empty list if the user doesn't exist """
        try:
            user = User.query.get(user_id)
            if user:
                return user.movies
            logging.warning(f"⚠ User {user_id} not found when fetching movies.")
            return []
        except Exception as e:
            logging.error(f" Error getting movies for user {user_id}: {e}")
            return []

    def add_movie(self, user_id, title, director, year, rating, poster):
        """ Adds a movie to a user's list and returns True if successful, otherwise False """
        try:
            user = User.query.get(user_id)
            if not user:
                logging.warning(f"️ User {user_id} not found. Cannot add movie.")
                return False

            movie = Movie(title=title, director=director, year=year, rating=rating, poster=poster)
            user.movies.append(movie)
            self.db.session.add(movie)
            self.db.session.commit()
            logging.info(f" Movie '{title}' added for user {user_id}.")
            return True
        except Exception as e:
            logging.error(f" Error adding movie '{title}' for user {user_id}: {e}")
            self.db.session.rollback()
            return False

    def update_movie(self, movie_id, title, director, year, rating):
        """ Updates a movie's details and returns True if successful, otherwise False """
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                logging.warning(f" Movie {movie_id} not found. Cannot update.")
                return False

            movie.title = title
            movie.director = director
            movie.year = year
            movie.rating = rating
            self.db.session.commit()
            logging.info(f" Movie '{title}' (ID: {movie_id}) updated successfully.")
            return True
        except Exception as e:
            logging.error(f" Error updating movie {movie_id}: {e}")
            self.db.session.rollback()
            return False

    def delete_movie(self, movie_id):
        """ Deletes a movie and returns True if successful, otherwise False """
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                logging.warning(f" Movie {movie_id} not found. Cannot delete.")
                return False

            self.db.session.delete(movie)
            self.db.session.commit()
            logging.info(f" Movie ID {movie_id} deleted successfully.")
            return True
        except Exception as e:
            logging.error(f" Error deleting movie {movie_id}: {e}")
            self.db.session.rollback()
            return False

    def get_user(self, user_id):
        """ Returns a User object by ID or None if not found """
        try:
            user = User.query.get(user_id)
            if not user:
                logging.warning(f"️ User {user_id} not found.")
            return user
        except Exception as e:
            logging.error(f" Error getting user {user_id}: {e}")
            return None

    def get_movie(self, movie_id):
        """ Returns a Movie object by ID or None if not found """
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                logging.warning(f" Movie {movie_id} not found.")
            return movie
        except Exception as e:
            logging.error(f" Error getting movie {movie_id}: {e}")
            return None

    def add_user(self, username):
        """ Adds a new user and returns True if successful, otherwise False """
        try:
            new_user = User(name=username)
            self.db.session.add(new_user)
            self.db.session.commit()
            logging.info(f" User '{username}' added successfully.")
            return True
        except Exception as e:
            logging.error(f" Error adding user '{username}': {e}")
            self.db.session.rollback()
            return False