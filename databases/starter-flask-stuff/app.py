import sqlite3
from flask import Flask, render_template, g, request

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

    # Load databse reference
    db = get_db()
    cursor = db.cursor()

    tags = None
    search = False

    # Get search query
    search_text = request.args.get('search-text')

    if (search_text is not None and search_text.strip() != ""):
        # If a search paramter was provided, search for tags
        search = True
        tags = cursor.execute("SELECT * FROM html_tags WHERE tag LIKE ?",
                              ("%" + search_text + "%",)).fetchall()

    else:
        # If there wasn't a seach paramater, get list of all tags
        tags = cursor.execute(
            "SELECT * FROM html_tags ORDER BY type DESC").fetchall()

    return render_template("html-tags.jinja", tags=tags, search=search)


# Start server, as long as this file is run directly
if __name__ == "__main__":
    app.run(port=6969, debug=True)
