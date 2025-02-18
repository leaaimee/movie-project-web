from flask import Flask, render_template
import os
from models import db
from datamanager.sqlite_data_manager import SQLiteDataManager


print("✅ Starting Flask App...")
app = Flask(__name__)


print("✅ Flask App Created!")
db_path = os.path.join(os.getcwd(), "data", "movies.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initalize when we are ready
# with app.app_context():
#     db.create_all()

data_manager = SQLiteDataManager(app, db)

@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


@app.route('/users')
def list_users():
    try:
        with app.app_context():
            users = data_manager.get_all_users()
            return render_template('users.html', users=users)
    except Exception as e:
        print(f"Error in list_users route: {e}")
        return "An error occurred", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)