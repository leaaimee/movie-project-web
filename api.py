from flask import Blueprint, jsonify, request, current_app
from models import db, User, Movie
from datamanager.sqlite_data_manager import SQLiteDataManager

# ✅ Define the Blueprint
api = Blueprint('api', __name__)

# ✅ Instantiate DataManager with current_app (only inside a request context)
def get_data_manager():
    return SQLiteDataManager(current_app, db)


@api.route("/users", methods=["GET"])
def get_users():
    """ Return a list of all users in JSON format """
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name} for user in users])


@api.route("/users/<int:user_id>/movies", methods=["GET"])
def get_user_movies(user_id):
    """ Return a list of movies for a specific user """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    movies = [
        {
            "id": movie.id,
            "title": movie.title,
            "director": movie.director,
            "year": movie.year,
            "rating": movie.rating,
            "genre": movie.genre,
        }
        for movie in user.movies
    ]
    return jsonify(movies)


@api.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie_to_user(user_id):
    """Add a movie to the user's collection."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    movie = Movie(
        title=data["title"],
        director=data.get("director", "Unknown"),
        year=data.get("year", 0),
        rating=data.get("rating", 0),
        genre=data.get("genre", "Unknown"),

    )
    user.movies.append(movie)
    db.session.add(movie)
    db.session.commit()

    return jsonify({"message": "Movie added successfully", "movie_id": movie.id}), 201


@api.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """ Fetch a specific movie by its ID """
    data_manager = get_data_manager()

    movie = data_manager.get_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    movie_data = {
        "id": movie.id,
        "title": movie.title,
        "director": movie.director,
        "year": movie.year,
        "rating": movie.rating,
        "genre": movie.genre,
        "poster": movie.poster,
    }

    return jsonify(movie_data)



