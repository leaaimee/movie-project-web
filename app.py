import os
import logging
import sys

from flask import Flask, render_template, request, redirect, url_for

from models import db
from datamanager.sqlite_data_manager import SQLiteDataManager
from omdb_service import fetch_movie_data, extract_movie_data

#Fix logging: Ensure logs go to BOTH file & terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode="a"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("Logging is fully enabled!")

app = Flask(__name__)

if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    print("Starting Flask App...")

db_path = os.path.join(os.getcwd(), "data", "movies.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# with app.app_context():
#     db.drop_all()  # ⚠ Deletes all data!
#     db.create_all()  # Recreates tables

# with app.app_context():
#     db.create_all()

data_manager = SQLiteDataManager(app, db)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="app.log", filemode="a")

@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


@app.route('/users')
def list_users():
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        logging.error(f"Error in list_users route: {e}")
        return "An error occurred", 500


@app.route('/users/<user_id>')
def user_movies(user_id):
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
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            if not username:
                logging.warning("User tried to add a user without a name.")
                return "Username is required!", 400

            success = data_manager.add_user(username)
            if success:
                logging.info(f"User '{username}' added successfully.")
                return redirect(url_for('list_users'))
            else:
                logging.error(f"Failed to add user '{username}'.")
                return "Error adding user", 500

        return render_template('add_user.html')

    except Exception as e:
        logging.error(f"Error in add_user route: {e}")
        return "An unexpected error occurred", 500


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    try:
        user = data_manager.get_user(user_id)
        if not user:
            logging.warning(f"⚠️ User {user_id} not found.")
            return "User not found", 404

        if request.method == 'POST':
            title = request.form.get('title')
            if not title:
                logging.warning("⚠️ Movie title is required.")
                return "Movie title is required!", 400

            # Fetch and extract movie data
            raw_data = fetch_movie_data(title)
            if not raw_data:
                return "Could not fetch movie details from OMDb.", 500

            movie_data = extract_movie_data(raw_data)

            # Store the fetched details
            success = data_manager.add_movie(
                user_id,
                movie_data["Title"],
                movie_data["Director"],
                movie_data["Year"],
                movie_data["Rating"],
                movie_data["Poster"]
            )

            if success:
                logging.info(f"✅ Movie '{title}' added for user {user_id}.")
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                logging.error(f"❌ Failed to add movie '{title}' for user {user_id}.")
                return "Error adding movie", 500

        return render_template('add_movie.html', user=user)

    except Exception as e:
        logging.exception(f" Error in add_movie route: {e}")
        return "An unexpected error occurred", 500


@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie():
    pass

@app.route('/users/<user_id>/delete_movie/<movie_id>')
def delete_movie():
    pass

if __name__ == "__main__":
    print("✅ Running Flask App...")
    app.run(host="0.0.0.0", port=5002, debug=True, use_reloader=False)

