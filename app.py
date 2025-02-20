import os
import logging
import random

from flask import Flask, render_template, request, redirect, url_for

from models import db, User
from datamanager.sqlite_data_manager import SQLiteDataManager
from omdb_service import fetch_movie_data, extract_movie_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Logging enabled!")

app = Flask(__name__)

if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    print("Starting Flask App...")

db_path = os.path.join(os.getcwd(), "data", "movies.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# with app.app_context():
#     db.create_all()

data_manager = SQLiteDataManager(app, db)

@app.route("/")
def index():
    """ Render the home page """
    random_titles = [
        "Inception", "The Matrix", "The Dark Knight", "Interstellar",
        "Pulp Fiction", "Fight Club", "The Godfather", "Blade Runner",
        "The Crow", "Mad Max", "12 Monkeys", "Terminator 2"
    ]

    selected_titles = random.sample(random_titles, 6)
    posters = []

    for title in selected_titles:
        movie_data = fetch_movie_data(title)
        if movie_data and "Poster" in movie_data:
            posters.append(movie_data["Poster"])

    return render_template("index.html", posters=posters)


@app.route('/users')
def list_users():
    """ Display a list of all users """
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        logging.error(f"Error in list_users route: {e}")
        return "An error occurred", 500


@app.route('/users/<user_id>')
def user_movies(user_id):
    """ Show a user's list of favorite movies """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            logging.warning(f"User {user_id} not found.")
            return "User not found", 404

        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)

    except Exception as e:
        logging.error(f"Error in user_movies route: {e}")
        return "An unexpected error occurred", 500



@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """ Render form and handle new user creation """
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            if not username:
                logging.warning("User tried to add a user without a name.")
                return "Username is required!", 400

            # Generate avatar URL from initials
            avatar_url = f"https://ui-avatars.com/api/?name={username}&background=random&color=fff&size=128&rounded=true"

            # Create user with avatar
            new_user = User(name=username, avatar=avatar_url)
            db.session.add(new_user)
            db.session.commit()
            logging.info(f"User '{username}' added successfully with avatar.")
            return redirect(url_for('list_users'))

        return render_template('add_user.html')

    except Exception as e:
        logging.error(f"Error in add_user route: {e}")
        return "An unexpected error occurred", 500


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """ Render form and handle adding a movie to a user's collection """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            logging.warning(f"User {user_id} not found.")
            return "User not found", 404

        if request.method == 'POST':
            title = request.form.get('title')
            if not title:
                logging.warning("Movie title is required.")
                return "Movie title is required!", 400

            raw_data = fetch_movie_data(title)
            if not raw_data or "Error" in raw_data:
                error_message = raw_data.get("Error", "Movie not found. Check the title and try again.")
                logging.warning(f"Failed to fetch movie details: {error_message}")
                return render_template('error.html', message=error_message, user_id=user_id), 400

            movie_data = extract_movie_data(raw_data)

            # Store the fetched details
            success = data_manager.add_movie(
                user_id,
                movie_data["Title"],
                movie_data["Director"],
                movie_data["Year"],
                movie_data["Rating"],
                movie_data["Poster"],
                movie_data["Genre"]
            )

            if success:
                logging.info(f"Movie '{title}' added for user {user_id}.")
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                logging.error(f"Failed to add movie '{title}' for user {user_id}.")
                return "Error adding movie", 500

        return render_template('add_movie.html', user=user)

    except Exception as e:
        logging.exception(f" Error in add_movie route: {e}")
        return "An unexpected error occurred", 500


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """ Render form and handle updating a movie's details """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            logging.warning(f"User {user_id} not found")
            return "User not found", 404

        movie = data_manager.get_movie(movie_id)
        if not movie or movie not in user.movies:
            logging.warning(f"User {movie_id} not found")
            return "Movie not found", 404

        if request.method == 'POST':
            title = request.form.get('title')
            director = request.form.get('director')
            year = request.form.get('year')
            rating = request.form.get('rating')

            if not title or not director or not year or not rating:
                logging.warning("Missing data in update form")
                return "All fields are required!", 400

            data_manager.update_movie(movie_id, title, director, year, rating)
            logging.info(f"Movie {movie_id} updated successfully.")
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('update_movie.html', user=user, movie=movie)

    except Exception as e:
        logging.error(f"Error in update_movie route: {e}")
        return "An unexpected error occurred", 500


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    """ Handle movie deletion from a user's collection """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            logging.warning(f"User {user_id} not found")
            return "User not found", 404

        movie = data_manager.get_movie(movie_id)
        if not movie or movie not in user.movies:
            logging.warning(f"User {movie_id} not found")
            return "Movie not found", 404

        data_manager.delete_movie(movie_id)
        logging.info(f"Deleted movie {movie.title} (ID {movie_id}) for user {user.name} (ID {user_id})")
        return redirect(url_for("user_movies", user_id=user_id))

    except Exception as e:
        logging.error(f"Error deleting movie {movie_id} for user {user_id}: {e}")
        return "An unexpected error occurred", 500


@app.errorhandler(404)
def page_not_found(e):
    logging.warning(f"404 Not Found: {request.url}")
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"500 Internal Server Error: {str(e)}")
    return "Something went wrong on our end. We're on it!", 500


if __name__ == "__main__":
    print("✅ Running Flask App...")
    app.run(host="0.0.0.0", port=5002, debug=True, use_reloader=False)

