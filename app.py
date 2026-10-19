from flask import Flask, jsonify, request, redirect, render_template
from urllib.parse import urlsplit
from pathlib import Path
import sqlite3
import secrets
import string

app = Flask(__name__)

# Store the database beside this Python file.
DATABASE = Path(__file__).with_name("urls.db")


def get_db_connection():
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the URLs table if it does not exist."""
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def validate_url(url):
    """Validate an HTTP or HTTPS URL."""

    if not isinstance(url, str):
        return False

    url = url.strip()

    if not url or len(url) > 2048:
        return False

    if any(character.isspace() for character in url):
        return False

    try:
        parsed = urlsplit(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.hostname:
            return False

        if parsed.username is not None or parsed.password is not None:
            return False

        # Validate the port, if one is present.
        _ = parsed.port

    except ValueError:
        return False

    return True


def generate_short_code(length=6):
    """Generate a random six-character code."""
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def save_url(original_url):
    """Save a URL and retry if a short code already exists."""

    with get_db_connection() as connection:
        for _ in range(10):
            short_code = generate_short_code()

            try:
                connection.execute(
                    """
                    INSERT INTO urls (original_url, short_code)
                    VALUES (?, ?)
                    """,
                    (original_url, short_code)
                )

                return short_code

            except sqlite3.IntegrityError:
                # A duplicate short code may have been generated.
                continue

    raise RuntimeError("Could not generate a unique short code.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/urls", methods=["POST"])
def create_short_url():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    original_url = data.get("url")

    if not isinstance(original_url, str) or not original_url.strip():
        return jsonify({
            "error": "The 'url' field is required."
        }), 400

    original_url = original_url.strip()

    if not validate_url(original_url):
        return jsonify({
            "error": "Enter a valid HTTP or HTTPS URL."
        }), 400

    try:
        short_code = save_url(original_url)
    except RuntimeError:
        app.logger.exception("Failed to generate a unique short code.")
        return jsonify({
            "error": "Could not create a short URL. Please try again."
        }), 500

    return jsonify({
        "original_url": original_url,
        "short_code": short_code,
        "short_url": request.host_url + short_code
    }), 201


@app.route("/api/urls/<short_code>", methods=["GET"])
def get_short_url(short_code):
    """Retrieve a saved URL using its short code."""

    with get_db_connection() as connection:
        row = connection.execute(
            """
            SELECT original_url, short_code, created_at
            FROM urls
            WHERE short_code = ?
            """,
            (short_code,)
        ).fetchone()

    if row is None:
        return jsonify({
            "error": "Short URL not found."
        }), 404

    return jsonify(dict(row)), 200

@app.route("/<short_code>", methods=["GET"])
def redirect_to_original_url(short_code):
    """Redirect a short URL to its original destination."""

    with get_db_connection() as connection:
        row = connection.execute(
            """
            SELECT original_url
            FROM urls
            WHERE short_code = ?
            """,
            (short_code,)
        ).fetchone()

    if row is None:
        return jsonify({
            "error": "Short URL not found."
        }), 404

    return redirect(row["original_url"], code=302)


init_db()


if __name__ == "__main__":
    app.run(debug=True)
