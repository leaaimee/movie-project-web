
from models import db, User, Movie
from datamanager.data_manager_interface import DataManagerInterface
import logging


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, database):
        self.db = database
        self.app = app

    def get_all_users(self):
        try:
            users = User.query.all()
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def get_user_movies(self, user_id):
        try:
            user = User.query.get(user_id)
            if user:
                movies = user.movies
                return movies
            else:
                return []
        except Exception as e:
            print(f"Error getting user movies: {e}")
            return []

    def add_movie(self, user_id, title, director, year, rating, poster):
        try:
            user = User.query.get(user_id)
            if user:
                movie = Movie(title=title, director=director, year=year, rating=rating, poster=poster)
                user.movies.append(movie)
                self.db.session.add(movie)
                self.db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Error adding movie: {e}")
            self.db.session.rollback()
            return False

    def update_movie(self, movie_id, title, director, year, rating):
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                movie.title = title
                movie.director = director
                movie.year = year
                movie.rating = rating
                self.db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating movie: {e}")
            self.db.session.rollback()
            return False

    def delete_movie(self, movie_id):
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                self.db.session.delete(movie)
                self.db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Error deleting movie: {e}")
            self.db.session.rollback()
            return False

    def get_user(self, user_id):
        try:
            return User.query.get(user_id)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def add_user(self, username):
        try:
            new_user = User(name=username)
            self.db.session.add(new_user)
            self.db.session.commit()
            logging.info(f"User '{username}' added successfully.")
            return True
        except Exception as e:
            logging.error(f"Error adding user '{username}': {e}")
            self.db.session.rollback()
            return False