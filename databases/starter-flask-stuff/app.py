import sqlite3
from flask import Flask, render_template, g

# Constants
DATABASE_NAME = 'zades-data.sqlite'


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


@app.route("/html-tags")
def html_tags():
    # HTML tags page
    db = get_db()
    cursor = db.cursor()
    tags = cursor.execute("SELECT * FROM html_tags").fetchall()
    return render_template("html-tags.jinja", tags=tags)


# Start server, as long as this file is run directly
if __name__ == "__main__":
    app.run(port=6969, debug=True)
