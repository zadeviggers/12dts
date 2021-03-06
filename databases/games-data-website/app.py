import sqlite3
from flask import Flask, render_template, g, request
import os

# Constants
DATABASE_NAME = 'games-data.sqlite'
DEBUG = False if 'ON_HEROKU' in os.environ else True
PORT = os.environ.get("PORT", 6969)


# Create server application
app = Flask(__name__)


def db_dict_factory(cursor, row):
    # Function to make database queries return dictionaries
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db():
    # Get database reference
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_NAME)
        db.row_factory = db_dict_factory
    return db


@app.teardown_appcontext
def close_connection(exception):
    # Close database connection on server stop
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    # Homepage
    return render_template("index.jinja")


@app.route("/game-sales")
def html_games():
    # Game sales page

    # Load databse reference
    db = get_db()
    cursor = db.cursor()

    games = None
    search = False

    # Get search query
    search_text = request.args.get('search-text')

    if (search_text is not None and search_text.strip() != ""):
        # If a search paramter was provided, search for games
        search = True
        games = cursor.execute("SELECT GameTitle, Year, Category, Platform, Publisher, Global FROM game_data WHERE GameTitle LIKE ? ORDER BY Year DESC",
                               ("%" + search_text + "%",)).fetchall()

    else:
        # If there wasn't a seach paramater, get list of all games
        games = cursor.execute(
            "SELECT GameTitle, Year, Category, Platform, Publisher, Global FROM game_data ORDER BY Year DESC").fetchall()

    updated_games = []
    for game in games:
        updated_games.append({
            "title": game["GameTitle"],
            "year": game["Year"],
            "genre": game["Category"],
            "platform": game["Platform"],
            "publisher": game["Publisher"],
            "sales": game["Global"],
        })

    return render_template("game-sales.jinja",
                           games=updated_games,
                           search=search,
                           # If search_text is none, replace it with an empty string
                           query=search_text or "")


# Start server, as long as this file is run directly
if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG)
