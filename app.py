# app.py
import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define a simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


# Create a user
@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
