# app.py
import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

MAX_NAME_LENGTH = 80


# Define a simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


def _validate_name(data):
    """Return an error message if `data` doesn't carry a usable name, else None."""
    if not isinstance(data, dict):
        return "request body must be a JSON object"
    name = data.get("name")
    if name is None:
        return '"name" is required'
    if not isinstance(name, str):
        return '"name" must be a string'
    if not name.strip():
        return '"name" must not be blank'
    if len(name) > MAX_NAME_LENGTH:
        return f'"name" must be at most {MAX_NAME_LENGTH} characters'
    return None


# Create a user
@app.route("/user", methods=["POST"])
def create_user():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "request body must be valid JSON"}), 400

    error = _validate_name(data)
    if error:
        return jsonify({"error": error}), 400

    new_user = User(name=data["name"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created!"}), 201


# Get all users
@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
    user_list = [{"id": user.id, "name": user.name} for user in users]
    return jsonify(user_list), 200


@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    db.session.rollback()
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
