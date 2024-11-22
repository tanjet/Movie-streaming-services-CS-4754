from flask import Flask
from .db import init_db
from .routes import main

def create_app():
    app = Flask(__name__)

    # Configuration for MySQL database
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_PORT'] = 3306
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '123456'
    app.config['MYSQL_DATABASE'] = 'movie_streaming'


    # Initialize the database
    from .db import init_db
    init_db(app)

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
