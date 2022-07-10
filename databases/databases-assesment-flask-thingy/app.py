import sqlite3
from flask import Flask, render_template, g, request
import os

# Constants
DATABASE_NAME = 'cwc-data.db'
PORT = 6969
DEBUG = True

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


@app.route("/cricket-stats")
def cricket_stats():
    # Cricket statistics page

    # Load databse reference
    db = get_db()
    cursor = db.cursor()

    players = None
    search = False

    # Get search query
    search_text = request.args.get('search-text')

    if (search_text is not None and search_text.strip() != ""):
        # If a search paramter was provided, search for players
        search = True
        players = cursor.execute("SELECT * FROM cricket_world_cup_data WHERE Player LIKE ?",
                                 ("%" + search_text + "%",)).fetchall()

    else:
        # If there wasn't a seach paramater, get list of all players
        players = cursor.execute(
            "SELECT * FROM cricket_world_cup_data").fetchall()

    updated_players = []
    for player in players:
        updated_players.append({
            "name": player["Player"],
            "country": player["Country"],
            "matches": player["Matches"],
            "innings": player["Innings"],
            "not_outs": player["NotOuts"],
            "runs": player["Runs"],
            "high_score": player["HighScore"],
            "average": player["Average"],
            "balls_faced": player["BallsFaced"],
            "strike_rate": player["StrikeRate"],
        })

    return render_template("cricket-stats.jinja",
                           players=updated_players,
                           search=search,
                           # If search_text is none, replace it with an empty string
                           query=search_text or "")


# Start server, as long as this file is run directly
if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG)
