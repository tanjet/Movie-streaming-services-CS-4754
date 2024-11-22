import mysql.connector
from flask import g, current_app

def get_db():
    """
    Create a connection to the database and store it in Flask's global context `g`.
    If a connection already exists, reuse it.
    """
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],          # Hostname (e.g., localhost)
            user=current_app.config['MYSQL_USER'],          # MySQL username
            password=current_app.config['MYSQL_PASSWORD'],  # MySQL password
            database=current_app.config['MYSQL_DATABASE']   # Database name
        )
    return g.db

def close_db(e=None):
    """
    Close the database connection at the end of a request.
    Flask calls this automatically if registered with `teardown_appcontext`.
    """
    db = g.pop('db', None)  # Remove the database connection from the `g` object
    if db is not None:
        db.close()

def init_db(app):
    """
    Register the `close_db` function with Flask so it gets called automatically
    when the application context is torn down (e.g., at the end of a request).
    """
    app.teardown_appcontext(close_db)

