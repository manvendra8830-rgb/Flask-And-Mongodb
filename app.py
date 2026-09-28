from pathlib import Path
import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Load environment variables
load_dotenv()

app = Flask(__name__)


# --------------------------------------------------
# MongoDB Configuration
# --------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is not configured. Please add it to the .env file."
    )

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["flask_db"]
collection = db["submissions"]


# --------------------------------------------------
# Task 1: JSON API Route
# --------------------------------------------------

@app.route("/api", methods=["GET"])
def api():
    """
    Reads data from backend/data.json
    and returns it as a JSON response.
    """

    data_file = Path(__file__).parent / "backend" / "data.json"

    try:
        with open(data_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        return jsonify(data)

    except FileNotFoundError:
        return jsonify({
            "error": "data.json file not found."
        }), 500

    except json.JSONDecodeError:
        return jsonify({
            "error": "Invalid JSON format in data.json."
        }), 500

    except Exception as error:
        return jsonify({
            "error": f"Unable to read data: {error}"
        }), 500


# --------------------------------------------------
# Task 2: Frontend Form + MongoDB Atlas
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get form values
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # Validate form fields
        if not name or not email or not message:
            return render_template(
                "index.html",
                error="All fields are required.",
                name=name,
                email=email,
                message=message
            )

        # Insert data into MongoDB Atlas
        try:
            document = {
                "name": name,
                "email": email,
                "message": message
            }

            collection.insert_one(document)

            # Successful submission → redirect to another page
            return redirect(url_for("success"))

        except PyMongoError as error:
            # Database error → stay on the same page
            return render_template(
                "index.html",
                error=f"Database error: {error}",
                name=name,
                email=email,
                message=message
            )

        except Exception as error:
            # Other errors → stay on the same page
            return render_template(
                "index.html",
                error=f"An unexpected error occurred: {error}",
                name=name,
                email=email,
                message=message
            )

    return render_template("index.html")


# --------------------------------------------------
# Success Page
# --------------------------------------------------

@app.route("/success", methods=["GET"])
def success():
    return render_template("success.html")


# --------------------------------------------------
# Application Entry Point
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)